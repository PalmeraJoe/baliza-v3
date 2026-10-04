# 34 — Phase 7 audit

Checked against `docs/scientific-library/` and the pages cited in `source-registry.md`. No model was trained. No application code was changed.

## A. Scientific literature collected — PARTIAL

A starter set was opened: Skirving et al. 2020, Liu et al. 2003, Hoegh-Guldberg 1999, Hughes et al. 2017, and the Science DOI 10.1126/science.aan8048. Glynn 1993 is recorded only as cited by that Science paper. This is not a systematic review.

## B. Primary sources identified — PASS

Agency method pages and the v3.1 paper are distinguished from reviews and from secondary citations.

## C. NOAA documented — PASS

Products, units, grid, time range, HotSpot, DHW, alert classes, virtual stations, and access paths are in `sources/noaa-crw.md`. Alert classes are marked external.

## D. EMODnet documented — PARTIAL

Bathymetry footprint, EUSeaMap 2023, and Physics parameters were read. Chemistry and biology portals were not opened. Reef-level completeness is `UNKNOWN`.

## E. Allen Coral Atlas documented — PARTIAL

Benthic, geomorphic, extent, depth, and turbidity match the methods and FAQ pages. Licence and CRS were not confirmed.

## F. BALIZA local data documented — PASS

The absence of station, transect, cover, and bleaching fields is explicit. The future column list is in `dataset-specification.md` and is not a table.

## G. Variables defined — PASS

`variable-registry.yaml` defines the thermal, physical, biological, and outcome names that were in scope, including those that are undefined on purpose.

## H. Units defined — PARTIAL

Thermal units and FNU are defined. Currents, waves, aspect, disease, and several history metrics stay `UNKNOWN`.

## I. Spatial resolution documented — PARTIAL

0.05°, 5 m, 10 m, and 1/16 arc minute are documented where the provider stated them. CRS is `UNKNOWN`.

## J. Temporal resolution documented — PARTIAL

Daily CRW grids, Allen epoch, annual turbidity, and survey time are separated. Clocks are listed. No aligner was built.

## K. Source provenance — PASS

Each adopted product points at a page or a DOI in the source registry.

## L. Evidence strength — PASS

Strength labels are separate from any model importance. Several variables remain `UNKNOWN` or `LIMITED_EVIDENCE`.

## M. Mechanisms — PARTIAL

Heat and symbiont breakdown are cited. Depth, turbidity, hydrodynamics, and diversity have no adopted effect size.

## N. Data availability — PASS

The capability and availability matrices use only `AVAILABLE`, `PARTIAL`, `UNKNOWN`, and `NOT_AVAILABLE`.

## O. Spatial alignment — PARTIAL

Station, transect, pixel, and footprint rules are written. They are not implemented.

## P. Temporal alignment — PARTIAL

Clocks are named. No nearest-neighbour rule was authorised.

## Q. Leakage risks — PASS

Temporal, spatial, station, survey, target, and duplicate leakage are written in `dataset-specification.md`. Bleaching percent is forbidden as a bleaching feature.

## R. XGBoost specification — PASS

Design only. Target, baseline, holdout types, uncertainty, and fallback are specified. No training.

## S. RBM specification — PASS

Components are named. No weight, score, or threshold.

## T. Playbook specification — PASS

Option concepts have no entry conditions and do not execute.

## U. Random Forest specification — PASS

Constrained to future allowed options. Cannot decide or act. Not built.

## V. Uncertainty — PASS

Qualitative. No confidence fraction.

## W. Data gaps — PASS

Listed in `20-evidence-gaps.md` and `docs/33-phase7-open-scientific-questions.md`.

## X. No arbitrary weights — PASS

No formula of the kind prohibited in the phase brief appears.

## Y. No arbitrary thresholds — PASS

CRW's published HotSpot and DHW class bounds are quoted as CRW product semantics and are not copied into a BALIZA rule.

## Z. No autonomous decisions — PASS

Decision, action, and alert behaviour from Phases 0–6 is unchanged. ML remains off the critical path.

## MERMAID and site calibration

`docs/scientific-library/sources/mermaid.md` records official methods, bleaching categories, depth fields, API, and the three data-sharing policies. Availability is PARTIAL or UNKNOWN or NOT_AVAILABLE as stated there. Nothing was marked available without that page. Resort history is documented as site calibration and site validation, not as default training of a base model. No calibration method was defined. `src/`, `alembic/`, and `tests/` were not changed.

## Consolidation

