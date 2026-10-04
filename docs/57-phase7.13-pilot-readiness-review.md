# 57 — Phase 7.13 Pilot Readiness Review

Documentation and assessment only. No ML, IMR connector, downscaling, local
estimation, or new scientific thresholds. Machine-readable twin:
`src/baliza/application/phase713_pilot_readiness.py` and
`data/phase713/pilot-readiness-assessment.json`.

---

## 1. Executive Summary

BALIZA can already operate as a **reproducible Decision Support System** on
**public scientific evidence**, with human decision in the loop and explicit
data gaps. It is **not** ready to train or deploy a local predictive bleaching
or temperature model.

| Question | Answer |
|----------|--------|
| Ready to talk to a scientific partner without pretending local validation or a predictive model exists? | **YES** |
| Product / DSS foundation | **READY WITH LIMITATIONS** |
| Scientific pilot | **CONDITIONAL GO** |
| Local prediction / ML | **NO-GO / NOT_AUTHORIZED** |
| IMR for current product foundation | **NONE** |
| IMR for scientific validation phase | **REQUIRED** |

```text
IMPLEMENTED ≠ TESTED ≠ SCIENTIFICALLY_VALIDATED
```

Phase 7.12 proved the DSS path with DEMO / NON-SCIENTIFIC thresholds. That is
product readiness evidence, not scientific model readiness.

---

## 2. Current Product Readiness

**Question:** Can BALIZA function as a DSS reproducibly?

**Answer:** `YES — WITH SCIENTIFIC DATA LIMITATIONS`

| Capability | Classification | Notes |
|------------|----------------|-------|
| Spot | READY_WITH_LIMITATIONS | DEMO heritage point; CRS UNKNOWN |
| Spot Intelligence | READY_WITH_LIMITATIONS | CRW + Allen + MERMAID integrated; gaps explicit |
| Evidence Chain | READY_WITH_LIMITATIONS | Traceable; completeness PARTIAL |
| Data Quality | READY_WITH_LIMITATIONS | Facets exist; many source qualities UNKNOWN |
| Indicators | READY_WITH_LIMITATIONS | Passthrough / formulas exist; DEMO labels in E2E |
| Rules | READY_WITH_LIMITATIONS | Deterministic engine; DEMO thresholds in E2E |
| Alerts | READY | Alert ≠ Decision; ACKNOWLEDGED ≠ Decision |
| DSS Package | READY | Options as RECOMMENDATION |
| Snapshot | READY | Immutable freeze tested |
| Protocol Options | READY_WITH_LIMITATIONS | Catalog present; entry conditions OPEN |
| Human Decision | READY | Requires Actor + Snapshot + justification |
| Action | READY | Requires Decision |
| Outcome | READY | Bound to Action + Decision |
| Audit | READY | Critical events recorded |

---

## 3. Current Scientific Readiness

### Scientific DSS readiness

BALIZA can present public evidence honestly (EXTERNAL_INDICATOR vs CONTEXT_ONLY
vs MEASURED ecological when compatible), including MERMAID
`DATA EXISTS BUT NO COMPATIBLE MATCH` without collapsing it to “healthy”.

**Verdict:** `READY_WITH_LIMITATIONS`

### Scientific model readiness

**Question:** Enough evidence to train and validate a local predictive model?

**Answer:** `NO`

| Item | Status |
|------|--------|
| THERMAL_GROUND_TRUTH | NOT_AVAILABLE |
| LOCAL_TARGET | OPEN (Phase 7.7) |
| SPATIAL_VALIDATION | OPEN |
| TEMPORAL_VALIDATION | OPEN |
| APPLICABILITY_DOMAIN | PARTIAL / UNKNOWN_DOMAIN |
| UNCERTAINTY | PARTIAL |

This is **not** a product failure.

---

## 4. Current ML Readiness

