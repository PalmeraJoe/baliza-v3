from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from baliza.application.queries import alert_chain, decision_context
from baliza.application.use_cases import (
    Repositories,
    acknowledge_alert,
    activate_rule_version,
    build_dss_package,
    calculate_indicator,
    evaluate_and_maybe_alert,
    record_human_action,
    record_human_decision,
    record_human_outcome,
    record_observation,
)
from baliza.domain.action import record_action
from baliza.domain.actor import Actor
from baliza.domain.enums import ComparisonOp, DataQualityFacet, PublicationStatus, RuleOutcome
from baliza.domain.errors import ActionWithoutDecision, PublishedVersionImmutable
from baliza.domain.ids import ActorId, IndicatorId, IndicatorVersionId, ProtocolId, ProtocolVersionId, RuleId, RuleVersionId
from baliza.domain.indicator import Indicator, IndicatorVersion, calculate_from_observations
from baliza.domain.protocol import Protocol, ProtocolVersion, recommendations_from_protocol
from baliza.domain.quality import DataQuality
from baliza.domain.rule import Rule, RuleVersion, Threshold, evaluate_rule
from baliza.infrastructure.clock import FixedClock
from baliza.infrastructure.memory import (
    InMemoryActionRepository,
    InMemoryActorRepository,
    InMemoryAlertRepository,
    InMemoryAuditRepository,
    InMemoryDecisionRepository,
    InMemoryDssRepository,
    InMemoryEvidenceRepository,
    InMemoryIndicatorRepository,
    InMemoryObservationRepository,
    InMemoryRuleRepository,
    MemoryUnitOfWork,
)
from baliza.infrastructure.persistence.models import Base, make_engine
from baliza.infrastructure.persistence.repositories import (
    SqlActionRepository,
    SqlAlertRepository,
    SqlAuditRepository,
    SqlDecisionRepository,
    SqlDssRepository,
    SqlEvidenceRepository,
    SqlIndicatorRepository,
    SqlObservationRepository,
    SqlRuleRepository,
    SqlUnitOfWork,
)
from baliza.interfaces.api.app import create_app

NOW = datetime(2026, 9, 30, 12, 0, tzinfo=UTC)


def _obs(repos, *, value, facet, variable="demo_metric"):
    return record_observation(
        repos,
        variable=variable,
        unit="demo",
        observed_at=NOW,
        quality=DataQuality(facet=facet, score=0.9 if facet is DataQualityFacet.VALID else None),
        value=value,
        spatial_ref="station-S1",
        metadata={"label": "DEMO / NON-SCIENTIFIC", "subject": "station-S1"},
    )


def test_missing_and_invalid_observations_are_not_safe(repos) -> None:
    missing = _obs(repos, value=None, facet=DataQualityFacet.MISSING)
    invalid = _obs(repos, value=None, facet=DataQualityFacet.INVALID)
    assert missing.quality.implies_no_risk() is False
    assert invalid.quality.implies_no_risk() is False
    assert missing.value is None
    actions = {e.action for e in repos.audit.events}
    assert "observation.recorded" in actions


def test_indicator_keeps_provenance(repos, published_indicator) -> None:
    indicator, version = published_indicator
    repos.indicators.add_definition(indicator, version)
    obs = _obs(repos, value=30.4, facet=DataQualityFacet.VALID)
    value = calculate_indicator(repos, version=version, observation=obs)
    assert value.source_observation_ids == (obs.id,)
    assert value.indicator_version == "1.0.0"
    assert value.value == pytest.approx(3.4)
    assert any(e.action == "indicator.calculated" for e in repos.audit.events)


def test_aggregate_does_not_treat_missing_as_zero(now) -> None:
    version = IndicatorVersion(
        id=IndicatorVersionId(),
        indicator_id=IndicatorId(),
        version="1.0.0",
        unit="demo",
        formula_kind="mean",
        status=PublicationStatus.PUBLISHED,
    )
    from baliza.domain.observation import Observation
    from baliza.domain.ids import ObservationId

    present = Observation(
        id=ObservationId(),
        variable="demo_metric",
        unit="demo",
        observed_at=now,
        processed_at=now,
        quality=DataQuality(facet=DataQualityFacet.VALID),
        value=10.0,
    )
    missing = Observation(
        id=ObservationId(),
        variable="demo_metric",
        unit="demo",
        observed_at=now,
        processed_at=now,
        quality=DataQuality(facet=DataQualityFacet.MISSING),
        value=None,
    )
    value = calculate_from_observations(version=version, observations=(present, missing), computed_at=now)
    assert value.value is None
    assert value.quality.facet is DataQualityFacet.MISSING
    assert value.quality.implies_no_risk() is False


