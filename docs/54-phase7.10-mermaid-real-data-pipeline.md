# 54 — Phase 7.10 MERMAID real data pipeline

MERMAID enters BALIZA as a field-ecology source. It is not a temperature label, not automatic CRW validation, and not a BALIZA alert.

## Access that was verified

Official root: `https://api.datamermaid.org/v1/`.

| Endpoint | Status |
| --- | --- |
| `summarysampleevents/` | AVAILABLE unauthenticated. Global count 16557. Australia page 45/45 complete. |
| `sites/` | ACCESS_GAP HTTP 401 |
| `projects/` | PARTIAL HTTP 200 with count 0 for this client |
| `summarysites/` | ACCESS_GAP HTTP 404 on the verified call |
| Observation-level bleaching / benthic / fish / habitat complexity | NOT_AVAILABLE without project authorization |

Raw response bodies were not stored, because they include person fields. SHA-256 hashes and a redacted Australia page remain in `data/phase763/`.

## Code

| Path | Role |
| --- | --- |
| `src/baliza/infrastructure/sources/mermaid/catalog.py` | Available and blocked datasets |
| `src/baliza/infrastructure/sources/mermaid/adapter.py` | discover / load / validate / normalize |
| `src/baliza/infrastructure/sources/mermaid/spot_intelligence.py` | DEMO Spot MERMAID view |
| `GET /scientific/mermaid/discovery` | Catalog |
| `GET /scientific/spots/DEMO-CRW-ORIG24-HERITAGE-POINT/mermaid` | Spot view |

Association helpers stay in `experimental/phase763`. Domain, RuleVersion, Decision, Action, and Outcome were not changed.

## DEMO Spot

`DEMO-CRW-ORIG24-HERITAGE-POINT` stays at -23.5, 152.0. No stored Australia coordinate equals that point. Heron Island name queries returned count 0. Spatial and temporal compatibility stay **UNKNOWN**. Usable observations of this Spot: **0**. That is `DATA EXISTS BUT NO COMPATIBLE MATCH`, not “no bleaching” and not “healthy”.

Australia summaries include protocol names for bleaching and benthic cover on some rows, and fish belt on others. Those names are not observation-level values attached to the DEMO Spot. `recently_dead` remains a category, not mortality percent. Bleaching is not temperature and not thermal ground truth.

## Verdict

PHASE 7.10 MERMAID REAL DATA PIPELINE — ESTIMATED NONE; DOWNSCALING / ML NOT AUTHORIZED.