| Capability | Classification |
|------------|----------------|
| AI analysis | NOT_AUTHORIZED |
| Model training | NOT_AUTHORIZED |
| Model validation | NOT_AUTHORIZED |
| Local estimation | NOT_AUTHORIZED |
| Downscaling | NOT_AUTHORIZED |
| Predictive risk | NOT_AUTHORIZED |

`ML_AUTHORIZATION_GATE = NOT_PASSED`

---

## 5. Public Data Capabilities

| Source | Product status | Scientific use now |
|--------|----------------|--------------------|
| NOAA CRW | REAL DATA AVAILABLE (PARTIAL association) | EXTERNAL_INDICATOR thermal |
| Allen Coral Atlas | PARTIAL | CONTEXT_ONLY; DEMO coverage NOT_AVAILABLE |
| MERMAID | PARTIAL access | Field ecology when compatible; DEMO = no match |

Provenance, quality, freshness, uncertainty remain **PARTIAL** where sources do
not supply them. They are **not** artificially closed here.

---

## 6. Known Scientific Limitations

- CRW production spatial association UNKNOWN (CRS)
- One of four candidate cells retrieved for DEMO
- Allen feature geometry null; DEMO outside stored bbox
- MERMAID observation-level / sites access blocked; no DEMO match
- Thermal ground truth NOT_AVAILABLE
- DEMO thresholds are not scientifically validated
- Freshness cutoffs not authorized
- No local depth / station series in product foundation

---

## 7. Minimum Pilot Data Package

Only fields needed to answer pilot questions. Classify:

### Local environmental measurements

| Field | Priority |
|-------|----------|
| timestamp (aware) | REQUIRED |
| latitude, longitude | REQUIRED |
| CRS / CRS statement | STRONGLY_PREFERRED |
| depth + unit + method | STRONGLY_PREFERRED |
| temperature + unit | REQUIRED (for thermal GT line) |
| sensor_id / instrument | STRONGLY_PREFERRED |
| sampling_method | STRONGLY_PREFERRED |
| quality_flag | STRONGLY_PREFERRED |
| uncertainty / notes | OPTIONAL |
| measurement metadata | OPTIONAL |

### Ecological observations (when available)

| Field | Priority |
|-------|----------|
| survey_date | REQUIRED |
| location / coordinates | REQUIRED |
| depth | STRONGLY_PREFERRED |
| transect / station id | STRONGLY_PREFERRED |
| bleaching categories (original) | STRONGLY_PREFERRED |
| recently_dead (as category, not mortality %) | OPTIONAL |
| benthic cover / method | OPTIONAL |
| survey_method / protocol | REQUIRED |
| observer metadata (if permitted) | OPTIONAL |
| quality metadata | STRONGLY_PREFERRED |

### Spatial context

| Field | Priority |
|-------|----------|
| reef / zone / station identifiers | STRONGLY_PREFERRED |
| geometry | OPTIONAL |
| CRS | STRONGLY_PREFERRED |

### Operational context

| Field | Priority |
|-------|----------|
| campaign / protocol name | STRONGLY_PREFERRED |
| sampling frequency | OPTIONAL |
| known events (documented) | OPTIONAL |

Do **not** demand datasets the partner cannot share. Absence remains a documented gap.

---

## 8. Scientific Pilot Questions

The pilot should prove usefulness of `BALIZA + partner data`, not that BALIZA
already predicts bleaching.

| Line | Question |
|------|----------|
| A. Data integration | Can BALIZA ingest partner local data with provenance? |
| B. Spatial association | Can station / reef / transect / sensor / survey link to the correct Spot without silent nearest-pixel promotion? |
| C. Temporal association | Are measurement, survey, satellite, processing, and retrieval times kept distinct? |
| D. Thermal validation | How do local temperatures compare to CRW under an agreed protocol (not assumed equality)? |
| E. Ecological response | Is there an interpretable spatial–temporal relationship between thermal stress and ecological observations (no assumed causality)? |
| F. DSS usefulness | Does the package help detect situations, gaps, priorities, conflicting evidence, uncertainty, and human options? |