@pytest.mark.parametrize(
    ("op", "bound", "upper", "sample", "expected"),
    [
        (ComparisonOp.GT, 2.0, None, 3.0, RuleOutcome.TRIGGERED),
        (ComparisonOp.GTE, 2.0, None, 2.0, RuleOutcome.TRIGGERED),
        (ComparisonOp.LT, 2.0, None, 1.0, RuleOutcome.TRIGGERED),
        (ComparisonOp.LTE, 2.0, None, 2.0, RuleOutcome.TRIGGERED),
        (ComparisonOp.EQ, 2.0, None, 2.0, RuleOutcome.TRIGGERED),
        (ComparisonOp.EQ, 2.0, None, 2.1, RuleOutcome.NOT_TRIGGERED),
        (ComparisonOp.BETWEEN, 1.0, 3.0, 2.0, RuleOutcome.TRIGGERED),
        (ComparisonOp.BETWEEN, 1.0, 3.0, 4.0, RuleOutcome.NOT_TRIGGERED),
    ],
)
def test_operators(op, bound, upper, sample, expected) -> None:
    rule = Rule(id=RuleId(), name="demo")
    thresholds = [Threshold("limit", bound)]
    if upper is not None:
        thresholds.append(Threshold("limit_upper", upper))
    version = RuleVersion(
        id=RuleVersionId(),
        rule_id=rule.id,
        version="1.0.0",
        thresholds=tuple(thresholds),
        operator=op,
        threshold_name="limit",
        severity_if_triggered="warning",
        status=PublicationStatus.PUBLISHED,
    )
    from baliza.domain.ids import IndicatorValueId, ObservationId
    from baliza.domain.indicator import IndicatorValue

    indicator = IndicatorValue(
        id=IndicatorValueId(),
        indicator_id=IndicatorId(),
        indicator_version_id=IndicatorVersionId(),
        indicator_version="1.0.0",
        computed_at=NOW,
        unit="demo",
        source_observation_ids=(ObservationId(),),
        quality=DataQuality(facet=DataQualityFacet.VALID),
        value=sample,
    )
    outcome = evaluate_rule(rule=rule, version=version, indicator_value=indicator, evaluated_at=NOW).outcome
    assert outcome is expected


def test_insufficient_data_is_not_not_triggered(published_rule) -> None:
    rule, version = published_rule
    ev = evaluate_rule(rule=rule, version=version, indicator_value=None, evaluated_at=NOW)
    assert ev.outcome is RuleOutcome.UNKNOWN
    assert ev.outcome is not RuleOutcome.NOT_TRIGGERED
    assert ev.outcome.value != "safe"


def test_suspect_quality_is_not_a_clear(published_rule) -> None:
    rule, version = published_rule
    from baliza.domain.ids import IndicatorValueId, ObservationId
    from baliza.domain.indicator import IndicatorValue

    indicator = IndicatorValue(
        id=IndicatorValueId(),
        indicator_id=IndicatorId(),
        indicator_version_id=IndicatorVersionId(),
        indicator_version="1.0.0",
        computed_at=NOW,
        unit="demo",
        source_observation_ids=(ObservationId(),),
        quality=DataQuality(facet=DataQualityFacet.SUSPECT),
        value=9.0,
    )
    ev = evaluate_rule(rule=rule, version=version, indicator_value=indicator, evaluated_at=NOW)
    assert ev.outcome is RuleOutcome.INSUFFICIENT_DATA


def test_acknowledge_is_not_a_decision(repos, published_indicator, published_rule) -> None:
    indicator, iversion = published_indicator
    rule, rversion = published_rule
    repos.indicators.add_definition(indicator, iversion)
    repos.rules.add_rule(rule, rversion)
    obs = _obs(repos, value=30.4, facet=DataQualityFacet.VALID)
    ivalue = calculate_indicator(repos, version=iversion, observation=obs)
    result = evaluate_and_maybe_alert(
        repos, observation=obs, indicator_value=ivalue, rule=rule, rule_version=rversion
    )
    actor = Actor(id=ActorId(), display_name="operator")
    repos.actors.add(actor)
    acknowledge_alert(repos, alert=result.alert, actor=actor)
    assert repos.decisions._items == {}
    assert result.alert.is_decision() is False


