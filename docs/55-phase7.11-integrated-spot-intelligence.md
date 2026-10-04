# 55 — Phase 7.11 integrated Spot Intelligence & scientific evidence closure

Infrastructure integration only. No model is trained. No local estimate is
created. No scientific threshold is set. No BALIZA alert, Decision, or Action
is generated.

## Objective

Consolidate the already-integrated official sources —

- NOAA Coral Reef Watch (Phase 7.8)
- Allen Coral Atlas (Phase 7.9)
- MERMAID (Phase 7.10)

— into one auditable **Spot Intelligence** reading for
`DEMO-CRW-ORIG24-HERITAGE-POINT`.

The reading must answer what is known, from which source, with which epistemic
status, which spatial/temporal association, what is missing, and what must not
be inferred.

## Architecture

```text
CRW adapter ──┐
Allen adapter ┼─► build_integrated_spot_intelligence ─► machine + human views
MERMAID adapter┘         │
                         ├─ evidence / quality / freshness / uncertainty
                         ├─ data_gaps (availability taxonomy)
                         ├─ source_conflicts (unresolved)
                         ├─ dss_compatibility (attachable, no recommendation)
                         └─ alert_compatibility (referenceable, no alert)
```

Per-source builders are reused. There is no second raw→checksum→normalize path.

Contract version: `phase711-integrated-spot-intelligence-1`.

## Epistemic layers (preserved)

| Source | Layer |
|--------|--------|
| NOAA CRW (SST, anomaly, HotSpot, DHW, BAA) | `EXTERNAL_INDICATOR` |
| Allen benthic / geomorphic | `CONTEXT_ONLY` |
| MERMAID compatible field row (none on DEMO) | `MEASURED` ecological observation when compatible |

`MEASURED` ecological observation ≠ measured temperature.
Allen ≠ field observation.
CRW Bleaching Alert Area ≠ BALIZA alert.
Pixel / NEAR association ≠ local measurement.

## DEMO Spot scientific acceptance

```text
THERMAL:
CRW evidence available

HABITAT:
Allen context partially available

FIELD ECOLOGY:
MERMAID data exists
BUT NO COMPATIBLE MATCH

THERMAL GROUND TRUTH:
NOT AVAILABLE

LOCAL ESTIMATION:
NOT AUTHORIZED
```

Coordinates remain `-23.5, 152.0`. CRS remains `UNKNOWN`.

## Availability taxonomy (not collapsed)

| Code | DEMO use |
|------|----------|
| `DATA_EXISTS_WITH_UNKNOWN_COMPATIBILITY` | CRW products on retrieved cell; production CRS association UNKNOWN |
| `DATA_EXISTS_NO_COMPATIBLE_MATCH` | Allen extracts exist but Spot outside bbox; MERMAID Australia rows exist but no Spot match |
| `DATA_EXISTS_BUT_ACCESS_BLOCKED` | MERMAID sites / observation-level (401) |
| `NO_DATA` | Thermal ground truth at Spot |
| `DATA_AVAILABLE_AND_COMPATIBLE` | Not claimed for DEMO |

Absence of a compatible MERMAID row is **not** `NO_DATA`, **not** no bleaching,
and **not** healthy.

## Source conflicts

- CRW thermal indicators present + MERMAID no compatible observation →
  `NO_DIRECT_CONFLICT` (missing field evidence is not disagreement; no automatic
  CRW validation or causality).
- Allen class not attached + MERMAID no match → `NO_DIRECT_CONFLICT`.
- Intra-CRW anomaly product difference (if any) stays unresolved.

No source-of-truth is chosen automatically. No `thermal_risk_score`.

## Quality / freshness / uncertainty

Remain **source-specific** and **dimension-specific**. No overall quality or
uncertainty score. Retrieval freshness ≠ observation recency ≠ scientific
temporal currency.

## Evidence completeness

`EVIDENCE_COMPLETENESS = PARTIAL` for the DEMO Spot. Missing pieces are listed
per item (e.g. production spatial association, observation_time, Allen geometry /
map epoch, MERMAID compatible record / raw body).

## DSS and Alert compatibility

- `dss_compatibility.can_feed_dss_package = true`
- Does **not** create recommendation, decision, action, or outcome
- `alert_compatibility.can_be_referenced_by_alert = true`
- Does **not** create an alert or change RuleVersion / thresholds / severity

## API

```text
GET /scientific/spots/DEMO-CRW-ORIG24-HERITAGE-POINT/intelligence
```

Existing per-source endpoints remain:

```text
GET /scientific/spots/{spot_id}/crw
GET /scientific/spots/{spot_id}/allen
GET /scientific/spots/{spot_id}/mermaid
```

## Artifacts

- `data/phase711/integrated-spot-intelligence.json`
- `data/phase711/integrated-spot-intelligence.txt`

## Limitations (honest PARTIAL)

- CRW: one of four candidate cells retrieved; CRS UNKNOWN; temporal policy NOT_DEFINED
- Allen: DEMO coverage NOT_AVAILABLE; feature geometry null
- MERMAID: no Spot match; observation-level access blocked; raw bodies not stored
- Thermal ground truth: NOT_AVAILABLE
- Local estimation / downscaling / ML: NOT_AUTHORIZED

## Status

```text
PHASE 7.11 INTEGRATED SPOT INTELLIGENCE — PARTIAL CLOSURE
ESTIMATED = NONE
DOWNSCALING = NOT_AUTHORIZED
ML_IMPLEMENTATION = NOT_AUTHORIZED
LOCAL_ESTIMATION = NOT_AUTHORIZED
```

Do not start ML, XGBoost, IMR, resort calibration, or thermal ground-truth
pipelines from this phase alone. Wait for human review.