---

## 9. Ground Truth Requirements

Do **not** fix the final ML target yet.

### Thermal ground truth

Candidate: **in-situ temperature**, only if location, time, depth (where method requires), unit, method, quality, and usable uncertainty/metadata exist.

### Ecological ground truth

Candidates: bleaching observation, benthic survey, recent mortality **as defined by the partner protocol**.

Do **not** convert ecological labels into temperature labels.

```text
THERMAL GROUND TRUTH  ≠  ECOLOGICAL GROUND TRUTH
```

---

## 10. Calibration vs Independent Validation

```text
CALIBRATION ≠ INDEPENDENT VALIDATION
```

| Role | May be used for |
|------|-----------------|
| Calibration | parameter adjustment, configuration selection, site calibration |
| Independent validation | final evaluation only |

A single row **must not** serve both. Resort / partner history used for site
calibration must not later be labeled independent validation of the same fit
(Phase 7.7).

---

## 11. Spatial Validation Strategy

Principle only — unit not fixed without partner structure.

Possible blocking units (choose after data inventory): reef, station group,
island, site, region.

No random row split as the primary scientific holdout.

---

## 12. Temporal Validation Strategy

```text
TRAIN / DEVELOPMENT PERIOD
        ↓
TEMPORAL GAP IF REQUIRED
        ↓
SEALED FUTURE PERIOD
```

The sealed period must not be used for feature selection, threshold tuning,
calibration, hyperparameter search, or pre-test error analysis.

Concrete dates: **TBD after partner data inventory**.

---

## 13. Leakage Controls (checklist)

- [ ] Future information
- [ ] Duplicate observations
- [ ] Derived products used as pseudo-labels of themselves
- [ ] Same-event ecological labels as temperature targets
- [ ] Spatial duplicates across train/test
- [ ] Temporal duplicates across train/test
- [ ] Calibration / test contamination
- [ ] Preprocessing leakage
- [ ] Threshold tuning leakage
- [ ] Feature engineering leakage

---

## 14. Applicability Domain

Pilot must label new cases:

```text
IN_DOMAIN | OUT_OF_DOMAIN | UNKNOWN
```

No local prediction if OUT_OF_DOMAIN or UNKNOWN without an explicit abstention
policy (`ESTIMATED = NONE`).

---

## 15. Uncertainty Requirements

Keep separate:

- measurement uncertainty  
- spatial uncertainty  
- temporal uncertainty  
- association uncertainty  
- model uncertainty  

Quantify only what the pilot can support; otherwise remain `UNKNOWN`. Do not
invent scores.

---

## 16. Pilot Success Criteria

### Product

- **P1** Public scientific evidence ingested correctly  
- **P2** Local partner data associated correctly  
- **P3** Provenance preserved  
- **P4** Evidence chain reconstructable  
- **P5** DSS snapshot reproducible  
- **P6** Human decision traceable  

### Scientific

- **S1** Spatial association validated under agreed protocol  
- **S2** Temporal association validated  
- **S3** Local thermal comparison protocol validated  
- **S4** Ecological observation semantics validated  
- **S5** Uncertainty characterization completed  
- **S6** Applicability domain characterized  

### Operational

- **O1** Scientist understands why an alert exists  
- **O2** Scientist can identify missing data  
- **O3** Scientist distinguishes FACT / INFERENCE / RECOMMENDATION / DECISION  
- **O4** Scientist can evaluate options  
- **O5** Decision process remains human-controlled  

No numerical ML performance targets until methodology and partner agreement exist.

---

## 17. IMR Questions (`IMR PILOT QUESTIONS`)

