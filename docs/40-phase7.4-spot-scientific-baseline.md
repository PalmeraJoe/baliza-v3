# 40 — Phase 7.4 spot scientific baseline

Documentation only. No production code. No model. No local estimate. No new scientific threshold. `src/`, `alembic/`, and `tests/` are unchanged.

This is the deterministic baseline BALIZA can defend today: observed values, external products kept at their own scale, and a short list of audits that do not score risk. Demo thresholds that already exist in the software are not this baseline.

Local downscaling remains **NOT AUTHORIZED**. Machine-learning training remains **NOT AUTHORIZED**.

## What can be calculated now

For a spot, BALIZA can name which measurements exist, which external products could be attached once a spatial rule is written, and which audit facts follow from clocks and required inputs. It cannot mint a local temperature, a local DHW, a local HotSpot, a bleaching probability, or a risk score.

```text
SOURCE DATA
  → SPOT ASSOCIATION, explicit or UNKNOWN
  → QUALITY, which is not upgraded in silence
  → INDICATORS
  → RULE EVALUATION, only a published rule
  → SPOT STATE
  → ALERT, only on that evaluation
  → PLAYBOOK OPTIONS, not an action
```

Three categories stay separate. Observed means measured at the station, transect, or sensor. External means a provider product associated with the spot and still labeled with the provider's footprint. Derived means a BALIZA calculation from those two, with a formula in this note or in an already published rule. An external indicator does not become a fake local observation.

```text
NOAA GRID CELL  associated_with  SPOT A
```

is allowed as a statement of relation. `NOAA GRID CELL = SPOT A` is not.

## Master inventory

`Spot usable` means the value may be shown beside the spot while keeping its own scale. It does not mean the value is a property of the spot. `Alert capable` means a BALIZA rule may fire an alert from it. None of the rows below are alert capable: no scientific rule version adopts them. Evidence use means the value may sit in an evidence package as what it is.

