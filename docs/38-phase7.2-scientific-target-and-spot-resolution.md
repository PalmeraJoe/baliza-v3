# 38 — Phase 7.2 scientific target, spot resolution, and operational mapping

Documentation only. No model is trained. No weight or scientific threshold is set. `src/`, `alembic/`, and `tests/` are unchanged.

This note answers what BALIZA must be able to say about a place, which of that knowledge is observed, which would be estimated, and which claims are not yet scientifically allowed.

Status of the first downscaling target: **NOT AUTHORIZED**.

## Operational question

BALIZA needs, for each spot, a reading a manager can interpret: what was measured, what was only estimated, how uncertain that estimate is, whether an estimate is allowed at all, which versioned indicator and rule produced any state or alert, and which playbook options a human may consider. It does not need a score that chooses the action.

The concepts below stay separate. An estimate is not an observation. An indicator is not an alert. An alert is not a decision. A playbook option is not an action.

| Layer | What it is | Example of the kind of statement | What it is not |
|-------|------------|----------------------------------|----------------|
| A. Observation | A recorded measurement | A sensor at spot A read 29.1 °C at time T | A filled gap |
| B. Estimation | A value computed from other sources | A local temperature estimate, with an uncertainty and a domain flag | Ground truth of itself |
| C. Indicator | A versioned transform of observations and/or estimates | A local thermal anomaly defined by a published formula | A rule outcome |
| D. State | A deterministic reading from a versioned rule | A named thermal-stress state | An alert by itself, and not a CRW class copied into BALIZA |
| E. Alert | A traceable signal that a condition needs human attention | An alert with evidence and a rule version | A decision or a NOAA Bleaching Alert Area |
| F. Playbook option | An allowed option in a catalog | MONITOR, VERIFY, INTENSIVE SURVEY, MITIGATION OPTION | An executed action |
| G. Decision | A recorded choice by an actor, with a justification and a time | A manager chooses an intensive survey | An agent recommendation |

NOAA Bleaching Alert Area remains external evidence. It is not layer E.

## Candidate targets

`ML candidate = no` means the variable is not proposed as something a model should learn. `OPEN` means the evidence in Phase 7 is not enough to authorise it. Coverage and independent sample size are `UNKNOWN` wherever no local series is in the system of record.

| Candidate | Why BALIZA might need it | Ground truth | Native spatial scale of what we actually have | Time scale of what we actually have | Source of that existing product | ML candidate? | Status |
|-----------|--------------------------|--------------|-----------------------------------------------|-------------------------------------|---------------------------------|---------------|--------|
| Local temperature | A manager asks how warm the water is at the spot, not in a 0.05° cell | In-situ temperature at a stated depth and time. Not in the BALIZA schema | NOAA CoralTemp is 0.05°, calibrated to 0.2 m, not colony temperature. EMODnet Physics temperature exists only where a series exists; reef completeness is UNKNOWN | Daily for CoralTemp; in-situ series UNKNOWN | NOAA; EMODnet Physics where present | Only if an independent in-situ label exists. Not authorised | OPEN |
| Local temperature anomaly | Departure from a local seasonal baseline | Local temperature minus a named, versioned climatology. CRW's anomaly is not this quantity | Same limit as local temperature | Daily once both inputs exist | Would be derived. CRW anomaly is a different variable | No, unless the anomaly itself is the label and the climatology is frozen outside the test period | OPEN |
| Thermal stress as CRW HotSpot or DHW | Regional heat context | The CRW product itself, as an external derived grid. It is not a bleaching survey | 0.05° | Daily; DHW uses an 84-day window | NOAA CRW v3.1 | No. These are ingested products, not local labels | CLOSED as external indicators. Not a downscaling target |
| A local thermal-stress index distinct from CRW | A spot-scale stress statement | Not defined. No formula and no local label are adopted | Not defined | Not defined | None | No | OPEN |
| Turbidity | Water clarity context | An in-situ optical measurement at the survey time. Allen annual turbidity is not that measurement | Allen: annual FNU, downloads stored as FNU×10, values capped | Annual map epoch, not the survey day | Allen Coral Atlas | No | OPEN as a local target. Map context only |
| Depth | Habitat and light context | Diver or instrument depth, Allen relative depth, and the EMODnet DTM are different quantities | Allen bathymetry 10 m where mapped; benthic classes shallower than about 10 m; EMODnet DTM only inside its footprint; MERMAID transect depth is PARTIAL and missing on the bleaching form | Allen is an imagery epoch; diver depth is the survey time | Allen, EMODnet, MERMAID | No | OPEN which depth a spot uses. Not an ML target |
| Coral cover, habitat complexity, fish metrics | Ecological description | MERMAID field methods where the project policy exposes the row. Not a global layer | Sample unit: one method, one site, one date | Survey date | MERMAID | No | PARTIAL as field observations. Not a downscaling target |
| Bleaching observation | Possible later validation reference or outcome | MERMAID bleaching categories and colony percentages, where public. Recently dead is not a later mortality rate | Quadrats at a site | Survey date | MERMAID | No as a predictor of the same event. Not assumed to be the model target | OPEN as a target. CLOSED as "not a same-event predictor" |
| Downscaled temperature estimate | A future model output | Cannot be its own ground truth | Would aim at a station or spot; that aim is not authorised | `observation_time` of the label | None. The model does not exist | Not authorised | OPEN |

