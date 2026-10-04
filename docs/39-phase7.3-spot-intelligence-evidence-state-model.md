# 39 — Phase 7.3 spot intelligence and evidence state

Documentation only. No model is trained. No local estimate is created. No scientific threshold is set. `src/`, `alembic/`, and `tests/` are unchanged.

BALIZA has to be useful before any local downscaling exists. This note defines the logical reading a person gets for one spot at one time. It does not add a table, a screen, or a rule version.

Local downscaling remains **NOT AUTHORIZED**. Estimated values in this reading are **NONE**.

## What the reading must answer

For a spot at an `as_of_time`: where; when; what was measured; what is an external product; what BALIZA derived; what was estimated; what is unknown; what is uncertain; which deterministic state results; which alert exists and why; which playbook options are compatible; who must decide.

Those answers stay in separate layers. A grid product is not a local measurement. An estimate is not an observation. A state is not an alert. An alert is not a decision. A playbook option is not an action. Absence of data is not absence of risk.

## SpotIntelligence

`SpotIntelligence` is a logical object. It is not implemented. A later implementation must reuse the existing evidence chain and the immutable DSS snapshot. It must not create a second history that a newer alert can rewrite.

```text
spot
as_of_time

observations              MEASURED
external_indicators       EXTERNAL INDICATOR
derived_indicators        DERIVED INDICATOR
estimated_values          ESTIMATED, currently NONE

data_quality
evidence
uncertainty
applicability

state                     from a versioned rule evaluation
alerts
playbook_options

decision                  human, or absent
action                    absent until that decision
outcome                   absent until an action is recorded
```

`spot` is still the operational place from `docs/38-phase7.2-scientific-target-and-spot-resolution.md`. Whether it is the same object as a Zone remains **OPEN**.

## Epistemic layers

### MEASURED

A value someone or some instrument recorded: a sensor temperature, a field note, a MERMAID survey row the project policy exposes, a survey depth, a local turbidity measurement. Each value keeps source, source version, timestamp, spatial precision, temporal precision, unit, method, quality, and provenance.

MERMAID bleaching, when the row is public, is a field observation. It is not a predictor of that same event and it is not a BALIZA alert.

Resort history, if stored, is measured or reported local material for later site calibration and independent validation. It is not base-model training.

### EXTERNAL INDICATOR

A product already computed by a provider: NOAA CoralTemp, HotSpot, DHW, SST anomaly, 7-day trend, Bleaching Alert Area; Allen turbidity, habitat, geomorphology, or relative depth; EMODnet bathymetry or an in-situ physics series where one exists.

The value keeps the provider's footprint. This is forbidden:

```text
NOAA DHW in the pixel = 4.2
        → Spot A DHW = 4.2
```

The pixel may be attached to the spot only through an explicit spatial relation, and the reading must still say the number is the pixel's, at the pixel's scale. NOAA Bleaching Alert Area stays external evidence. It is not a BALIZA alert.

### DERIVED INDICATOR

A metric BALIZA computes from available inputs, with a definition, a formula or rule, the inputs, a version, provenance, uncertainty, and a temporal scope. Candidates that do not need a new scientific threshold:

- whether each input a published indicator declares required is present or absent;
- the clocks of the newest measurement and the newest external product;
- a completeness label from the categories below, once a later domain note sets the cutoffs per source.

A local thermal-stress index is not adopted. CRW HotSpot and DHW stay external. A BALIZA trend formula is not adopted. The NOAA 7-day trend, when used, stays an external indicator.

No derived indicator may fill a missing local temperature, depth, or turbidity by copying another product.

### ESTIMATED

A value from an authorised method, later: the number, model version, uncertainty, applicability domain, training provenance, and validation provenance.

No such method is authorised. The slot is **NONE**. Silent interpolation, nearest-pixel assignment, and a model estimate presented as a measurement are forbidden. Abstention is the reading, not a fabricated local value. It is not zero risk.

### STATE

A deterministic result of versioned rules over indicators. The path is evidence, then indicators, then rule evaluation, then state. An LLM does not produce the state.