| Indicator | Category | Source | Input | Spatial scale | Temporal scale | Formula / method | Spot usable? | Alert capable? | Evidence | Status |
|-----------|----------|--------|-------|---------------|----------------|------------------|--------------|----------------|----------|--------|
| CoralTemp SST | EXTERNAL_INDICATOR | NOAA CRW v3.1 | Nighttime foundation SST | 0.05° grid cell | UTC day | Provider product. Calibrated by CRW to 0.2 m | Only as the cell, after a written point-in-pixel rule | No | Yes, as external | AVAILABLE as a product. Association OPEN |
| SST anomaly | EXTERNAL_INDICATOR | NOAA CRW v3.1 | SST minus CRW daily climatology | 0.05° | UTC day | Provider formula. Not HotSpot | Same | No | Yes, as external | AVAILABLE as a product. Association OPEN |
| HotSpot | EXTERNAL_INDICATOR | NOAA CRW v3.1 | max(SST − MMM, 0) | 0.05° | UTC day | Provider formula | Same | No | Yes, as external | AVAILABLE as a product. Association OPEN |
| DHW | EXTERNAL_INDICATOR | NOAA CRW v3.1 | 84-day sum of HotSpot ≥ 1 °C, each divided by 7 | 0.05° | UTC day; 84-day window inside the product | Provider formula. °C-weeks | Same | No | Yes, as external | AVAILABLE as a product. Not a local DHW |
| Climatology / MMM | EXTERNAL_INDICATOR | NOAA CRW v3.1 | Monthly means 1985–2012 adjusted to 1988.2857; MMM is the max month | 0.05° | Fixed for that product version | Provider climatology | Same | No | Yes, as the baseline version | AVAILABLE as a product. CONTEXT |
| 7-day SST trend | EXTERNAL_INDICATOR | NOAA CRW v3.1 | CRW 7-day change and CRW's own test | 0.05° | 7 days ending on the product day | Provider product. Not a BALIZA trend | Same | No | Yes, as external | AVAILABLE as a product |
| Bleaching Alert Area | EXTERNAL_INDICATOR | NOAA CRW v3.1 | CRW classes from HotSpot and DHW | 0.05° | Single-day and 7-day maximum | Provider classes | Same | No. Not a BALIZA alert | Yes, as external evidence only | AVAILABLE as a product. CONTEXT |
| EMODnet bathymetry | CONTEXT_ONLY | EMODnet 2024 DTM | Soundings compiled by EMODnet | 1/16 arc minute inside listed European seas | DTM edition | Provider grid. World base layer is a different product | Only inside that footprint | No | As context, inside the footprint | PARTIAL. Outside the footprint: NOT_AVAILABLE |
| EMODnet physics | CONTEXT_ONLY | EMODnet Physics | In-situ temperature, salinity, currents, sea level, waves, wind, light, and other series where a platform exists | The platform, not a reef grid | Series-specific | Provider series. Not CRW | Only where a series is actually found | No | As that series | PARTIAL. Reef completeness UNKNOWN |
| EUSeaMap habitat | CONTEXT_ONLY | EMODnet | Broad-scale predictive habitats | About 100 m where the European DTM is used | 2023 edition | Provider map. Not global reef habitat | Only inside the mapped seas and named Caribbean territories | No | As context | PARTIAL |
| Reef mask | CONTEXT_ONLY | Allen Coral Atlas v2 | Shallow-reef extent | 5 m | Imagery epoch about 2018–2020 | Provider mask | As map context after a point sample rule | No | As context | AVAILABLE as a map. Not a management boundary |
| Benthic class | CONTEXT_ONLY | Allen v2 | Map class, roughly shallower than 10 m | 5 m | Same epoch | Provider classification. Not coral-cover percent | Same | No | As context | AVAILABLE as a map |
| Geomorphic zone | CONTEXT_ONLY | Allen v2 | Map zone, roughly shallower than 15 m | 5 m | Same epoch | Provider classification | Same | No | As context | AVAILABLE as a map. Not a BALIZA Zone |
| Satellite depth | CONTEXT_ONLY | Allen | Relative depth from imagery | 10 m | 12-month composite | Provider method. Not surveyed depth | Same | No | As context | PARTIAL. Not `depth_local` |
| Allen turbidity | CONTEXT_ONLY | Allen | Annual FNU; downloads are FNU × 10; cap 100 FNU | Stated with the depth method; confirm per file | Annual | Provider product. Not the survey day | Same | No | As context | AVAILABLE as an annual map |
| Bleaching observation | DIRECT_OBSERVATION and VALIDATION_ONLY | MERMAID | Quadrat colonies by genus and category | Site and transect of that project | Survey date | McClanahan and Darling, as cited by MERMAID | Only if the site is identified with the spot and the policy exposes the row | No | Yes, as that survey | PARTIAL. Not a predictor |
| Hard coral, soft coral, macroalgae cover | DIRECT_OBSERVATION | MERMAID | PIT, LIT, photo quadrat, or bleaching-quadrat cover | Sample unit | Survey date | Percent cover as calculated by MERMAID | Same access rule | No | Yes, as that survey | PARTIAL |
| Benthic observations | DIRECT_OBSERVATION | MERMAID | Attribute and growth form | Sample unit | Survey date | MERMAID benthic methods | Same | No | Yes, as that survey | PARTIAL. Not Allen classes |
| Fish observations | DIRECT_OBSERVATION | MERMAID | Belt count, size, biomass | Belt | Survey date | Ahmadia et al. 2013, as cited by MERMAID | Same | No | Yes, as that survey | PARTIAL. Not a vulnerability score |
| Habitat complexity | DIRECT_OBSERVATION | MERMAID | Visual score 0–5 | Transect intervals | Survey date | Wilson 2007 and Darling 2017, as cited by MERMAID | Same | No | Yes, as that survey | PARTIAL. Not rugosity |
| Survey metadata | DIRECT_OBSERVATION | MERMAID | Site, country, coordinates, reef type, zone, exposure, date | Site | Survey date | Project metadata | Identity only. Coordinates are not a join by themselves | No | As provenance | PARTIAL. CRS UNKNOWN |
| Recently dead colonies | DIRECT_OBSERVATION | MERMAID | One bleaching category | Quadrat | Survey date | Category on the collect form | Same access rule | No | Yes, as that category | PARTIAL. Not a later mortality percentage |
| Resort local temperature | DIRECT_OBSERVATION | Resort | A sensor or survey the operator recorded | Station or sensor | `observation_time` | Whatever method the record states | When a row exists, as a site measurement | No, until a published rule | Yes, as a measurement | NOT_AVAILABLE in the schema |
| Resort surveys and operational notes | DIRECT_OBSERVATION | Resort | Operator files | As recorded | As recorded | After the ingestion path in `docs/36` | Site calibration and independent validation | No | Only after quality and provenance | NOT_AVAILABLE until a resort actually deposits them |
| Local downscaled temperature | NOT_AVAILABLE | None | None | — | — | No authorised method | No | No | No | NOT_AVAILABLE |
| Local DHW or local HotSpot | NOT_AVAILABLE | None | Would copy or reshape the CRW cell | — | — | Not defined | No | No | No | NOT_AVAILABLE |
| Disease prevalence | NOT_AVAILABLE | — | Not on the MERMAID pages read | — | — | — | No | No | No | NOT_AVAILABLE |
| BALIZA risk score | NOT_AVAILABLE | — | — | — | — | Weights would be invented | No | No | No | NOT_AVAILABLE |

