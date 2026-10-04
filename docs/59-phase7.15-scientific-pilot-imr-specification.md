# 59 — Phase 7.15 Scientific Pilot Preparation / IMR

**Specification for a real meeting with IMR.** Documentation only.

No IMR connector, importer, credentials, tables, migrations, ML, downscaling,
local estimation, calibration, or new scientific thresholds are implemented in
this phase.

Machine-readable twin: `src/baliza/application/phase715_scientific_pilot.py` and
`data/phase715/scientific-pilot-imr-specification.json`.

Priority vocabulary used throughout:

| Label | Meaning |
|-------|---------|
| **REQUIRED** | Needed to run a scientifically honest local pilot |
| **STRONGLY PREFERRED** | Strongly improves validation quality |
| **OPTIONAL** | Useful if available; absence is a documented gap |
| **UNKNOWN / TO CONFIRM** | Must be confirmed with IMR; not assumed |

**Critical rule:** Do not convert assumptions about IMR into scientific
requirements. Everything not confirmed remains `UNKNOWN / TO CONFIRM`.

---

## 1. Pilot objective

> Validate scientifically whether BALIZA can reproducibly associate public
> environmental information with **local** observations and produce a
> **traceable, useful DSS** for a real reef-management setting.

**Not** the initial objective:

> Train a predictive model.

Local prediction is a **possible later phase**, only if the ML Authorization Gate
is passed.

---

## 2. Scientific questions

| ID | Question |
|----|----------|
| **Q1** Spatial association | Can BALIZA correctly associate regional/pixel indicators with local Spots? |
| **Q2** Temporal association | Can BALIZA associate environmental indicators with local observations given datetime, depth, and temporal window semantics? |
| **Q3** Local observation | Are local observations precise enough to characterize the real system state? |
| **Q4** Quality | Can we quantify quality and uncertainties of those observations? |
| **Q5** Evidence chain | Can BALIZA preserve a reproducible chain: source → observation → association → indicator → evidence → alert → DSS? |
| **Q6** Operational usefulness | Does the DSS help a responsible person interpret the situation and choose among options? |
| **Q7** Future prediction *(posterior only)* | Is there enough **independent** ground truth to justify local estimation/prediction? |

Do **not** assume Q7 will be yes.

---

## 3. Minimum Pilot Data Package

### A. REQUIRED — Spatial identity

For each station / spot / transect:

| Field | Priority |
|-------|----------|
| site_id | REQUIRED |
| station_id / spot_id | REQUIRED |
| latitude | REQUIRED |
| longitude | REQUIRED |
| CRS | REQUIRED (for scientific use) |
| geometry type | REQUIRED |
| site / reef / zone relationship | STRONGLY PREFERRED |
| reef_id / zone_id / transect_id | STRONGLY PREFERRED if they exist |

A coordinate **without** a known CRS is not acceptable for scientific spatial
association (record as gap; do not invent CRS).

### B. REQUIRED — Time

For each observation:

| Field | Priority |
|-------|----------|
| observation_datetime | REQUIRED |
| timezone / UTC semantics | REQUIRED |
| sampling date / period | STRONGLY PREFERRED |

Keep distinct (never silently substitute):

```text
observation time
processing time
publication time
ingestion time
```

### C. REQUIRED — Local temperature (if any temperature series exist)

| Field | Priority |
|-------|----------|
| temperature_value | REQUIRED |
| temperature_unit | REQUIRED |
| sensor_id | STRONGLY PREFERRED |
| sensor_type | STRONGLY PREFERRED |
| depth | STRONGLY PREFERRED |
| measurement_datetime | REQUIRED |
| sampling interval | STRONGLY PREFERRED |
| sensor location | STRONGLY PREFERRED |
| calibration information | STRONGLY PREFERRED |
| quality flags | STRONGLY PREFERRED |

Also confirm (`UNKNOWN / TO CONFIRM` until answered):

```text
continuous / discrete
raw / processed
logger frequency
missing-data policy
known sensor failures
```

Local temperature is the strongest **candidate** thermal ground truth — not
automatically adopted.

### D. REQUIRED — Sensor metadata (if sensors exist)

| Field | Priority |
|-------|----------|
| manufacturer / model | STRONGLY PREFERRED |
| accuracy / resolution | STRONGLY PREFERRED |
| calibration date / method | STRONGLY PREFERRED |
| deployment / retrieval period | STRONGLY PREFERRED |
| maintenance / known drift | OPTIONAL |

If IMR cannot provide uncertainty: record `UNKNOWN`. Do not invent it.

### E. Ecological observations

Ask which of these exist (`UNKNOWN / TO CONFIRM` per variable):

```text
coral bleaching
bleaching severity
recent mortality
live coral cover
benthic composition
macroalgae
fish
disease
recruitment
habitat complexity
other
```

