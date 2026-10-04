# 53 — Phase 7.9 Allen Coral Atlas real data pipeline

Allen enters BALIZA through the same public-data pattern as CRW. Map classes stay context. They are not field observations, not local measurements, and not BALIZA alerts.

## Access that was verified

Official WFS at `https://allencoralatlas.org/geoserver/ows`, version 2.0.0, unauthenticated. Layers used:

* `coral-atlas:benthic_data_verbose`
* `coral-atlas:geomorphic_data_verbose`

Stored request bbox: `-23.48,151.97,-23.47,151.98` with service CRS `urn:ogc:def:crs:EPSG::4326`. Property names: `class_name`, `area_sqkm`. Feature geometry was not requested and is null in the stored files. Feature `crs` is null. Product version and map epoch on the features are UNKNOWN.

Not on this WFS path: reef mask, satellite-derived depth, turbidity. Portal package download is not automated.

## Code

| Path | Role |
| --- | --- |
| `src/baliza/infrastructure/sources/allen/catalog.py` | Available and unavailable products |
| `src/baliza/infrastructure/sources/allen/adapter.py` | discover / validate / parse / normalize / provenance |
| `src/baliza/infrastructure/sources/allen/spot_intelligence.py` | DEMO and research-test Spot Intelligence |
| `GET /scientific/allen/discovery` | Catalog |
| `GET /scientific/spots/{spot_id}/allen` | Spot Allen view |

Raw checksum helpers are reused from `crw/raw_store.py`. Domain, RuleVersion, Decision, Action, and Outcome were not changed.

## Spots

`DEMO-CRW-ORIG24-HERITAGE-POINT` stays at -23.5, 152.0. That point is outside the stored Allen bbox. Allen spatial coverage for the DEMO Spot is **NOT_AVAILABLE**. Coordinates were not moved.

`ALLEN-RESEARCH-TEST-SPOT` at -23.475, 151.975 is only a pipeline test inside the stored bbox. It is not a validation of the DEMO Spot. Even there, no class is attached to the point, because geometry is null.

## Epistemic rules

Benthic and geomorphic extracts are `CONTEXT_ONLY`. Transformation type is provider `MODEL_ESTIMATED`, not a BALIZA estimate. Map epoch is not observation time. `ESTIMATED` is `NONE`. Uncertainty is `UNKNOWN`. Freshness separates retrieval time from scientific currency.

## Verdict

PHASE 7.9 ALLEN CORAL ATLAS REAL DATA PIPELINE — ESTIMATED NONE; DOWNSCALING / ML NOT AUTHORIZED.