Answers that are the same for every OPEN row: BALIZA does not have a count of independent examples, does not have a measured spatial or temporal variance of a local label, and does not have a near-real-time local feed. NOAA daily grids are usually about one day behind UTC. That lag is publication delay, not local truth.

### Ten questions, short form

| Candidate | Observable? | Derived? | Ground truth exists in hand? | Coverage enough? | Resolution enough for a spot? | Near real time? | Validable now? | Operational at a spot? | Leakage risk if misused? | ML target or deterministic indicator? |
|-----------|-------------|----------|------------------------------|------------------|-------------------------------|-----------------|----------------|-------------------------|--------------------------|----------------------------------------|
| Local temperature | Yes, if a sensor or survey measured it | No | No series in the schema | UNKNOWN | NOAA 0.05° is not spot-scale | Only after a local feed exists. NOAA is ~1 day lagged | Not until labels exist | Yes, if it were measured | Using later SST, or NOAA SST as both feature and label | OPEN. Working hypothesis only. Not authorised |
| Local anomaly | Only after local temperature exists | Yes | No | UNKNOWN | No | No | No | Yes, as an indicator, once defined | Climatology that includes the test period | Deterministic indicator later. Not an ML target now |
| CRW HotSpot, DHW, SST, CRW anomaly, 7-day trend | The grids are published products | Yes, by CRW | The product is the product, not a reef survey | Global grid | No. 0.05° is regional relative to a transect | Near-real-time with ~1 day lag | Against in-situ temperature only for SST, and only as a mismatch study | As context, with the footprint stored | Future days inside a window; climatology leakage | Deterministic external indicators |
| Local thermal stress | Not defined | Would be | No | UNKNOWN | UNKNOWN | UNKNOWN | No | UNKNOWN | High if built from post-event bleaching | OPEN |
| Turbidity | Allen map is a product; in-situ turbidity is not in the schema | Allen value is derived | Local optical truth not in hand | Map is wide; survey-week match is UNKNOWN | Annual, capped, not a spot hour | No | Not against a survey week without a written rule | As context | Treating the annual map as the survey day | Not an ML target |
| Depth | Diver depth is observable where recorded | Allen and DTM are products | Three incompatible depths | PARTIAL | Depends on the product footprint | Diver depth is campaign time | Not by equating the three | As context | Filling missing diver depth from the DTM without saying so | Not an ML target |
| Cover, complexity, fish | Observable in MERMAID when policy allows | Some MERMAID fields are calculated | PARTIAL, project by project | Not global | Survey, not a grid | No. Campaign time | As a survey, not as a grid skill score | As evidence, not as a pixel | Repeated sites treated as independent | Not an ML target |
| Bleaching observation | Observable when the quadrat row is public | Percentages are calculated by MERMAID | PARTIAL | Not global | Survey | No | As ground truth of that survey only | As evidence or a later outcome | Using it to predict the same event | Not assumed to be the target |

## Ground truth

| Target | Ground truth | Method | Spatial precision | Temporal precision | Uncertainty | Usable for validation? |
|--------|--------------|--------|-------------------|--------------------|-------------|------------------------|
| Local temperature | In-situ temperature | Sensor or field instrument at a stated depth | The station or sensor point. CRS of a future file is UNKNOWN until read | `observation_time` | Instrument and depth mismatch versus a 0.2 m foundation SST. No number is assigned | Not yet. No series is in the system of record |
| Local anomaly | That temperature and a frozen climatology | Derived | Same as the temperature | Same | Baseline choice dominates | No |
| CRW SST, anomaly, HotSpot, DHW | The versioned CRW grid | Satellite foundation SST and CRW formulas | 0.05° pixel | UTC day; DHW is 84 days | Surface versus colony; early record has lower density | As a check that ingestion copied the product. Not as local reef truth |
| Turbidity | In-situ optics at the question's time | Not in the schema | UNKNOWN | Survey time | Allen annual FNU is a different quantity | No |
| Depth | The method named on the value | Diver, Allen relative depth, or DTM | Method-specific | Survey or map epoch | Methods are not interchangeable | Only inside one method |
| MERMAID ecology and bleaching | The survey row | PIT, LIT, photo quadrat, fish belt, bleaching quadrats, as documented | Site and transect of that project | Survey date | Observer, method, and policy. Sharing may hide the observations | Only for rows the policy exposes. Not a global test set |
| Any model estimate | None | A model | The model's claim | The model's clock | Unknown until a method exists | An estimate is never ground truth of itself |

