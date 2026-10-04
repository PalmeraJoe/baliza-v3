from datetime import UTC, datetime

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from baliza.application.use_cases import activate_rule_version, record_human_action, record_human_decision, record_human_outcome
from baliza.domain.actor import Actor
from baliza.domain.agent import AgentRun
from baliza.domain.ids import AgentId, AgentRunId, AgentVersionId, IndicatorId, IndicatorVersionId
from baliza.domain.decision import record_decision
from baliza.domain.dss import DssPackage, RecommendationView, freeze_dss_package
from baliza.domain.enums import ComparisonOp, EpistemicLabel, EvidenceKind, PublicationStatus, RuleOutcome
from baliza.domain.errors import InvariantViolation, MissingActor, MissingSnapshot
from baliza.domain.hashing import sha256_canonical
from baliza.domain.ids import (
    ActorId,
    AlertId,
    DssPackageId,
    EvidenceItemId,
    EvidencePackageId,
    IndicatorValueId,
    ObservationId,
    RuleEvaluationId,
    RuleId,
    RuleVersionId,
)
from baliza.domain.evidence import EvidenceItem, EvidencePackage
from baliza.domain.indicator import Indicator, IndicatorValue, IndicatorVersion
from baliza.domain.observation import Observation
from baliza.domain.quality import DataQuality, DataQualityFacet
from baliza.domain.rule import Rule, RuleEvaluation, RuleVersion, Threshold
from baliza.infrastructure.persistence.models import (
    AlertRow,
    Base,
    DecisionRow,
    DssSnapshotRow,
    ImmutablePersistenceError,
    RuleVersionRow,
    make_engine,
)
from baliza.infrastructure.persistence.repositories import (
    SqlAlertRepository,
    SqlDecisionRepository,
    SqlDssRepository,
    SqlEvidenceRepository,
    SqlIndicatorRepository,
    SqlObservationRepository,
    SqlRuleRepository,
)

NOW = datetime(2026, 9, 30, 12, 0, tzinfo=UTC)


def _package() -> DssPackage:
    return DssPackage(
        id=DssPackageId(),
        opened_at=NOW,
        recommendations=[RecommendationView("r1", "protocol", "monitor")],
        gaps=["missing-current"],
    )


def test_nested_snapshot_cannot_be_mutated() -> None:
    inner = ["keep"]
    original_gaps = ["missing-current"]
    package = _package()
    package.gaps = original_gaps
    extra = {"layer": {"inner": inner, "bag": {"a", "b"}}}
    snapshot = freeze_dss_package(package, frozen_at=NOW, extra=extra)
    before = sha256_canonical(snapshot.payload)
    assert snapshot.content_hash == before

    with pytest.raises(AttributeError):
        snapshot.payload["gaps"].append("tamper")
    with pytest.raises(TypeError):
        snapshot.payload["recommendations"][0]["text"] = "tamper"
    with pytest.raises(TypeError):
        snapshot.payload["layer"]["inner"] = ("tamper",)
    inner.append("changed-original")
    original_gaps.append("changed-original")
    package.add_gap("live-only")

    assert snapshot.payload["gaps"] == ("missing-current",)
    assert snapshot.payload["layer"]["inner"] == ("keep",)
    assert snapshot.content_hash == before
    assert sha256_canonical(snapshot.payload) == before


def test_rule_evaluation_input_snapshot_is_frozen() -> None:
    evaluation = RuleEvaluation(
        id=RuleEvaluationId(),
        rule_id=RuleId(),
        rule_version_id=RuleVersionId(),
        rule_version="1.0.0",
        evaluated_at=NOW,
        outcome=RuleOutcome.TRIGGERED,
        input_indicator_value_ids=(),
        thresholds_applied={"anomaly_high": 2.0},
        evaluator_engine_id="baliza.rules.threshold_v1",
        reason="test",
        input_snapshot={"nested": {"values": [1]}},
    )
    with pytest.raises(AttributeError):
        evaluation.input_snapshot["nested"]["values"].append(2)
    with pytest.raises(TypeError):
        evaluation.input_snapshot["nested"]["values"] = (9,)
    with pytest.raises(TypeError):
        evaluation.thresholds_applied["anomaly_high"] = 9.0