`CONTEXT_ONLY` cannot fire an alert. `VALIDATION_ONLY` cannot be used as a predictor unless a later scientific decision says so. MERMAID bleaching is both a field observation and a validation-only target. It is not a feature of the same event.

## Spatial association

Permitted relations are the ones that do not invent a finer measurement. The relation stored for a real spot stays `UNKNOWN` until that rule is applied to coordinates whose CRS is known. CRS codes for these grids are still `UNKNOWN`.

| Source unit | Permitted relation to a spot | Forbidden reading |
|-------------|------------------------------|-------------------|
| NOAA 0.05° cell | `CONTAINS` or `INTERSECTS` after a written point-in-pixel test. The value remains `GRID_CELL` | `DIRECT`. `NEAREST` as a default. Equality with the spot |
| CRW Regional Virtual Station | `ASSOCIATED` only as a regional summary, and only if a later note names the region | Treating it as a BALIZA Station |
| Allen 5 m or 10 m pixel | `INTERSECTS` by a point sample. Class stays a map class | `DIRECT`. Cover percent. Live colony depth |
| EMODnet DTM cell | `INTERSECTS` only inside the European footprint. Elsewhere the result is `NOT_AVAILABLE` | Filling the Indo-Pacific with the world base layer and calling it the same DTM |
| EMODnet physics platform | `DIRECT` only when the platform is the station. Otherwise `UNKNOWN` until a catalogue is queried | A nearby series copied onto the reef |
| MERMAID site | `DIRECT` only when project site identity is the spot or its station | `NEAREST` survey adopted as this spot's observation |
| Resort record | `DIRECT` when the record names that station | Using it as a global training row |

`AGGREGATED` is not permitted for any of these sources until a written method says what is aggregated, over which units, and what uncertainty that adds.

## Temporal association

| Indicator | Native time | Window | Publication delay | Alignment | Maximum age |
|-----------|-------------|--------|-------------------|-----------|-------------|
| CRW daily grids | UTC day | DHW already contains 84 days; the 7-day products contain 7 days | Usually about one day. This is a provider fact, not a staleness cutoff | A value may be used only if `publication_time` ≤ `as_of_time`. Unstated nearest day is forbidden | OPEN |
| CRW climatology | Product version, 1985–2012 adjusted | Not a survey day | The version's publication | Store the version. Do not rebuild it with years inside the question period | OPEN |
| Allen habitat and depth | Epoch about 2018–2020 | Map composite, not a day | Map edition | Do not label it as the survey hour | OPEN |
| Allen turbidity | Annual | Year of the product | Map edition | Not the survey week | OPEN |
| EMODnet DTM and EUSeaMap | Edition date | Static until the next edition | Edition publication | Not a tide or a survey hour | OPEN |
| EMODnet physics | Series timestamp | Series-specific | Series-specific | Match only on that timestamp. Gap-filling is not authorised | OPEN |
| MERMAID sample | Survey date | One method, one site, one date | Whenever the project published the row | Not available at a time before publication | OPEN |
| Resort record | `observation_time` on the file | As recorded | As recorded | Same `as_of` rule | OPEN |