Epistemic classes stay distinct: in-situ sensor, field campaign, MERMAID observation, satellite-derived product, model estimate, interpolated value, aggregated value. Co-location in space and time does not make them equivalent.

## Spot

```text
Resort     an Entity: the managed place (resort, MPA, or operator)
  Zone     a spatial operational or ecological unit inside it
    Spot   the place a manager asks about
      Station / Transect / Sensor
           where a measurement is actually taken
```

`Spot` is the operational place of interpretation: the unit at which a situation, an estimate, an alert, and a playbook option are shown together. It is not a cluster built to suit a model. It is not a NOAA pixel and not a CRW Regional Virtual Station.

Whether a Spot is the same object as a Zone, a named subdivision of a Zone, or a declared group of stations is **OPEN**. The glossary already leaves Zone nesting and geometry format as `TBD`. Phase 7.2 does not close that by convenience.

A Spot may carry, when a human has defined them and a source supports them: latitude and longitude or a geometry, a CRS, a depth with its method, a reef extent, a geomorphic class, a habitat class, exposure, coastal proximity, bathymetry, the monitoring gear that actually exists, and ecological notes from a real survey. Missing properties stay missing. Allen classes are map context for the footprint, not a new survey of cover. Reef extent is ecological, not automatically a Zone.

Stations, transects, and sensors sit inside a Spot. Many observations can share one station. Alerts and decisions stay scoped to the operational place (Zone or Spot once those are identified), not silently to a single pixel.

## Spatial resolution

```text
Global CRW grid
  → regional cell (0.05°, or a CRW virtual station)
    → Resort
      → Zone
        → Spot
          → Station / Transect
```

| Source | Native resolution | Useful as | Time | Spatial uncertainty | Downscaling required to speak about a spot? | Defensible now? |
|--------|-------------------|-----------|------|---------------------|---------------------------------------------|-----------------|
| NOAA CRW v3.1 | 0.05° daily global | External thermal context at the pixel that contains the spot | Daily, ~1 day publication lag | Pixel footprint. CRS code UNKNOWN | A local claim would require it | No. Sampling the pixel is allowed only with the footprint stored |
| EMODnet Bathymetry 2024 | 1/16 arc minute inside listed European seas | Bathymetric context inside the footprint | DTM edition | Outside the footprint: not available | No. Do not paint it onto other oceans | Only inside the footprint, as that DTM |
| EMODnet Physics | In-situ series where they exist | Context | Series-specific | Reef completeness UNKNOWN | No | Only where a series exists |
| EUSeaMap | About 100 m where the EMODnet DTM was used; European seas, Caspian, and named Caribbean territories | Habitat map context | Map edition | Not global | No | Only inside the map |
| Allen Coral Atlas v2 | Benthic and geomorphic 5 m; reef mask 5 m; bathymetry 10 m; turbidity annual | Shallow-reef map context. Benthic classes are for roughly the upper 10 m; geomorphic for roughly the upper 15 m | Imagery epoch about 2018–2020 | Regional accuracy stated as 60–90%. Not coral-cover percent | No | As a map class, not as a live spot survey |
| MERMAID | One method at one site on one date | Field evidence | Survey date | Site coordinates; CRS UNKNOWN | No | Where policy exposes the row |
| Resort history | Whatever the operator recorded | Site calibration and independent site validation | As recorded | As recorded, after quality checks | Not a base-model grid | Not in base training |

Spatial-temporal coincidence does not imply scientific equivalence. A 5 km SST value does not describe a 10 m transect. Spots are not assumed to be estimable at one shared precision.

## Time

Clocks already recorded: `observation_time`, `acquisition_time`, `processing_time`, `publication_time`, `ingestion_time`, plus the start and end of an aggregation window.

`Information available at time t` means a value whose publication time is at or before `t`, whose valid window is the one being used, and whose construction did not use observations that existed only after `t`. Ingestion time does not qualify a value. A near-real-time CRW day that is published the next day is not available at `t` on the measurement day.

