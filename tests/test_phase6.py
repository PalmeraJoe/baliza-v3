from dataclasses import replace
from datetime import UTC, datetime

import pytest

from fastapi.testclient import TestClient

from baliza.application.queries import alert_situation, package_situation
from baliza.application.use_cases import (
    build_dss_package,
    calculate_indicator,
    evaluate_and_maybe_alert,
    record_human_decision,
    record_human_outcome,
    record_observation,
    record_human_action,
)
from baliza.domain.actor import Actor
from baliza.domain.enums import AlertStatus, DataQualityFacet, EvidenceKind, PublicationStatus, RuleOutcome, UncertaintyType
from baliza.domain.errors import MissingActor, InvariantViolation, PublishedVersionImmutable
from baliza.domain.evidence import EvidencePackage
from baliza.domain.hashing import sha256_canonical
from baliza.domain.ids import ActorId, EvidencePackageId, ProtocolId, ProtocolVersionId
from baliza.domain.protocol import ProtocolOption, ProtocolVersion
from baliza.domain.quality import DataQuality
from baliza.domain.rule import evaluate_rule
from baliza.domain.situation import interpret_situation, quality_statement
from baliza.interfaces.api.app import create_app

NOW = datetime(2026, 9, 30, 12, 0, tzinfo=UTC)


def _chain(repos, published_indicator, published_rule, *, value=30.4, facet=DataQualityFacet.VALID, spatial=None):
    indicator, iversion = published_indicator
    rule, rversion = published_rule
    repos.indicators.add_definition(indicator, iversion)
    repos.rules.add_rule(rule, rversion)
    obs = record_observation(
        repos,
        variable="sst",
        unit="degC",
        observed_at=NOW,
        quality=DataQuality(facet=facet),
        value=value,
        spatial_ref=spatial,
    )
    ivalue = calculate_indicator(repos, version=iversion, observation=obs)
    result = evaluate_and_maybe_alert(
        repos, observation=obs, indicator_value=ivalue, rule=rule, rule_version=rversion
    )
    return obs, ivalue, result


def test_triggered_reading_keeps_version_threshold_and_clocks(repos, published_indicator, published_rule) -> None:
    obs, ivalue, result = _chain(repos, published_indicator, published_rule, spatial="station-ref-demo")
    protocol = ProtocolVersion(
        id=ProtocolVersionId(),
        protocol_id=ProtocolId(),
        version="0.0.1-demo",
        options=(),
        option_details=(
            ProtocolOption(code="watch", description="Increase sampling frequency", preconditions=("duty officer",), constraints=("no automatic execution",)),
        ),
        status=PublicationStatus.PUBLISHED,
    )
    package = build_dss_package(repos, alert=result.alert, protocol=protocol)
    reading = package_situation(repos, package.id)
    signal = reading.readings[0]
    assert signal.outcome == RuleOutcome.TRIGGERED.value
    assert signal.indicator_version == "1.0.0"
    assert signal.thresholds["anomaly_high"] == 2.0
    assert signal.observed_value == ivalue.value
    assert signal.quality == "valid"
    assert signal.quality_statement == "Evidence supports the signal"
    assert signal.observed_at == obs.observed_at.isoformat()
    assert signal.evaluated_at == result.evaluation.evaluated_at.isoformat()
    assert signal.alerted_at == result.alert.alerted_at.isoformat()
    assert signal.spatial_ref == "station-ref-demo"
    assert reading.supports
    assert reading.recommendations[0].epistemic_label == "RECOMMENDATION"
    assert reading.recommendations[0].preconditions == ("duty officer",)
    assert reading.to_dict()["decision"] is None
    assert any(e.action == "recommendation.presented" for e in repos.audit.events)


def test_unknown_and_insufficient_stay_distinct(published_rule) -> None:
    rule, version = published_rule
    unknown = evaluate_rule(rule=rule, version=version, indicator_value=None, evaluated_at=NOW)
    reading = interpret_situation(evaluations=(unknown,))
    assert unknown.outcome is RuleOutcome.UNKNOWN
    assert reading.gaps[0].kind.value == "missing_observation"
    assert reading.uncertainty[0].uncertainty_type is UncertaintyType.UNKNOWN
    assert quality_statement(None, unknown.outcome) == "State cannot be determined reliably"
    assert reading.to_dict()["decision"] is None


def test_conflicting_evidence_is_not_a_decision() -> None:
    package = EvidencePackage(
        id=EvidencePackageId(),
        subject="demo",
        item_ids=(),
        assembled_at=NOW,
        gaps=("window incomplete",),
        conflicts=("station readings disagree",),
        incomplete=True,
    )
    reading = interpret_situation(evidence_packages=(package,))
    assert reading.contradictory == ("station readings disagree",)
    assert reading.uncertainty[0].uncertainty_type is UncertaintyType.CONFLICTING
    assert reading.gaps[0].reason == "window incomplete"
    assert reading.to_dict()["decision"] is None