def test_protocol_options_do_not_create_actions(repos) -> None:
    protocol = Protocol(id=ProtocolId(), name="demo-watch")
    version = ProtocolVersion(
        id=ProtocolVersionId(),
        protocol_id=protocol.id,
        version="0.0.1-demo",
        options=("watch", "no_action"),
        status=PublicationStatus.PUBLISHED,
    )
    views = recommendations_from_protocol(version)
    package = build_dss_package(repos, protocol=version)
    assert package.recommendations[0].source == "protocol"
    assert views[0].epistemic_label == "RECOMMENDATION"
    assert repos.actions.actions == {}
    with pytest.raises(PublishedVersionImmutable):
        version.with_options(("other",))


def test_evidence_failure_does_not_leave_an_alert(repos, published_indicator, published_rule) -> None:
    repos.uow = MemoryUnitOfWork(repos)
    indicator, iversion = published_indicator
    rule, rversion = published_rule
    repos.indicators.add_definition(indicator, iversion)
    repos.rules.add_rule(rule, rversion)
    obs = _obs(repos, value=30.4, facet=DataQualityFacet.VALID)
    ivalue = calculate_indicator(repos, version=iversion, observation=obs)

    def boom(_package):
        raise RuntimeError("evidence store failed")

    repos.evidence.add_package = boom
    with pytest.raises(RuntimeError):
        evaluate_and_maybe_alert(
            repos, observation=obs, indicator_value=ivalue, rule=rule, rule_version=rversion
        )
    assert repos.alerts._items == {}
    assert repos.rules.evaluations == {}


def test_alert_and_snapshot_failures_roll_back(repos, published_indicator, published_rule) -> None:
    repos.uow = MemoryUnitOfWork(repos)
    indicator, iversion = published_indicator
    rule, rversion = published_rule
    repos.indicators.add_definition(indicator, iversion)
    repos.rules.add_rule(rule, rversion)
    obs = _obs(repos, value=30.4, facet=DataQualityFacet.VALID)
    ivalue = calculate_indicator(repos, version=iversion, observation=obs)

    def alert_boom(_alert):
        raise RuntimeError("alert store failed")

    repos.alerts.add = alert_boom
    with pytest.raises(RuntimeError):
        evaluate_and_maybe_alert(
            repos, observation=obs, indicator_value=ivalue, rule=rule, rule_version=rversion
        )
    assert repos.evidence.packages == {}
    assert repos.alerts._items == {}

    repos.alerts.add = InMemoryAlertRepository.add.__get__(repos.alerts, InMemoryAlertRepository)
    result = evaluate_and_maybe_alert(
        repos, observation=obs, indicator_value=ivalue, rule=rule, rule_version=rversion
    )
    package = build_dss_package(repos, alert=result.alert)
    actor = Actor(id=ActorId(), display_name="operator")

    def snap_boom(_snapshot):
        raise RuntimeError("snapshot store failed")

    repos.dss.add_snapshot = snap_boom
    with pytest.raises(RuntimeError):
        record_human_decision(
            repos, actor=actor, package=package, justification="should not stick", selected_option="watch"
        )
    assert repos.decisions._items == {}


def test_action_requires_decision() -> None:
    with pytest.raises(ActionWithoutDecision):
        record_action(decision_id=None, acted_at=NOW, description="skip", action_type="notify")


def test_multi_alert_decision(repos, published_indicator, published_rule) -> None:
    indicator, iversion = published_indicator
    rule, rversion = published_rule
    repos.indicators.add_definition(indicator, iversion)
    repos.rules.add_rule(rule, rversion)
    alerts = []
    for value in (30.4, 31.0):
        obs = _obs(repos, value=value, facet=DataQualityFacet.VALID, variable=f"demo_metric_{value}")
        ivalue = calculate_indicator(repos, version=iversion, observation=obs)
        result = evaluate_and_maybe_alert(
            repos, observation=obs, indicator_value=ivalue, rule=rule, rule_version=rversion
        )
        alerts.append(result.alert)
    actor = Actor(id=ActorId(), display_name="operator")
    package = build_dss_package(repos, alerts=alerts, extra_gaps=["demo-gap"])
    decision = record_human_decision(
        repos, actor=actor, package=package, justification="reviewed both signals", selected_option="watch"
    )
    snap = repos.dss.get_snapshot(decision.dss_context_snapshot_id)
    assert len(package.alert_ids) == 2
    assert snap.payload["alert_ids"] == tuple(str(a.id) for a in alerts)
    action = record_human_action(
        repos, decision=decision, description="notify duty officer", actor=actor, action_type="notify"
    )
    before = snap.content_hash
    record_human_outcome(repos, action=action, decision=decision, notes="officer notified")
    assert repos.dss.get_snapshot(decision.dss_context_snapshot_id).content_hash == before