Aggregation period, processing time, and prediction time stay labeled. A monthly composite is not the survey-day temperature. An 84-day DHW window used for a condition at `t` may include only days up to `t`.

## Downscaling

```text
REGIONAL / COARSE DATA
        + LOCAL CONTEXT
        + SCIENTIFIC FEATURES
        → LOCAL ESTIMATE
          + UNCERTAINTY
          + APPLICABILITY DOMAIN
```

| Question | Local temperature | Local anomaly | CRW thermal products | Turbidity | Depth | Ecology / bleaching |
|----------|-------------------|---------------|----------------------|-----------|-------|---------------------|
| Variable to downscale | In-situ temperature | Not a downscale; a formula | Already on the CRW grid | Not justified from an annual map to an hour | Not a downscale across methods | Not justified from these grids |
| From | 0.05° CoralTemp, plus context | — | — | — | — | — |
| Toward | Station or spot. Which one is OPEN | — | Pixel, stored as a pixel | — | — | — |
| Explanatory variables | Candidates only: SST, CRW anomaly, HotSpot, DHW, depth, habitat class. None approved | — | — | — | — | — |
| Ground truth | In-situ, absent from the schema | Absent | The product | Absent | Method-specific | MERMAID where allowed; not the same-event feature |
| Independent examples | UNKNOWN | UNKNOWN | The grid is one product family, not independent local trials | UNKNOWN | UNKNOWN | UNKNOWN; repeats are dependent |
| Spatial variance of the label | UNKNOWN | UNKNOWN | Not a local label | UNKNOWN | UNKNOWN | UNKNOWN |
| Temporal variance of the label | UNKNOWN | UNKNOWN | Not a local label | UNKNOWN | UNKNOWN | UNKNOWN |
| Leakage | NOAA SST as feature and label; future days; nearby stations; resort rows in the base set | Climatology overlap | Window past `t` | Annual map as a day | Filling one depth method with another | Bleaching percent predicting that survey |
| Baseline to beat | Persistence and the NOAA pixel, if the label is ever local temperature. Not selected | A stated climatology | Copy the product exactly | The map value, labeled as annual | The recorded method | A survey replay, not a model |

No row authorises XGBoost. The working hypothesis remains local temperature versus the NOAA pixel, and it stays unauthorised until ground truth, depth, spatial group, uncertainty method, and the applicability boundary exist.

## Uncertainty and abstention

An estimate, if one is ever produced, carries four separate statements:

- the number;
- uncertainty of the data and uncertainty of the model, kept apart;
- reliability, meaning whether the validation error for this kind of case is known;
- applicability, meaning whether the spot is inside the supported domain.

Do not collapse these into one confidence fraction. Phase 6 types stay qualitative: known, unknown, insufficient, conflicting, suspect. No new numeric uncertainty is invented.

Conceptual status of an estimate:

| Status | Meaning | Becomes an alert? |
|--------|---------|-------------------|
| `VALID` | Inside the domain, required inputs present, uncertainty method applied | No |
| `VALID_WITH_HIGH_UNCERTAINTY` | Inside the domain, uncertainty too large for a precise claim, method still named | No |
| `INSUFFICIENT_DATA` | A required input is missing or unusable | No |
| `OUT_OF_APPLICABILITY_DOMAIN` | Place, variable mix, source, or resolution is outside the supported domain | No |
| `NOT_ESTIMABLE` | No scientifically defensible estimate | No |

The boundaries between these statuses are **OPEN**. They are not thresholds.

BALIZA must be able to abstain: there is no scientifically defensible estimate. Conditions that force abstention, without numeric cutoffs: too few observations, out-of-domain conditions, insufficient spatial coverage, insufficient temporal coverage, uncertainty that the method itself calls excessive, a missing critical feature, spatial extrapolation the domain does not support, temporal extrapolation the domain does not support. Abstention is a gap in the reading. It is not zero risk and it is not "no bleaching".

## Validation

The split rules are `docs/37-phase7.1-ml-validation-protocol.md`. Scenario A is the same site at a later time. Scenario B is an unseen site in a period already used historically. Scenario C is an unseen site at a later time. Passing one does not pass the others. A random row split is not the scientific validation.

The blocking unit remains **OPEN**: reef, zone, site, station, transect, or another group the tables support. Spot is not chosen as that unit merely because this note defines Spot as an operational place. Nearby stations can still leak across a Spot boundary.

## Resort history

Unchanged:

```text
RESORT HISTORICAL DATA
        → SITE-SPECIFIC CALIBRATION
        + INDEPENDENT VALIDATION
```

Resort rows do not train the base model unless a later scientific decision says so.

