"""Phase 7.11 — Integrated Spot Intelligence tests."""

from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from baliza.domain.dss import DssPackage, freeze_dss_package
from baliza.domain.ids import DssPackageId
from baliza.infrastructure.sources.crw.catalog import DEMO_SPOT
from baliza.infrastructure.sources.integrated.spot_intelligence import (
    GAP_EXISTS_ACCESS_BLOCKED,
    GAP_EXISTS_NO_MATCH,
    GAP_EXISTS_UNKNOWN_COMPAT,
    build_integrated_spot_intelligence,
    render_human_readable,
)
from baliza.interfaces.api.app import app
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
client = TestClient(app)


def _package() -> dict:
    return build_integrated_spot_intelligence(ROOT, spot_id=DEMO_SPOT["spot_id"])


def test_crw_evidence_appears_as_external_indicators() -> None:
    package = _package()
    thermal = package["thermal_evidence"]
    assert thermal["epistemic"] == "EXTERNAL_INDICATOR"
    assert thermal["product_status"]["SST"] == "available"
    assert thermal["product_status"]["SST anomaly"] == "available"
    assert thermal["product_status"]["HotSpot"] == "available"
    assert thermal["product_status"]["DHW"] == "available"
    assert thermal["product_status"]["Bleaching Alert Area"] == "available"
    assert thermal["thermal_risk_score"] is None
    assert thermal["local_temperature"] is False
    assert all(item["epistemic"] == "EXTERNAL_INDICATOR" for item in thermal["indicators"])
    assert len(thermal["indicators"]) == 6


def test_allen_evidence_is_context_only_not_field() -> None:
    package = _package()
    habitat = package["ecological_habitat_context"]
    assert habitat["epistemic"] == "CONTEXT_ONLY"
    assert habitat["field_observation"] is False
    assert habitat["class_attached_to_spot"] is False
    assert habitat["coverage"] == "NOT_AVAILABLE"
    assert habitat["availability"] == GAP_EXISTS_NO_MATCH
    assert package["epistemic_rules"]["allen_is_field_observation"] is False


def test_mermaid_no_match_is_not_no_data_or_no_risk() -> None:
    package = _package()
    field = package["field_ecological_observations"]
    assert field["availability"] == GAP_EXISTS_NO_MATCH
    assert field["status_label"] == "DATA EXISTS BUT NO COMPATIBLE MATCH"
    assert field["compatible_count"] == 0
    assert "NOT AVAILABLE FOR THIS SPOT" in field["summary"]
    mermaid_gaps = [g for g in package["data_gaps"] if g["source"] == "MERMAID"]
    assert any(g["availability"] == GAP_EXISTS_NO_MATCH for g in mermaid_gaps)
    assert any(g["availability"] == GAP_EXISTS_ACCESS_BLOCKED for g in mermaid_gaps)
    assert all(g.get("implies_no_bleaching") is not True for g in mermaid_gaps)
    assert all(g.get("implies_healthy") is not True for g in mermaid_gaps)
    assert all(g.get("implies_no_risk") is False for g in package["data_gaps"])


def test_epistemic_layers_stay_separate() -> None:
    package = _package()
    assert package["epistemic_rules"]["measured_ecological_observation_is_measured_temperature"] is False
    assert package["epistemic_rules"]["crw_is_local_temperature"] is False
    assert package["epistemic_rules"]["crw_baa_is_baliza_alert"] is False
    assert package["epistemic_rules"]["near_promoted_to_measured"] is False
    assert package["epistemic_rules"]["pixel_association_is_local_measurement"] is False
    assert package["sources"]["NOAA_CORAL_REEF_WATCH"]["epistemic"] == "EXTERNAL_INDICATOR"
    assert package["sources"]["ALLEN_CORAL_ATLAS"]["epistemic"] == "CONTEXT_ONLY"
    assert "MEASURED" in package["sources"]["MERMAID"]["epistemic"]


