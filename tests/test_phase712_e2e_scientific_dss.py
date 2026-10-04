"""Phase 7.12 — End-to-end scientific DSS integration tests."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from baliza.application.phase712_scientific_dss import (
    DEMO_ONLY,
    DEMO_SPOT,
    SCIENTIFICALLY_VALIDATED,
    THRESHOLD_STATUS,
    evaluate_dhw_demo_not_triggered,
    run_e2e_scientific_dss,
)
from baliza.application.use_cases import record_human_decision
from baliza.domain.action import record_action
from baliza.domain.actor import Actor
from baliza.domain.agent import AgentRun
from baliza.domain.decision import record_decision
from baliza.domain.enums import EpistemicLabel, RuleOutcome
from baliza.domain.errors import ActionWithoutDecision, InvariantViolation, MissingActor, MissingSnapshot
from baliza.domain.ids import ActorId, AgentId, AgentRunId, AgentVersionId
from baliza.domain.rule import evaluate_rule
from baliza.interfaces.api.app import create_app

ROOT = Path(__file__).resolve().parents[1]
NOW = datetime(2026, 9, 30, 12, 0, tzinfo=UTC)


def test_e2e_public_data_to_outcome(repos) -> None:
    result = run_e2e_scientific_dss(repos, ROOT)
    assert result.spot_intelligence["spot"]["spot_id"] == DEMO_SPOT["spot_id"]
    assert result.spot_intelligence["spot"]["latitude"] == -23.5
    assert result.spot_intelligence["spot"]["longitude"] == 152.0
    assert len(result.observations) == 6
    assert all(obs.metadata["epistemic"] == "EXTERNAL_INDICATOR" for obs in result.observations)
    assert all(obs.metadata["local_measured_temperature"] == "false" for obs in result.observations)
    assert result.evaluation.outcome is RuleOutcome.TRIGGERED
    assert result.alert is not None
    assert result.alert.is_decision() is False
    assert result.dss_package.recommendations
    assert all(r.epistemic_label == "RECOMMENDATION" for r in result.dss_package.recommendations)
    assert result.decision.justification
    assert result.decision.actor_id is not None
    assert result.decision.dss_context_snapshot_id == result.snapshot.id
    assert result.action.decision_id == result.decision.id
    assert result.outcome.action_id == result.action.id
    assert result.outcome.decision_id == result.decision.id
    assert result.machine_summary["demo_only"] is True
    assert result.machine_summary["scientifically_validated"] is False
    assert result.machine_summary["ml_implementation"] == "NOT_AUTHORIZED"
    assert result.machine_summary["imr_dependency"] == "NONE"
    assert result.machine_summary["autonomous_action"] is False
    actions = {e.action for e in repos.audit.events}
    for required in (
        "observation.recorded",
        "indicator.calculated",
        "rule.evaluated",
        "evidence.package_created",
        "alert.created",
        "dss.package_opened",
        "recommendation.presented",
        "dss_context_snapshot.frozen",
        "decision.recorded",
        "action.recorded",
        "outcome.recorded",
    ):
        assert required in actions
    assert "Not LOCAL_MEASURED_TEMPERATURE" in result.brief
    assert "DEMO / NON-SCIENTIFIC" in result.brief
    assert "SCIENTIFICALLY_VALIDATED: false" in result.brief
    assert "MERMAID" in result.brief and "not NO BLEACHING" in result.brief
    assert "THERMAL GROUND TRUTH = NOT_AVAILABLE" in result.brief
    # Persist reproducible artifacts for human review.
    out = ROOT / "data" / "phase712"
    out.mkdir(parents=True, exist_ok=True)
    (out / "e2e-brief.txt").write_text(result.brief, encoding="utf-8")
    (out / "e2e-summary.json").write_text(json.dumps(result.machine_summary, indent=2), encoding="utf-8")


def test_unknown_is_not_not_triggered(repos, published_rule) -> None:
    rule, version = published_rule
    unknown = evaluate_rule(rule=rule, version=version, indicator_value=None, evaluated_at=NOW)
    assert unknown.outcome is RuleOutcome.UNKNOWN
    assert unknown.outcome is not RuleOutcome.NOT_TRIGGERED
    assert unknown.outcome is not RuleOutcome.TRIGGERED


def test_alert_cannot_create_action_without_decision(repos) -> None:
    result = run_e2e_scientific_dss(repos, ROOT)
    with pytest.raises(ActionWithoutDecision):
        record_action(
            decision_id=None,
            acted_at=NOW,
            description="illegal alert shortcut",
            action_type="notify",
        )
    assert result.alert is not None


def test_recommendation_cannot_create_action_without_decision(repos) -> None:
    result = run_e2e_scientific_dss(repos, ROOT)
    recommendation = result.dss_package.recommendations[0]
    assert recommendation.epistemic_label == "RECOMMENDATION"
    with pytest.raises(ActionWithoutDecision):
        record_action(
            decision_id=None,
            acted_at=NOW,
            description=recommendation.text,
            action_type="from_recommendation",
        )


def test_agent_run_is_not_decision_and_cannot_auto_decide() -> None:
    run = AgentRun(
        id=AgentRunId(),
        agent_id=AgentId(),
        agent_version_id=AgentVersionId(),
        agent_version="0.0.1",
        started_at=NOW,
        completed_at=NOW,
        epistemic_label=EpistemicLabel.RECOMMENDATION,
        summary="assistive note",
    )
    assert run.is_decision() is False
    with pytest.raises(MissingActor):
        record_decision(
            actor_id=None,
            snapshot=None,
            decided_at=NOW,
            justification="agent tried",
            selected_option="continue_monitoring",
        )


def test_decision_requires_actor_snapshot_justification(repos) -> None:
    result = run_e2e_scientific_dss(repos, ROOT)
    with pytest.raises(MissingSnapshot):
        record_decision(
            actor_id=ActorId(),
            snapshot=None,
            decided_at=NOW,
            justification="missing snapshot",
            selected_option="continue_monitoring",
        )
    with pytest.raises(InvariantViolation):
        record_human_decision(
            repos,
            actor=Actor(id=ActorId(), display_name="x"),
            package=result.dss_package,
            justification="   ",
            selected_option="continue_monitoring",
        )


def test_snapshot_hash_stable_after_later_mutation(repos) -> None:
    result = run_e2e_scientific_dss(repos, ROOT)
    before = result.snapshot.content_hash
    # Mutate live package / alert after freeze.
    result.dss_package.gaps.append("post-freeze mutation")
    repos.dss.save_package(result.dss_package)
    again = repos.dss.get_snapshot(result.decision.dss_context_snapshot_id)
    assert again.content_hash == before
    assert "post-freeze mutation" in result.dss_package.gaps
    assert "post-freeze mutation" not in list(again.payload.get("gaps", ()))
    frozen_gaps = again.payload.get("data_gaps_at_freeze") or []
    assert "post-freeze mutation" not in str(frozen_gaps)


def test_data_gap_is_not_absence_of_risk(repos) -> None:
    result = run_e2e_scientific_dss(repos, ROOT)
    mermaid_gaps = [g for g in result.dss_package.gaps if "MERMAID" in g]
    assert mermaid_gaps
    # Absence of match must not be reinterpreted as a negative ecological finding.
    assert all("status=NO_BLEACHING" not in g for g in mermaid_gaps)
    assert all("status=HEALTHY" not in g for g in mermaid_gaps)
    assert all("implies_no_risk=true" not in g.lower() for g in mermaid_gaps)
    si = result.spot_intelligence
    assert si["field_ecological_observations"]["status_label"] == "DATA EXISTS BUT NO COMPATIBLE MATCH"
    assert all(g.get("implies_no_risk") is False for g in si["data_gaps"])


def test_crw_not_presented_as_local_measured_temperature(repos) -> None:
    result = run_e2e_scientific_dss(repos, ROOT)
    sst = next(obs for obs in result.observations if obs.variable == "crw_coraltemp_sst")
    assert sst.metadata["epistemic"] == "EXTERNAL_INDICATOR"
    assert sst.metadata["local_measured_temperature"] == "false"
    assert "association:UNKNOWN" in sst.spatial_ref
    assert result.snapshot.payload["crw_not_local_measured_temperature"] is True
    assert "Not LOCAL_MEASURED_TEMPERATURE" in result.brief


def test_mermaid_absence_is_not_no_bleaching(repos) -> None:
    result = run_e2e_scientific_dss(repos, ROOT)
    field = result.spot_intelligence["field_ecological_observations"]
    assert field["compatible_count"] == 0
    assert "NO BLEACHING" not in field["summary"]
    assert "does not imply absence of bleaching" in result.spot_intelligence["human_readable"]
    assert any("NO COMPATIBLE MATCH" in g or "compatible field observation" in g for g in result.dss_package.gaps)


def test_demo_threshold_not_scientifically_validated(repos) -> None:
    result = run_e2e_scientific_dss(repos, ROOT)
    assert DEMO_ONLY is True
    assert SCIENTIFICALLY_VALIDATED is False
    assert THRESHOLD_STATUS == "DEMO / NON-SCIENTIFIC"
    assert result.snapshot.payload["demo_only"] is True
    assert result.snapshot.payload["scientifically_validated"] is False
    assert result.snapshot.payload["threshold_status"] == THRESHOLD_STATUS
    assert "SCIENTIFICALLY_VALIDATED: false" in result.brief


def test_dhw_not_triggered_is_not_unknown(repos) -> None:
    evaluation = evaluate_dhw_demo_not_triggered(repos, ROOT)
    assert evaluation.outcome is RuleOutcome.NOT_TRIGGERED
    assert evaluation.outcome is not RuleOutcome.UNKNOWN
    assert evaluation.outcome is not RuleOutcome.TRIGGERED


def test_existing_api_can_read_dss_brief_and_intelligence(repos) -> None:
    result = run_e2e_scientific_dss(repos, ROOT)
    client = TestClient(create_app(repos=repos))
    intelligence = client.get(f"/scientific/spots/{DEMO_SPOT['spot_id']}/intelligence")
    assert intelligence.status_code == 200
    assert intelligence.json()["field_ecological_observations"]["compatible_count"] == 0
    brief = client.get(f"/dss/packages/{result.dss_package.id}/brief")
    assert brief.status_code == 200
    body = brief.json()
    assert body["threshold_status"] == "DEMO / NON-SCIENTIFIC"
    assert body["decision"] is None or "decision" in body
    evidence = client.get(f"/dss/packages/{result.dss_package.id}/evidence")
    options = client.get(f"/dss/packages/{result.dss_package.id}/options")
    assert evidence.status_code == 200
    assert options.status_code == 200
    option_rows = options.json()["options"]
    assert option_rows
    assert all(item["epistemic_label"] == "RECOMMENDATION" for item in option_rows)
    assert all(item["is_decision"] is False for item in option_rows)
    context = client.get(f"/alerts/{result.alert.id}/context")
    assert context.status_code == 200
    assert context.json()["threshold_status"] == "DEMO / NON-SCIENTIFIC"
    assert context.json()["decision"] is None
    snaps = client.get(f"/dss/packages/{result.dss_package.id}/snapshots")
    assert snaps.status_code == 200
    assert snaps.json()["snapshots"]
    assert snaps.json()["snapshots"][0]["content_hash"] == result.snapshot.content_hash
