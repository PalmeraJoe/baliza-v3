from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from baliza.application.use_cases import (
    acknowledge_alert,
    build_dss_package,
    calculate_indicator,
    evaluate_and_maybe_alert,
    record_human_decision,
    record_human_outcome,
    record_observation,
    record_human_action,
)
from baliza.domain.actor import Actor
from baliza.domain.enums import DataQualityFacet, PublicationStatus
from baliza.domain.hashing import sha256_canonical
from baliza.domain.ids import ActorId
from baliza.domain.protocol import Protocol, ProtocolVersion
from baliza.domain.ids import ProtocolId, ProtocolVersionId
from baliza.domain.quality import DataQuality
from baliza.domain.rule import RuleVersion
from baliza.infrastructure.clock import FixedClock
from baliza.infrastructure.memory import InMemoryActorRepository
from baliza.infrastructure.persistence.models import (
    AlertRow,
    AuditEventRow,
    Base,
    EvidenceItemRow,
    EvidencePackageRow,
    RuleEvaluationRow,
    make_engine,
)
from baliza.infrastructure.persistence.repositories import SqlUnitOfWork, open_database, sql_repositories
from baliza.interfaces.api.app import create_app

NOW = datetime(2026, 9, 30, 12, 0, tzinfo=UTC)


def _chain(repos, published_indicator, published_rule, *, with_protocol: bool = False):
    indicator, iversion = published_indicator
    rule, rversion = published_rule
    repos.indicators.add_definition(indicator, iversion)
    draft = RuleVersion(
        id=rversion.id,
        rule_id=rule.id,
        version=rversion.version,
        thresholds=rversion.thresholds,
        operator=rversion.operator,
        threshold_name=rversion.threshold_name,
        severity_if_triggered=rversion.severity_if_triggered,
        status=PublicationStatus.DRAFT,
    )
    repos.rules.add_rule(rule, draft)
    from baliza.application.use_cases import activate_rule_version

    activate_rule_version(repos, draft)
    obs = record_observation(
        repos,
        variable="demo_metric",
        unit="demo",
        observed_at=NOW,
        quality=DataQuality(facet=DataQualityFacet.VALID, score=0.9),
        value=30.4,
        spatial_ref="station-S1",
        metadata={"label": "DEMO / NON-SCIENTIFIC"},
    )
    ivalue = calculate_indicator(repos, version=iversion, observation=obs)
    result = evaluate_and_maybe_alert(
        repos,
        observation=obs,
        indicator_value=ivalue,
        rule=rule,
        rule_version=draft.publish(),
    )
    protocol = None
    if with_protocol:
        protocol = ProtocolVersion(
            id=ProtocolVersionId(),
            protocol_id=ProtocolId(),
            version="0.0.1-demo",
            options=("watch", "no_action"),
            status=PublicationStatus.PUBLISHED,
        )
    package = build_dss_package(repos, alert=result.alert, protocol=protocol, extra_gaps=["demo-gap"])
    return result, package


def test_snapshot_keeps_alert_evidence_thresholds_and_options(repos, published_indicator, published_rule):
    result, package = _chain(repos, published_indicator, published_rule, with_protocol=True)
    actor = Actor(id=ActorId(), display_name="operator")
    decision = record_human_decision(
        repos, actor=actor, package=package, justification="reviewed the demo signal", selected_option="watch"
    )
    snap = repos.dss.get_snapshot(decision.dss_context_snapshot_id)
    frozen_alert = snap.payload["alerts_at_freeze"][0]
    assert frozen_alert["alert_status_at_freeze"] == "OPEN"
    assert frozen_alert["severity"] == "critical"
    descriptor = snap.payload["evidence_descriptors_at_freeze"][0]
    assert descriptor["kind"] in {"primary", "derived"}
    assert descriptor["epistemic_label"] == "FACT"
    assert snap.payload["thresholds_at_freeze"][0]["thresholds"]["anomaly_high"] == 2.0
    assert snap.payload["protocol_options_at_freeze"] == ("watch", "no_action")
    assert snap.content_hash == sha256_canonical(snap.payload)

    acknowledge_alert(repos, alert=result.alert, actor=actor)
    package.add_gap("after-decision")
    again = repos.dss.get_snapshot(decision.dss_context_snapshot_id)
    assert again.payload["alerts_at_freeze"][0]["alert_status_at_freeze"] == "OPEN"
    assert again.content_hash == snap.content_hash
    assert "after-decision" not in again.payload["gaps"]


