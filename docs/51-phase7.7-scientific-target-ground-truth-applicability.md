# 51 — Phase 7.7 scientific target, ground truth, and applicability

No target is eligible for modeling. The decision is `NO`: **TARGET NOT YET ELIGIBLE FOR MODELING**. The record is `src/baliza/experimental/phase77/eligibility.py`. It does not train a model, score a risk, or emit an estimate.

The stored evidence is the Phase 7.5–7.6.6 set: six NOAA grid files for one cell on 2026-09-26, Allen class extracts whose geometry is null and whose bbox does not contain the demonstration point, no EMODnet file, a partial MERMAID summary read with no associated survey, and no resort file. The stored CoralTemp description calls that product a global 5 km gap-free sea-surface temperature. That description is a grid product. It is not a local measurement.

## Eligibility

| Target | DSS relevance | Independent ground truth | Spatial match | Temporal match | Measurement uncertainty | Leakage risk | Transferability | Eligible now |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Local absolute temperature | PARTIAL | NOT_AVAILABLE | NOT_AVAILABLE | NOT_AVAILABLE | NOT_AVAILABLE | OPEN | OPEN | NOT_AVAILABLE |
| Local anomaly | PARTIAL | NOT_AVAILABLE | NOT_AVAILABLE | NOT_AVAILABLE | NOT_AVAILABLE | OPEN | OPEN | NOT_AVAILABLE |
| Local–regional residual | PARTIAL | NOT_AVAILABLE | NOT_AVAILABLE | NOT_AVAILABLE | NOT_AVAILABLE | OPEN | OPEN | NOT_AVAILABLE |
| Ecological response | PARTIAL | PARTIAL | UNKNOWN | UNKNOWN | UNKNOWN | OPEN | OPEN | NOT_AVAILABLE |

DSS relevance is partial because a manager can ask the question. That does not create a label. NOAA is not ground truth for a NOAA-based estimate. An estimate is not ground truth for itself. MERMAID bleaching is not a temperature. Recently dead is not a mortality percentage. A local anomaly is not created, because no local climatology is stored and the two NOAA anomaly values on the retrieved cell are different products. The residual is not formed, because the local term is missing.

## Units that stay open

`TARGET_SPATIAL_UNIT`, `GROUND_TRUTH_SPATIAL_UNIT`, and `VALIDATION_SPATIAL_UNIT` are **OPEN**. The predictor unit for the stored NOAA files is a grid cell. Spot-level accuracy is not claimed. The spatial blocking unit is **OPEN**. A random row split is not adopted.

`DEVELOPMENT PERIOD`, `VALIDATION PERIOD`, and `SEALED FINAL TEST PERIOD` are **OPEN**. No nearness window is defined. The NOAA grid time is not an observation time, and the ingestion date is not that grid time.

The demonstration spot is `UNKNOWN_DOMAIN`. In-domain behavior is not available. Out of domain and unknown domain both require `ESTIMATED = NONE`.

Resort rows are not in the base training set. Site-specific calibration and site-specific validation are **NOT_AVAILABLE**. A calibration row cannot later be called independent validation.

## What would have to exist before implementation

An independent in-situ temperature series, or a MERMAID row that is actually associated and is used only as an ecological label, with location, time, depth where the method has it, uncertainty, and a sample large enough to hold out by place and by later time. A named spatial block. A sealed period that is not used to choose the target. A versioned uncertainty method. None of those are in the stored files.

## Verdict

PHASE 7.7 SCIENTIFIC TARGET, GROUND TRUTH & APPLICABILITY — ML IMPLEMENTATION NOT AUTHORIZED.
