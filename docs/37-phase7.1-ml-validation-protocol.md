# 37 — Phase 7.1 scientific ML validation protocol

Documentation only. No model is trained. No dataset is downloaded. No threshold, weight, or score is set.

Status:

**PHASE 7.1 SCIENTIFIC ML VALIDATION PROTOCOL RECORDED — MODEL IMPLEMENTATION NOT AUTHORIZED.**

The question this protocol answers is whether a future model can be shown to generalize to locations and periods it has not seen, without leakage. It does not answer which XGBoost score is best.

## Dataset levels

```text
FULL SCIENTIFIC DATASET
        │
        ▼
DEVELOPMENT DATASET          80% of the scientific split, initial design
        ├── TRAIN
        └── VALIDATION / structured CV
        │
        ▼
FINAL HOLDOUT TEST           20% of the scientific split, initial design
```

The 80/20 ratio is an initial design, not a claim that a random 80/20 split is scientifically sufficient. The 20% is isolated by location, spatial dependence, time, transect, station, campaign, duplicates, and provenance. A random row split is forbidden as the scientific split.

Resort historical data are not in the full scientific dataset by default. They have their own calibration set and independent validation set (`docs/36-phase7-scientific-data-integration.md`).

## Final holdout

The final holdout is untouched during feature selection, preprocessing fits, hyperparameter search, model selection, calibration, threshold selection, error analysis that changes the model, and algorithm choice. It is used once, for the final evaluation of a frozen candidate.

If the holdout is used to change any of those choices, it is no longer independent. That run is void as a final test. A new holdout must be declared before another final claim. The spent holdout is not reused under a new name.

## Spatial holdout

Training locations and test locations are disjoint. A site, station, or transect that appears in train does not appear in test when the question is generalization across places.

The grouping unit is not chosen here. Before any training, the hierarchy that the real tables support must be written down, using only levels that exist in the data:

```text
reef, zone, site, station, transect, survey location
```

Different identifiers are not enough. Stations on the same reef or transect, or so close that they share the same water, are one spatial group until a written distance or membership rule says otherwise. A point that falls on several NOAA cells is not assigned to one of them (`docs/44-phase7.6-spatial-association-spot-mapping.md`). The grouping rule is **OPEN** until the dataset exists. Training is not authorised while it is open.

## Temporal validation

Forward or rolling validation, inside the development set:

```text
TRAIN 2010–2016    VALIDATE 2017
TRAIN 2010–2017    VALIDATE 2018
TRAIN 2010–2018    VALIDATE 2019
```

The years are an example of the pattern, not a chosen study period. No feature for a condition at time `t` may use information that existed only after `t`.

Clocks stay separate: `observation_time`, `acquisition_time`, `processing_time`, `publication_time`, `ingestion_time`. Which clock is the scientific one depends on the variable and must be named in the feature table. Ingestion time is never that clock.

Repeated surveys at one station are not independent rows. The split follows the question: generalization across sites, or generalization across time. Mixing those questions in one random split is not a result.

## Three claims, three tests

| Scenario | What it tests | What it does not prove |
|----------|----------------|------------------------|
| A. Same site, later time | Temporal generalization | Spatial generalization |
| B. Unseen site, historical period already in the development era | Spatial generalization | A forecast |
| C. Unseen site and a later period | Both | Success on A or on B |

Passing A does not imply passing B or C. The final holdout must state which of A, B, or C it is. A single mixed holdout is not all three.

## Tuning and cross-validation

Hyperparameters are searched only inside the development set, on train versus structured validation. The final holdout is not in that search. Fitting on train plus final test is forbidden.

Random K-fold is not the default. It is invalid when it places the same reef, station, transect, campaign, or time period on both sides. Candidates to be chosen later from the real structure, not now: group folds, spatial groups, forward temporal folds, blocked folds, and spatial-temporal folds. The chosen technique is **OPEN**.

## Preprocessing and features

Anything that learns from data is fit on train only, then applied to validation and, at the end, to the final holdout: imputation, scaling, normalisation, feature selection, dimensionality reduction, encoding, and other learned transforms. Fitting on the full dataset and then splitting is leakage. If the algorithm does not need scaling, scaling is not added.

Each future feature needs a row:

```text
FEATURE, SOURCE, OBSERVATION TIME, AVAILABLE AT PREDICTION TIME,
TRANSFORMATION, WINDOW, LOOK-AHEAD RISK
```

Derived products that share a parent grid are one lineage, not independent samples. NOAA raw, NOAA processed, and NOAA aggregated from the same product are documented as one family.

## Targets, duplicates, and MERMAID

The XGBoost target stays **OPEN**. Before training it must name the variable, unit, time, spatial scale, observation method, ground truth, and acceptable uncertainty. Local temperature, anomaly, bleaching, and DHW are not assumed. Candidate targets and the reason none is authorised are in `docs/38-phase7.2-scientific-target-and-spot-resolution.md`.

