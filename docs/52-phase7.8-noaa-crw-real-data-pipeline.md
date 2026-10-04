# 52 — Phase 7.8 NOAA Coral Reef Watch real data pipeline

The first operational public-data path is NOAA Coral Reef Watch on CoastWatch ERDDAP. It does not estimate a local temperature, create a BALIZA alert, train a model, or downscale.

## Code

| Path | Role |
| --- | --- |
| `src/baliza/infrastructure/sources/crw/catalog.py` | Verified available products and documented unavailable ones |
| `src/baliza/infrastructure/sources/crw/raw_store.py` | SHA-256 preservation; refuses overwrite |
| `src/baliza/infrastructure/sources/crw/adapter.py` | `discover`, `retrieve`, `validate`, `parse`, `normalize`, `extract_metadata`, `emit_provenance` |
| `src/baliza/infrastructure/sources/crw/spot_intelligence.py` | Spot Intelligence for the demonstration heritage point |
| `GET /scientific/crw/discovery` | Catalog without download |
| `GET /scientific/spots/DEMO-CRW-ORIG24-HERITAGE-POINT/crw` | Stored CRW Spot Intelligence |

Domain, RuleVersion, Decision, Action, and Outcome were not changed. Demo thresholds in the API remain DEMO / NON-SCIENTIFIC and are not CRW science.

## Products actually used

Stored under `data/phase75/raw/` with checksums in `data/phase75/provenance.json`:

| Dataset | Variable | Version attr | Role |
| --- | --- | --- | --- |
| `noaacrwsstDaily` | `analysed_sst` | 3.1 / CoralTemp-v3.1 | temperature indicator |
| `noaacrwsstanomalyDaily` | `sea_surface_temperature_anomaly` | 3.1 | anomaly indicator |
| `noaacrwsstanomalybaselineDaily` | `sea_surface_temperature_anomaly` | 3.1 / 1991–2020 baseline | anomaly indicator |
| `noaacrwhotspotDaily` | `hotspot` | 3.1 | thermal stress indicator |
| `noaacrwdhwDaily` | `degree_heating_week` | 3.1 | accumulated stress indicator |
| `noaacrwbaa7dDaily` | `bleaching_alert_area` | 3.1 | external NOAA alert-area indicator |

Not available as files in this pipeline: 7-day SST trend, single-day Bleaching Alert Area, MMM climatology grid. Those remain `SOURCE_GAP`.

Coverage for the stored request is one cell at -23.475, 151.975 on `2026-09-26T12:00:00Z`. The heritage point -23.5, 152.0 sits equidistant from four centers. Production association stays `UNKNOWN` because CRS is unknown. A TEST CRS regression keeps four boundary hits without an average.

## Epistemic rules

Every CRW value is `EXTERNAL_INDICATOR` / `FACT` about the source product. It is not `MEASURED` at the Spot. Bleaching Alert Area is not a BALIZA alert. `ESTIMATED` is `NONE`. Uncertainty is `UNKNOWN`, not zero. Freshness status is `UNKNOWN`. No new HotSpot or DHW threshold was added.

## Verification

Full suite: 141 passed. New tests: `tests/test_phase78_crw_pipeline.py`. Artifact: `data/phase78/crw-spot-intelligence.json`.

## Verdict

PHASE 7.8 NOAA CORAL REEF WATCH REAL DATA PIPELINE — ESTIMATED NONE; DOWNSCALING / ML NOT AUTHORIZED.
