"""EXPERIMENTAL / PHASE 7.7. Target eligibility only.

No model, no estimate, and no new threshold. Eligibility is read from the
stored evidence, not from a preferred method.
"""

from __future__ import annotations

NOT_ELIGIBLE = "NOT_ELIGIBLE"
ESTIMATED_NONE = "NONE"

CANDIDATES = (
    {
        "target_id": "A-local-absolute-temperature",
        "name": "Local absolute water temperature",
        "definition": "A temperature measured at the spot, at a stated depth and time. Not a NOAA grid value.",
        "unit": "UNKNOWN",
        "spatial_unit": "OPEN",
        "temporal_unit": "OPEN",
        "ground_truth_requirement": "Independent in-situ temperature with location, depth, time, and uncertainty.",
        "predictor_requirements": "Named grids may be predictors only against that independent label.",
        "current_eligibility": NOT_ELIGIBLE,
        "limitations": "No in-situ temperature file is stored. The NOAA cell is not that label.",
    },
    {
        "target_id": "B-local-thermal-anomaly",
        "name": "Local thermal anomaly",
        "definition": "Local temperature minus a named local climatology. The climatology is not adopted.",
        "unit": "UNKNOWN",
        "spatial_unit": "OPEN",
        "temporal_unit": "OPEN",
        "ground_truth_requirement": "The same independent temperature, plus a frozen baseline that was not fit on the test period.",
        "predictor_requirements": "A local baseline. A NOAA anomaly product is a different variable.",
        "current_eligibility": NOT_ELIGIBLE,
        "limitations": "No local baseline is stored. Two NOAA anomaly products on one cell already differ.",
    },
    {
        "target_id": "C-local-regional-residual",
        "name": "Local minus regional thermal residual",
        "definition": "Independent local temperature minus a named regional grid value at a justified time.",
        "unit": "UNKNOWN",
        "spatial_unit": "OPEN",
        "temporal_unit": "OPEN",
        "ground_truth_requirement": "Independent local temperature. The grid value is the reference, not the label.",
        "predictor_requirements": "Both terms must exist and stay separate.",
        "current_eligibility": NOT_ELIGIBLE,
        "limitations": "The local term is not stored, so the residual cannot be formed.",
    },
    {
        "target_id": "D-ecological-response",
        "name": "Ecological response",
        "definition": "A field observation such as a MERMAID bleaching category or cover, where the policy exposes the row.",
        "unit": "As published by the survey. Recently dead is not a mortality percentage.",
        "spatial_unit": "OPEN",
        "temporal_unit": "Survey date, not an exact hour unless the row has one.",
        "ground_truth_requirement": "The survey row itself. It is not thermal ground truth.",
        "predictor_requirements": "Not defined. Thermal grids are not labels for this target.",
        "current_eligibility": NOT_ELIGIBLE,
        "limitations": "No MERMAID row is associated with the demonstration spot. Site access returned HTTP 401.",
    },
)

GROUND_TRUTH = (
    {
        "source": "In-situ temperature sensor",
        "variable": "local water temperature",
        "status": "NOT_AVAILABLE",
        "independence": "Required. A NOAA value cannot label a NOAA-based estimate.",
        "uncertainty": "UNKNOWN",
    },
    {
        "source": "NOAA Coral Reef Watch",
        "variable": "grid SST and related grids",
        "status": "NOT_APPLICABLE",
        "independence": "Not ground truth for an estimate that uses those grids.",
        "uncertainty": "UNKNOWN",
    },
    {
        "source": "MERMAID",
        "variable": "ecological survey",
        "status": "PARTIAL",
        "independence": "Not thermal ground truth. Spatial and temporal compatibility with the spot are UNKNOWN.",
        "uncertainty": "UNKNOWN",
    },
    {
        "source": "Resort history",
        "variable": "site records",
        "status": "NOT_AVAILABLE",
        "independence": "Not base-model training. Calibration rows cannot be reused as validation.",
        "uncertainty": "UNKNOWN",
    },
)

DO_NOT_ESTIMATE = (
    "NO_INDEPENDENT_GROUND_TRUTH",
    "GRID_IS_NOT_A_LOCAL_MEASUREMENT",
    "CRS_UNKNOWN",
    "TEMPORAL_ASSOCIATION_UNKNOWN",
    "OUTSIDE_OR_UNKNOWN_DOMAIN",
    "PROVENANCE_INSUFFICIENT",
    "LEAKAGE_NOT_PREVENTED",
    "MERMAID_IS_NOT_THERMAL_GROUND_TRUTH",
    "RESORT_ROWS_NOT_IN_BASE_TRAINING",
)


def eligibility_decision() -> dict:
    """No candidate is eligible. The estimate slot stays empty."""
    return {
        "decision": "NO",
        "statement": "TARGET NOT YET ELIGIBLE FOR MODELING",
        "eligible_target_ids": [],
        "candidates": list(CANDIDATES),
        "ground_truth": list(GROUND_TRUTH),
        "spatial_units": {
            "target_spatial_unit": "OPEN",
            "ground_truth_spatial_unit": "OPEN",
            "predictor_spatial_unit": "GRID",
            "validation_spatial_unit": "OPEN",
            "spatial_blocking_unit": "OPEN",
            "reason": "No independent label exists, so no validation unit is supported.",
        },
        "temporal_units": {
            "development_period": "OPEN",
            "validation_period": "OPEN",
            "sealed_final_test_period": "OPEN",
            "near_window": "NOT_DEFINED",
        },
        "applicability": {
            "current_domain": "UNKNOWN_DOMAIN",
            "in_domain_behavior": "Not available. No spot meets an in-domain rule because that rule is not defined.",
            "out_of_domain_behavior": "ESTIMATED = NONE",
            "unknown_domain_behavior": "ESTIMATED = NONE",
        },
        "estimated": ESTIMATED_NONE,
        "do_not_estimate": list(DO_NOT_ESTIMATE),
        "resort": {
            "base_model_training": False,
            "site_specific_calibration": "NOT_AVAILABLE",
            "site_specific_validation": "NOT_AVAILABLE",
        },
        "ml_implementation": "NOT_AUTHORIZED",
        "downscaling": "NOT_AUTHORIZED",
        "alerts": [],
        "thresholds": [],
    }
