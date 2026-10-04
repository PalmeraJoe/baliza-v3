# Variable registry

Canonical records: `variable-registry.yaml`.

Each record answers the Phase 7 questions as follows.

| Question | Field |
|----------|--------|
| What is it? | `definition` |
| Mechanism | `mechanism` |
| Evidence | `evidence_strength`, `evidence_sources` |
| Who provides it? | `available_in_*` |
| Which product? | `canonical_name` plus the source note |
| Spatial resolution | `spatial_resolution` |
| Temporal resolution and coverage | `temporal_resolution` |
| Local data | `available_in_BALIZA` |
| Role | `scientific_role` |
| XGBoost | `candidate_XGBOOST` |
| RBM | `candidate_RBM` |
| Random Forest | `candidate_RANDOM_FOREST` |
| Uncertainty | `uncertainty` |
| Leakage | `leakage` |
| What we cannot infer | `limitations` |

`candidate_*` does not approve training. `not_authorized` means the Random Forest and the playbook are not allowed to consume the variable until a later phase adopts a versioned method. `UNKNOWN` means this registry does not know.

## What is justified and obtainable

| Variable | Role | Obtainable now | From |
|----------|------|----------------|------|
| SST, SST anomaly, HotSpot, DHW, MMM, 7-day trend | Hazard or context | Yes, as external grids | NOAA CRW v3.1 |
| Bleaching Alert Area | Context only | Yes, as external evidence | NOAA CRW. Not a BALIZA Alert |
| Reef extent, benthic class, geomorphic class | Exposure or context | Yes, as map epoch | Allen Coral Atlas v2 |
| Turbidity, satellite depth | Context | Yes, with the limits in the Allen note | Allen Coral Atlas |
| European bathymetry, EUSeaMap habitats | Context | Only inside the documented footprints | EMODnet |
| In situ temperature, currents, waves | Context | Only where a series exists. Reef completeness unknown | EMODnet Physics |
| Local depth, cover, richness, bleaching %, mortality, disease | Observation, target, or outcome | Not typed in BALIZA. MERMAID has partial field methods; see `sources/mermaid.md` | MERMAID where a project and policy allow; otherwise future local surveys |
| Downscaled temperature | Hazard estimate | No | Future model |

## What cannot be inferred

- A CRW class is not a survey of bleached tissue.
- An Allen benthic class is not coral-cover percent.
- EMODnet does not supply global reef DHW.
- No variable in this registry has a BALIZA weight or a BALIZA threshold.
- `bleaching_percentage` is a target. It is not a predictor of bleaching.
- A MERMAID bleaching percent is a field observation. It is not predicted by DHW in this registry.
- Resort history calibrates and validates a site. It is not the default training set of a base model.
