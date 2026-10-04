"""Phase 7.12 — End-to-end scientific DSS integration over public Spot Intelligence.

Uses DEMO / NON-SCIENTIFIC thresholds only to exercise the DSS path.
Does not invent scientific thresholds, ML, downscaling, or local estimation.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from baliza.application.use_cases import (
    Repositories,
    build_dss_package,
    calculate_indicator,
    evaluate_and_maybe_alert,
    record_human_action,
    record_human_decision,
    record_human_outcome,
    record_observation,
)
from baliza.domain.actor import Actor
from baliza.domain.enums import ComparisonOp, DataQualityFacet, PublicationStatus, RuleOutcome
from baliza.domain.ids import ActorId, IndicatorId, IndicatorVersionId, ProtocolId, ProtocolVersionId, RuleId, RuleVersionId
from baliza.domain.indicator import Indicator, IndicatorVersion
from baliza.domain.protocol import ProtocolOption, ProtocolVersion
from baliza.domain.quality import DataQuality
from baliza.domain.rule import Rule, RuleVersion, Threshold, evaluate_rule
from baliza.infrastructure.sources.crw.catalog import DEMO_SPOT
from baliza.infrastructure.sources.integrated.spot_intelligence import (
    GAP_EXISTS_NO_MATCH,
    build_integrated_spot_intelligence,
)

PHASE = "7.12"
DEMO_RULE_NAME = "demo_crw_external_sst_watch"
DEMO_INDICATOR_NAME = "demo_crw_coraltemp_passthrough"
DEMO_THRESHOLD_NAME = "demo_sst_watch"
# Technical demonstration only. Not a BALIZA scientific bleaching threshold.
DEMO_SST_WATCH_THRESHOLD = 20.0
DEMO_ONLY = True
SCIENTIFICALLY_VALIDATED = False
THRESHOLD_STATUS = "DEMO / NON-SCIENTIFIC"


@dataclass(frozen=True, slots=True)
class Phase712Result:
    spot_intelligence: dict[str, Any]
    observations: tuple[Any, ...]
    indicator_value: Any
    evaluation: Any
    alert: Any
    dss_package: Any
    decision: Any
    action: Any
    outcome: Any
    snapshot: Any
    brief: str
    machine_summary: dict[str, Any]


def demo_definitions() -> dict[str, Any]:
    indicator = Indicator(
        id=IndicatorId(),
        name=DEMO_INDICATOR_NAME,
        description=(
            "DEMO / NON-SCIENTIFIC passthrough of NOAA CRW CoralTemp SST "
            "as EXTERNAL_INDICATOR. Not a local temperature measurement."
        ),
    )
    indicator_version = IndicatorVersion(
        id=IndicatorVersionId(),
        indicator_id=indicator.id,
        version="0.0.1-demo",
        unit="degree_C",
        formula_kind="passthrough",
        status=PublicationStatus.PUBLISHED,
        input_variable="crw_coraltemp_sst",
    )
    rule = Rule(
        id=RuleId(),
        name=DEMO_RULE_NAME,
        description=(
            "DEMO / NON-SCIENTIFIC watch on CRW external SST. "
            "DEMO_ONLY=true. SCIENTIFICALLY_VALIDATED=false. "
            "Not a BALIZA scientific bleaching threshold."
        ),
    )
    rule_version = RuleVersion(
        id=RuleVersionId(),
        rule_id=rule.id,
        version="0.0.1-demo",
        thresholds=(Threshold(name=DEMO_THRESHOLD_NAME, value=DEMO_SST_WATCH_THRESHOLD),),
        operator=ComparisonOp.GT,
        threshold_name=DEMO_THRESHOLD_NAME,
        severity_if_triggered="warning",
        status=PublicationStatus.PUBLISHED,
    )
    protocol = ProtocolVersion(
        id=ProtocolVersionId(),
        protocol_id=ProtocolId(),
        version="0.0.1-demo",
        options=(),
        option_details=(
            ProtocolOption(
                code="continue_monitoring",
                description="Continue monitoring with existing public sources",
                preconditions=("human_review",),
                constraints=("no automatic execution", "DEMO / NON-SCIENTIFIC"),
            ),
            ProtocolOption(
                code="increase_field_observation_frequency",
                description="Increase field observation frequency if operationally available",
                preconditions=("human_review",),
                constraints=("no automatic execution", "DEMO / NON-SCIENTIFIC"),
            ),
            ProtocolOption(
                code="review_local_environmental_conditions",
                description="Review local environmental conditions with available context",
                preconditions=("human_review",),
                constraints=("no automatic execution", "DEMO / NON-SCIENTIFIC"),
            ),
            ProtocolOption(
                code="initiate_predefined_response_protocol",
                description="Initiate a predefined response protocol only after human decision",
                preconditions=("human_decision",),
                constraints=("no automatic execution", "DEMO / NON-SCIENTIFIC"),
            ),
        ),
        status=PublicationStatus.PUBLISHED,
    )
    return {
        "indicator": indicator,
        "indicator_version": indicator_version,
        "rule": rule,
        "rule_version": rule_version,
        "protocol": protocol,
        "demo_only": DEMO_ONLY,
        "scientifically_validated": SCIENTIFICALLY_VALIDATED,
        "threshold_status": THRESHOLD_STATUS,
    }


def _parse_grid_time(value: str) -> datetime:
    # CRW grid time is ISO Z; Observation requires aware datetime.
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def ingest_crw_external_observations(
    repos: Repositories,
    spot_intelligence: dict[str, Any],
) -> list[Any]:
    """Record CRW products as Observations without promoting them to local measurements."""
    observations = []
    for item in spot_intelligence["thermal_evidence"]["indicators"]:
        when = item["temporal_association"]["source_time"]
        obs = record_observation(
            repos,
            variable=item["what"],
            unit=str(item.get("unit") or "UNKNOWN"),
            observed_at=_parse_grid_time(when),
            quality=DataQuality(
                facet=DataQualityFacet.VALID,
                notes="CRW external indicator row; association to Spot remains UNKNOWN",
            ),
            value=float(item["value"]),
            spatial_ref=(
                f"crw_cell:{item['cell']['latitude']},{item['cell']['longitude']}"
                f"|spot:{DEMO_SPOT['spot_id']}|association:UNKNOWN"
            ),
            metadata={
                "label": THRESHOLD_STATUS,
                "epistemic": "EXTERNAL_INDICATOR",
                "scientific_layer": "EXTERNAL_INDICATOR",
                "local_measured_temperature": "false",
                "source": "NOAA_CORAL_REEF_WATCH",
                "dataset_id": item["dataset_id"],
                "spot_id": DEMO_SPOT["spot_id"],
                "spatial_association": item["spatial_association"]["association_type"],
                "applies_to": item["applies_to"],
                "demo_only": "true",
                "scientifically_validated": "false",
            },
        )
        observations.append(obs)
    return observations


def run_e2e_scientific_dss(
    repos: Repositories,
    root: Path,
    *,
    actor_display_name: str = "demo-operator",
    selected_option: str = "continue_monitoring",
    justification: str = (
        "Human review of DEMO / NON-SCIENTIFIC CRW external SST watch for the heritage DEMO Spot. "
        "Does not claim local temperature, thermal ground truth, or scientific threshold validation."
    ),
) -> Phase712Result:
    defs = demo_definitions()
    repos.indicators.add_definition(defs["indicator"], defs["indicator_version"])
    repos.rules.add_rule(defs["rule"], defs["rule_version"])

    spot_intelligence = build_integrated_spot_intelligence(root, spot_id=DEMO_SPOT["spot_id"])
    observations = ingest_crw_external_observations(repos, spot_intelligence)
    sst_obs = next(obs for obs in observations if obs.variable == "crw_coraltemp_sst")
    indicator_value = calculate_indicator(
        repos,
        version=defs["indicator_version"],
        observation=sst_obs,
    )
    if indicator_value.value != sst_obs.value:
        raise RuntimeError("Passthrough must preserve CRW external SST value.")

    critical = evaluate_and_maybe_alert(
        repos,
        observation=sst_obs,
        indicator_value=indicator_value,
        rule=defs["rule"],
        rule_version=defs["rule_version"],
    )
    if critical.evaluation.outcome is not RuleOutcome.TRIGGERED or critical.alert is None:
        raise RuntimeError(
            "Phase 7.12 DEMO scenario expects TRIGGERED on demo SST watch; "
            f"got {critical.evaluation.outcome}"
        )

    gaps = [
        f"MERMAID:{GAP_EXISTS_NO_MATCH}:compatible field observation not available for this Spot",
        "ALLEN:DATA_EXISTS_NO_COMPATIBLE_MATCH:mapped context not attached to DEMO Spot",
        "CRW:DATA_EXISTS_WITH_UNKNOWN_COMPATIBILITY:production spatial association UNKNOWN",
        "THERMAL_GROUND_TRUTH:NOT_AVAILABLE",
        "LOCAL_ESTIMATION:NOT_AUTHORIZED",
        "DOWNSCALING:NOT_AUTHORIZED",
        "ML_IMPLEMENTATION:NOT_AUTHORIZED",
        "THRESHOLD_STATUS:DEMO / NON-SCIENTIFIC",
    ]
    for gap in spot_intelligence.get("data_gaps", []):
        if gap.get("availability") in {
            GAP_EXISTS_NO_MATCH,
            "DATA_EXISTS_BUT_ACCESS_BLOCKED",
            "NO_DATA",
        }:
            gaps.append(f"{gap['source']}:{gap.get('kind')}:{gap.get('detail')}")

    uncertainty_notes = [
        f"measurement={spot_intelligence['uncertainty']['measurement_uncertainty']}",
        f"spatial={spot_intelligence['uncertainty']['spatial_uncertainty']}",
        f"temporal={spot_intelligence['uncertainty']['temporal_uncertainty']}",
        f"association={spot_intelligence['uncertainty']['association_uncertainty']}",
        "CRW values remain EXTERNAL_INDICATOR; not LOCAL_MEASURED_TEMPERATURE",
        "MERMAID absence is not NO_BLEACHING",
        f"threshold_status={THRESHOLD_STATUS}",
    ]
    package = build_dss_package(
        repos,
        alert=critical.alert,
        protocol=defs["protocol"],
        extra_gaps=gaps,
        uncertainty_notes=uncertainty_notes,
    )
    actor = Actor(id=ActorId(), display_name=actor_display_name)
    repos.actors.add(actor)
    decision = record_human_decision(
        repos,
        actor=actor,
        package=package,
        justification=justification,
        selected_option=selected_option,
        extra_snapshot={
            "phase": PHASE,
            "spot_id": DEMO_SPOT["spot_id"],
            "spot_intelligence_contract": spot_intelligence["contract_version"],
            "threshold_status": THRESHOLD_STATUS,
            "demo_only": DEMO_ONLY,
            "scientifically_validated": SCIENTIFICALLY_VALIDATED,
            "thermal_ground_truth": "NOT_AVAILABLE",
            "local_estimation": "NOT_AUTHORIZED",
            "downscaling": "NOT_AUTHORIZED",
            "ml_implementation": "NOT_AUTHORIZED",
            "imr_dependency": "NONE",
            "mermaid_compatible_observation": "NOT_AVAILABLE",
            "scientific_acceptance": spot_intelligence["scientific_acceptance"],
            "crw_not_local_measured_temperature": True,
            "spot_coordinates": {
                "latitude": DEMO_SPOT["latitude"],
                "longitude": DEMO_SPOT["longitude"],
                "crs": DEMO_SPOT["crs"],
                "unchanged": True,
            },
        },
    )
    snapshot = repos.dss.get_snapshot(decision.dss_context_snapshot_id)
    action = record_human_action(
        repos,
        decision=decision,
        description="Recorded DEMO monitoring follow-up after human decision",
        actor=actor,
        action_type="continue_monitoring",
        metadata={
            "demo_only": True,
            "scientifically_validated": False,
            "automatic": False,
        },
    )
    outcome = record_human_outcome(
        repos,
        action=action,
        decision=decision,
        notes="DEMO outcome recorded. No autonomous operational closure or ML inference.",
    )
    brief = render_dss_brief(
        spot_intelligence=spot_intelligence,
        indicator_value=indicator_value,
        evaluation=critical.evaluation,
        alert=critical.alert,
        package=package,
        decision=decision,
        snapshot=snapshot,
        defs=defs,
        observation=sst_obs,
    )
    machine_summary = {
        "phase": PHASE,
        "spot_id": DEMO_SPOT["spot_id"],
        "threshold_status": THRESHOLD_STATUS,
        "demo_only": DEMO_ONLY,
        "scientifically_validated": SCIENTIFICALLY_VALIDATED,
        "rule": {
            "name": defs["rule"].name,
            "version": defs["rule_version"].version,
            "threshold_name": DEMO_THRESHOLD_NAME,
            "threshold_value": DEMO_SST_WATCH_THRESHOLD,
            "operator": defs["rule_version"].operator.value,
            "outcome": critical.evaluation.outcome.value,
            "reason": critical.evaluation.reason,
        },
        "alert_id": str(critical.alert.id),
        "dss_package_id": str(package.id),
        "snapshot_id": str(snapshot.id),
        "snapshot_hash": snapshot.content_hash,
        "decision_id": str(decision.id),
        "action_id": str(action.id),
        "outcome_id": str(outcome.id),
        "thermal_ground_truth": "NOT_AVAILABLE",
        "local_estimation": "NOT_AUTHORIZED",
        "downscaling": "NOT_AUTHORIZED",
        "ml_implementation": "NOT_AUTHORIZED",
        "imr_dependency": "NONE",
        "autonomous_action": False,
        "autonomous_decision": False,
    }
    return Phase712Result(
        spot_intelligence=spot_intelligence,
        observations=tuple(observations),
        indicator_value=indicator_value,
        evaluation=critical.evaluation,
        alert=critical.alert,
        dss_package=package,
        decision=decision,
        action=action,
        outcome=outcome,
        snapshot=snapshot,
        brief=brief,
        machine_summary=machine_summary,
    )


def render_dss_brief(
    *,
    spot_intelligence: dict[str, Any],
    indicator_value: Any,
    evaluation: Any,
    alert: Any,
    package: Any,
    decision: Any,
    snapshot: Any,
    defs: dict[str, Any],
    observation: Any,
) -> str:
    lines = [
        "BALIZA DSS BRIEF — PHASE 7.12",
        "THRESHOLD STATUS: DEMO / NON-SCIENTIFIC",
        "SCIENTIFICALLY_VALIDATED: false",
        "",
        "SPOT",
        DEMO_SPOT["spot_id"],
        f"Latitude: {DEMO_SPOT['latitude']}",
        f"Longitude: {DEMO_SPOT['longitude']}",
        f"CRS: {DEMO_SPOT['crs']}",
        "",
        "TIME",
        f"Grid / source time: {observation.observed_at.isoformat()}",
        f"Evaluated at: {evaluation.evaluated_at.isoformat()}",
        f"Alerted at: {alert.alerted_at.isoformat()}",
        f"Decided at: {decision.decided_at.isoformat()}",
        "",
        "CURRENT STATE",
        f"Rule outcome: {evaluation.outcome.value}",
        f"Alert status: {alert.status.value}",
        f"Alert severity: {alert.severity.value}",
        "Alert is not a Decision.",
        "",
        "EVIDENCE [FACT]",
        "Source: NOAA Coral Reef Watch (EXTERNAL_INDICATOR)",
        f"Variable: {observation.variable}",
        f"Value: {observation.value} {observation.unit}",
        f"Spatial ref: {observation.spatial_ref}",
        "Not LOCAL_MEASURED_TEMPERATURE.",
        "",
        "Allen: CONTEXT_ONLY — not attached to DEMO Spot",
        "MERMAID: DATA EXISTS BUT NO COMPATIBLE MATCH — not NO BLEACHING",
        "",
        "INDICATORS [FACT / DERIVED from EXTERNAL_INDICATOR]",
        f"Indicator: {defs['indicator'].name} v{defs['indicator_version'].version}",
        f"Value: {indicator_value.value} {indicator_value.unit}",
        f"Formula: {defs['indicator_version'].formula_kind}",
        "",
        "ALERT [FACT of rule evaluation; not a Decision]",
        f"Alert id: {alert.id}",
        f"Why: {evaluation.reason}",
        f"Rule: {defs['rule'].name} / {defs['rule_version'].version}",
        f"Threshold: {DEMO_THRESHOLD_NAME}={DEMO_SST_WATCH_THRESHOLD} ({THRESHOLD_STATUS})",
        "What it does not mean: local bleaching confirmation, thermal ground truth, or scientific BALIZA threshold.",
        "",
        "UNCERTAINTIES",
        f"- measurement: {spot_intelligence['uncertainty']['measurement_uncertainty']}",
        f"- spatial: {spot_intelligence['uncertainty']['spatial_uncertainty']}",
        f"- temporal: {spot_intelligence['uncertainty']['temporal_uncertainty']}",
        f"- association: {spot_intelligence['uncertainty']['association_uncertainty']}",
        "",
        "DATA GAPS",
    ]
    for gap in package.gaps[:12]:
        lines.append(f"- {gap}")
    lines.extend(
        [
            "",
            "RULE / VERSION",
            f"{defs['rule'].name} @ {defs['rule_version'].version}",
            f"DEMO_ONLY={DEMO_ONLY}",
            f"SCIENTIFICALLY_VALIDATED={SCIENTIFICALLY_VALIDATED}",
            "",
            "AVAILABLE OPTIONS [RECOMMENDATION]",
        ]
    )
    for rec in package.recommendations:
        lines.append(f"- {rec.recommendation_id}: {rec.text} [{rec.epistemic_label}]")
    lines.extend(
        [
            "",
            "HUMAN DECISION [DECISION]",
            f"Actor: {decision.actor_id}",
            f"Selected option: {decision.selected_option}",
            f"Justification: {decision.justification}",
            f"Snapshot: {snapshot.id}",
            f"Snapshot hash: {snapshot.content_hash}",
            "",
            "BOUNDARIES",
            "THERMAL GROUND TRUTH = NOT_AVAILABLE",
            "LOCAL ESTIMATION = NOT_AUTHORIZED",
            "DOWNSCALING = NOT_AUTHORIZED",
            "ML = NOT_AUTHORIZED",
            "MERMAID COMPATIBLE OBSERVATION = NOT_AVAILABLE",
            "AUTONOMOUS ACTION = false",
            "AUTONOMOUS DECISION = false",
        ]
    )
    return "\n".join(lines)


def evaluate_dhw_demo_not_triggered(repos: Repositories, root: Path) -> Any:
    """Separate DEMO path: DHW external indicator vs a non-scientific watch that does not fire."""
    spot = build_integrated_spot_intelligence(root, spot_id=DEMO_SPOT["spot_id"])
    dhw = next(
        item
        for item in spot["thermal_evidence"]["indicators"]
        if item["dataset_id"] == "noaacrwdhwDaily"
    )
    obs = record_observation(
        repos,
        variable="crw_dhw",
        unit=str(dhw.get("unit") or "degree_Celsius_weeks"),
        observed_at=_parse_grid_time(dhw["temporal_association"]["source_time"]),
        quality=DataQuality(facet=DataQualityFacet.VALID, notes="EXTERNAL_INDICATOR"),
        value=float(dhw["value"]),
        spatial_ref="crw_cell_external|association:UNKNOWN",
        metadata={
            "label": THRESHOLD_STATUS,
            "epistemic": "EXTERNAL_INDICATOR",
            "local_measured_temperature": "false",
            "demo_only": "true",
            "scientifically_validated": "false",
        },
    )
    indicator = Indicator(id=IndicatorId(), name="demo_crw_dhw_passthrough")
    version = IndicatorVersion(
        id=IndicatorVersionId(),
        indicator_id=indicator.id,
        version="0.0.1-demo",
        unit=obs.unit,
        formula_kind="passthrough",
        status=PublicationStatus.PUBLISHED,
        input_variable="crw_dhw",
    )
    repos.indicators.add_definition(indicator, version)
    ivalue = calculate_indicator(repos, version=version, observation=obs)
    rule = Rule(id=RuleId(), name="demo_crw_dhw_watch")
    rule_version = RuleVersion(
        id=RuleVersionId(),
        rule_id=rule.id,
        version="0.0.1-demo",
        thresholds=(Threshold(name="demo_dhw_watch", value=4.0),),
        operator=ComparisonOp.GT,
        threshold_name="demo_dhw_watch",
        severity_if_triggered="warning",
        status=PublicationStatus.PUBLISHED,
    )
    evaluation = evaluate_rule(
        rule=rule,
        version=rule_version,
        indicator_value=ivalue,
        evaluated_at=repos.clock.now(),
    )
    return evaluation
