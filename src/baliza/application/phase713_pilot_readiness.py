"""Phase 7.13 Pilot Readiness Review — assessment only.

No ML, IMR connector, downscaling, or scientific threshold changes.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

PHASE = "7.13"
ASSESSMENT_VERSION = "phase713-pilot-readiness-1"

# Readiness vocabulary (Phase 7.13 §3).
READY = "READY"
READY_WITH_LIMITATIONS = "READY_WITH_LIMITATIONS"
REQUIRES_PILOT = "REQUIRES_PILOT"
NOT_READY = "NOT_READY"
NOT_AUTHORIZED = "NOT_AUTHORIZED"
NOT_APPLICABLE = "NOT_APPLICABLE"


def build_pilot_readiness_assessment() -> dict[str, Any]:
    """Canonical machine-readable Pilot Readiness Review."""
    return {
        "phase": PHASE,
        "assessment_version": ASSESSMENT_VERSION,
        "implemented_vs_tested_vs_scientifically_validated": {
            "note": (
                "IMPLEMENTED ≠ TESTED ≠ SCIENTIFICALLY_VALIDATED. "
                "Product DSS flow is implemented and tested. "
                "Local scientific validation and ML remain open / not authorized."
            ),
            "product_dss_flow": {
                "implemented": True,
                "tested": True,
                "scientifically_validated": False,
            },
            "demo_thresholds": {
                "implemented": True,
                "tested": True,
                "scientifically_validated": False,
                "label": "DEMO / NON-SCIENTIFIC",
            },
            "thermal_ground_truth": {
                "implemented": False,
                "tested": False,
                "scientifically_validated": False,
                "status": "NOT_AVAILABLE",
            },
            "ml_local_prediction": {
                "implemented": False,
                "tested": False,
                "scientifically_validated": False,
                "status": NOT_AUTHORIZED,
            },
            "imr_integration": {
                "implemented": False,
                "tested": False,
                "scientifically_validated": False,
                "status": "NOT_STARTED",
                "required_for_current_product_foundation": False,
                "required_for_scientific_pilot": True,
            },
        },
        "product_capabilities": {
            "Spot": READY_WITH_LIMITATIONS,
            "Spot_Intelligence": READY_WITH_LIMITATIONS,
            "Evidence_Chain": READY_WITH_LIMITATIONS,
            "Data_Quality": READY_WITH_LIMITATIONS,
            "Indicators": READY_WITH_LIMITATIONS,
            "Rules": READY_WITH_LIMITATIONS,
            "Alerts": READY,
            "DSS_Package": READY,
            "Snapshot": READY,
            "Protocol_Options": READY_WITH_LIMITATIONS,
            "Human_Decision": READY,
            "Action": READY,
            "Outcome": READY,
            "Audit": READY,
        },
        "science_capabilities": {
            "thermal_indicators": READY_WITH_LIMITATIONS,
            "spatial_association": REQUIRES_PILOT,
            "temporal_association": REQUIRES_PILOT,
            "ecological_observations": REQUIRES_PILOT,
            "ground_truth": NOT_READY,
            "uncertainty": REQUIRES_PILOT,
            "applicability_domain": REQUIRES_PILOT,
            "validation": REQUIRES_PILOT,
            "calibration": NOT_READY,
            "reproducibility": READY_WITH_LIMITATIONS,
        },
        "ml_capabilities": {
            "AI_analysis": NOT_AUTHORIZED,
            "model_training": NOT_AUTHORIZED,
            "model_validation": NOT_AUTHORIZED,
            "local_estimation": NOT_AUTHORIZED,
            "downscaling": NOT_AUTHORIZED,
            "predictive_risk": NOT_AUTHORIZED,
        },
        "product_readiness": {
            "verdict": READY_WITH_LIMITATIONS,
            "question": "Can BALIZA function as a DSS reproducibly?",
            "answer": "YES — WITH SCIENTIFIC DATA LIMITATIONS",
            "basis": "Phase 7.12 closed DATA → DSS → HUMAN DECISION on public sources.",
        },
        "scientific_dss_readiness": {
            "verdict": READY_WITH_LIMITATIONS,
            "question": "Can BALIZA present public scientific evidence honestly in a DSS?",
            "answer": "YES — WITH EXPLICIT GAPS AND UNCERTAINTY",
        },
        "scientific_model_readiness": {
            "verdict": NOT_READY,
            "question": "Is there enough evidence to train and validate a local predictive model?",
            "answer": "NO",
            "reasons": [
                "THERMAL_GROUND_TRUTH = NOT_AVAILABLE",
                "LOCAL_TARGET = OPEN",
                "SPATIAL_VALIDATION = OPEN",
                "TEMPORAL_VALIDATION = OPEN",
                "APPLICABILITY_DOMAIN = PARTIAL / UNKNOWN_DOMAIN",
                "UNCERTAINTY = PARTIAL",
            ],
        },
        "ml_readiness": {
            "verdict": NOT_AUTHORIZED,
            "authorization_gate": "NOT_PASSED",
        },
        "known_limitations": {
            "PROVENANCE": "PARTIAL",
            "QUALITY": "PARTIAL",
            "FRESHNESS": "PARTIAL",
            "UNCERTAINTY": "PARTIAL",
            "THERMAL_GROUND_TRUTH": "NOT_AVAILABLE",
            "CRW_PRODUCTION_SPATIAL_ASSOCIATION": "UNKNOWN",
            "ALLEN_DEMO_COVERAGE": "NOT_AVAILABLE",
            "MERMAID_COMPATIBLE_OBSERVATION": "NOT_AVAILABLE",
            "DEMO_THRESHOLDS": "NOT scientifically validated",
        },
        "imr": {
            "dependency_for_current_product": "NONE",
            "required_for_scientific_pilot": True,
            "connector_implemented": False,
            "conversation_framing": (
                "Validate the system scientifically with the partner; "
                "study later whether predictive capabilities can be justified. "
                "Do not ask IMR only to 'train BALIZA'."
            ),
        },
        "go_no_go": {
            "PRODUCT_PILOT": "GO",
            "SCIENTIFIC_VALIDATION": "CONDITIONAL_GO",
            "SCIENTIFIC_PILOT": "CONDITIONAL_GO",
            "ML_LOCAL_PREDICTION": "NO_GO",
            "ML_AUTHORIZATION": NOT_AUTHORIZED,
            "COMMERCIAL_PILOT": "NOT_READY",
            "overall": (
                "BALIZA PRODUCT/DSS: READY WITH LIMITATIONS. "
                "SCIENTIFIC PILOT: READY WITH CONDITIONS. "
                "LOCAL PREDICTION: NOT_READY. "
                "ML: NOT_AUTHORIZED. "
                "IMR: REQUIRED FOR SCIENTIFIC VALIDATION PHASE, "
                "NOT REQUIRED FOR CURRENT PRODUCT FOUNDATION."
            ),
        },
        "ml_authorization_gate": {
            "status": "NOT_PASSED",
            "required_closures": [
                "TARGET_DEFINITION",
                "GROUND_TRUTH",
                "SPATIAL_RESOLUTION",
                "TEMPORAL_RESOLUTION",
                "SPATIAL_VALIDATION",
                "TEMPORAL_VALIDATION",
                "LEAKAGE_CONTROL",
                "APPLICABILITY_DOMAIN",
                "UNCERTAINTY",
                "INDEPENDENT_TEST_SET",
                "SCIENTIFIC_PARTNER_APPROVAL",
            ],
            "authorized_now": False,
        },
        "calibration_vs_validation": {
            "calibration_equals_independent_validation": False,
            "same_row_may_serve_both": False,
            "rule": "CALIBRATION ≠ INDEPENDENT VALIDATION",
        },
        "explicit_non_goals": [
            "No ML implementation in this phase",
            "No IMR technical connector",
            "No new scientific thresholds",
            "No artificial closure of PARTIAL provenance/quality/freshness/uncertainty",
            "No claim that DEMO thresholds are scientifically validated",
            "No claim that MERMAID absence means no bleaching",
            "No claim that CRW is local measured temperature",
            "No autonomous decisions or actions",
            "No training on resort data as base model labels",
        ],
        "next_recommended_step": (
            "Scientific Pilot Readiness conversation with IMR / scientific partner: "
            "agree access, minimum data package, protocols, holdout principles, "
            "and pilot success criteria — before any IMR importer or ML work."
        ),
    }


def write_assessment_artifact(root: Path) -> Path:
    import json

    path = root / "data" / "phase713" / "pilot-readiness-assessment.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(build_pilot_readiness_assessment(), indent=2), encoding="utf-8")
    return path