def test_sources_remain_separate_and_conflicts_unresolved() -> None:
    package = _package()
    assert set(package["sources"]) == {
        "NOAA_CORAL_REEF_WATCH",
        "ALLEN_CORAL_ATLAS",
        "MERMAID",
    }
    assert package["indicators"]["derived"] == []
    assert package["thermal_evidence"]["thermal_risk_score"] is None
    assert all("risk_score" not in item for item in package["indicators"]["external"])
    conflicts = package["source_conflicts"]
    assert any(c["result"] == "NO_DIRECT_CONFLICT" and "MERMAID" in c["sources"] for c in conflicts)
    assert all(c.get("resolved") is False for c in conflicts)
    assert all(c.get("automatic_validation") is not True for c in conflicts)
    assert all(c.get("automatic_causality") is not True for c in conflicts)


def test_spatial_and_temporal_associations_preserved() -> None:
    package = _package()
    spatial = package["associations"]["spatial"]
    temporal = package["associations"]["temporal"]
    assert spatial["NOAA_CORAL_REEF_WATCH"]["production"]["association_type"] == "UNKNOWN"
    assert spatial["NOAA_CORAL_REEF_WATCH"]["production"]["nearest_selected"] is False
    assert spatial["NOAA_CORAL_REEF_WATCH"]["production"]["interpolated"] is False
    assert spatial["NOAA_CORAL_REEF_WATCH"]["production"]["averaged_value"] is None
    assert spatial["ALLEN_CORAL_ATLAS"]["association_type"] == "UNKNOWN"
    assert spatial["MERMAID"]["association_type"] == "UNKNOWN"
    assert spatial["MERMAID"]["near_promoted_to_measured"] is False
    assert package["thermal_evidence"]["availability"] == GAP_EXISTS_UNKNOWN_COMPAT
    crw_temporal = temporal["NOAA_CORAL_REEF_WATCH"][0]
    assert crw_temporal["association_type"] == "UNKNOWN"
    assert crw_temporal["ingestion_time"] != crw_temporal.get("observation_time") or crw_temporal[
        "observation_time"
    ] == "UNKNOWN"
    assert temporal["MERMAID"]["policy"] == "NOT_DEFINED"
    assert temporal["ALLEN_CORAL_ATLAS"]["map_epoch_is_observation_time"] is False


def test_quality_freshness_uncertainty_not_aggregated() -> None:
    package = _package()
    assert package["quality"]["overall_quality_score"] is None
    assert package["quality"]["by_source"]["NOAA_CORAL_REEF_WATCH"] == "PARTIAL"
    assert package["uncertainty"]["aggregate_uncertainty_score"] is None
    assert package["uncertainty"]["measurement_uncertainty"] == "UNKNOWN"
    freshness_note = package["freshness"]["note"]
    assert "Retrieval freshness" in freshness_note
    mermaid_fresh = package["freshness"]["by_source"]["MERMAID"]
    assert mermaid_fresh["retrieval_freshness"] != mermaid_fresh.get("observation_recency") or mermaid_fresh[
        "observation_recency"
    ] == "UNKNOWN"


def test_evidence_chain_provenance_and_reproducibility() -> None:
    first = _package()
    second = _package()
    assert first["evidence"]["evidence_completeness"] == "PARTIAL"
    assert first["evidence"]["traceable"] is True
    crw_ids = [e["evidence_id"] for e in first["evidence"]["items"] if e["source"] == "NOAA_CORAL_REEF_WATCH"]
    assert len(crw_ids) == 6
    assert all(e.get("raw_checksum_sha256") for e in first["evidence"]["items"] if e["source"] == "NOAA_CORAL_REEF_WATCH")
    assert any(e["evidence_id"] == "mermaid-demo-no-match" for e in first["evidence"]["items"])
    # Drop bulky nested source packages for equality of the canonical contract fields.
    for key in ("spot", "scientific_acceptance", "estimated", "thermal_ground_truth", "data_gaps"):
        assert first[key] == second[key]
    assert first["spot"]["latitude"] == -23.5
    assert first["spot"]["longitude"] == 152.0
    assert first["spot"]["coordinates_unchanged"] is True


