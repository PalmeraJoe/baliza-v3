"""Integrated Spot Intelligence for CRW + Allen + MERMAID.

Reuses the per-source builders. Does not invent matches, scores, alerts,
decisions, actions, estimates, or thermal ground truth.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from baliza.infrastructure.sources.allen.spot_intelligence import build_allen_spot_intelligence
from baliza.infrastructure.sources.crw.catalog import DEMO_SPOT as CRW_DEMO_SPOT
from baliza.infrastructure.sources.crw.spot_intelligence import build_crw_spot_intelligence
from baliza.infrastructure.sources.mermaid.spot_intelligence import build_mermaid_spot_intelligence

PHASE = "7.11"
CONTRACT_VERSION = "phase711-integrated-spot-intelligence-1"
DEMO_SPOT_ID = CRW_DEMO_SPOT["spot_id"]

# Explicit availability taxonomy (Phase 7.11 §16). Not collapsed.
GAP_NO_DATA = "NO_DATA"
GAP_EXISTS_NO_MATCH = "DATA_EXISTS_NO_COMPATIBLE_MATCH"
GAP_EXISTS_ACCESS_BLOCKED = "DATA_EXISTS_BUT_ACCESS_BLOCKED"
GAP_EXISTS_UNKNOWN_COMPAT = "DATA_EXISTS_WITH_UNKNOWN_COMPATIBILITY"
GAP_AVAILABLE_COMPATIBLE = "DATA_AVAILABLE_AND_COMPATIBLE"


def default_paths(root: Path) -> dict[str, Path]:
    return {
        "crw_raw": root / "data" / "phase75" / "raw",
        "crw_provenance": root / "data" / "phase75" / "provenance.json",
        "allen_raw": root / "data" / "phase75" / "allen" / "raw",
        "allen_provenance": root / "data" / "phase75" / "allen" / "provenance.json",
        "mermaid_inquiry": root / "data" / "phase763" / "mermaid-inquiry.json",
        "mermaid_australia": root / "data" / "phase763" / "mermaid-australia-summary.json",
    }


def build_integrated_spot_intelligence(
    root: Path,
    *,
    spot_id: str | None = None,
    paths: dict[str, Path] | None = None,
) -> dict[str, Any]:
    spot_id = spot_id or DEMO_SPOT_ID
    if spot_id != DEMO_SPOT_ID:
        raise KeyError(spot_id)
    resolved = paths or default_paths(root)

    crw = build_crw_spot_intelligence(resolved["crw_raw"], resolved["crw_provenance"])
    allen = build_allen_spot_intelligence(
        resolved["allen_raw"],
        resolved["allen_provenance"],
        spot_id=spot_id,
    )
    mermaid = build_mermaid_spot_intelligence(
        resolved["mermaid_inquiry"],
        resolved["mermaid_australia"],
        spot_id=spot_id,
    )

    thermal = _thermal_section(crw)
    habitat = _habitat_section(allen)
    field = _field_section(mermaid)
    sources = {
        "NOAA_CORAL_REEF_WATCH": {
            "role": "THERMAL",
            "integration": "PARTIAL",
            "epistemic": "EXTERNAL_INDICATOR",
            "availability": thermal["availability"],
            "summary": thermal["summary"],
        },
        "ALLEN_CORAL_ATLAS": {
            "role": "HABITAT_SPATIAL_CONTEXT",
            "integration": "PARTIAL",
            "epistemic": "CONTEXT_ONLY",
            "availability": habitat["availability"],
            "summary": habitat["summary"],
        },
        "MERMAID": {
            "role": "FIELD_ECOLOGICAL_OBSERVATIONS",
            "integration": "PARTIAL",
            "epistemic": "MEASURED_ECOLOGICAL_OBSERVATION_WHEN_COMPATIBLE",
            "availability": field["availability"],
            "summary": field["summary"],
        },
    }
    data_gaps = _integrated_gaps(crw, allen, mermaid, thermal, habitat, field)
    conflicts = _source_conflicts(crw, allen, mermaid, thermal, habitat, field)
    evidence = _evidence_chain(crw, allen, mermaid)
    quality = {
        "by_source": {
            "NOAA_CORAL_REEF_WATCH": "PARTIAL",
            "ALLEN_CORAL_ATLAS": "PARTIAL",
            "MERMAID": "PARTIAL",
        },
        "overall_quality_score": None,
        "note": "Quality stays source-specific. No aggregate quality formula is authorized.",
    }
    freshness = {
        "by_source": {
            "NOAA_CORAL_REEF_WATCH": crw["freshness"],
            "ALLEN_CORAL_ATLAS": allen["freshness"],
            "MERMAID": mermaid["freshness"],
        },
        "note": "Retrieval freshness is not observation recency or scientific temporal currency.",
    }
    uncertainty = {
        "measurement_uncertainty": "UNKNOWN",
        "spatial_uncertainty": "PARTIAL",
        "temporal_uncertainty": "PARTIAL",
        "association_uncertainty": "PARTIAL",
        "methodological_uncertainty": "PARTIAL",
        "model_uncertainty": "NOT_APPLICABLE",
        "aggregate_uncertainty_score": None,
        "by_source": {
            "NOAA_CORAL_REEF_WATCH": crw["uncertainty"],
            "ALLEN_CORAL_ATLAS": allen["uncertainty"],
            "MERMAID": mermaid["uncertainty"],
        },
        "note": "Dimensions stay separate. UNKNOWN is not zero.",
    }
    scientific_acceptance = {
        "THERMAL": "CRW evidence available",
        "HABITAT": "Allen context partially available",
        "FIELD_ECOLOGY": "MERMAID data exists BUT NO COMPATIBLE MATCH",
        "THERMAL_GROUND_TRUTH": "NOT_AVAILABLE",
        "LOCAL_ESTIMATION": "NOT_AUTHORIZED",
    }
    package = {
        "contract_version": CONTRACT_VERSION,
        "phase": PHASE,
        "spot": {
            "spot_id": spot_id,
            "label": crw["spot"]["label"],
            "geometry_type": crw["spot"]["geometry_type"],
            "latitude": crw["spot"]["latitude"],
            "longitude": crw["spot"]["longitude"],
            "crs": crw["spot"]["crs"],
            "spatial_precision": crw["spot"]["spatial_precision"],
            "coordinates_unchanged": True,
            "source": crw["spot"]["source"],
        },
        "spatial_context": {
            "spot_crs": crw["spot"]["crs"],
            "note": "Source geometries keep their own CRS status. UNKNOWN CRS blocks production comparison.",
        },
        "temporal_context": {
            "spot_reference_time": "UNKNOWN",
            "policy": "NOT_DEFINED",
            "note": "retrieved_at is never used as observed_at.",
        },
        "sources": sources,
        "thermal_evidence": thermal,
        "ecological_habitat_context": habitat,
        "field_ecological_observations": field,
        "indicators": {
            "external": thermal["indicators"],
            "derived": [],
            "note": "No thermal_risk_score or weighted combination is produced.",
        },
        "associations": {
            "spatial": {
                "NOAA_CORAL_REEF_WATCH": crw["spatial_associations"],
                "ALLEN_CORAL_ATLAS": allen["spatial_association"],
                "MERMAID": mermaid["spatial_association"],
            },
            "temporal": {
                "NOAA_CORAL_REEF_WATCH": [item["temporal_association"] for item in crw["external_indicators"]],
                "ALLEN_CORAL_ATLAS": allen["temporal_association"],
                "MERMAID": mermaid["temporal_association"],
            },
        },
        "evidence": evidence,
        "quality": quality,
        "freshness": freshness,
        "uncertainty": uncertainty,
        "data_gaps": data_gaps,
        "source_conflicts": conflicts,
        "provenance": {
            "sources": ["NOAA_CORAL_REEF_WATCH", "ALLEN_CORAL_ATLAS", "MERMAID"],
            "per_source_builders": {
                "NOAA_CORAL_REEF_WATCH": "build_crw_spot_intelligence",
                "ALLEN_CORAL_ATLAS": "build_allen_spot_intelligence",
                "MERMAID": "build_mermaid_spot_intelligence",
            },
            "paths": {key: str(value) for key, value in resolved.items()},
            "note": "Each evidence item retains raw file / checksum / transformation chain from its source builder.",
        },
        "scientific_acceptance": scientific_acceptance,
        "epistemic_rules": {
            "measured_ecological_observation_is_measured_temperature": False,
            "allen_is_field_observation": False,
            "crw_is_local_temperature": False,
            "crw_baa_is_baliza_alert": False,
            "mermaid_absence_is_no_bleaching": False,
            "mermaid_absence_is_healthy": False,
            "near_promoted_to_measured": False,
            "pixel_association_is_local_measurement": False,
        },
        "estimated": "NONE",
        "downscaling": "NOT_AUTHORIZED",
        "ml_implementation": "NOT_AUTHORIZED",
        "local_estimation": "NOT_AUTHORIZED",
        "thermal_ground_truth": "NOT_AVAILABLE",
        "alerts": [],
        "decisions": [],
        "actions": [],
        "outcomes": [],
        "baliza_alert_separation": {
            "integrated_spot_intelligence_creates_baliza_alert": False,
            "crw": crw["baliza_alert_separation"],
            "allen": allen["baliza_alert_separation"],
            "mermaid": mermaid["baliza_alert_separation"],
        },
        "dss_compatibility": _dss_compatibility(evidence, data_gaps, uncertainty, conflicts),
        "alert_compatibility": _alert_compatibility(evidence),
        "human_readable": None,  # filled below
        "source_packages": {
            "crw": crw,
            "allen": allen,
            "mermaid": mermaid,
        },
    }
    package["human_readable"] = render_human_readable(package)
    return package


def render_human_readable(package: dict[str, Any]) -> str:
    thermal = package["thermal_evidence"]
    habitat = package["ecological_habitat_context"]
    field = package["field_ecological_observations"]
    lines = [
        "SPOT INTELLIGENCE",
        "",
        "SPOT",
        package["spot"]["spot_id"],
        f"Latitude: {package['spot']['latitude']}",
        f"Longitude: {package['spot']['longitude']}",
        f"CRS: {package['spot']['crs']}",
        "",
        "THERMAL",
        "NOAA CRW",
    ]
    for name, status in thermal["product_status"].items():
        lines.append(f"- {name}: {status}")
    lines.extend(
        [
            "",
            "Classification:",
            "EXTERNAL INDICATOR",
            "",
            "HABITAT / SPATIAL CONTEXT",
            "Allen Coral Atlas",
            f"- benthic classification: {habitat['benthic_status']}",
            f"- geomorphic context: {habitat['geomorphic_status']}",
            f"- coverage for this Spot: {habitat['coverage']}",
            "",
            "Classification:",
            "CONTEXT ONLY",
            "",
            "FIELD ECOLOGICAL OBSERVATIONS",
            "MERMAID",
            f"- compatible field observations: {field['compatible_count']}",
            f"- status: {field['status_label']}",
            "",
            "IMPORTANT:",
            "Absence of a compatible MERMAID observation",
            "does not imply absence of bleaching.",
            "",
            "THERMAL GROUND TRUTH",
            package["thermal_ground_truth"],
            "",
            "LOCAL ESTIMATION",
            package["local_estimation"],
            "",
            "UNCERTAINTY",
            f"- measurement: {package['uncertainty']['measurement_uncertainty']}",
            f"- spatial: {package['uncertainty']['spatial_uncertainty']}",
            f"- temporal: {package['uncertainty']['temporal_uncertainty']}",
            f"- association: {package['uncertainty']['association_uncertainty']}",
            f"- methodological: {package['uncertainty']['methodological_uncertainty']}",
            f"- model: {package['uncertainty']['model_uncertainty']}",
            "",
            "DATA GAPS",
        ]
    )
    for gap in package["data_gaps"]:
        lines.append(f"- [{gap['availability']}] {gap['source']}: {gap['detail']}")
    lines.extend(["", "SOURCE CONFLICTS"])
    for item in package["source_conflicts"]:
        lines.append(f"- {item['result']}: {item['detail']}")
    lines.extend(
        [
            "",
            "ESTIMATED: NONE",
            "DOWNSCALING: NOT_AUTHORIZED",
            "ML_IMPLEMENTATION: NOT_AUTHORIZED",
            "No thermal_risk_score.",
            "No Decision. No Action. No BALIZA alert from this integration.",
        ]
    )
    return "\n".join(lines)


def _thermal_section(crw: dict) -> dict:
    product_map = {
        "SST": "noaacrwsstDaily",
        "SST anomaly": "noaacrwsstanomalyDaily",
        "HotSpot": "noaacrwhotspotDaily",
        "DHW": "noaacrwdhwDaily",
        "Bleaching Alert Area": "noaacrwbaa7dDaily",
    }
    available_ids = {item["dataset_id"] for item in crw["external_indicators"]}
    product_status = {
        label: "available" if dataset_id in available_ids else "not available"
        for label, dataset_id in product_map.items()
    }
    # Baseline anomaly is also present; keep products separate, no risk score.
    indicators = []
    for item in crw["external_indicators"]:
        ind = item["indicator"]
        indicators.append(
            {
                "source": "NOAA_CORAL_REEF_WATCH",
                "dataset_id": item["dataset_id"],
                "what": ind["what"],
                "value": ind["value"],
                "unit": ind.get("unit") or ind.get("original_unit"),
                "epistemic": "EXTERNAL_INDICATOR",
                "applies_to": item["applies_to"],
                "spatial_association": item["spatial_association"],
                "temporal_association": item["temporal_association"],
                "cell": item["cell"],
                "baliza_alert": ind.get("baliza_alert"),
            }
        )
    return {
        "source": "NOAA_CORAL_REEF_WATCH",
        "epistemic": "EXTERNAL_INDICATOR",
        "availability": GAP_EXISTS_UNKNOWN_COMPAT,
        "summary": "Six CRW products on one retrieved cell. Production spatial association UNKNOWN (CRS unknown).",
        "product_status": product_status,
        "indicators": indicators,
        "thermal_risk_score": None,
        "local_temperature": False,
        "nearest_selected": False,
        "interpolated": False,
        "averaged": False,
    }


def _habitat_section(allen: dict) -> dict:
    coverage = allen.get("allen_spatial_coverage", "NOT_AVAILABLE")
    layers_elsewhere = allen.get("context_layers_available_elsewhere") or []
    has_extract = bool(layers_elsewhere) or bool(allen.get("external_indicators"))
    if coverage == "NOT_AVAILABLE":
        availability = GAP_EXISTS_NO_MATCH if has_extract else GAP_NO_DATA
        benthic = "partial (extract exists elsewhere; not attached to this Spot)"
        geomorphic = "partial (extract exists elsewhere; not attached to this Spot)"
        summary = "Allen WFS extracts exist, but the DEMO Spot is outside the stored bbox. Classes are not attached."
    else:
        availability = GAP_EXISTS_UNKNOWN_COMPAT
        benthic = "partial"
        geomorphic = "partial"
        summary = "Allen attributes available for a containing bbox; feature geometry null; no class attached as Spot value."
    context_items = []
    for layer in layers_elsewhere:
        context_items.append(
            {
                "source": "ALLEN_CORAL_ATLAS",
                "product": layer["indicator"].get("product") or layer["indicator"].get("layer"),
                "layer": layer["indicator"].get("layer"),
                "version": layer["provenance"].get("version", "UNKNOWN"),
                "epoch": layer["provenance"].get("epoch", "UNKNOWN"),
                "epistemic_type": "CONTEXT_ONLY",
                "spatial_relationship": allen["spatial_association"],
                "temporal_semantics": allen["temporal_association"],
                "quality": allen["quality"],
                "uncertainty": allen["uncertainty"],
                "provenance": {
                    "raw_file": layer["provenance"].get("raw_file"),
                    "raw_checksum_sha256": layer["provenance"].get("raw_checksum_sha256"),
                },
                "field_observation": False,
                "applies_to_this_spot": False,
            }
        )
    return {
        "source": "ALLEN_CORAL_ATLAS",
        "epistemic": "CONTEXT_ONLY",
        "availability": availability,
        "coverage": coverage,
        "benthic_status": benthic,
        "geomorphic_status": geomorphic,
        "summary": summary,
        "context_items": context_items,
        "class_attached_to_spot": allen.get("class_attached_to_spot", False),
        "field_observation": False,
    }


def _field_section(mermaid: dict) -> dict:
    compatible = mermaid.get("field_observations_for_spot") or []
    match = mermaid.get("demo_spot_match")
    australia_count = mermaid.get("australia_summary", {}).get("count", 0)
    if compatible:
        availability = GAP_AVAILABLE_COMPATIBLE
        status_label = "DATA AVAILABLE AND COMPATIBLE"
    elif match == "NO_MATCH" and australia_count:
        availability = GAP_EXISTS_NO_MATCH
        status_label = "DATA EXISTS BUT NO COMPATIBLE MATCH"
    else:
        availability = GAP_NO_DATA
        status_label = "NO DATA"
    access_gaps = [
        gap for gap in mermaid.get("data_gaps", []) if gap.get("kind") == "LICENSE_ACCESS_GAP"
    ]
    return {
        "source": "MERMAID",
        "epistemic": "MEASURED_ECOLOGICAL_OBSERVATION_WHEN_COMPATIBLE",
        "availability": availability,
        "status_label": status_label,
        "compatible_count": len(compatible),
        "compatible_observations": compatible,
        "summary": (
            "MERMAID FIELD OBSERVATION: NOT AVAILABLE FOR THIS SPOT. "
            "Australia summary records exist elsewhere. Absence is not 'no bleaching' or 'healthy'."
        ),
        "mermaid_access": mermaid.get("mermaid_access"),
        "mermaid_spatial_compatibility": mermaid.get("mermaid_spatial_compatibility"),
        "mermaid_temporal_compatibility": mermaid.get("mermaid_temporal_compatibility"),
        "mermaid_thermal_ground_truth": mermaid.get("mermaid_thermal_ground_truth"),
        "ground_truth_availability": mermaid.get("ground_truth_availability"),
        "access_blocked_note": access_gaps[0]["detail"] if access_gaps else None,
        "australia_summary_count": australia_count,
        "bleaching_semantics": mermaid.get("bleaching_semantics"),
    }


def _integrated_gaps(
    crw: dict,
    allen: dict,
    mermaid: dict,
    thermal: dict,
    habitat: dict,
    field: dict,
) -> list[dict]:
    gaps = [
        {
            "source": "NOAA_CORAL_REEF_WATCH",
            "availability": thermal["availability"],
            "kind": "SPATIAL_GAP",
            "detail": "CRW products exist on one retrieved cell; production association stays UNKNOWN (CRS unknown).",
            "implies_no_risk": False,
        },
        {
            "source": "ALLEN_CORAL_ATLAS",
            "availability": habitat["availability"],
            "kind": "SPATIAL_GAP",
            "detail": "Allen extracts exist; DEMO Spot has no attached class (bbox / null geometry).",
            "implies_no_risk": False,
        },
        {
            "source": "MERMAID",
            "availability": field["availability"],
            "kind": "GROUND_TRUTH_GAP",
            "detail": (
                "MERMAID data exists (Australia summaries) but no compatible field observation "
                "for this Spot. Not equivalent to NO_DATA, NO_BLEACHING, or HEALTHY."
            ),
            "implies_no_risk": False,
            "implies_no_bleaching": False,
            "implies_healthy": False,
        },
        {
            "source": "MERMAID",
            "availability": GAP_EXISTS_ACCESS_BLOCKED,
            "kind": "LICENSE_ACCESS_GAP",
            "detail": "Observation-level / sites access remains blocked (HTTP 401 on sites).",
            "implies_no_risk": False,
        },
        {
            "source": "INTEGRATED",
            "availability": GAP_NO_DATA,
            "kind": "GROUND_TRUTH_GAP",
            "detail": "THERMAL_GROUND_TRUTH = NOT_AVAILABLE. No local temperature measurement.",
            "implies_no_risk": False,
        },
    ]
    # Preserve source-level gap details without promoting them.
    for source_name, package in (
        ("NOAA_CORAL_REEF_WATCH", crw),
        ("ALLEN_CORAL_ATLAS", allen),
        ("MERMAID", mermaid),
    ):
        for gap in package.get("data_gaps", []):
            gaps.append(
                {
                    "source": source_name,
                    "availability": "SOURCE_REPORTED",
                    "kind": gap.get("kind", "DATA_GAP"),
                    "detail": gap.get("detail") or gap.get("reason") or json.dumps(gap),
                    "implies_no_risk": False,
                }
            )
    return gaps


def _source_conflicts(
    crw: dict,
    allen: dict,
    mermaid: dict,
    thermal: dict,
    habitat: dict,
    field: dict,
) -> list[dict]:
    conflicts = []
    # Intra-CRW anomaly conflict retained, unresolved.
    for item in crw.get("source_conflicts") or []:
        conflicts.append(
            {
                "sources": ["NOAA_CORAL_REEF_WATCH"],
                "dimension": item.get("dimension"),
                "result": "SOURCE_DIFFERENCE" if item.get("conflict") else "NO_DIRECT_CONFLICT",
                "resolved": False,
                "detail": f"CRW internal anomaly comparison; resolved={item.get('resolved')}",
                "values": item.get("values"),
            }
        )
    # CRW present + MERMAID no match is not a conflict about bleaching state.
    conflicts.append(
        {
            "sources": ["NOAA_CORAL_REEF_WATCH", "MERMAID"],
            "dimension": "thermal_indicator_vs_field_observation",
            "result": "NO_DIRECT_CONFLICT",
            "resolved": False,
            "detail": (
                f"CRW availability={thermal['availability']}; "
                f"MERMAID={field['status_label']}. "
                "Missing field observation is not disagreement with CRW, and does not validate CRW."
            ),
            "automatic_causality": False,
            "automatic_validation": False,
        }
    )
    # Allen vs MERMAID cannot conflict without a compatible MERMAID row and attached Allen class.
    if not habitat["class_attached_to_spot"] or field["compatible_count"] == 0:
        conflicts.append(
            {
                "sources": ["ALLEN_CORAL_ATLAS", "MERMAID"],
                "dimension": "mapped_habitat_vs_field_benthic",
                "result": "NO_DIRECT_CONFLICT",
                "resolved": False,
                "detail": (
                    "Allen class is not attached to the DEMO Spot and/or no compatible MERMAID "
                    "field observation exists. Sources remain separate; no source-of-truth chosen."
                ),
            }
        )
    else:
        conflicts.append(
            {
                "sources": ["ALLEN_CORAL_ATLAS", "MERMAID"],
                "dimension": "mapped_habitat_vs_field_benthic",
                "result": "SOURCE_DIFFERENCE",
                "resolved": False,
                "detail": "Both sources present different epistemic layers. No automatic reconciliation.",
            }
        )
    return conflicts


def _evidence_chain(crw: dict, allen: dict, mermaid: dict) -> dict:
    items = []
    for item in crw.get("evidence") or []:
        items.append(
            {
                **item,
                "source": "NOAA_CORAL_REEF_WATCH",
                "evidence_completeness": "PARTIAL",
                "missing": ["production spatial association confirmation", "observation_time"],
            }
        )
    for item in allen.get("evidence") or []:
        items.append({**item, "source": "ALLEN_CORAL_ATLAS"})
    # DEMO Allen returns empty evidence by design; still note context provenance from layers.
    for layer in allen.get("context_layers_available_elsewhere") or []:
        items.append(
            {
                "evidence_id": f"allen-context-{layer['indicator'].get('layer')}",
                "source": "ALLEN_CORAL_ATLAS",
                "scientific_layer": "CONTEXT_ONLY",
                "epistemic_label": "FACT",
                "raw_file": layer["provenance"].get("raw_file"),
                "raw_checksum_sha256": layer["provenance"].get("raw_checksum_sha256"),
                "applies_to_this_spot": False,
                "evidence_completeness": "PARTIAL",
                "missing": ["spot attachment", "feature geometry", "map_epoch"],
                "field_observation": False,
            }
        )
    for item in mermaid.get("evidence") or []:
        items.append({**item, "source": "MERMAID"})
    if not (mermaid.get("evidence") or []):
        items.append(
            {
                "evidence_id": "mermaid-demo-no-match",
                "source": "MERMAID",
                "scientific_layer": "NOT_AVAILABLE",
                "epistemic_label": "FACT",
                "narrative": "No compatible MERMAID field observation for this Spot.",
                "evidence_completeness": "PARTIAL",
                "missing": [
                    "compatible record",
                    "spatial association",
                    "temporal association",
                    "raw body (privacy)",
                ],
                "inquiry_provenance": mermaid.get("inquiry_provenance"),
                "australia_response_sha256": mermaid.get("australia_summary", {}).get("response_sha256"),
            }
        )
    complete = all(item.get("evidence_completeness") == "COMPLETE" for item in items) if items else False
    return {
        "items": items,
        "evidence_completeness": "COMPLETE" if complete else "PARTIAL",
        "traceable": True,
        "note": "Each item keeps source raw checksum / path when available. Gaps are explicit.",
    }


def _dss_compatibility(
    evidence: dict,
    data_gaps: list[dict],
    uncertainty: dict,
    conflicts: list[dict],
) -> dict:
    """Payload a later DssPackage can attach without converting evidence→recommendation."""
    return {
        "can_feed_dss_package": True,
        "creates_recommendation": False,
        "creates_decision": False,
        "creates_action": False,
        "creates_outcome": False,
        "attachable": {
            "evidence_refs": [item["evidence_id"] for item in evidence["items"]],
            "gaps": [
                {
                    "kind": gap["kind"],
                    "reason": gap["detail"],
                    "source_type": gap["source"],
                    "source_id": gap.get("availability", "UNKNOWN"),
                }
                for gap in data_gaps
                if gap.get("availability") != "SOURCE_REPORTED"
            ],
            "uncertainty_notes": [
                f"{key}={value}"
                for key, value in uncertainty.items()
                if key.endswith("_uncertainty") or key == "model_uncertainty"
            ],
            "conflicts_unresolved": [item for item in conflicts if not item.get("resolved")],
        },
        "note": "DSS may present this classified evidence. It must not auto-convert indicators into decisions.",
    }


def _alert_compatibility(evidence: dict) -> dict:
    """An Alert may reference these evidence ids later; this phase creates none."""
    return {
        "can_be_referenced_by_alert": True,
        "creates_alert": False,
        "rule_version_changed": False,
        "thresholds_changed": False,
        "severity_policy_changed": False,
        "referenceable_evidence_ids": [item["evidence_id"] for item in evidence["items"]],
        "note": "Integration does not generate BALIZA alerts. Future alerts may cite these evidence ids.",
    }
