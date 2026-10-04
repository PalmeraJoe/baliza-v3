"""Phase 7.15 — Scientific Pilot / IMR specification (assessment only).

No IMR connector, importer, ML, or scientific threshold changes.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

PHASE = "7.15"
SPEC_VERSION = "phase715-scientific-pilot-imr-1"

REQUIRED = "REQUIRED"
STRONGLY_PREFERRED = "STRONGLY_PREFERRED"
OPTIONAL = "OPTIONAL"
TO_CONFIRM = "UNKNOWN / TO CONFIRM"


def build_scientific_pilot_specification() -> dict[str, Any]:
    return {
        "phase": PHASE,
        "spec_version": SPEC_VERSION,
        "pilot_objective": (
            "Validate scientifically whether BALIZA can reproducibly associate "
            "public environmental information with local observations and produce "
            "a traceable, useful DSS for a real reef-management setting."
        ),
        "pilot_objective_is_not": "Train a predictive model as the first goal.",
        "scientific_questions": ["Q1", "Q2", "Q3", "Q4", "Q5", "Q6", "Q7_POSTERIOR_ONLY"],
        "minimum_data_package": {
            "spatial_identity": REQUIRED,
            "time_semantics": REQUIRED,
            "local_temperature_if_exists": REQUIRED,
            "sensor_metadata_if_sensors_exist": STRONGLY_PREFERRED,
            "ecological_observations": TO_CONFIRM,
            "bleaching_protocol_if_bleaching_exists": REQUIRED,
            "depth": STRONGLY_PREFERRED,
            "methodology": REQUIRED,
            "historical_coverage": REQUIRED,
            "quality_flags": STRONGLY_PREFERRED,
        },
        "required_from_imr": [
            "site/station identity with coordinates and CRS",
            "observation datetime with timezone/UTC semantics",
            "local temperature series fields if temperature exists",
            "methodology / protocol for each local variable",
            "historical coverage (earliest/latest; gaps if known)",
            "data owner, access mechanism, and license",
            "confirmation of calibration vs independent validation policy",
        ],
        "strongly_preferred": [
            "sensor metadata (accuracy, calibration, drift)",
            "quality / QA-QC flags",
            "depth with reference",
            "reef/zone/transect relationships",
            "ecological observation inventories and protocols",
            "missing-data and reprocessing policy",
        ],
        "optional": [
            "fish / disease / recruitment / habitat complexity series",
            "commercial-use rights beyond research pilot",
            "seasonality notes",
        ],
        "to_confirm": [
            "exact access format (API/CSV/NetCDF/…)",
            "which ecological variables actually exist",
            "bleaching category definitions",
            "spatial and temporal holdout structure",
            "rights for validation / calibration / ML training",
            "BALIZA–IMR operational boundary",
        ],
        "data_governance": {
            "calibration_equals_independent_validation": False,
            "imr_automatically_ground_truth": False,
            "raw_must_be_preserved": True,
        },
        "candidate_targets": {
            "A_local_absolute_temperature": "CANDIDATE_NOT_ADOPTED",
            "B_local_thermal_anomaly": "CANDIDATE_NOT_ADOPTED",
            "C_local_regional_residual": "CANDIDATE_NOT_ADOPTED",
            "D_ecological_response_bleaching": "CANDIDATE_NOT_ADOPTED",
        },
        "ml_gate": {
            "status": "NOT_AUTHORIZED",
            "required": [
                "target defined",
                "ground truth available",
                "spatial resolution defined",
                "temporal resolution defined",
                "independent validation available",
                "leakage controls defined",
                "applicability domain defined",
                "uncertainty methodology defined",
                "data governance permits modeling",
                "scientific partner approval",
            ],
        },
        "success_criteria": ["S1_data", "S2_spatial", "S3_temporal", "S4_evidence", "S5_dss", "S6_human_usefulness"],
        "failure_blocking_conditions": [
            "No reliable coordinates",
            "No reliable timestamps",
            "Unknown observation methodology",
            "No usable local observations",
            "No independent validation",
            "Unclear data rights",
            "Severe spatial mismatch",
            "Severe temporal mismatch",
            "Unquantifiable uncertainty",
            "Data leakage risk",
        ],
        "implementation_status": {
            "imr_connector": "NOT_IMPLEMENTED",
            "imr_data_import": "NOT_IMPLEMENTED",
            "imr_endpoints": "NOT_IMPLEMENTED",
            "imr_tables": "NOT_IMPLEMENTED",
            "ml": "NOT_AUTHORIZED",
            "local_estimation": "NOT_AUTHORIZED",
            "downscaling": "NOT_AUTHORIZED",
        },
        "possible_next_states_after_imr_answers": ["A", "B", "C", "D", "E"],
        "assumed_next_state": None,
        "explicit_non_goals": [
            "No IMR connector in this phase",
            "No ML training",
            "No invented IMR formats or values",
            "No new scientific thresholds",
        ],
    }


def write_specification_artifact(root: Path) -> Path:
    import json

    path = root / "data" / "phase715" / "scientific-pilot-imr-specification.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(build_scientific_pilot_specification(), indent=2), encoding="utf-8")
    return path