def test_end_to_end_sqlite_chain(published_indicator, published_rule) -> None:
    engine = make_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    indicator, iversion = published_indicator
    rule, rversion = published_rule
    actor = Actor(id=ActorId(), display_name="ACTOR1")
    with Session(engine) as session:
        repos = Repositories(
            actors=InMemoryActorRepository(),
            observations=SqlObservationRepository(session),
            indicators=SqlIndicatorRepository(session),
            rules=SqlRuleRepository(session),
            evidence=SqlEvidenceRepository(session),
            alerts=SqlAlertRepository(session),
            dss=SqlDssRepository(session),
            decisions=SqlDecisionRepository(session),
            actions=SqlActionRepository(session),
            audit=SqlAuditRepository(session),
            clock=FixedClock(NOW),
            uow=SqlUnitOfWork(session),
        )
        repos.actors.add(actor)
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
        activate_rule_version(repos, draft)
        obs = _obs(repos, value=30.4, facet=DataQualityFacet.VALID)
        ivalue = calculate_indicator(repos, version=iversion, observation=obs)
        result = evaluate_and_maybe_alert(
            repos, observation=obs, indicator_value=ivalue, rule=rule, rule_version=draft.publish()
        )
        package = build_dss_package(repos, alert=result.alert, extra_gaps=["demo-gap"])
        decision = record_human_decision(
            repos,
            actor=actor,
            package=package,
            justification="DEMO / NON-SCIENTIFIC hold",
            selected_option="watch",
        )
        action = record_human_action(
            repos, decision=decision, description="log the review", actor=actor, action_type="log"
        )
        outcome = record_human_outcome(repos, action=action, decision=decision, notes="logged")
        session.commit()
        alert_id = result.alert.id
        decision_id = decision.id
        outcome_id = outcome.id
    with Session(engine) as session:
        repos = Repositories(
            actors=InMemoryActorRepository(),
            observations=SqlObservationRepository(session),
            indicators=SqlIndicatorRepository(session),
            rules=SqlRuleRepository(session),
            evidence=SqlEvidenceRepository(session),
            alerts=SqlAlertRepository(session),
            dss=SqlDssRepository(session),
            decisions=SqlDecisionRepository(session),
            actions=SqlActionRepository(session),
            audit=SqlAuditRepository(session),
            clock=FixedClock(NOW),
        )
        chain = alert_chain(repos, alert_id)
        ctx = decision_context(repos, decision_id)
        loaded_outcome = repos.actions.get_outcome(outcome_id)
        assert chain.observations[0].variable == "demo_metric"
        assert chain.indicator_values[0].value == pytest.approx(3.4)
        assert chain.evaluations[0].thresholds_applied["anomaly_high"] == 2.0
        assert chain.evaluations[0].rule_version == "1.0.0"
        assert chain.evidence_package is not None
        assert chain.alert.evidence_package_id == chain.evidence_package.id
        assert ctx.snapshot.content_hash == ctx.decision.snapshot_hash
        assert str(chain.alert.id) in ctx.snapshot.payload["alert_ids"]
        assert loaded_outcome.decision_id == ctx.decision.id
        from baliza.infrastructure.persistence.models import AuditEventRow

        recorded = {row.action for row in session.query(AuditEventRow).all()}
        for required in {
            "observation.recorded",
            "indicator.calculated",
            "rule.evaluated",
            "evidence.package_created",
            "alert.created",
            "dss.package_opened",
            "dss_context_snapshot.frozen",
            "decision.recorded",
            "action.recorded",
            "outcome.recorded",
            "rule_version.activated",
        }:
            assert required in recorded


def test_api_observation_roundtrip() -> None:
    app = create_app()
    client = TestClient(app)
    created = client.post(
        "/observations",
        json={
            "variable": "demo_metric",
            "unit": "demo",
            "observed_at": NOW.isoformat(),
            "value": 1.5,
            "quality_facet": "missing",
            "subject": "station-S1",
            "spatial_ref": "station-S1",
        },
    )
    assert created.status_code == 200
    body = created.json()
    assert body["implies_no_risk"] is False
    loaded = client.get(f"/observations/{body['id']}")
    assert loaded.status_code == 200
    assert loaded.json()["quality"] == "missing"
    assert loaded.json()["metadata"]["label"] == "DEMO / NON-SCIENTIFIC"