Do **not** assume IMR has all of them.

For each confirmed variable:

| Field | Priority |
|-------|----------|
| variable, unit, method | REQUIRED |
| observation protocol | REQUIRED |
| sampling unit | REQUIRED |
| observer / instrument | STRONGLY PREFERRED |
| date, depth, location | REQUIRED |
| quality, uncertainty | STRONGLY PREFERRED |

### F. Bleaching definition (if bleaching data exist)

Document exactly (`TO CONFIRM`):

```text
what constitutes bleaching
categories
percentage definition
colony-level vs transect-level
visual vs instrumental
recently dead definition
observation protocol
observer training
```

Rules:

- Do not convert qualitative categories into arbitrary percentages.
- Do not convert `recently_dead` into `mortality_percent`.

### G. Depth

For relevant observations:

| Field | Priority |
|-------|----------|
| depth_value | STRONGLY PREFERRED / REQUIRED for thermal GT use |
| depth_unit | REQUIRED when depth present |
| depth_reference | REQUIRED when depth present |

Confirm whether depth is sensor / transect / reef / approximate / surface.
Do not assume equivalence across protocols.

### H. Methodology

Confirm (`TO CONFIRM`):

```text
Who collected it?
How?
With what instrument?
Under which protocol?
How often?
At what spatial scale?
At what temporal scale?
```

Methodology is part of the evidence.

### I. Historical coverage

| Field | Priority |
|-------|----------|
| earliest / latest observation | REQUIRED |
| continuous periods / gaps | STRONGLY PREFERRED |
| seasonality | OPTIONAL |
| number of sites / observations | STRONGLY PREFERRED |

“Years of data” ≠ continuous coverage.

### J. Data quality

Ask for (`TO CONFIRM`):

```text
quality flags, validation flags, sensor QA/QC
manual review, outlier treatment, missing values
duplicate handling, reprocessing history
```

BALIZA must preserve **original** raw data. Do not overwrite raw with cleaned
versions.

---

## 4. Data access & governance

### Access mechanism (`TO CONFIRM`)

```text
API? CSV? Excel? NetCDF? GeoJSON?
database export? cloud/object storage? manual export?
authentication, access restrictions
license, research-only / commercial-use restrictions
retention requirements, citation requirements
```

**Do not implement any access until these are known.**

### Governance questions (`TO CONFIRM`)

```text
Who owns the data?
Who may access it?
Can BALIZA store it?
Can BALIZA transform it?
Can BALIZA derive indicators?
Can BALIZA use it for validation?
Can BALIZA use it for calibration?
Can BALIZA use it for ML training?
Can derived data leave the institution?
Can results be shown to third parties?
```

```text
CALIBRATION ≠ INDEPENDENT VALIDATION
```

A row used for calibration **must not** later be reused as independent
validation of the same fit.

---

## 5. Scientific holdout

Discuss from the start (choice `TO CONFIRM` after inventory):

```text
SPATIAL HOLDOUT
TEMPORAL HOLDOUT
SITE HOLDOUT
SENSOR HOLDOUT
```

Ask IMR which data structure allows real independent validation. Do not fix the
unit arbitrarily.

---

## 6. Candidate targets (not adopted)

From Phase 7.7 — remain **CANDIDATE / NOT ADOPTED** until compatible data exist:

| ID | Target |
|----|--------|
| A | Local absolute water temperature |
| B | Local thermal anomaly |
| C | Local–regional thermal residual |
| D | Ecological response / bleaching |

None are implemented here.

---

## 7. ML Authorization Gate

`ML = NOT_AUTHORIZED` unless **all** are demonstrated:

```text
target defined
ground truth available
spatial resolution defined
temporal resolution defined
independent validation available
leakage controls defined
applicability domain defined
uncertainty methodology defined
data governance permits modeling
scientific partner approval
```

If any critical element is missing: keep `ML = NOT_AUTHORIZED`.

---

## 8. Pilot success criteria (not ML metrics)

| ID | Criterion |
|----|-----------|
| **S1** Data | Local data accessible and reproducible |
| **S2** Spatial | Spatial association reproducible |
| **S3** Temporal | Temporal association reproducible |
| **S4** Evidence | Evidence Chain complete enough to audit |
| **S5** DSS | Interpretable DSS context produced |
| **S6** Human usefulness | A responsible human can use it for a documented decision |

---

## 9. Failure / blocking conditions

Do **not** advance to modeling if:

```text
No reliable coordinates
No reliable timestamps
Unknown observation methodology
No usable local observations
No independent validation
Unclear data rights
Severe spatial mismatch
Severe temporal mismatch
Unquantifiable uncertainty
Data leakage risk
```

Interpretation:

```text
MODEL / VALIDATION NOT READY
```

