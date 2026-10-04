# 25 — Phase 7 scientific foundation

Phase 7 records what BALIZA may later use for thermal downscaling, a risk reading, a playbook, and a decision-support model. It does not implement those systems. No schema, no weight, and no threshold was added. Domain and architecture from Phases 0–6 are unchanged.

Integration rules, the resort historical channel, dataset versioning, and cold start are consolidated in `docs/36-phase7-scientific-data-integration.md`. That note does not authorise implementation. Status remains **PHASE 7 SCIENTIFIC FOUNDATION RECORDED — MODEL IMPLEMENTATION NOT AUTHORIZED.**

The detailed library is `docs/scientific-library/`. This file is the decision-facing summary.

## What is scientifically supported here

Mass bleaching is tied, in the opened literature, to elevated sea temperature and the breakdown of the coral–symbiont relationship. NOAA CRW v3.1 defines SST, anomaly, HotSpot, DHW, and a categorical alert layer on a global 0.05° daily grid from 1985. Those thermal fields are external observations. The alert layer is external evidence, not a BALIZA Alert.

## What we can actually obtain

| Need | Source | Status |
|------|--------|--------|
| Surface heat, anomaly, HotSpot, DHW, climatology, 7-day trend | NOAA CRW v3.1 | Documented and globally gridded |
| Shallow reef mask, benthic class, geomorphic class | Allen Coral Atlas v2 | Documented map epoch, not a survey |
| Satellite depth and annual turbidity | Allen Coral Atlas | Documented, with optical limits |
| European bathymetry and broad-scale habitats | EMODnet | Documented inside listed seas and named Caribbean territories |
| In situ physics | EMODnet Physics | Parameters exist; reef coverage unknown |
| Field cover, bleaching categories, fish, habitat scores | MERMAID | Partial: only submitted samples, and only at the access level the project policy allows |
| Cover, species, bleaching percent, mortality, local depth | Resort / BALIZA schema | Not in the schema. Resort rows are for later site calibration and validation, not default base training |

## What a later phase may use

- Thermal downscaling features: NOAA thermal fields plus depth and habitat context, and MERMAID only as allowed field observations. The exact target stays OPEN. Resort history calibrates and validates a site; it does not train the base model by default. Output, if ever built, is an estimate, not an observation. See `docs/29-xgboost-design.md`.
- RBM hazard candidates: SST, HotSpot, DHW. Exposure candidate: reef mask. Vulnerability is not assigned. See `docs/30-rbm-framework.md`.
- Playbook: named concepts only, no entry rules. See `docs/31-playbook-framework.md`.
- Random Forest: not authorized to rank anything until an RBM state and an allowed option list exist. See `docs/32-random-forest-design.md`.

## What this phase refuses

NOAA alert classes as BALIZA alerts. Invented scores. Invented thresholds. Bleaching percent as a predictor of bleaching. EMODnet as a global thermal product. Allen classes as coral-cover percent.