Names such as `NORMAL`, `ELEVATED`, `HIGH`, and `CRITICAL` are illustrations in the conceptual matrix below. They are not adopted states and they have no thresholds. Existing rule outcomes already include `UNKNOWN` and `INSUFFICIENT_DATA`. Those outcomes are not `NOT_TRIGGERED` and they are not low risk. A later scientific state vocabulary has to be a published rule version. This phase does not publish one.

The evaluation must be replayable from the rule version, the inputs, the thresholds stored on that version, the outcome, and the timestamp.

### ALERT

An operational signal from state, rule evaluation, evidence, and uncertainty. It must say what happened, where, when, which rule version fired, which evidence supports it, which uncertainty applies, which data are missing, and which rule version was used. The critical path is unchanged: an alert still requires the existing deterministic evaluation. An LLM cannot create a critical alert beside that path. NOAA's alert layer cannot be copied in as this alert.

### PLAYBOOK OPTION

A catalog entry compatible with the published playbook: `MONITOR`, `VERIFY`, `INTENSIVE_SURVEY`, `MITIGATION_OPTION`. The option is not a decision, not an executed action, and not an LLM recommendation. Entry conditions remain **OPEN**. No option runs because an alert exists.

`DATA COLLECTION` appears in the conceptual matrix as a name for "go and measure". It is not in the current catalog and it is not an automatic campaign.

### DECISION

Only an authorised human actor creates one. The record holds the actor, the DSS snapshot that was shown, the justification, and `decided_at`.

`ACKNOWLEDGED` is not a decision. `AgentRun` is not a decision. A recommendation is not a decision.

## Snapshot

```text
Spot
  + as_of
  + evidence available at as_of
  + indicators
  + state
  + uncertainty
  + alert, if the rules produced one
  + playbook options
```

The same spot, the same `as_of`, the same dataset versions, and the same rule versions reproduce the same reading. A later alert, a later decision, or a later file does not change that snapshot. This is the same immutability rule as the DSS context snapshot. Phase 7.3 does not add a store.

## Time

```text
observation_time     when the measurement was made
processing_time      when the provider or BALIZA produced the value
publication_time     when the value became knowable from the provider
ingestion_time       when BALIZA stored it
as_of_time           the instant of the reading
```

`as_of_time` means everything BALIZA may use to interpret the spot at that instant. A value is inside the snapshot only if it was published at or before `as_of_time`, its valid window is the one being used, and its construction did not use anything that existed only after that instant. Ingestion time does not qualify it.

An observation made at T1, published at T2, and processed at T3 is not evidence available at T1. It can enter a reading only at an `as_of_time` on or after T2, and the reading still shows T1 as the observation time.

## Space

Every piece of evidence keeps its original scale:

```text
GLOBAL, REGIONAL, GRID_CELL, REEF, ZONE, SPOT, STATION, TRANSECT
```

A grid cell does not become a spot. The link, when one is declared, is a `spatial_relation_type`:

```text
DIRECT, CONTAINS, INTERSECTS, NEAREST, AGGREGATED, ASSOCIATED, UNKNOWN
```

`DIRECT` is only for a measurement taken at that spot, station, or transect. A NOAA pixel that contains the spot's coordinate is `CONTAINS` or `INTERSECTS` only after the point-in-pixel rule is written, and the scale label stays `GRID_CELL`. Until that rule is written for a given source, the relation is `UNKNOWN`. `NEAREST` and `AGGREGATED` are not defaults. Using either without a written rule is invented precision.

## Freshness

The reading can carry `data_age`, `freshness`, `last_observation`, and `last_update`. Freshness labels:

```text
NO DATA, STALE DATA, RECENT DATA, CURRENT DATA
```

No age cutoff is set. Cutoffs will be per source and per domain, in a later published definition. Until then the label for a numeric age is **OPEN**, while `NO DATA` may be used when the slot is empty. `NO DATA` is not `CURRENT DATA` and it is not a normal state.

## Completeness