def test_decision_requires_actor_snapshot_justification_and_time(now) -> None:
    package = _package()
    snapshot = freeze_dss_package(package, frozen_at=now)
    with pytest.raises(MissingActor):
        record_decision(
            actor_id=None,
            snapshot=snapshot,
            decided_at=now,
            justification="because",
            selected_option="watch",
        )
    with pytest.raises(MissingSnapshot):
        record_decision(
            actor_id=ActorId(),
            snapshot=None,
            decided_at=now,
            justification="because",
            selected_option="watch",
        )
    with pytest.raises(InvariantViolation):
        record_decision(
            actor_id=ActorId(),
            snapshot=snapshot,
            decided_at=now,
            justification="  ",
            selected_option="watch",
        )
    with pytest.raises(ValueError):
        record_decision(
            actor_id=ActorId(),
            snapshot=snapshot,
            decided_at=datetime(2026, 9, 30, 12, 0),
            justification="because",
            selected_option="watch",
        )
    run = AgentRun(
        id=AgentRunId(),
        agent_id=AgentId(),
        agent_version_id=AgentVersionId(),
        agent_version="0.1.0",
        started_at=now,
        completed_at=None,
        epistemic_label=EpistemicLabel.INFERENCE,
        summary="assistive only",
    )
    assert run.is_decision() is False


def test_audit_events_for_activation_snapshot_action_outcome(repos, published_rule) -> None:
    rule, version = published_rule
    draft = RuleVersion(
        id=version.id,
        rule_id=rule.id,
        version=version.version,
        thresholds=version.thresholds,
        operator=version.operator,
        threshold_name=version.threshold_name,
        severity_if_triggered=version.severity_if_triggered,
        status=PublicationStatus.DRAFT,
    )
    repos.rules.add_rule(rule, draft)
    activate_rule_version(repos, draft)
    actor = Actor(id=ActorId(), display_name="operator")
    repos.actors.add(actor)
    package = _package()
    decision = record_human_decision(repos, actor=actor, package=package, justification="hold", selected_option="watch")
    action = record_human_action(repos, decision=decision, description="notify team", actor=actor)
    record_human_outcome(repos, action=action, decision=decision, notes="team notified")
    actions = {event.action for event in repos.audit.events}
    assert "rule_version.activated" in actions
    assert "dss_context_snapshot.frozen" in actions
    assert "action.recorded" in actions
    assert "outcome.recorded" in actions


def _engine():
    engine = make_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return engine


def test_snapshot_is_insert_only_and_survives_reload() -> None:
    engine = _engine()
    package = _package()
    snapshot = freeze_dss_package(package, frozen_at=NOW)
    with Session(engine) as session:
        SqlDssRepository(session).save_package(package)
        SqlDssRepository(session).add_snapshot(snapshot)
        session.commit()
    package.add_gap("after-freeze")
    with Session(engine) as session:
        loaded = SqlDssRepository(session).get_snapshot(snapshot.id)
        assert loaded is not None
        assert loaded.content_hash == snapshot.content_hash
        assert loaded.payload["gaps"] == ("missing-current",)
        row = session.get(DssSnapshotRow, snapshot.id.value)
        row.content_hash = "tampered"
        with pytest.raises(ImmutablePersistenceError):
            session.flush()
        session.rollback()
        session.delete(session.get(DssSnapshotRow, snapshot.id.value))
        with pytest.raises(ImmutablePersistenceError):
            session.flush()


def test_published_rule_version_unique_and_immutable() -> None:
    engine = _engine()
    rule = Rule(id=RuleId(), name="thermal")
    draft = RuleVersion(
        id=RuleVersionId(),
        rule_id=rule.id,
        version="1.0.0",
        thresholds=(Threshold("anomaly_high", 2.0),),
        operator=ComparisonOp.GT,
        threshold_name="anomaly_high",
        severity_if_triggered="critical",
        status=PublicationStatus.DRAFT,
    )
    with Session(engine) as session:
        repo = SqlRuleRepository(session)
        repo.add_rule(rule, draft)
        session.commit()
        published = draft.publish()
        repo.replace_version(published)
        session.commit()
        row = session.get(RuleVersionRow, draft.id.value)
        row.threshold_name = "other"
        with pytest.raises(ImmutablePersistenceError):
            session.flush()
        session.rollback()
        session.delete(session.get(RuleVersionRow, draft.id.value))
        with pytest.raises(ImmutablePersistenceError):
            session.flush()
    newer = RuleVersion(
        id=RuleVersionId(),
        rule_id=rule.id,
        version="1.1.0",
        thresholds=(Threshold("anomaly_high", 2.5),),
        operator=ComparisonOp.GT,
        threshold_name="anomaly_high",
        severity_if_triggered="critical",
        status=PublicationStatus.PUBLISHED,
    )
    with Session(engine) as session:
        SqlRuleRepository(session).add_rule(rule, newer)
        session.commit()
        duplicate = RuleVersionRow(
            id=RuleVersionId().value,
            rule_id=rule.id.value,
            version="1.0.0",
            status="published",
            operator="gt",
            threshold_name="anomaly_high",
            thresholds={"anomaly_high": 2.0},
            severity_if_triggered="critical",
            evaluator_engine_id="baliza.rules.threshold_v1",
        )
        session.add(duplicate)
        with pytest.raises(IntegrityError):
            session.flush()


