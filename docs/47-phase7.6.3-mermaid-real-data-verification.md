# 47 — Phase 7.6.3 MERMAID real-data verification

The heritage spot `DEMO-CRW-ORIG24-HERITAGE-POINT` was not given a MERMAID association. The result is an **ACCESS GAP**, not a proof that MERMAID has no records anywhere, and not a `NO_COMPATIBLE_RECORD`.

Reads were unauthenticated `GET` requests to `https://api.datamermaid.org/v1/`. No credential was sent. Raw bodies were not stored, because they include project-admin and observer fields. SHA-256 values of those bodies are in `data/phase763/mermaid-inquiry.json`. A redacted Australia page is in `data/phase763/mermaid-australia-summary.json`.

## What answered

| Query | HTTP | What came back |
| --- | --- | --- |
| `summarysampleevents/?limit=1` | 200 | Count 16557. One page of one row. Not a spatial search. |
| `summarysampleevents/?country_name=Australia&limit=100` | 200 | Count 45, 45 rows, no next page. |
| `summarysampleevents/?site_name=Heron Island` | 200 | Count 0. |
| `summarysampleevents/?site_name=Heron` | 200 | Count 0. |
| `projects/?limit=1` | 200 | Count 0 for this client. |
| `sites/?limit=1` | 401 | No credentials. |
| `summarysites/?limit=1` | 404 | That path did not resolve on this call. |
| Australia plus `date_min` and `date_max` of 2026-09-26 | 502 | No body kept. |

The Australia page includes sample dates other than 2026-09-26. None of its coordinates equals -23.5, 152.0. The spot CRS and the MERMAID coordinate CRS are both unknown, so those numbers were not turned into a distance in metres or into `NEAR`. The country filter is not a proximity search. No row was promoted to a candidate.

`/sites/` remains unauthorized, so observation-level rows were not read. A bounding-box parameter is not in the summary filters that were used. The evidence record that keeps this access gap, without turning 16557 summaries into spot observations, is `docs/48-phase7.6.4-evidence-quality-freshness-uncertainty.md`. The audit that recomputes stored checksums is `docs/49-phase7.6.5-evidence-chain-real-dataset-audit.md`.

## What the code refuses

`src/baliza/experimental/phase763/mermaid.py` is not on the critical path. Synthetic tests are marked `TEST / SYNTHETIC / NON-SCIENTIFIC`. An exact synthetic row can be `MEASURED` at that point. A positive supplied distance is `NEAR` and is not a local measurement. `recently_dead` stays a category. No NOAA value is marked validated. No estimate, threshold, or alert is created.

## Verdict

PHASE 7.6.3 MERMAID REAL-DATA ASSOCIATION & GROUND-TRUTH VERIFICATION — LOCAL ESTIMATION / DOWNSCALING / ML NOT AUTHORIZED.
