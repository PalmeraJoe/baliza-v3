"""Phase 7.15 — Scientific Pilot / IMR specification coherence tests."""

from __future__ import annotations

from pathlib import Path

from baliza.application.phase715_scientific_pilot import (
    REQUIRED,
    TO_CONFIRM,
    build_scientific_pilot_specification,
    write_specification_artifact,
)

ROOT = Path(__file__).resolve().parents[1]


def test_pilot_objective_is_validation_not_ml_first() -> None:
    spec = build_scientific_pilot_specification()
    assert "predictive model" in spec["pilot_objective_is_not"].lower()
    assert "dss" in spec["pilot_objective"].lower()
    assert spec["assumed_next_state"] is None


def test_imr_connector_not_implemented() -> None:
    spec = build_scientific_pilot_specification()
    assert spec["implementation_status"]["imr_connector"] == "NOT_IMPLEMENTED"
    assert spec["implementation_status"]["imr_data_import"] == "NOT_IMPLEMENTED"
    assert spec["implementation_status"]["ml"] == "NOT_AUTHORIZED"
    assert spec["implementation_status"]["local_estimation"] == "NOT_AUTHORIZED"
    assert spec["implementation_status"]["downscaling"] == "NOT_AUTHORIZED"
    assert not (ROOT / "src" / "baliza" / "infrastructure" / "sources" / "imr").exists()


def test_imr_not_automatic_ground_truth_and_calibration_split() -> None:
    spec = build_scientific_pilot_specification()
    assert spec["data_governance"]["imr_automatically_ground_truth"] is False
    assert spec["data_governance"]["calibration_equals_independent_validation"] is False
    assert spec["data_governance"]["raw_must_be_preserved"] is True


def test_candidate_targets_remain_not_adopted() -> None:
    spec = build_scientific_pilot_specification()
    assert set(spec["candidate_targets"].values()) == {"CANDIDATE_NOT_ADOPTED"}


def test_ml_gate_not_authorized_and_complete() -> None:
    spec = build_scientific_pilot_specification()
    assert spec["ml_gate"]["status"] == "NOT_AUTHORIZED"
    assert "independent validation available" in spec["ml_gate"]["required"]
    assert "scientific partner approval" in spec["ml_gate"]["required"]


def test_minimum_package_and_confirm_lists_nonempty() -> None:
    spec = build_scientific_pilot_specification()
    assert spec["minimum_data_package"]["spatial_identity"] == REQUIRED
    assert spec["minimum_data_package"]["ecological_observations"] == TO_CONFIRM
    assert len(spec["required_from_imr"]) >= 5
    assert len(spec["strongly_preferred"]) >= 3
    assert len(spec["optional"]) >= 1
    assert len(spec["to_confirm"]) >= 3
    assert len(spec["success_criteria"]) == 6
    assert len(spec["failure_blocking_conditions"]) >= 5


def test_artifact_matches_spec_and_docs_exist() -> None:
    import json

    path = write_specification_artifact(ROOT)
    stored = json.loads(path.read_text(encoding="utf-8"))
    assert stored == build_scientific_pilot_specification()
    assert (ROOT / "docs" / "59-phase7.15-scientific-pilot-imr-specification.md").is_file()
