# 36 — Phase 7 scientific data integration

Consolidation of the Phase 7 foundation. Documentation only. It does not authorise Phase 7.1, a schema, a pipeline, a weight, a threshold, or a model.

Status remains:

**PHASE 7 SCIENTIFIC FOUNDATION RECORDED — MODEL IMPLEMENTATION NOT AUTHORIZED.**

## Reef Data Fabric

NOAA CRW, EMODnet, Allen Coral Atlas, and BALIZA local data are not one original homogeneous database. Each source keeps its own structure, provenance, spatial resolution, temporal resolution, units, observation method, uncertainty, version, licence or terms of use, and limitations.

A later BALIZA layer may align them. That layer is the Reef Data Fabric. It does not exist as software.

```text
NOAA CRW          thermal products
EMODnet            physical and oceanographic context
Allen Coral Atlas reef, habitat, geomorphology
MERMAID            field ecological observations
BALIZA local / resort history
        site calibration and validation, not default base training
        │
        ▼
SPATIAL-TEMPORAL ALIGNMENT
        │
        ├── location
        ├── date/time
        ├── spatial resolution
        ├── temporal resolution
        ├── depth
        ├── CRS
        └── provenance
        │
        ▼
BALIZA REEF DATA FABRIC
```

The join key is not only coordinates plus a date. It is:

`WHERE + WHEN + WHAT + SOURCE + RESOLUTION + METHOD + QUALITY + PROVENANCE`

`WHAT` is the variable identity in `variable-registry.yaml`. Two rows that share a reef and a day and differ in `WHAT` or `SOURCE` stay different records.

## No false homogeneity

Coincidence in space and time does not make observations equivalent.

```text
NOAA SST
≠ BALIZA in-situ temperature
≠ a future downscaled temperature estimate
```

```text
satellite habitat class ≠ field survey
regional SST ≠ local transect temperature
```

A regional cell must not be presented as a local observation. If a later pipeline resamples, interpolates, aggregates, matches in space, or downscales, that step is stored as provenance. The original record remains.

## Spatial requirements for a future fabric

CRS, latitude and longitude, geometry, spatial resolution, grid or pixel identity, reef, zone, station, transect, and depth. Entity, Zone, and Station stay distinct, as in the glossary. A NOAA pixel and a CRW Regional Virtual Station are not BALIZA stations. CRS codes that were not read from file metadata stay `UNKNOWN`.

## Temporal requirements

Keep separate: observation time, the start and end of the window the value represents, temporal resolution, acquisition date, processing date, publication date, and ingestion date. Ingestion time never replaces the scientific observation time.

## Base science versus site calibration

A future base scientific set may use NOAA, EMODnet, Allen Coral Atlas, and MERMAID, each only where the value exists, the policy allows it, and the design still says so. Source available does not mean feature selected.

Resort historical data are not in that base set by default.

```text
RESORT HISTORICAL DATA
        → SITE-SPECIFIC CALIBRATION
        → SITE-SPECIFIC VALIDATION
```

They do not go to global or base-model training unless a later scientific decision says so explicitly. Calibration is not defined as retraining. Which parameters could be calibrated is open. No correction factor is set.

```text
GENERAL SCIENTIFIC MODEL
        → SITE-SPECIFIC DATA
        → CALIBRATION
        → SITE-CALIBRATED MODEL
        → INDEPENDENT SITE VALIDATION
```

Data used to calibrate a model are not afterwards called an independent validation of that same model. A later comparison may look at error, bias, uncertainty, and temporal and spatial stability before and after calibration. Those metrics are not implemented.

## Resort historical data channel

Local contracting data remain a first-class future source for that site role. They are not a substitute for NOAA, EMODnet, Allen, or MERMAID, and they are not automatically true.

```text
LOCAL / CONTRACTING DATA
        └── Resort / MPA / operator
             ├── historical monitoring
             ├── temperature
             ├── transects
             ├── coral cover
             ├── bleaching observations
             ├── mortality
             ├── disease
             ├── biodiversity
             ├── recovery
             ├── interventions
             └── historical outcomes
```

A later path, not built here:

```text
INGESTION → VALIDATION → NORMALIZATION → QUALITY
        → SPATIAL/TEMPORAL ALIGNMENT → PROVENANCE
```

The resort does not have to deliver BALIZA-shaped tables. Accepted future inputs include CSV, Excel, JSON, GeoJSON, shapefiles, GPX, databases, sensors, reports, manual logs, photographs, and transects. Normalisation belongs to that future ingestion path.

