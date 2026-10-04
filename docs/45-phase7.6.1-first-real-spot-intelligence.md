# 45 — Phase 7.6.1 first real spot intelligence record

One demonstration spot, built only from files already stored. No download, no filled gap, no local estimate, no alert.

The human text is `data/phase761/spot-intelligence.txt`. The structured object is `data/phase761/spot-intelligence.json`. Both are produced by `src/baliza/experimental/phase761/record.py`, which is not on the critical path.

## The spot

`DEMO-CRW-ORIG24-HERITAGE-POINT` is a **DEMONSTRATION / RESEARCH TEST SPOT**. It is not a resort.

The geometry is a point at latitude -23.5 and longitude 152.0. Those numbers are the heritage 50 km station coordinates NOAA published in `orig24_names.txt`. The CRS of that publication was not stated, so the spot CRS is **UNKNOWN**. Spatial precision is **UNKNOWN**. `valid_from` and `valid_to` are **UNKNOWN**.

## What the record shows

Measured observations: none. NOAA and Allen are not placed in that block.

The six NOAA products retrieved on 2026-09-26 belong to the cell whose center is -23.475, 151.975. They stay `EXTERNAL_INDICATOR` and `FACT` about that cell. Association to the spot is `UNKNOWN`, because the spot CRS and the grid CRS are both unknown. The HotSpot value -4.39 keeps BALIZA quality `QUESTIONABLE`. The source supplied no quality flag. Nothing is marked GOOD.

The published point lies 0.025° from four cell centers. That count is an inference about the published spacing, not a confirmed intersection. Only one cell was retrieved. The other three values are **UNKNOWN**. No center was chosen and no mean was taken.

The stored Allen WFS bbox is -23.48 to -23.47 latitude and 151.97 to 151.98 longitude. It does not contain this point, so no benthic or geomorphic class is attached. EMODnet has no retrieved value here. MERMAID was not associated with this point. The later read is `docs/47-phase7.6.3-mermaid-real-data-verification.md`.

The two SST-anomaly products on the retrieved cell are 0.78 `degree_C` and 0.4 `degree_Celsius`. Both are shown. Neither is selected.

Freshness timestamps are the grid time `2026-09-26T12:00:00Z` and the retrieval calendar date 2026-10-01. Age is not classified. Every uncertainty dimension is `UNKNOWN`. Derived indicators are none. Estimated values are none. Downscaling is not authorized. No alert is created and no playbook option is selected.

Each NOAA row points at its raw CSV and the SHA-256 already stored in `data/phase75/provenance.json`. The three unretrieved cells have a provenance gap.

The association engine in `docs/46-phase7.6.2-spatial-temporal-association-engine.md` reads this same spot. It still does not confirm an intersection, because the CRS is unknown. The evidence chain for these same files is `docs/48-phase7.6.4-evidence-quality-freshness-uncertainty.md`. The file-by-file checksum audit is `docs/49-phase7.6.5-evidence-chain-real-dataset-audit.md`.

## Verdict

PHASE 7.6.1 FIRST REAL SPOT INTELLIGENCE RECORD — LOCAL ESTIMATION / DOWNSCALING / ML NOT AUTHORIZED.