## Quality

Reading labels: `GOOD`, `QUESTIONABLE`, `POOR`, `MISSING`, `UNKNOWN`.

This phase assigns `MISSING` when the input is absent or the source is unavailable, and `UNKNOWN` when quality cannot be determined. It does not assign `GOOD`. Existing facets such as suspect, low quality, delayed, or insufficient stay at least `QUESTIONABLE` until a published mapping says otherwise. They are never upgraded.

A derived indicator inherits the poorer quality of its inputs. It becomes better only with an explicit, versioned justification. No such justification is adopted here.

## Freshness and completeness

`DATA_FRESHNESS` may be stored as a duration: `as_of_time` minus the observation time, and separately minus the publication time. Labels `CURRENT`, `RECENT`, `STALE`, and `UNKNOWN` exist. The ages that separate the first three are **OPEN**. An empty clock is `UNKNOWN`, not `CURRENT`.

`EVIDENCE_COMPLETENESS` labels remain `COMPLETE`, `PARTIAL`, `INSUFFICIENT`, and `UNKNOWN`. The cutoff between them is **OPEN**. The deterministic substitute that is allowed now is the list of required inputs that are missing. `INSUFFICIENT` is not `NORMAL`.

## Thermal products

| Product | Observable or derived | External? | Resolution | Spot association | Evidence? | BALIZA indicator? | BALIZA rule? | Limit |
|---------|----------------------|-----------|------------|------------------|-----------|-------------------|--------------|-------|
| SST | Derived by CRW from satellite SST | Yes | 0.05°, daily | Cell contains the point, or `UNKNOWN` | Yes | Only by citing the cell | No rule adopted | Surface foundation temperature, not colony temperature. Lower data density before late 2002 |
| SST anomaly | Derived by CRW | Yes | 0.05°, daily | Same | Yes | Same | No | Not HotSpot. Baseline is the CRW climatology version |
| HotSpot | Derived by CRW | Yes | 0.05°, daily | Same | Yes | Same | No | Warm-season exceedance of MMM. Cold stress is clipped off. Not a bleaching survey |
| DHW | Derived by CRW | Yes | 0.05°, daily | Same | Yes | Same | No | 84-day product window. Not a local accumulation |
| 7-day trend | Derived by CRW | Yes | 0.05° | Same | Yes | Same | No | CRW's test is not a BALIZA threshold |
| Climatology | Derived by CRW | Yes | 0.05°, versioned | Same | Yes | As version context | No | Not a local seasonal normal |
| Bleaching Alert Area | Derived by CRW | Yes | 0.05° | Same | Yes, external only | No BALIZA copy | No | Not a BALIZA alert. Single-day layer is the unstable one, by CRW's own statement |

## Ecological products

Observed bleaching, bleaching category, hard-coral cover, soft-coral cover, macroalgae, fish, and habitat complexity are MERMAID field records when a project collected them and the sharing policy exposes them. They are evidence of that survey. They are not a grid. Bleaching may later be ground truth or a validation target. It is not a predictor of the same event. Recently dead is a colony category on that form. It is not `mortality_percentage`. Fish biomass is not a coral-vulnerability score. Habitat complexity is not bathymetric rugosity.

## Spatial products

Allen reef mask, benthic class, and geomorphic zone are `CONTEXT_ONLY`. Satellite depth and annual turbidity are `CONTEXT_ONLY`. None of them becomes a `DERIVED_INDICATOR`: turning a map class into coral cover, a relative depth into diver depth, or an annual turbidity into the survey day's turbidity would be an inference this record does not support.

EMODnet bathymetry and EUSeaMap are `CONTEXT_ONLY` inside their footprints and `NOT_AVAILABLE` outside them. Physics series are `CONTEXT_ONLY` at the platform that measured them. They do not replace CRW heat products.

## Resort data

A local sensor, survey, or operational record may be a `DIRECT_OBSERVATION` after ingestion, quality, and provenance. It belongs to site calibration and independent site validation. It is not base-model training. No resort series is in the schema, so every resort row is `NOT_AVAILABLE` until a real file exists. A missing resort history does not authorise a filled local value.