Datasets used for science or for a later model must be versioned (`HistoricalDataset` v1, v2, v3). A version already used for base training, site calibration, validation, testing, model evaluation, or a scientific analysis is not edited in place. The analysis must be able to name the version it used. Calibration rows and independent validation rows are different versions or explicitly disjoint subsets.

## Observed, derived, and modelled

```text
OBSERVED
DERIVED
INTERPOLATED
AGGREGATED
MODEL_ESTIMATED
DOWNSCALED
```

A local observation is not a model estimate. A future model must not write an estimate back as an observation. Downscaled temperature, if it is ever produced, stays `DOWNSCALED` or `MODEL_ESTIMATED` and carries uncertainty and model provenance.

## Later uses, still not authorised

**Temperature estimation.** NOAA, EMODnet, Allen, and MERMAID may later form a base set whose output is an estimated local temperature plus uncertainty and provenance. The exact target stays **OPEN**. Resort history is not in that base set by default. XGBoost is not implemented.

**Risk reading.** Local history may later inform hazard, exposure, vulnerability, consequence, uncertainty, historical response, and recovery. No RBM engine, weight, score, probability, or new threshold is created.

**Decision support.** A later learning set may use recorded state, human decision, action, and outcome. Historical decisions are not assumed to be optimal. Resort history is not used to train a Random Forest in this phase. Random Forest is not trained. It still may not propose an option outside a future playbook, and it may not decide or act.

## Leakage

Already listed kinds remain: temporal, spatial, station, survey, target, and duplicates. Repeated use of the same station or transect, and using calibration rows as if they were an independent test, are the same family of leakage. This consolidation adds the same rule in operational form, plus post-event and future-information leakage:

A variable used to estimate a condition at time `t` must not include information that was available only after `t`.

Post-event surveys, annual maps that include months after `t`, and revised datasets that silently include later corrections are future-information leakage unless the version and the cutoff are explicit.

## Cold start

A resort with no local history still has the external sources, including MERMAID only where a site and a data policy actually provide a row, and the existing DSS path. Missing history is a gap. It is not zero risk, not "no bleaching", and not a reason to invent precision. Site-specific calibration starts only after resort data have been validated, and that calibration is not the base model.

```text
NO RESORT HISTORY → EXTERNAL SOURCES → BASE SCIENTIFIC CONTEXT → DSS
RESORT DATA → CALIBRATION → SITE-SPECIFIC MODEL → INDEPENDENT VALIDATION
```

## Governance

Future resort contributions need a provider, an owner, a licence, usage rights, a training permission, a retention policy, and a sharing policy. Permission to store is not permission to train. Training permission is a separate flag and defaults to absent.

## Compatibility with Phases 0–6

This note does not change the chain:

```text
Observation → IndicatorValue → RuleEvaluation → Evidence
        → Alert → DSS → Decision → Action → Outcome
```

Human decision, the evidence chain, immutable snapshots, versioned rules, and the deterministic critical path stay as they are. `ACKNOWLEDGED` is not a decision. `AgentRun` is not a decision. No data is not no risk. Resort files and aligned grids are future inputs to that chain, not a bypass of it. An external NOAA class remains external evidence. An estimate is not an observation and not an alert.

## Recorded versus not authorised

Recorded: NOAA CRW, EMODnet, Allen Coral Atlas, MERMAID as field observations, the variable registry, the literature library, spatial and temporal integration, provenance, uncertainty, resort history as site calibration and validation, leakage, and cold start.

Not authorised: XGBoost, Random Forest, an RBM engine, risk scoring, weights, new thresholds, an executable playbook, training, automatic recommendations, and automatic decisions.

How a future XGBoost would be split, held out, and checked for leakage is recorded in `docs/37-phase7.1-ml-validation-protocol.md`. What a spot must show, and why no downscaling target is authorised, is in `docs/38-phase7.2-scientific-target-and-spot-resolution.md`. Neither note authorises training. How a spot is read without a local model is in `docs/39-phase7.3-spot-intelligence-evidence-state-model.md`. The estimate slot is empty. Which of those sources can be shown today, and which formulas are allowed, is in `docs/40-phase7.4-spot-scientific-baseline.md`. What a live retrieval actually returned is in `docs/41-phase7.5-real-scientific-data-acquisition.md`. How a source may be tied to a spot without becoming a local value is in `docs/44-phase7.6-spatial-association-spot-mapping.md`. Resort history remains site calibration and independent validation.