An observed value is not a model estimate. An in-situ observation is kept even when an estimate exists. The model's own output is never ground truth.

MERMAID bleaching, when the project policy allows the row, may be a target, a validation reference, or ground truth. It is not a predictor of the same bleaching event. Repeated projects, sites, transects, surveys, observers, and methods are groups, not independent draws. Privacy, licence, attribution, and per-project availability still apply.

Duplicates that must not cross the split: same observation id, transect, survey, timestamp, coordinate, photograph, source product, or the same export stored twice.

Post-event variables used to predict that event are target leakage.

## Resort data

Resort history is not in base-model training unless a later scientific decision says so.

```text
BASE SCIENTIFIC MODEL
        → RESORT HISTORICAL DATA
        → SITE CALIBRATION
        → INDEPENDENT SITE VALIDATION
```

Calibration rows and independent validation rows are disjoint. A row that calibrated the site model is not evidence that the calibration worked. When volume and structure allow, the resort channel has at least a calibration subset and a validation subset.

A new resort with no history is evaluated with NOAA, EMODnet, Allen, and MERMAID only where those sources actually have an allowed row. Missing local history is a gap in calibration. It is not a fabricated local prediction and it is not zero risk.

## Overfitting, baselines, metrics, shift

Report train, development validation, spatial holdout, temporal holdout, and final test separately. A large drop from train to unseen data is a warning. No universal overfitting cutoff is defined. Interpretation depends on the target, scale, noise, sample size, heterogeneity, and uncertainty.

Before any claim of usefulness, compare with baselines that match the target. Candidates: persistence or climatology, a simple statistical model, a linear model, and an existing scientific product such as the NOAA pixel when the target is local temperature. None is declared best.

Metrics follow the target. For a continuous target, consider MAE, RMSE, bias, the error distribution, and R² only as a complement. Also break results by site, region, season, depth, source, and data quality when those fields exist. One metric is not the decision.

Train and test must be compared as distributions: space, time, environment, source, depth, and habitat. A score inside the training distribution does not transfer outside it. That risk is **out-of-distribution / domain shift**.

A future prediction must say whether it is inside the supported domain or outside it. Silent extrapolation is forbidden when the place is outside the domain, the variable combination was not seen, a required source is missing, or the resolution does not match. The rule that draws that boundary is **OPEN**. No uncertainty number is invented. A later method must be scientifically stated before a prediction interval is shown. Until then the output, if it existed, would be an estimate plus an explicit unknown uncertainty, plus provenance.

## Reproducibility and model card

A future evaluation names: dataset version, source versions, feature-definition version, target-definition version, split definition, random seed when one is used, code version, model version, hyperparameters, training period, validation period, test period, spatial groups, metrics, and uncertainty method. A dataset version already used is not edited in place.

Production is not authorised until a report states objective, target, data, sources, period, spatial coverage, features, preprocessing, split, validation protocol, leakage controls, metrics, uncertainty, limitations, applicability domain, known failure modes, calibration procedure, and validation results. That report does not exist, because the model does not exist.

## Readiness

| Item | State |
|------|--------|
| Target | OPEN |
| Ground truth | OPEN until the target is named |
| Dataset | Specified as a future station × time table, not built |
| Spatial grouping unit | OPEN; the rule that it must be written first is recorded |
| Temporal strategy | Recorded as forward/rolling; years not chosen |
| 80/20 | Recorded as an initial ratio, not as a random split |
| Final holdout | Recorded as sealed |
| Leakage controls | Recorded |
| Preprocessing | Recorded as train-only fits |
| Hyperparameters | Recorded as development-only |
| Metrics | Family recorded; the set depends on the target |
| Baselines | Candidates recorded; none selected |
| Uncertainty method | OPEN |
| Applicability domain | Principle recorded; the boundary rule is OPEN |
| Reproducibility list | Recorded |

Because target, spatial unit, uncertainty method, and applicability boundary remain OPEN, XGBoost is not scientifically ready to train.

## Phase 7.1 validation design audit

| Check | Result |
|-------|--------|
| No ML code, no training, no downloaded training set | Pass. This file is documentation. `src/`, `alembic/`, and `tests/` were not edited. |
| No new threshold, weight, score, RBM, Random Forest, playbook, recommendation, or decision | Pass. |
| Phases 0–6 behaviour unchanged | Pass. The observation-to-outcome chain is not altered. |
| Resort history is not base training | Pass. |
| Spatial holdout defined, unit not invented | Pass as a rule. The unit stays OPEN. |
| Temporal validation defined | Pass as forward/rolling. |
| Final holdout sealed | Pass. |
| Leakage controls defined | Pass, including preprocessing, look-ahead, post-event, duplicates, lineage, and calibration-versus-validation. |

## Verdict

PHASE 7.1 SCIENTIFIC ML VALIDATION PROTOCOL RECORDED — MODEL IMPLEMENTATION NOT AUTHORIZED.