1. Which stations / zones / reefs can participate?  
2. Which temperature series exist?  
3. What depths?  
4. What temporal frequency?  
5. Which sensors / instruments?  
6. What quality and calibration practices?  
7. Which ecological observations exist?  
8. Which bleaching protocols?  
9. What CRS / geometry metadata?  
10. What historical span can be shared?  
11. Access / licence restrictions?  
12. What may be used for calibration?  
13. What must be reserved for independent validation?  
14. What future period could be sealed as test?  
15. Which variables are scientifically relevant?  
16. What constitutes a useful alert?  
17. Which operational decisions should BALIZA support?  
18. Which outputs must BALIZA **not** produce?  

Framing: **scientific validation and joint study of whether prediction can later
be justified** — not “please give us training data for BALIZA”.

---

## 18. ML Authorization Gate

```text
ML_AUTHORIZATION_GATE = NOT_PASSED
```

Required closures before authorization:

TARGET_DEFINITION, GROUND_TRUTH, SPATIAL_RESOLUTION, TEMPORAL_RESOLUTION,
SPATIAL_VALIDATION, TEMPORAL_VALIDATION, LEAKAGE_CONTROL, APPLICABILITY_DOMAIN,
UNCERTAINTY, INDEPENDENT_TEST_SET, SCIENTIFIC_PARTNER_APPROVAL.

No authorization is granted in this phase.

---

## 19. Scientific Pilot Scope

Prefer:

```text
1–2 locations
+ limited spots / stations
+ defined historical period
+ defined observation protocols
```

Avoid whole-region / all-datasets / all-variables first passes. Exact counts:
**TBD with partner**.

---

## 20. Commercial Pilot Boundary

```text
SCIENTIFIC PILOT ≠ COMMERCIAL PILOT
```

| Scientific pilot | Commercial pilot |
|------------------|------------------|
| validation, compatibility, uncertainty, ground truth, workflow | operational usefulness, UX, SLA, pricing, multi-tenant deploy |

BALIZA is **not** commercially validated. Future commercial questions (not in
7.13): user, SLA, deployment, pricing, support, data contracts, security,
multi-tenancy, integration, operational ownership.

---

## 21. Explicit Non-Goals (this phase)

- No ML / XGBoost / downscaling / local estimation  
- No `src/baliza/infrastructure/sources/imr/`  
- No new scientific RuleVersion thresholds  
- No artificial closure of PARTIAL fields  
- No training on resort data  
- No autonomous decisions or actions  

---

## 22. Go / Conditional Go / No-Go Assessment

| Track | Verdict |
|-------|---------|
| PRODUCT PILOT | **GO** |
| SCIENTIFIC VALIDATION / SCIENTIFIC PILOT | **CONDITIONAL GO** |
| ML / LOCAL PREDICTION | **NO-GO / NOT_AUTHORIZED** |
| COMMERCIAL PILOT | **NOT_READY** |

**Why:** Phase 7.12 shows a working DSS on public data with human control.
Scientific validation needs partner data, agreed GT, association protocols, and
holdouts. Local prediction still lacks thermal GT, resolved target, and
validation design (Phase 7.7).

```text
BALIZA PRODUCT/DSS: READY (with scientific data limitations)
SCIENTIFIC PILOT: READY WITH CONDITIONS
LOCAL PREDICTION: NOT_READY
ML: NOT_AUTHORIZED
IMR: REQUIRED FOR SCIENTIFIC VALIDATION PHASE,
     NOT REQUIRED FOR CURRENT PRODUCT FOUNDATION
```

---

## Sequence after this review

```text
BALIZA FOUNDATION
        ↓
PUBLIC SCIENTIFIC DATA
        ↓
END-TO-END DSS
        ↓
PILOT READINESS REVIEW          ← this phase
        ↓
SCIENTIFIC PILOT — IMR
        ↓
SCIENTIFIC VALIDATION
        ↓
ML AUTHORIZATION GATE
        ↓
[ONLY IF PASSED]
PREDICTIVE MODEL
        ↓
COMMERCIAL PILOT
```

Do not place ML before the scientific pilot.