def test_sqlite_historical_snapshot_survives_later_mutations(published_indicator, published_rule):
    factory, _engine = open_database("sqlite://", create_schema=True)
    session = factory()
    repos = sql_repositories(session, FixedClock(NOW))
    result, package = _chain(repos, published_indicator, published_rule, with_protocol=True)
    actor = Actor(id=ActorId(), display_name="operator")
    repos.actors.add(actor)
    decision = record_human_decision(
        repos, actor=actor, package=package, justification="DEMO / NON-SCIENTIFIC hold", selected_option="watch"
    )
    action = record_human_action(repos, decision=decision, description="log", actor=actor, action_type="log")
    record_human_outcome(repos, action=action, decision=decision, notes="logged")
    session.commit()
    snapshot_id = decision.dss_context_snapshot_id
    alert_id = result.alert.id.value
    item_id = result.evidence_items[0].id.value
    before_hash = decision.snapshot_hash
    session.close()

    mutate = factory()
    alert = mutate.get(AlertRow, alert_id)
    alert.status = "ACKNOWLEDGED"
    item = mutate.get(EvidenceItemRow, item_id)
    item.narrative = "changed-after-decision"
    mutate.execute(text('UPDATE rule_evaluations SET thresholds_applied = \'{"anomaly_high": 99}\''))
    mutate.commit()
    mutate.close()

    fresh = factory()
    loaded = sql_repositories(fresh, FixedClock(NOW)).dss.get_snapshot(snapshot_id)
    assert loaded.content_hash == before_hash
    assert loaded.payload["alerts_at_freeze"][0]["alert_status_at_freeze"] == "OPEN"
    narratives = [row["narrative"] for row in loaded.payload["evidence_descriptors_at_freeze"]]
    assert "changed-after-decision" not in narratives
    assert loaded.payload["thresholds_at_freeze"][0]["thresholds"]["anomaly_high"] == 2.0
    assert loaded.payload["protocol_options_at_freeze"] == ("watch", "no_action")
    fresh.close()


def _count(session: Session) -> dict[str, int]:
    return {
        "evaluations": len(session.scalars(select(RuleEvaluationRow)).all()),
        "items": len(session.scalars(select(EvidenceItemRow)).all()),
        "packages": len(session.scalars(select(EvidencePackageRow)).all()),
        "alerts": len(session.scalars(select(AlertRow)).all()),
        "audits": len(session.scalars(select(AuditEventRow)).all()),
    }


def test_sqlite_rollback_leaves_no_partial_critical_path(published_indicator, published_rule):
    factory, _engine = open_database("sqlite://", create_schema=True)

    def run(fail: str) -> None:
        session = factory()
        repos = sql_repositories(session, FixedClock(NOW))
        indicator, iversion = published_indicator
        rule, rversion = published_rule
        repos.indicators.add_definition(indicator, iversion)
        repos.rules.add_rule(rule, rversion)
        obs = record_observation(
            repos,
            variable="demo_metric",
            unit="demo",
            observed_at=NOW,
            quality=DataQuality(facet=DataQualityFacet.VALID, score=0.9),
            value=30.4,
        )
        ivalue = calculate_indicator(repos, version=iversion, observation=obs)
        if fail == "evidence":
            def boom(_package):
                raise RuntimeError("evidence failed")

            repos.evidence.add_package = boom
        elif fail == "alert":
            def boom(_alert):
                raise RuntimeError("alert failed")

            repos.alerts.add = boom
        elif fail == "commit":
            def boom():
                raise RuntimeError("commit failed")

            repos.uow.commit = boom
        with pytest.raises(RuntimeError):
            evaluate_and_maybe_alert(
                repos, observation=obs, indicator_value=ivalue, rule=rule, rule_version=rversion
            )
        session.close()
        check = factory()
        assert _count(check) == {"evaluations": 0, "items": 0, "packages": 0, "alerts": 0, "audits": 0}
        check.close()

    run("evidence")
    run("alert")
    run("commit")


def test_http_sqlite_persists_observation():
    application = create_app(database_url="sqlite://", create_schema=True)
    client = TestClient(application)
    created = client.post(
        "/observations",
        json={
            "variable": "demo_metric",
            "unit": "demo",
            "observed_at": NOW.isoformat(),
            "value": 1.0,
            "quality_facet": "valid",
            "quality_score": 0.9,
            "subject": "station-S1",
        },
    )
    assert created.status_code == 200
    observation_id = created.json()["id"]
    session = application.state.session_factory()
    from baliza.domain.ids import ObservationId
    from baliza.infrastructure.persistence.repositories import SqlObservationRepository

    loaded = SqlObservationRepository(session).get(ObservationId(observation_id))
    session.close()
    assert loaded is not None
    assert loaded.variable == "demo_metric"
    assert application.state.session_factory is not None