Evidence completeness answers whether the inputs required to interpret the spot are present. Labels:

```text
COMPLETE, PARTIAL, INSUFFICIENT, UNKNOWN
```

The numeric or logical test that separates them is **OPEN**, except for one rule already in force: a missing required input is not success. `NO DATA` is not `NORMAL`, not `NOT_TRIGGERED`, and not low risk. `INSUFFICIENT` and `UNKNOWN` stay visible.

## Uncertainty

The reading shows uncertainty in separate kinds. They are not one risk score.

| Kind | What it is | Present now? |
|------|------------|--------------|
| Measurement | Instrument or survey method | Only when the observation carries it. No new instrument error is invented |
| Source | Known limits of the provider | Yes, as already recorded: 0.05° foundation SST versus colony temperature, Allen accuracy by region, annual turbidity versus a survey day, CRW climatology version |
| Spatial | Error of tying an aggregate grid to the spot | Yes, as the scale plus `spatial_relation_type`. No metre error is invented |
| Temporal | Lag between observation, publication, and `as_of` | Yes, as the clocks. No "close enough in time" rule is adopted |
| Model | Error of an authorised model | No. The estimate slot is NONE, so this kind is absent |
| Evidence insufficiency | Required inputs missing or unusable | Yes, as a gap. It is not a risk score |

Phase 6 types remain qualitative: known, unknown, insufficient, conflicting, suspect. No confidence fraction is added.

## Disagreement

Signals may disagree. Example of the kind of case, not a recorded event: a CRW DHW pixel in an elevated external class, a local sensor the operator calls ordinary, a MERMAID bleaching row, and partial quality. BALIZA does not collapse that into one number.

When the attached signals do not support one story, the reading shows `SIGNAL CONFLICT` together with each signal, its provenance, its uncertainty, its time alignment, and its spatial relation. `SIGNAL CONFLICT` is a situation flag for the reader. It is not a rule outcome, not an alert by itself, and not a resolution. The existing critical path is unchanged: conflicting evidence is shown, not scored away.

## Evidence chain

```text
SOURCE
  → OBSERVATION or EXTERNAL INDICATOR
  → DERIVED INDICATOR
  → RULE EVALUATION
  → EVIDENCE ITEM
  → EVIDENCE PACKAGE
  → ALERT
  → DSS PACKAGE
  → DECISION
  → ACTION
  → OUTCOME
```

An estimated value, when one day authorised, would sit beside the observation as `MODEL_ESTIMATED` and would still pass through evidence. It cannot skip to an alert. Provenance is required at every step. This is the chain from Phases 0–6, with the epistemic labels of this phase written on the values. It is not a new architecture.

## Playbook matrix

Conceptual only. The state names are not adopted. "Low", "medium", and "acceptable" uncertainty are not defined. Nothing in the matrix is an entry condition.

| Illustrated state | Evidence | Uncertainty | Options a later playbook might list |
|-------------------|----------|-------------|--------------------------------------|
| NORMAL | sufficient | low | MONITOR |
| ELEVATED | sufficient | low or medium | MONITOR, VERIFY |
| HIGH | sufficient | called acceptable by a future rule | VERIFY, INTENSIVE SURVEY |
| UNKNOWN | insufficient | high | VERIFY, and DATA COLLECTION only if a later catalog adds it |
| INSUFFICIENT_DATA | insufficient | high | DATA COLLECTION only if a later catalog adds it |

Still undefined, and therefore not operational: which measurements count as sufficient evidence, which uncertainty is low or high, which state names exist, which rule outcome unlocks which option, and what monitoring density a spot needs. `MITIGATION_OPTION` stays a catalog name without an entry condition. Listing options is allowed. Selecting or executing one is not.

The legal chain is:

```text
ALERT → DSS → PLAYBOOK OPTIONS → HUMAN DECISION → ACTION
```

`ALERT → AUTOMATIC ACTION` is forbidden.

## What the person sees

What we know. What we observed. What is external. What we derived. What we do not know. What is uncertain. Which alert exists. Why. Which options are available. Which additional data would reduce uncertainty.