`docs/36-phase7-scientific-data-integration.md` records the Reef Data Fabric, the ban on treating co-located sources as equivalent, the resort historical channel, dataset versions, epistemic classes of values, cold start, and the rule that storage permission is not training permission. It does not add software, weights, or thresholds. The chain from observation to outcome, human decision, snapshots, and the deterministic critical path are unchanged.

## Verdict

PHASE 7 SCIENTIFIC FOUNDATION RECORDED — MODEL IMPLEMENTATION NOT AUTHORIZED

The fifteen questions in the phase brief are answered for each registry variable, including where the answer is `UNKNOWN` or `NOT_AVAILABLE`. That is enough to choose inputs later. It is not permission to train XGBoost, Random Forest, or an RBM engine.

Phase 7.1 (`docs/37-phase7.1-ml-validation-protocol.md`) records how a future model would be validated. It does not train one. Its status is **PHASE 7.1 SCIENTIFIC ML VALIDATION PROTOCOL RECORDED — MODEL IMPLEMENTATION NOT AUTHORIZED.**

## PHASE 7.2 STATUS

`docs/38-phase7.2-scientific-target-and-spot-resolution.md` records the operational chain from observation to human decision, candidate targets, ground-truth classes, a Spot that is not an ML cluster, native source resolutions, clocks, abstention statuses, and the existing playbook gate. No code, weight, threshold, or model was added.

### CLOSED

- Observation, estimate, indicator, state, alert, playbook option, and human decision stay distinct.
- CRW thermal grids are external indicators at 0.05°. NOAA Bleaching Alert Area is not a BALIZA alert.
- Spatial-temporal coincidence is not scientific equivalence.
- An estimate is not its own ground truth. MERMAID bleaching is not a predictor of the same event.
- Resort history is site calibration and independent validation, not base training.
- Abstention does not become an alert by itself. A person decides.

### PARTIAL

- Spot is the operational place of interpretation. Identity versus Zone is open.
- Native resolutions are known. Defensible spot-scale resolution is not.
- "Available at time t" is defined. Per-feature clocks are not filled.
- Uncertainty statuses and the applicability flag are named. Methods and boundaries are not.
- Playbook names and the human gate are defined. Alert-to-option entry conditions are not.
- Resort calibration rows and validation rows must be disjoint. The cut inside a real resort is not.

### OPEN

- First downscaling target and its in-situ ground truth.
- Which depth a spot uses.
- Spatial blocking unit.
- Independent sample size and label variance.
- Numeric abstention bounds and the uncertainty method.

### NOT AUTHORIZED

XGBoost, Random Forest, RBM, weights, new scientific thresholds, training, and any use of resort history as the base training set. ML implementation is not authorised.

PHASE 7.2 SCIENTIFIC TARGET & SPOT RESOLUTION DEFINED — ML IMPLEMENTATION NOT AUTHORIZED.

## PHASE 7.3 STATUS

`docs/39-phase7.3-spot-intelligence-evidence-state-model.md` defines the logical spot reading: measured, external indicator, derived indicator, and an estimate slot that is empty. State still comes from versioned rules. An alert still cannot start an action. No code, threshold, weight, or local value was added.

### CLOSED

- Epistemic layers stay separate. A CRW grid value is not a spot measurement.
- `as_of_time` excludes anything published later.
- No data is not no risk. Uncertainty is not a risk score. Conflicting signals stay visible.
- Evidence chain and human decision boundary are unchanged. `ACKNOWLEDGED` is not a decision.
- Model readiness is `NOT_READY`.

### PARTIAL

- `SpotIntelligence` fields are specified and not implemented. Spot versus Zone is open.
- Spatial scales and relation types are named. Real joins stay `UNKNOWN`.
- Freshness and completeness labels exist. Their cutoffs do not.
- The playbook matrix is illustrative. Entry conditions do not.

### OPEN

- Target, local ground truth, state names, state and alert thresholds, uncertainty method, freshness cutoffs, completeness test, spatial aggregation, monitoring density.

### NOT AUTHORIZED

Local downscaling. ML implementation. Training. New scientific thresholds. Automatic action. Resort history as base training.

ML IMPLEMENTATION = NOT AUTHORIZED

LOCAL DOWNSCALING = NOT AUTHORIZED

PHASE 7.3 SPOT INTELLIGENCE & EVIDENCE STATE MODEL DEFINED — ML IMPLEMENTATION NOT AUTHORIZED.

## PHASE 7.4 STATUS