def test_evidence_chain_roundtrip_across_sessions() -> None:
    engine = _engine()
    observation = Observation(
        id=ObservationId(),
        variable="sst",
        unit="degC",
        observed_at=NOW,
        processed_at=NOW,
        quality=DataQuality(facet=DataQualityFacet.VALID),
        value=30.4,
    )
    indicator_def = Indicator(id=IndicatorId(), name="demo")
    indicator_version = IndicatorVersion(
        id=IndicatorVersionId(),
        indicator_id=indicator_def.id,
        version="1.0.0",
        unit="degC",
        formula_kind="passthrough",
        status=PublicationStatus.PUBLISHED,
    )
    indicator = IndicatorValue(
        id=IndicatorValueId(),
        indicator_id=indicator_def.id,
        indicator_version_id=indicator_version.id,
        indicator_version="1.0.0",
        computed_at=NOW,
        unit="degC",
        source_observation_ids=(observation.id,),
        quality=DataQuality(facet=DataQualityFacet.VALID),
        value=3.4,
    )
    version_id = RuleVersionId()
    rule = Rule(id=RuleId(), name="thermal")
    version = RuleVersion(
        id=version_id,
        rule_id=rule.id,
        version="1.0.0",
        thresholds=(Threshold("anomaly_high", 2.0),),
        operator=ComparisonOp.GT,
        threshold_name="anomaly_high",
        severity_if_triggered="critical",
        status=PublicationStatus.PUBLISHED,
    )
    evaluation = RuleEvaluation(
        id=RuleEvaluationId(),
        rule_id=rule.id,
        rule_version_id=version_id,
        rule_version="1.0.0",
        evaluated_at=NOW,
        outcome=RuleOutcome.TRIGGERED,
        input_indicator_value_ids=(indicator.id,),
        thresholds_applied={"anomaly_high": 2.0},
        evaluator_engine_id="baliza.rules.threshold_v1",
        reason="above",
        input_snapshot={"value": 3.4},
    )
    item = EvidenceItem(
        id=EvidenceItemId(),
        kind=EvidenceKind.DERIVED,
        epistemic_label=EpistemicLabel.FACT,
        referenced_type="RuleEvaluation",
        referenced_id=str(evaluation.id),
        created_at=NOW,
    )
    package = EvidencePackage(
        id=EvidencePackageId(),
        subject="thermal",
        item_ids=(item.id,),
        assembled_at=NOW,
        gaps=(),
        incomplete=False,
    )
    from baliza.domain.alert import Alert
    from baliza.domain.enums import AlertSeverity, AlertStatus
    from baliza.domain.quality import ScopeHealth

    alert = Alert(
        id=AlertId(),
        severity=AlertSeverity.CRITICAL,
        status=AlertStatus.OPEN,
        alerted_at=NOW,
        evidence_package_id=package.id,
        rule_evaluation_ids=(evaluation.id,),
        health=ScopeHealth.DEGRADED,
    )
    with Session(engine) as session:
        SqlObservationRepository(session).add(observation)
        SqlIndicatorRepository(session).add_definition(indicator_def, indicator_version)
        SqlIndicatorRepository(session).add_value(indicator)
        SqlRuleRepository(session).add_rule(rule, version)
        SqlRuleRepository(session).add_evaluation(evaluation)
        SqlEvidenceRepository(session).add_item(item)
        SqlEvidenceRepository(session).add_package(package)
        session.flush()
        SqlAlertRepository(session).add(alert)
        session.commit()
    with Session(engine) as session:
        loaded_obs = SqlObservationRepository(session).get(observation.id)
        loaded_ind = SqlIndicatorRepository(session).get_value(indicator.id)
        loaded_eval = SqlRuleRepository(session).get_evaluation(evaluation.id)
        loaded_items = SqlEvidenceRepository(session).items_for_package(package.id)
        loaded_alert = SqlAlertRepository(session).get(alert.id)
        assert loaded_obs.value == 30.4
        assert loaded_ind.source_observation_ids == (observation.id,)
        assert loaded_eval.input_indicator_value_ids == (indicator.id,)
        assert loaded_items[0].referenced_id == str(evaluation.id)
        assert loaded_alert.evidence_package_id == package.id
        bare = AlertRow(
            id=AlertId().value,
            severity="critical",
            status="open",
            alerted_at=NOW,
            evidence_package_id=None,
            history=[],
            health="unknown",
        )
        session.add(bare)
        with pytest.raises(IntegrityError):
            session.flush()


def test_sql_decision_rejects_missing_required_columns() -> None:
    engine = _engine()
    with Session(engine) as session:
        session.add(
            DecisionRow(
                id=RuleId().value,
                actor_id=None,
                dss_context_snapshot_id=RuleId().value,
                dss_package_id=None,
                decided_at=NOW,
                justification="because",
                selected_option="watch",
                snapshot_hash="abc",
            )
        )
        with pytest.raises(IntegrityError):
            session.flush()
