# 49 — Phase 7.6.5 evidence chain and real dataset audit

The manifest is `data/phase765/audit-manifest.json`. It reads files already stored and recomputes SHA-256. A stored checksum that does not match is left in place and marked `PROVENANCE_INTEGRITY_ISSUE`. This run had no mismatch. The audit code is `src/baliza/experimental/phase765/audit.py`. Existing parsers were not changed.

## Inventory

| Dataset | Raw | Checksum | Version | CRS | Association | Chain |
| --- | --- | --- | --- | --- | --- | --- |
| noaacrwsstDaily | File present | MATCH | 3.1 from the ERDDAP attribute | UNKNOWN | UNKNOWN. Four centers, one value, no average | PARTIAL |
| noaacrwsstanomalyDaily | File present | MATCH | 3.1 | UNKNOWN | Same cell | PARTIAL |
| noaacrwsstanomalybaselineDaily | File present | MATCH | 3.1 | UNKNOWN | Same cell | PARTIAL |
| noaacrwhotspotDaily | File present | MATCH | 3.1 | UNKNOWN | Same cell. BALIZA quality QUESTIONABLE | PARTIAL |
| noaacrwdhwDaily | File present | MATCH | 3.1 | UNKNOWN | Same cell | PARTIAL |
| noaacrwbaa7dDaily | File present | MATCH | 3.1 | UNKNOWN | Same cell | PARTIAL |
| allen benthic JSON | File present | MATCH | UNKNOWN | UNKNOWN. Feature crs is null | Not associated. Not a field observation | PARTIAL |
| allen geomorphic JSON | File present | MATCH | UNKNOWN | UNKNOWN | Not associated | PARTIAL |
| allen map catalogue | File present | MATCH | UNKNOWN | UNKNOWN | Not a spot class | PARTIAL |
| allen WFS XML (3 files) | Files present | No stored checksum to compare | UNKNOWN | Not copied onto features | Not a spot association | PARTIAL |
| EMODnet bathymetry | No file | NOT_AVAILABLE | UNKNOWN | UNKNOWN | Not retrieved | BROKEN |
| MERMAID summary events | Body not stored | Hash stored, body cannot be recomputed | UNKNOWN | UNKNOWN | NO_MATCH_WITH_DEMO_SPOT | PARTIAL |
| Resort | No file | NOT_AVAILABLE | NOT_AVAILABLE | NOT_AVAILABLE | Not base-model training | NOT_AVAILABLE |

NOAA grid time stays `2026-09-26T12:00:00Z`. Ingestion stays the calendar date `2026-10-01`. The CSV unit is the original unit. No unit conversion was applied. The NOAA product is a provider transformation. BALIZA parsed the file and did not interpolate or downscale.

EMODnet GetCapabilities was documented as HTTP 200. The body is not in the repository. Documented is not retrieved.

MERMAID official access stays partial. The summary count is 16557. Usable observations of this spot stay 0. Australia returned 45 events and no identical coordinate. `/sites/` returned 401. That is not a statement that MERMAID has no data.

Freshness status is unknown. Uncertainty is unknown, not zero. No alert and no risk state were produced.

## Source summary

| Source | Retrieved | Raw | Provenance | Association | Status |
| --- | --- | --- | --- | --- | --- |
| NOAA | Six cells files | Present and checksum-matched | Partial. Calendar retrieval. CRS unknown | Partial. Four centers, one value | PARTIAL |
| EMODnet | No | Not available | The call was documented only | Not available | NOT_AVAILABLE |
| Allen | Attribute extracts | JSON checksum-matched. XML not previously hashed | Partial. No feature geometry | Not associated | PARTIAL |
| MERMAID | Summary counts and a redacted Australia page | Response bodies not stored | Partial | No match with this spot | PARTIAL |
| Resort | No | Not available | Not available | Not in base training | NOT_AVAILABLE |

## Verdict

PHASE 7.6.5 EVIDENCE CHAIN CLOSURE & REAL DATASET AUDIT — NO SCIENTIFIC ESTIMATION / DOWNSCALING / ML AUTHORIZED.

The operational pass that closes raw identity and checksums, and records why the other partials remain, is `docs/50-phase7.6.6-evidence-chain-operational-closure.md`.
