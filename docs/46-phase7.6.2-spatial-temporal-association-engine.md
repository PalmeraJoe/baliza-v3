# 46 — Phase 7.6.2 spatial and temporal association engine

Deterministic association only. The code is `src/baliza/experimental/phase762/engine.py`, version `phase762-1`. It is not on the critical path. It does not estimate a local value, average cells, convert degrees to metres, or emit `TEMPORALLY_NEAR`.

No file under `src/baliza/domain`, `alembic/`, or the Phase 0–6 tests was changed. The new test file is `tests/test_phase762_association.py`.

## What an association is

A relation between a spot and a source geometry. The source keeps its scientific layer. A NOAA cell stays `EXTERNAL_INDICATOR`. An Allen map class stays `CONTEXT_ONLY`. Neither becomes a measured value at the spot.

Spatial codes are `DIRECT`, `CONTAINS`, `INTERSECTS`, `NEAREST`, `AGGREGATED`, `ASSOCIATED`, and `UNKNOWN`. Point codes are `EXACT`, `WITHIN`, `NEAR`, and `UNKNOWN`. `NEAR` and `NEAREST` are reserved. This version does not assign them, because no distance cutoff is authorized. A supplied distance is kept. If the unit is degrees, `distance_m` stays `UNKNOWN`.

## CRS

Each record stores `source_crs`, `spot_crs`, and `calculation_crs`. No datum transform is implemented. The transformation block says method `NONE`. If either CRS is missing, or the two differ, coordinates are not compared. The real NOAA files and the heritage spot both have CRS `UNKNOWN`, so the production link stays `UNKNOWN`.

Tests that need a comparison pass an explicit shared token, `TEST-SAME-AXIS`. That token is not a NOAA CRS and not an EPSG code.

## Pixels

Closed footprints come from Phase 7.6. A point inside one cell, under a shared CRS, is `CONTAINS`. A point on the corner of four cells is `INTERSECTS` on each cell. The four values stay separate. There is no mean. `overlap_fraction` for a point stays `UNKNOWN`, because a point has no area.

On the real heritage point the same four centers are listed, and comparison is not performed. One HotSpot value, `-4.39` `degree_C`, is the stored cell `-23.475, 151.975`, with the SHA-256 of `noaacrwhotspotDaily_2026-09-26.csv`. The other three values are `UNKNOWN`, and their provenance is `PARTIAL`. The human text is produced by `render_noaa_case`.

## Polygons and transects

Axis-aligned boxes can be compared when the CRS matches. The overlap fraction is the overlap area divided by the spot-box area. It is not a geodesic. A class on that box is context.

The stored Allen benthic file has `geometry: null` and `crs: null`. Its request bbox does not contain `-23.5, 152.0`. No class is attached. Overlap and epoch are `UNKNOWN`. The file checksum is kept, and the overlay chain is `PARTIAL`.

No MERMAID row is stored as a spot association. The official read and the access gap are `docs/47-phase7.6.3-mermaid-real-data-verification.md`. How that gap sits in the evidence chain is `docs/48-phase7.6.4-evidence-quality-freshness-uncertainty.md`. The checksum audit of the stored files is `docs/49-phase7.6.5-evidence-chain-real-dataset-audit.md`. A transect record, if one is supplied, keeps transect geometry and does not reduce it to a representative value.

## Time, quality, conflict

`EXACT_TIME` is an equal timestamp. `SAME_DAY` is the same UTC date on a daily product. `AGGREGATED_PERIOD` is a monthly composite. Anything else with two timestamps stores the absolute difference and stays `UNKNOWN`, with policy `NOT_DEFINED`. Ingestion time is stored apart from observation time and is not used as the scientific time. The heritage spot has no reference time, so the real NOAA rows are temporally `UNKNOWN` even though the grid time is `2026-09-26T12:00:00Z`.

`source_quality`, `baliza_quality`, and `association_quality` stay separate. Association quality is `UNKNOWN`. Freshness status is `UNKNOWN`. Age is the timestamp difference only when both an observation time and a reference time exist. All five uncertainty fields are `UNKNOWN`, not zero.

The two SST-anomaly products on the retrieved cell, `0.78` `degree_C` and `0.4` `degree_Celsius`, are a conflict. Neither is selected.

## Verdict

PHASE 7.6.2 SPATIAL & TEMPORAL ASSOCIATION ENGINE — LOCAL ESTIMATION / DOWNSCALING / ML NOT AUTHORIZED.
