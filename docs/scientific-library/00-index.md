# Scientific library — index

Phase 7 records a scientific and data foundation. It does not train models, adopt weights, or adopt thresholds as BALIZA rules.

Checked on 30 September 2026 against the pages cited in `source-registry.md`. A cell marked `UNKNOWN` was not verified. A cell marked `NOT_AVAILABLE` is absent from the current BALIZA system of record, or is outside the documented coverage of a source.

| File | Subject |
|------|---------|
| `01`–`20` | Topic notes. They do not add relationships beyond the cited sources. |
| `source-registry.md` | Sources actually consulted. |
| `sources/` | NOAA CRW, EMODnet, Allen Coral Atlas, MERMAID, literature notes. |
| `variable-registry.yaml` | Canonical variable records. |
| `variable-registry.md` | The same records in readable form, including the 15 Phase 7 questions. |
| `source-capability-matrix.md` | What each provider actually offers. |
| `data-source-variable-mapping.md` | Paper → mechanism → variable → product. Not a rule. |
| `data-availability-matrix.md` | Availability, gaps, and suitability flags. |
| `spatial-temporal-model.md` | Conceptual alignment only. No pipeline. |
| `dataset-specification.md` | Future station × time table. Not created in the database. |
| `xgboost-design.md` | Thermal downscaling specification. |
| `rbm-framework.md` | Risk-based management specification. No scores. |
| `playbook-framework.md` | Option catalog specification. No activation. |
| `random-forest-design.md` | Decision-support model specification. Not a decision engine. |

Phase-level copies and the audit live in `docs/25` through `docs/34`. The integration rules (Reef Data Fabric, no false homogeneity, resort historical channel, dataset versions, cold start) are in `docs/36-phase7-scientific-data-integration.md`. If a summary and this library disagree, this library and `variable-registry.yaml` win on variables. `docs/36` wins on how sources are aligned. Model implementation stays unauthorised.