def test_multi_alert_snapshot_ignores_later_mutation(repos, published_indicator, published_rule) -> None:
    indicator, iversion = published_indicator
    rule, rversion = published_rule
    repos.indicators.add_definition(indicator, iversion)
    repos.rules.add_rule(rule, rversion)
    alerts = []
    for sample in (30.4, 31.0):
        obs = record_observation(
            repos,
            variable="sst",
            unit="degC",
            observed_at=NOW,
            quality=DataQuality(facet=DataQualityFacet.VALID),
            value=sample,
        )
        ivalue = calculate_indicator(repos, version=iversion, observation=obs)
        result = evaluate_and_maybe_alert(
            repos, observation=obs, indicator_value=ivalue, rule=rule, rule_version=rversion
        )
        alerts.append(result)
    protocol = ProtocolVersion(
        id=ProtocolVersionId(),
        protocol_id=ProtocolId(),
        version="0.0.1-demo",
        options=("watch",),
        status=PublicationStatus.DRAFT,
    )
    package = build_dss_package(repos, alerts=[item.alert for item in alerts], protocol=protocol)
    actor = Actor(id=ActorId(), display_name="manager")
    repos.actors.add(actor)
    decision = record_human_decision(
        repos, actor=actor, package=package, justification="reviewed both demo signals", selected_option="watch"
    )
    snap = repos.dss.get_snapshot(decision.dss_context_snapshot_id)
    before = snap.content_hash
    assert len(snap.payload["signal_readings_at_freeze"]) == 2
    assert snap.payload["signal_readings_at_freeze"][0]["quality_statement"] == "Evidence supports the signal"
    assert snap.content_hash == sha256_canonical(snap.payload)
    repos.alerts.save(replace(alerts[0].alert, status=AlertStatus.ACKNOWLEDGED))
    item = alerts[0].evidence_items[0]
    repos.evidence.items[str(item.id)] = replace(item, narrative="changed after decision")
    package.recommendations[0] = replace(package.recommendations[0], text="changed option text")
    repos.dss.save_package(package)
    assert protocol.with_options(("other",)).options == ("other",)
    published = replace(protocol, status=PublicationStatus.PUBLISHED)
    with pytest.raises(PublishedVersionImmutable):
        published.with_option_details((ProtocolOption(code="x", description="x"),))
    again = repos.dss.get_snapshot(decision.dss_context_snapshot_id)
    assert again.content_hash == before
    assert again.payload["signal_readings_at_freeze"][0]["alert_status"] == "OPEN"
    assert again.payload["protocol_options_at_freeze"] == ("watch",)
    action = record_human_action(
        repos, decision=decision, description="notify", actor=actor, action_type="notify"
    )
    record_human_outcome(repos, action=action, decision=decision, notes="noted")
    assert repos.dss.get_snapshot(decision.dss_context_snapshot_id).content_hash == before
    assert decision.dss_context_snapshot_id == again.id


def test_decision_still_requires_actor_snapshot_and_justification(repos, published_indicator, published_rule) -> None:
    from baliza.domain.decision import record_decision

    _, _, result = _chain(repos, published_indicator, published_rule)
    package = build_dss_package(repos, alert=result.alert)
    actor = Actor(id=ActorId(), display_name="manager")
    with pytest.raises(InvariantViolation):
        record_human_decision(repos, actor=actor, package=package, justification="  ", selected_option="watch")
    with pytest.raises(MissingActor):
        record_decision(
            actor_id=None, snapshot=None, decided_at=NOW, justification="because", selected_option="watch"
        )


def test_alert_context_endpoint(repos, published_indicator, published_rule) -> None:
    _, _, result = _chain(repos, published_indicator, published_rule)
    package = build_dss_package(repos, alert=result.alert)
    client = TestClient(create_app(repos=repos))
    context = client.get(f"/alerts/{result.alert.id}/context")
    assert context.status_code == 200
    body = context.json()
    assert body["signals"][0]["outcome"] == "triggered"
    assert body["signals"][0]["rule_version"] == "1.0.0"
    assert body["ai_used"] is False
    assert body["decision"] is None
    assert body["threshold_status"] == "DEMO / NON-SCIENTIFIC"
    brief = client.get(f"/dss/packages/{package.id}/brief")
    evidence = client.get(f"/dss/packages/{package.id}/evidence")
    options = client.get(f"/dss/packages/{package.id}/options")
    assert brief.status_code == 200
    assert evidence.json()["supports"]
    assert any(row["kind"] == EvidenceKind.PRIMARY.value for row in evidence.json()["supports"])
    assert options.json()["options"] == []
    direct = alert_situation(repos, result.alert.id)
    assert direct.readings[0].alert_id == str(result.alert.id)