The **DSS product** may still continue on public data.

---

## 10. IMR meeting checklist

```text
[ ] Data owner identified
[ ] Access mechanism identified
[ ] Data license identified
[ ] Coordinates confirmed
[ ] CRS confirmed
[ ] Time semantics confirmed
[ ] Temperature data confirmed
[ ] Sensor metadata confirmed
[ ] Ecological observations confirmed
[ ] Bleaching protocol confirmed
[ ] Depth confirmed
[ ] QA/QC confirmed
[ ] Historical period confirmed
[ ] Missing-data policy confirmed
[ ] Spatial holdout discussed
[ ] Temporal holdout discussed
[ ] Validation protocol discussed
[ ] Calibration policy discussed
[ ] ML rights discussed
[ ] Commercial-use rights discussed
[ ] Pilot success criteria agreed
```

---

## 11. Conceptual data contract — DO NOT IMPLEMENT

Proposed future shape only (`TO CONFIRM` every field):

```text
IMRObservation
├── source
├── dataset
├── record_id
├── site_id
├── geometry
├── crs
├── observed_at
├── variable
├── value
├── unit
├── depth
├── method
├── instrument
├── quality
├── uncertainty
├── provenance
└── access_policy
```

**Not** created as domain code, tables, or migrations in Phase 7.15.

**Not** created: `src/baliza/infrastructure/sources/imr/`.

---

## 12. Pilot capability matrix

| Capability | Public data | IMR required | Validation role | ML role |
|------------|-------------|--------------|-----------------|---------|
| SST | CRW | optional | contextual | possible feature* |
| SST anomaly | CRW | optional | contextual | possible feature* |
| HotSpot | CRW | optional | contextual | possible feature* |
| DHW | CRW | optional | contextual | possible feature* |
| Local temperature | limited | REQUIRED if available | candidate ground truth | candidate target |
| Bleaching | MERMAID / IMR | REQUIRED for local ecological validation | ecological validation | candidate target |
| Reef habitat | Allen | optional | spatial context | possible feature* |
| Local protocols | public/none | REQUIRED | operational validation | N/A |

\* “Possible feature” is **not** ML authorization.

---

## 13. BALIZA / IMR boundary — PROPOSED / TO CONFIRM

```text
BALIZA provides (proposed):
- data integration, provenance, evidence
- indicators, alerts, DSS, options
- human decision recording

IMR provides / validates (proposed):
- local observations, scientific protocols
- sensor information, ecological observations
- validation knowledge, pilot feedback
```

Do not claim this split is agreed until IMR confirms it.

---

## 14. IMR is not automatic ground truth

> IMR data will **not** automatically be treated as ground truth. Each dataset
> must be evaluated according to its measurement method, spatial/temporal
> semantics, uncertainty, and intended validation role.

An IMR observation may be classified as:

```text
MEASURED | VALIDATION | CALIBRATION | CONTEXT
```

depending on how it was acquired — not by institutional label alone.

---

## 15. Pilot architecture

```text
NOAA CRW
Allen Coral Atlas
MERMAID
        ↓
PUBLIC DATA FABRIC
        ↓
              IMR   ← TO CONFIRM (access + semantics)
               ↓
        LOCAL DATA FABRIC
               ↓
     SPATIAL / TEMPORAL ASSOCIATION
               ↓
        SPOT INTELLIGENCE
               ↓
             EVIDENCE
               ↓
          BALIZA DSS
               ↓
       HUMAN DECISION
```

Only later, if the gate passes:

```text
Validated local observations
          ↓
Target definition
          ↓
Model readiness gate
          ↓
ML
```

---

## 16. Possible next states after IMR answers

| State | Meaning |
|-------|---------|
| **A** | IMR data sufficient → design adapter |
| **B** | Partially sufficient → limited scientific pilot |
| **C** | Insufficient for ML → continue DSS validation without ML |
| **D** | Enough for validation, not prediction → validate DSS; keep ML blocked |
| **E** | Defined target + independent validation → prepare ML authorization review |

**Do not assume A.**

---

## 17. Explicit non-goals (this phase)

- No IMR connector / importer / credentials / endpoints / tables
- No ML / XGBoost / downscaling / local estimation
- No new scientific RuleVersion thresholds
- No invented IMR formats, sensors, coordinates, or frequencies

---

## 18. Status

```text
PHASE 7.15 SCIENTIFIC PILOT PREPARATION / IMR — SPECIFICATION COMPLETE
IMR CONNECTOR: NOT_IMPLEMENTED
ML: NOT_AUTHORIZED
LOCAL ESTIMATION: NOT_AUTHORIZED
DOWNSCALING: NOT_AUTHORIZED
```

Next engineering step depends on **real answers from IMR**, not on this document alone.
