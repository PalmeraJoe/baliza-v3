from datetime import UTC, datetime

import pytest

from baliza.domain.actor import Actor
from baliza.domain.agent import AgentRun
from baliza.domain.alert import Alert
from baliza.domain.decision import record_decision
from baliza.domain.dss import DssPackage, freeze_dss_package
from baliza.domain.enums import (
    AlertSeverity,
    AlertStatus,
    DataQualityFacet,
    EpistemicLabel,
    PublicationStatus,
)
from baliza.domain.errors import (
    ActionWithoutDecision,
    MissingActor,
    MissingSnapshot,
    PublishedVersionImmutable,
    SnapshotImmutable,
)
from baliza.domain.ids import (
    ActorId,
    AgentId,
    AgentRunId,
    AgentVersionId,
    AlertId,
    DssPackageId,
    EvidencePackageId,
    RuleEvaluationId,
)
from baliza.domain.action import record_action
from baliza.domain.quality import DataQuality

NOW = datetime(2026, 9, 30, 12, 0, tzinfo=UTC)


def _alert() -> Alert:
    return Alert(
        id=AlertId(),
        severity=AlertSeverity.CRITICAL,
        status=AlertStatus.OPEN,
        alerted_at=NOW,
        evidence_package_id=EvidencePackageId(),
        rule_evaluation_ids=(RuleEvaluationId(),),
    )


def test_decision_requires_actor() -> None:
    snap = freeze_dss_package(DssPackage(id=DssPackageId(), opened_at=NOW), frozen_at=NOW)
    with pytest.raises(MissingActor):
        record_decision(
            actor_id=None,
            snapshot=snap,
            decided_at=NOW,
            justification="because",
            selected_option="monitor",
        )


def test_decision_requires_snapshot() -> None:
    with pytest.raises(MissingSnapshot):
        record_decision(
            actor_id=ActorId(),
            snapshot=None,
            decided_at=NOW,
            justification="because",
            selected_option="monitor",
        )


def test_agent_run_is_not_a_decision() -> None:
    run = AgentRun(
        id=AgentRunId(),
        agent_id=AgentId(),
        agent_version_id=AgentVersionId(),
        agent_version="0.1.0",
        started_at=NOW,
        completed_at=NOW,
        epistemic_label=EpistemicLabel.INFERENCE,
        summary="soft signal",
    )
    assert run.is_decision() is False


def test_acknowledged_is_not_a_decision() -> None:
    alert = _alert().acknowledge(reviewed_at=NOW, actor_id="op-1")
    assert alert.status is AlertStatus.ACKNOWLEDGED
    assert alert.is_decision() is False


def test_published_rule_version_immutable(published_rule) -> None:
    _, version = published_rule
    assert version.status is PublicationStatus.PUBLISHED
    with pytest.raises(PublishedVersionImmutable):
        version.with_threshold("anomaly_high", 9.9)


def test_action_requires_decision() -> None:
    with pytest.raises(ActionWithoutDecision):
        record_action(decision_id=None, acted_at=NOW, description="restrict")


def test_snapshot_immutable_after_freeze() -> None:
    pkg = DssPackage(id=DssPackageId(), opened_at=NOW)
    snap = freeze_dss_package(pkg, frozen_at=NOW)
    pkg.add_gap("new-gap-after-decision")
    with pytest.raises(SnapshotImmutable):
        snap.with_payload({"tamper": True})
    assert "new-gap-after-decision" not in list(snap.payload.get("gaps", []))


def test_no_data_quality_does_not_imply_no_risk() -> None:
    q = DataQuality(facet=DataQualityFacet.MISSING)
    assert q.implies_no_risk() is False
    assert q.is_usable_for_critical_rules is False