## Derived indicators permitted now

| Indicator | Justification | Formula | Inputs | Limitation |
|-----------|---------------|---------|--------|------------|
| Missing required inputs | A published indicator cannot be evaluated as success when a required input is absent. This is the existing rule behaviour | List each required input that has no usable value at `as_of_time` | The indicator version and the values available at `as_of_time` | The list is not a completeness percentage |
| Direct observation count | States how many local measurements are in the snapshot | Count of `DIRECT` measured records with observation time and publication time at or before `as_of_time` | Measured records only | Repeats are not independent. The count is not evidence strength |
| Time since last direct observation | States the age of the newest local measurement | `as_of_time` minus the latest such observation time. If the count is zero, the result is empty | Those records | Empty is not zero age and not `NORMAL` |
| Attached external set | States which products were associated without copying them onto the spot | The set of external values that have a permitted relation and a publication time at or before `as_of_time`, each with its scale | External products and the relation | Membership is not spatial downscaling |
| Signal list | Disagreement cannot be resolved by a sum | The list of those values, unchanged | The attached set and the direct observations | No conflict bit is set by this formula |

Not permitted: a weighted sum, a 0–100 score, a BALIZA thermal trend, a local DHW, a completeness fraction, or a freshness class. Source agreement is the signal list. A `SIGNAL_CONFLICT` flag waits for a versioned rule that defines what disagrees. Until that rule exists the flag is `UNKNOWN`, not false, and it does not select `VERIFY`.

## Conflict, state, alert, playbook

Signals stay separate. An example of the kind of case, not a stored event: a CRW heat product, a local sensor, and a MERMAID bleaching row. BALIZA keeps signal A, signal B, and signal C. It does not collapse them.

| Illustrated state | Status in this baseline | Definition adopted? | Inputs | Rule family | Uncertainty and evidence | Transition and exit |
|-------------------|-------------------------|---------------------|--------|-------------|--------------------------|---------------------|
| NORMAL | OPEN | No | — | — | — | OPEN. No-data must not enter here by default |
| ELEVATED | OPEN | No | — | — | — | OPEN |
| HIGH | OPEN | No | — | — | — | OPEN |
| CRITICAL | OPEN | No | — | — | — | OPEN |
| UNKNOWN | Already a rule outcome | Yes, as outcome, not as a new heat state | Quality cannot be determined, or a required input is absent | Existing evaluation | Stays visible | Not `NOT_TRIGGERED` |
| INSUFFICIENT_DATA | Already a rule outcome | Yes, as outcome | Sample or quality below what that rule already requires | Existing evaluation | Stays visible | Not `NOT_TRIGGERED` and not `NORMAL` |

`NOT_TRIGGERED` means a published rule ran and its condition was not met. It is not the label for missing data.

An alert, when a published rule produces one, carries `alert_id`, scope (the spot once that identity exists), `alert_type`, `severity`, `status`, `created_at`, `rule_version`, `evidence_package`, and uncertainty. It is traceable, versioned, reproducible, and auditable. The deterministic engine produces it. An LLM does not. Copying Bleaching Alert Area into `alert_type` is forbidden. No thermal rule in this baseline creates an alert, so a scientific heat alert is not available today.

Playbook options remain `MONITOR`, `VERIFY`, `INTENSIVE_SURVEY`, and `MITIGATION_OPTION`. `DATA_COLLECTION` is still only a candidate name. Eligible options are not chosen and not executed. The matrix of state × evidence × uncertainty × quality is the illustrative one in `docs/39-phase7.3-spot-intelligence-evidence-state-model.md`. Entry conditions are **OPEN**. A conflict does not by itself make `VERIFY` eligible.

## Actionability