The last item is a list of missing inputs that a published indicator or this reading already marks as required: for example an in-situ temperature at a stated depth, a survey-time turbidity, or a depth method that matches the question. The reason is the gap itself. BALIZA does not rank those gaps into an optimal survey plan. That optimisation is not authorised.

A future view may group the same fields as observed, external, estimated, indicators, uncertainty, alert, playbook options, and human decision. Any number drawn in a mock layout is an illustration, not an observation stored by BALIZA. The estimated panel says that no local model is authorised.

## Agents

A later agent may summarise evidence, explain a conflict, restate indicators, list open questions, draft a briefing, or compare playbook options that the catalog already allows. It may not invent data, invent ground truth, change a threshold, create a critical alert outside the deterministic engine, decide an action, edit a historical snapshot, or hide uncertainty.

## Model readiness

```text
NOT_READY
TARGET_UNDEFINED
GROUND_TRUTH_INSUFFICIENT
VALIDATION_INSUFFICIENT
READY_FOR_DEVELOPMENT
AUTHORIZED_FOR_TRAINING
```

Current value: **NOT_READY**. The blocking reasons that already apply are `TARGET_UNDEFINED`, `GROUND_TRUTH_INSUFFICIENT`, and `VALIDATION_INSUFFICIENT`. `READY_FOR_DEVELOPMENT` and `AUTHORIZED_FOR_TRAINING` are not reached. No training is started.

## Open questions

Left open, without a guess:

- the scientific target and its local ground truth;
- whether Spot and Zone are the same object;
- the spatial relation actually used for each source, and any aggregation;
- temporal aggregation and per-source freshness cutoffs;
- the uncertainty method and the applicability boundary;
- state names and state thresholds;
- alert thresholds beyond the existing deterministic path;
- playbook entry conditions;
- the monitoring density a spot requires;
- how to separate `COMPLETE`, `PARTIAL`, and `INSUFFICIENT` without a cutoff.

## What is resolved

CLOSED:

- The epistemic layers and the ban on mixing them.
- A grid value stays at grid scale until an explicit spatial relation is stored.
- The estimate slot is NONE. No silent interpolation.
- `as_of_time` cannot include a value published later.
- `NO DATA` is not no risk.
- Uncertainty kinds stay separate and are not a risk score.
- Disagreement is shown as `SIGNAL CONFLICT`, not collapsed.
- State comes from a versioned rule evaluation, not from an LLM.
- The evidence chain and the human decision boundary stand. An alert does not execute an action.
- Model readiness is `NOT_READY`.

PARTIAL:

- The logical fields of `SpotIntelligence` are listed. Spot versus Zone is open, and the object is not implemented.
- Scale labels and relation types are defined. The relation on each real pair is `UNKNOWN` until a join rule exists.
- Clocks and `as_of_time` are defined. Per-feature scientific clocks and freshness cutoffs are not.
- Completeness labels exist. The sufficiency test does not.
- Alert contents required for traceability match the existing alert. New alert bands do not.
- The playbook matrix is illustrative. Entry conditions do not exist.

OPEN: target, ground truth, state vocabulary, numeric uncertainty, freshness cutoffs, completeness cutoffs, spatial joins, monitoring density.

NOT AUTHORIZED: local downscaling, XGBoost, Random Forest, RBM, weights, new scientific thresholds, training, resort history as base training, automatic action, LLM-authored critical state.

## Verdict

PHASE 7.3 SPOT INTELLIGENCE & EVIDENCE STATE MODEL DEFINED — ML IMPLEMENTATION NOT AUTHORIZED.

Which indicators that reading may use today, and which formulas are specified, is `docs/40-phase7.4-spot-scientific-baseline.md`. Categorical freshness, completeness, and `SIGNAL_CONFLICT` stay open there. The conflict flag is `UNKNOWN` until a versioned rule defines it. A retrieved CRW cell is not a spot reading (`docs/41-phase7.5-real-scientific-data-acquisition.md`).