def test_dss_and_alert_compatibility_without_decision_or_action() -> None:
    package = _package()
    assert package["dss_compatibility"]["can_feed_dss_package"] is True
    assert package["dss_compatibility"]["creates_recommendation"] is False
    assert package["dss_compatibility"]["creates_decision"] is False
    assert package["dss_compatibility"]["creates_action"] is False
    assert package["alert_compatibility"]["creates_alert"] is False
    assert package["alert_compatibility"]["rule_version_changed"] is False
    assert package["alerts"] == []
    assert package["decisions"] == []
    assert package["actions"] == []
    assert package["outcomes"] == []
    assert package["estimated"] == "NONE"
    assert package["downscaling"] == "NOT_AUTHORIZED"
    assert package["ml_implementation"] == "NOT_AUTHORIZED"
    assert package["local_estimation"] == "NOT_AUTHORIZED"
    assert package["thermal_ground_truth"] == "NOT_AVAILABLE"

    now = datetime(2026, 10, 4, 8, 0, tzinfo=timezone.utc)
    dss = DssPackage(id=DssPackageId(), opened_at=now)
    for gap in package["dss_compatibility"]["attachable"]["gaps"]:
        dss.add_gap(f"{gap['source_type']}:{gap['kind']}:{gap['reason']}")
    for note in package["dss_compatibility"]["attachable"]["uncertainty_notes"]:
        dss.uncertainty_notes.append(note)
    snapshot = freeze_dss_package(
        dss,
        frozen_at=now,
        extra={"spot_intelligence_contract": package["contract_version"]},
    )
    assert "spot_intelligence_contract" in snapshot.payload
    assert dss.recommendations == []
    assert package["alert_compatibility"]["referenceable_evidence_ids"]


def test_human_readable_and_scientific_acceptance() -> None:
    package = _package()
    text = package["human_readable"]
    assert "THERMAL" in text
    assert "EXTERNAL INDICATOR" in text
    assert "CONTEXT ONLY" in text
    assert "DATA EXISTS BUT NO COMPATIBLE MATCH" in text
    assert "does not imply absence of bleaching" in text
    assert "THERMAL GROUND TRUTH" in text
    assert "NOT_AVAILABLE" in text
    assert "LOCAL ESTIMATION" in text
    assert "NOT_AUTHORIZED" in text
    assert "thermal_risk_score" not in text.lower() or "No thermal_risk_score" in text
    acceptance = package["scientific_acceptance"]
    assert acceptance["THERMAL"] == "CRW evidence available"
    assert "Allen" in acceptance["HABITAT"]
    assert "NO COMPATIBLE MATCH" in acceptance["FIELD_ECOLOGY"]
    assert acceptance["THERMAL_GROUND_TRUTH"] == "NOT_AVAILABLE"
    assert acceptance["LOCAL_ESTIMATION"] == "NOT_AUTHORIZED"
    # Re-render is stable.
    assert render_human_readable(package) == text


def test_api_integrated_intelligence() -> None:
    response = client.get(f"/scientific/spots/{DEMO_SPOT['spot_id']}/intelligence")
    assert response.status_code == 200
    body = response.json()
    assert body["contract_version"].startswith("phase711")
    assert body["spot"]["spot_id"] == DEMO_SPOT["spot_id"]
    assert body["thermal_evidence"]["product_status"]["DHW"] == "available"
    assert body["field_ecological_observations"]["availability"] == GAP_EXISTS_NO_MATCH
    assert body["estimated"] == "NONE"
    assert body["ml_implementation"] == "NOT_AUTHORIZED"
    missing = client.get("/scientific/spots/NOT-A-SPOT/intelligence")
    assert missing.status_code == 404
