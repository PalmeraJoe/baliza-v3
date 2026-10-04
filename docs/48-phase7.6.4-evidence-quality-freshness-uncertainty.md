# 48 — Phase 7.6.4 evidence, quality, freshness, and uncertainty

The chain says where a value came from and what happened to it. It does not certify that the value is scientifically correct.

The builder is `src/baliza/experimental/phase764/evidence.py`. It is not on the critical path. The real reading is `data/phase764/evidence-chain.json` and `data/phase764/evidence-chain.txt`. Checksums are the ones already stored. Nothing was downloaded again.

## Real sources

NOAA CoralTemp SST on the retrieved cell is 22.72 `degree_C`. The grid time is `2026-09-26T12:00:00Z`. That time is kept as the source time. It is not labeled an observation time, and the ingestion date `2026-10-01` is not used in its place. The file checksum is the stored SHA-256. The spot CRS and the grid CRS are unknown, so the spatial association stays `UNKNOWN`. Four cell centers are listed. Three have no value. No mean was taken. Source quality is `UNKNOWN` because the row has no quality flag. HotSpot `-4.39` keeps BALIZA quality `QUESTIONABLE`. Association quality is `UNKNOWN`. Every uncertainty dimension is `UNKNOWN` or, for a BALIZA model, `NOT_APPLICABLE`. None of them is zero.

The two SST-anomaly products on that cell still disagree. They stay an unresolved conflict. A NOAA heating-week value and a MERMAID bleaching note are different variables, so they are complementary, not a conflict. No bleaching value was associated.

Allen's stored benthic extract keeps its checksum. Feature geometry is null, so no class is attached. The gap is spatial. This phase does not add a model estimate.

EMODnet still has no depth for this cell. That is a source gap.

MERMAID official access stays partial. The summary sample-event count is 16557. That number is not a count of usable observations of this spot. Usable spot observations remain 0. Spatial and temporal compatibility stay `UNKNOWN`. `/sites/` returned 401. This is an access gap, not a global absence.

## Rules that stay closed

Freshness status is `UNKNOWN`. No 24-hour, 72-hour, or other cutoff was added. Interpolation, downscaling, and a new model estimate are not authorized steps. A broken chain is marked unusable for a later indicator. Unknown uncertainty is not stored as zero. The file-by-file checksum audit is `docs/49-phase7.6.5-evidence-chain-real-dataset-audit.md`.

## Verdict

PHASE 7.6.4 EVIDENCE CHAIN / QUALITY / FRESHNESS / UNCERTAINTY — LOCAL ESTIMATION / DOWNSCALING / ML NOT AUTHORIZED.
