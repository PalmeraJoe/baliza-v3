"""Phase 7.13 — Pilot Readiness Review coherence tests.

Does not claim scientific validation is closed.
"""

from __future__ import annotations

from pathlib import Path

from baliza.application.phase713_pilot_readiness import (
    NOT_AUTHORIZED,
    NOT_READY,
    READY,
    READY_WITH_LIMITATIONS,
    REQUIRES_PILOT,
    build_pilot_readiness_assessment,
    write_assessment_artifact,
)

ROOT = Path(__file__).resolve().parents[1]


def test_product_ready_science_and_ml_not_confused() -> None:
    a = build_pilot_readiness_assessment()
    assert a["product_readiness"]["verdict"] == READY_WITH_LIMITATIONS
    assert "YES" in a["product_readiness"]["answer"]
    assert a["scientific_model_readiness"]["verdict"] == NOT_READY
    assert a["scientific_model_readiness"]["answer"] == "NO"
    assert a["ml_readiness"]["verdict"] == NOT_AUTHORIZED
    assert a["ml_readiness"]["authorization_gate"] == "NOT_PASSED"
    assert a["ml_authorization_gate"]["authorized_now"] is False
    assert a["ml_authorization_gate"]["status"] == "NOT_PASSED"


def test_imr_not_product_dependency_but_needed_for_pilot() -> None:
    a = build_pilot_readiness_assessment()
    assert a["imr"]["dependency_for_current_product"] == "NONE"
    assert a["imr"]["required_for_scientific_pilot"] is True
    assert a["imr"]["connector_implemented"] is False
    assert a["implemented_vs_tested_vs_scientifically_validated"]["imr_integration"][
        "required_for_current_product_foundation"
    ] is False
    assert not (ROOT / "src" / "baliza" / "infrastructure" / "sources" / "imr").exists()


def test_ml_capabilities_all_not_authorized() -> None:
    a = build_pilot_readiness_assessment()
    assert set(a["ml_capabilities"].values()) == {NOT_AUTHORIZED}


def test_calibration_not_equal_validation() -> None:
    a = build_pilot_readiness_assessment()
    assert a["calibration_vs_validation"]["calibration_equals_independent_validation"] is False
    assert a["calibration_vs_validation"]["same_row_may_serve_both"] is False


def test_partial_scientific_limitations_not_closed() -> None:
    a = build_pilot_readiness_assessment()
    lim = a["known_limitations"]
    assert lim["PROVENANCE"] == "PARTIAL"
    assert lim["QUALITY"] == "PARTIAL"
    assert lim["FRESHNESS"] == "PARTIAL"
    assert lim["UNCERTAINTY"] == "PARTIAL"
    assert lim["THERMAL_GROUND_TRUTH"] == "NOT_AVAILABLE"
    assert a["science_capabilities"]["ground_truth"] == NOT_READY
    assert a["science_capabilities"]["spatial_association"] == REQUIRES_PILOT
    assert a["science_capabilities"]["temporal_association"] == REQUIRES_PILOT


def test_go_no_go_matrix() -> None:
    a = build_pilot_readiness_assessment()
    g = a["go_no_go"]
    assert g["PRODUCT_PILOT"] == "GO"
    assert g["SCIENTIFIC_VALIDATION"] == "CONDITIONAL_GO"
    assert g["SCIENTIFIC_PILOT"] == "CONDITIONAL_GO"
    assert g["ML_LOCAL_PREDICTION"] == "NO_GO"
    assert g["ML_AUTHORIZATION"] == NOT_AUTHORIZED
    assert g["COMMERCIAL_PILOT"] == "NOT_READY"
    assert "NOT_AUTHORIZED" in g["overall"]
    assert "NOT_READY" in g["overall"]


def test_demo_thresholds_not_scientifically_validated() -> None:
    a = build_pilot_readiness_assessment()
    demo = a["implemented_vs_tested_vs_scientifically_validated"]["demo_thresholds"]
    assert demo["implemented"] is True
    assert demo["tested"] is True
    assert demo["scientifically_validated"] is False
    assert a["implemented_vs_tested_vs_scientifically_validated"]["product_dss_flow"][
        "scientifically_validated"
    ] is False


def test_human_decision_and_dss_remain_ready() -> None:
    a = build_pilot_readiness_assessment()
    assert a["product_capabilities"]["Human_Decision"] == READY
    assert a["product_capabilities"]["DSS_Package"] == READY
    assert a["product_capabilities"]["Snapshot"] == READY
    assert a["product_capabilities"]["Action"] == READY
    assert any("autonomous" in item.lower() for item in a["explicit_non_goals"])
    assert any("IMR" in item for item in a["explicit_non_goals"])
    assert any("ML" in item for item in a["explicit_non_goals"])


def test_artifact_written_matches_assessment() -> None:
    import json

    path = write_assessment_artifact(ROOT)
    stored = json.loads(path.read_text(encoding="utf-8"))
    assert stored == build_pilot_readiness_assessment()
    assert stored["assessment_version"].startswith("phase713")