`docs/40-phase7.4-spot-scientific-baseline.md` records which products can sit beside a spot, which relations are allowed, and which deterministic audits have a formula. No local value, score, weight, threshold, or alert band was added.

### CLOSED

- External CRW grids stay grid cells. Bleaching Alert Area is not a BALIZA alert.
- `CONTEXT_ONLY` does not fire an alert. MERMAID bleaching is not a same-event predictor. Recently dead is not a later mortality percentage.
- Allen and EMODnet layers used here are context, not derived heat or cover.
- Quality is not upgraded in silence. Empty local data is not `NORMAL`.
- Five audit formulas are specified: missing inputs, direct-observation count, time since last direct observation, attached external set, and the uncollapsed signal list.

### PARTIAL

- The inventory is specified. Resort rows and local downscaling are `NOT_AVAILABLE`. EMODnet reef coverage is unknown.
- Permitted spatial relations are written. They are not applied, so a real link is `UNKNOWN`.
- Temporal windows of the products are known. Maximum age and freshness classes are open.
- `UNKNOWN` and `INSUFFICIENT_DATA` exist as rule outcomes. Heat state names do not.

### OPEN

- Freshness cutoffs, completeness cutoffs, conflict rule, state thresholds, alert thresholds, playbook entry conditions, CRS-backed joins.

### NOT_AVAILABLE

Local temperature in the schema, local DHW, local HotSpot, a BALIZA risk score, disease prevalence as a verified MERMAID product.

### NOT_AUTHORIZED

LOCAL DOWNSCALING = NOT AUTHORIZED

ML TRAINING = NOT AUTHORIZED

Resort history as base training. Automatic action. LLM-authored critical state.

PHASE 7.4 SPOT SCIENTIFIC BASELINE DEFINED — ML IMPLEMENTATION NOT AUTHORIZED.

## PHASE 7.5 STATUS

`docs/41-phase7.5-real-scientific-data-acquisition.md` records a live CoastWatch ERDDAP retrieval of one CRW grid cell on 2026-09-26, plus failed or restricted probes of Allen, MERMAID observations, and resort files. The experimental parser is not on the critical path. No model, threshold, or local estimate was added.

REAL DATA ACQUISITION: PARTIAL. Six CRW variables, one cell. Not a world archive.

SOURCE ADAPTERS: PARTIAL. CSV parser only. No Allen, EMODnet value, or MERMAID observation adapter.

PROVENANCE: PARTIAL. Endpoint, version, checksums, and license text are stored. The sub-second retrieval clock was not written.

RAW DATA PRESERVATION: PARTIAL. The six CSV files and metadata excerpts are unmodified inputs to the parser.

NORMALIZATION: PARTIAL. Celsius label identity only. The two anomaly products stay distinct. Negative HotSpot is not clipped.

SPATIAL CHARACTERIZATION: PARTIAL. The returned center is a grid. The heritage station point does not pick a unique cell.

TEMPORAL CHARACTERIZATION: PARTIAL. One instant. Product end dates differ. Freshness classes remain open.

QUALITY CHARACTERIZATION: PARTIAL. Source flags are absent. HotSpot is `QUESTIONABLE` against the clipped definition.

SPOT ASSOCIATION: OPEN. No spot exists. The relation to the published heritage point is `UNKNOWN`.

DATA GAPS: PARTIAL. The gaps are listed and not filled.

LOCAL DOWNSCALING: NOT AUTHORIZED

ML IMPLEMENTATION: NOT AUTHORIZED

PHASE 7.5 REAL SCIENTIFIC DATA ACQUISITION & SOURCE CHARACTERIZATION — ML IMPLEMENTATION NOT AUTHORIZED.

## PHASE 7.5.1 STATUS

`docs/42-phase7.5.1-allen-automated-access-test.md` records an unauthenticated WFS attribute retrieval for one small bbox. Benthic and geomorphic class names were stored with checksums. Bathymetry, turbidity, and the reef mask were not on that service. The logged-in website download was not automated. No credential was stored. No class was chosen as the spot value.

PHASE 7.5.1 ALLEN CORAL ATLAS AUTOMATED ACCESS TEST — SCIENTIFIC DATA INTEGRATION NOT YET AUTHORIZED BEYOND THE TEST.

## PHASE 7.5.2 STATUS

`docs/43-phase7.5.2-allen-provenance-metadata-reproducibility.md` records checksums, the WFS request, the service CRS, the schema, and a repeat call. Class and area matched. Bytes did not, because feature ids change. Resolution, map epoch, and feature geometry remain unknown. The raw extracts were not overwritten. No spot was associated.