For each resort, once volume and structure allow, two disjoint subsets:

- calibration set, used only to adjust a site-specific layer;
- validation set, unused in that adjustment.

A row cannot move from the first to the second after the adjustment and still be called independent. The rule that cuts a particular resort (by time, by station, or by campaign) is **OPEN** until that resort's structure is known. The base-model holdout in `docs/37` is a different dataset from both subsets.

Cold start stays as in `docs/36`: NOAA, EMODnet, Allen, and MERMAID where a row is actually allowed. Missing resort history reduces local calibration. It does not create a local estimate.

## From estimate to indicator, and from alert to a person

```text
Raw source
  → Observation          epistemic class stored
  → Estimated local variable, or abstention
  → IndicatorValue       versioned formula
  → RuleEvaluation       versioned rule
  → EvidenceItem
  → EvidencePackage
  → Alert                only on the existing critical path
  → DSS package
  → Compatible playbook options
  → Human decision       actor, justification, timestamp
  → Action
  → Outcome
```

A model estimate enters as `MODEL_ESTIMATED`. It does not skip evidence. It does not create an alert by itself. Generative AI is not on this path.

Playbook options remain MONITOR, VERIFY, INTENSIVE SURVEY, and MITIGATION OPTION, with no entry conditions. BALIZA may list the options that a future published protocol marks as compatible with the package. It does not choose one. Which alert would make which option compatible is **OPEN**, because writing that link would be a policy threshold. The human record is actor, decision, justification, and timestamp.

## Spot state

A future `SpotState` is a reading, not a new table in this phase. It would hold: `spot_id`, timestamp, observations, estimated variables, indicators, evidence references, uncertainty, applicability status, rule evaluations, alert reference if one exists, and playbook options. It would not hold a chosen action. It is not implemented.

## What may run without a person

Automatic, when the corresponding phase has already authorised the step: ingestion, normalisation, quality checks, indicator calculation, rule evaluation, evidence generation, alert generation, DSS package generation. Downscaling and a numeric uncertainty method become automatic only after they are authorised. They are not.

Human: accepting what the evidence means in context, choosing a playbook option, deciding, authorising an action, judging the outcome.

## Traceability

For any BALIZA alert the chain already required by the evidence model must reach: alert, rule version, indicator, estimate or observation, source data, source version, processing, uncertainty, evidence, DSS package, human decision, action, outcome. This note adds no new link and removes none. `ACKNOWLEDGED` is not a decision. `AgentRun` is not a decision.

## What is resolved

CLOSED as rules, not as trained science:

- The seven layers stay distinct.
- CRW HotSpot, DHW, SST, CRW anomaly, and the 7-day trend are external indicators at 0.05°, not local labels and not BALIZA alerts.
- NOAA Bleaching Alert Area is not a BALIZA alert.
- Coincidence of time and place is not scientific equivalence.
- An estimate is not its own ground truth.
- MERMAID bleaching is not a predictor of the same event and is not assumed to be the target.
- Resort history is calibration plus independent validation, not base training.
- Abstention is allowed and does not become an alert by itself.
- The final holdout and the A/B/C scenarios of Phase 7.1 still apply.
- A person decides. An agent does not.

PARTIAL:

- Spot is defined as the operational place of interpretation. Its identity versus Zone is open.
- Native resolutions of the four external sources are known. The resolution BALIZA may defend at a spot is not.
- Clocks and the meaning of "available at t" are defined. The scientific clock of each future feature still has to be filled in the feature table.
- Uncertainty statuses are named. The method and the boundaries are not.
- Applicability is a required flag. The boundary rule is not.
- Playbook option names and the human gate are defined. The alert-to-option map is not.
- Resort calibration and validation must be disjoint. The cut for a real resort is not.

OPEN, and therefore blocking:

- The first downscaling target.
- Ground truth in the system of record for that target.
- Which depth a spot uses.
- The spatial blocking unit.
- Independent sample size, spatial variance, and temporal variance of any local label.
- Numeric abstention bounds.
- Uncertainty method.
- Entry conditions for playbook options.

## Verdict

PHASE 7.2 SCIENTIFIC TARGET & SPOT RESOLUTION DEFINED — ML IMPLEMENTATION NOT AUTHORIZED.

The operational reading that uses this target status, with no local estimate, is `docs/39-phase7.3-spot-intelligence-evidence-state-model.md`. Model readiness there is `NOT_READY`. The deterministic baseline that does not fill that gap is `docs/40-phase7.4-spot-scientific-baseline.md`. Linking an external product to a spot does not create the missing local value (`docs/44-phase7.6-spatial-association-spot-mapping.md`).