| Indicator | Class now | May a later rule change the class? |
|-----------|-----------|------------------------------------|
| Allen benthic, geomorphic, reef mask, satellite depth, turbidity | CONTEXTUAL | Not into an alert without a new scientific decision |
| EMODnet bathymetry, habitats, physics | CONTEXTUAL | Same |
| NOAA SST, anomaly, HotSpot, DHW, trend, climatology | INFORMATIONAL as external evidence | `STATE_RELEVANT` or `ALERT_RELEVANT` only after a published rule. Not assumed |
| NOAA Bleaching Alert Area | CONTEXTUAL external evidence | It does not become a BALIZA alert by relabeling |
| MERMAID ecology and bleaching | INFORMATIONAL evidence; bleaching also VALIDATION_ONLY | Not a predictor by default |
| Missing-input list, observation count, time since last observation | INFORMATIONAL | Not a risk score |
| Resort measurements | INFORMATIONAL when present | Site validation, not base training |

## Minimum spot reading

| Field | Status today |
|-------|----------------|
| Spot identity | PARTIAL. Operational place named; equality with Zone is OPEN |
| Observations | REQUIRES_LOCAL_DATA for a resort sensor. MERMAID is PARTIAL and policy-limited |
| External indicators | PARTIAL. Products are specified. The spatial link is OPEN, so they are not yet attached |
| Derived indicators | PARTIAL. The five formulas above are specified. Categorical freshness, completeness, and conflict are OPEN |
| Data quality | PARTIAL. `MISSING` and `UNKNOWN` can be stated. `GOOD` is not assigned |
| Freshness | PARTIAL. A duration can be computed. `CURRENT` / `RECENT` / `STALE` are OPEN |
| Evidence completeness | REQUIRES_SCIENTIFIC_DECISION for the four labels. The missing-input list is specified |
| Signal conflict | PARTIAL. Signals are listed. The flag is `UNKNOWN` until a rule defines conflict |
| Uncertainty | PARTIAL. Kinds are named. No numeric method |
| State | REQUIRES_SCIENTIFIC_DECISION for heat states. `UNKNOWN` and `INSUFFICIENT_DATA` already exist as rule outcomes |
| Alert | NOT_AVAILABLE as a scientific heat alert. The alert object on the existing path is unchanged and is not fed by these products |
| Playbook options | PARTIAL. Names exist. Eligibility is OPEN |
| Human decision | AVAILABLE_NOW as a boundary. The value is pending until a person decides |

## No data

No data is not no risk. Without a published rule that explicitly concludes a normal condition, missing inputs do not produce `NORMAL`. The evaluation can produce `INSUFFICIENT_DATA` or `UNKNOWN`, as it already does. `DATA_COLLECTION` and `VERIFY` are not automatically offered.

## Worked spot

SPOT A, at an `as_of_time`, with no local series in the system of record and no coordinates joined:

```text
Observed:
  none in the schema

External:
  NOAA CRW products exist as 0.05° cells and are not attached
  EMODnet is not attached; outside a known footprint it is NOT_AVAILABLE
  Allen classes exist as a map epoch and are not attached

Derived:
  direct observation count = 0
  time since last direct observation = empty
  missing required inputs = those a published indicator lists, not a heat score
  attached external set = empty until a relation is written
  signal list = empty
  SIGNAL_CONFLICT = UNKNOWN

Quality:
  MISSING for local measurements

Freshness:
  UNKNOWN

Evidence completeness:
  not classified

Uncertainty:
  spatial relation UNKNOWN; no model uncertainty because no model

State:
  not NORMAL
  heat states not assigned

Alert:
  none from this baseline

Playbook options:
  none selected

Human decision:
  PENDING
```

## Boundary for a future model

Ready as specifications, not as a training set: source inventory, the ban on silent spatial copying, `as_of_time`, quality inheritance, the indicator path, and the evidence chain.

Not ready: target, ground truth, local downscaling, applicability domain, uncertainty method, spatial joins on real coordinates, freshness cutoffs, state thresholds, alert thresholds, and playbook entry conditions.

Training is not authorised. Model readiness stays `NOT_READY`.

## Verdict

PHASE 7.4 SPOT SCIENTIFIC BASELINE DEFINED — ML IMPLEMENTATION NOT AUTHORIZED.

A later retrieval (`docs/41-phase7.5-real-scientific-data-acquisition.md`) found two different SST-anomaly products on ERDDAP, a negative HotSpot in the sampled cell, and no unique cell for the published heritage coordinate -23.5, 152.0. Those facts do not authorise a local indicator or an alert.