PHASE 7.5.2 ALLEN PROVENANCE, METADATA & REPRODUCIBILITY CLOSURE — SPATIAL ASSOCIATION STILL OPEN.

## PHASE 7.6 STATUS

`docs/44-phase7.6-spatial-association-spot-mapping.md` defines how a source may be linked to a spot without becoming a local measurement. A point on a cell boundary stays in every adjacent cell. Missing or differing CRS values block the comparison. The published NOAA coordinate is not assigned a production link, because that grid has no CRS code. Allen classes are not field identifications. No estimate, interpolation, or alert was added.

PHASE 7.6 SPATIAL ASSOCIATION & SPOT MAPPING — LOCAL ESTIMATION / DOWNSCALING / ML NOT AUTHORIZED.

## PHASE 7.6.1 STATUS

`docs/45-phase7.6.1-first-real-spot-intelligence.md` records one demonstration point at the published heritage coordinates. The six NOAA values stay on the one retrieved cell. Three neighbouring cells have no value. Allen classes are not attached, because the stored bbox does not contain the point. Nothing was estimated.

PHASE 7.6.1 FIRST REAL SPOT INTELLIGENCE RECORD — LOCAL ESTIMATION / DOWNSCALING / ML NOT AUTHORIZED.

## PHASE 7.6.2 STATUS

`docs/46-phase7.6.2-spatial-temporal-association-engine.md` adds a versioned association engine. A shared CRS can list one cell as `CONTAINS` or four boundary cells as separate `INTERSECTS` records, with no mean. The real NOAA grid has no CRS, so those four centers stay `UNKNOWN` and three values stay unknown. Allen classes are not overlaid. No nearness rule, estimate, or alert was added.

PHASE 7.6.2 SPATIAL & TEMPORAL ASSOCIATION ENGINE — LOCAL ESTIMATION / DOWNSCALING / ML NOT AUTHORIZED.

## PHASE 7.6.3 STATUS

`docs/47-phase7.6.3-mermaid-real-data-verification.md` records an unauthenticated read of MERMAID summary sample events for the same demonstration point. The Australia page has 45 events and no identical coordinate. `/sites/` returned 401. No row was associated, and no local measurement was created. The gap is an access gap, not a claim that MERMAID has no data.

PHASE 7.6.3 MERMAID REAL-DATA ASSOCIATION & GROUND-TRUTH VERIFICATION — LOCAL ESTIMATION / DOWNSCALING / ML NOT AUTHORIZED.

## PHASE 7.6.4 STATUS

`docs/48-phase7.6.4-evidence-quality-freshness-uncertainty.md` records the evidence chain for the same demonstration spot. Retrieved NOAA files keep their stored checksums. The grid time is not treated as an observation time, and ingestion is not substituted for it. Quality, freshness, and uncertainty stay unknown where the source did not supply them. HotSpot remains questionable. MERMAID stays an access gap. No local value, freshness cutoff, or alert was added.

PHASE 7.6.4 EVIDENCE CHAIN / QUALITY / FRESHNESS / UNCERTAINTY — LOCAL ESTIMATION / DOWNSCALING / ML NOT AUTHORIZED.

## PHASE 7.6.5 STATUS

`docs/49-phase7.6.5-evidence-chain-real-dataset-audit.md` checks the files on disk. The six NOAA CSV checksums match the stored SHA-256 values. The ERDDAP metadata attribute gives product version 3.1. CRS stays unknown. Allen JSON checksums match, and the feature geometry is still null. EMODnet has no stored file. MERMAID stays a partial access with no spot match. Resort data are not available and are not base-model training. No checksum was replaced. No alert was added.

PHASE 7.6.5 EVIDENCE CHAIN CLOSURE & REAL DATASET AUDIT — NO SCIENTIFIC ESTIMATION / DOWNSCALING / ML AUTHORIZED.

## PHASE 7.6.6 STATUS

`docs/50-phase7.6.6-evidence-chain-operational-closure.md` recomputes checksums for the files already stored. Those raw files are identified and hashed. Acquisition checksums still match. Allen XML files had no stored checksum, so the new hash is marked as computed here and the old record was not rewritten. CRS, observation time, Allen version, Allen geometry, MERMAID site access, freshness, and uncertainty stay unresolved for the reasons in that note. EMODnet and resort data stay unavailable. No download, estimate, or alert was added.

PHASE 7.6.6 EVIDENCE CHAIN OPERATIONAL CLOSURE — SCIENTIFIC ESTIMATION / DOWNSCALING / ML NOT AUTHORIZED.

## PHASE 7.7 STATUS

`docs/51-phase7.7-scientific-target-ground-truth-applicability.md` reviews the stored NOAA, Allen, EMODnet, MERMAID, and resort evidence against four candidate targets. None is eligible. No local estimate is produced. Resort history stays out of base training. No model was implemented.

PHASE 7.7 SCIENTIFIC TARGET, GROUND TRUTH & APPLICABILITY — ML IMPLEMENTATION NOT AUTHORIZED.

## PHASE 7.8 STATUS

`docs/52-phase7.8-noaa-crw-real-data-pipeline.md` adds the CRW infrastructure adapter over the stored CoastWatch ERDDAP files. Six products are normalized as external indicators. Raw checksums are verified and never overwritten. The demonstration Spot lists four candidate cells and one retrieved value. CRW Bleaching Alert Area stays external. No local estimate, downscaling, ML, or new BALIZA alert threshold was added.

PHASE 7.8 NOAA CORAL REEF WATCH REAL DATA PIPELINE — ESTIMATED NONE; DOWNSCALING / ML NOT AUTHORIZED.

## PHASE 7.9 STATUS

`docs/53-phase7.9-allen-coral-atlas-real-data-pipeline.md` adds the Allen WFS infrastructure adapter over the stored benthic and geomorphic attribute extracts. The DEMO Spot keeps its coordinates and has no Allen coverage. A separate research-test Spot only proves the extract parses. Map classes stay CONTEXT_ONLY. Reef mask, depth, and turbidity remain unavailable on this WFS. No estimate, alert, or ML was added.

PHASE 7.9 ALLEN CORAL ATLAS REAL DATA PIPELINE — ESTIMATED NONE; DOWNSCALING / ML NOT AUTHORIZED.

## PHASE 7.10 STATUS

`docs/54-phase7.10-mermaid-real-data-pipeline.md` adds the MERMAID infrastructure adapter over the stored unauthenticated summary inquiry and Australia page. The DEMO Spot keeps its coordinates and has no compatible MERMAID match. Spatial and temporal compatibility stay UNKNOWN. Summary protocol names are not observation-level values on the Spot. Bleaching is not thermal ground truth. No estimate, alert, or ML was added.

PHASE 7.10 MERMAID REAL DATA PIPELINE — ESTIMATED NONE; DOWNSCALING / ML NOT AUTHORIZED.

## PHASE 7.11 STATUS

`docs/55-phase7.11-integrated-spot-intelligence.md` consolidates CRW, Allen, and MERMAID into one machine-readable and human-readable Spot Intelligence for the DEMO heritage point. Epistemic layers stay separate. MERMAID absence is data-exists-but-no-compatible-match, not no bleaching. No risk score, alert, decision, estimate, or ML was added.

PHASE 7.11 INTEGRATED SPOT INTELLIGENCE & SCIENTIFIC EVIDENCE CLOSURE — ESTIMATED NONE; DOWNSCALING / ML NOT AUTHORIZED.

## PHASE 7.12 STATUS

`docs/56-phase7.12-end-to-end-scientific-dss-integration.md` runs the DEMO Spot from integrated Spot Intelligence through evidence, DEMO/NON-SCIENTIFIC indicator and rule, alert, DSS package, frozen snapshot, human decision, action, and outcome. CRW stays EXTERNAL_INDICATOR. MERMAID no-match stays a data gap. No ML, downscaling, IMR, or autonomous action was added.

PHASE 7.12 END-TO-END SCIENTIFIC DSS INTEGRATION — ESTIMATED NONE; DOWNSCALING / ML / IMR NOT AUTHORIZED.

## PHASE 7.13 STATUS

`docs/57-phase7.13-pilot-readiness-review.md` records the Pilot Readiness Review. Product/DSS is ready with scientific data limitations. Scientific pilot is a conditional go. Local prediction and ML remain not authorized. IMR is not a dependency of the current product foundation and is required for the scientific validation phase. No IMR connector, ML, or new scientific thresholds were added. Provenance, quality, freshness, and uncertainty stay PARTIAL.

PHASE 7.13 PILOT READINESS REVIEW — PRODUCT GO (LIMITATIONS); SCIENTIFIC PILOT CONDITIONAL GO; ML NOT_AUTHORIZED.
