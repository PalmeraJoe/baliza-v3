# 22 — Phase 5 audit

Scope: canonical relations, published indicator immutability, and `UNKNOWN` versus `INSUFFICIENT_DATA`. Code and tests are the evidence. Phase 6 was not started.

## A. Canonical relational source — PASS

`SqlIndicatorRepository`, `SqlRuleRepository`, `SqlEvidenceRepository`, and `SqlAlertRepository` read membership from `indicator_value_observations`, `rule_evaluation_inputs`, `evidence_package_items`, and `alert_evaluations`. `tests/test_phase5.py::test_links_come_from_junction_not_notes` reloads observation ids and package items from a new session.

## B. JSON semantics — PASS

Operational id lists were removed from indicator values, rule evaluations, evidence packages, and alerts. `notes`, `input_snapshot`, thresholds, alert history, the DSS package payload, and the snapshot payload remain JSON. Changing `notes` does not change the observation link.

## C. IndicatorVersion immutability — PASS

`with_formula` raises `PublishedVersionImmutable` when status is not draft. ORM listeners reject update and delete when the previous or current status is published. A second published version can be stored; the first formula stays `max`. PostgreSQL trigger `indicator_versions_published_immutable` is in `0004_phase5` and was not executed (see O).

## D. Indicator reproducibility — PASS

`IndicatorValue.indicator_version_id` is a foreign key to `indicator_versions.id`. The value also stores `indicator_version`, computed time, quality, inputs via the junction, and the version row holds `formula_kind`.

## E. UNKNOWN semantics — PASS

`RuleOutcome.UNKNOWN` is a separate value. Missing input and facet `UNKNOWN` produce `UNKNOWN` with reasons `required_input_absent` and `quality_not_determinable`. Tests assert it is not `NOT_TRIGGERED` and not `INSUFFICIENT_DATA`.

## F. INSUFFICIENT_DATA semantics — PASS

Facet `INSUFFICIENT` yields `insufficient_sample`. `SUSPECT`, `LOW_QUALITY`, and `DELAYED` yield `below_minimum_quality:<facet>`. Tests assert that outcome is not `NOT_TRIGGERED`.

## G. DataQuality mapping — PASS

The mapping in section 3 of `docs/21-phase5-implementation.md` is the code in `evaluate_rule`. No branch assigns `UNKNOWN` or `INSUFFICIENT_DATA` to `NOT_TRIGGERED`.

## H. Evidence semantics — PASS

`run_critical_path` writes a `DATA_QUALITY` fact whose narrative is the evaluation reason when the outcome is `UNKNOWN`, `INSUFFICIENT_DATA`, or `INVALID_INPUT`, and appends that reason to package gaps.

## I. Alert semantics — PASS

An alert is created only for `TRIGGERED`. The missing-data critical-path test expects `alert is None` with outcome `UNKNOWN`. No new uncertainty-alert policy was invented.

## J. Snapshot completeness — PASS

`presented_context_payload` copies alert state, evidence descriptors, thresholds, protocol options, and now `indicator_version` and `input_quality`. Phase 4.1 tests still show acknowledge, narrative edits, and threshold edits do not change the frozen snapshot.

## K. Snapshot hash — PASS

The snapshot hash is the canonical hash of that frozen payload. Outcome recording does not change it (Phase 4.1 test still passes).

## L. Transaction regression — PASS

`evaluate_and_maybe_alert` still requires a unit of work and rolls back evidence, alert, and commit failures on SQLite.

## M. Decision reconstruction — PASS

A new SQLite session still reconstructs the decision from the frozen snapshot without reading the later alert status.

## N. SQL persistence — PASS

SQLite repositories round-trip the chain, including the new alert junction and indicator-version foreign key (`tests/test_phase36.py` evidence chain).

## O. Migration integrity — PENDING

`alembic/versions/0004_phase5.py` backfills junctions, drops the duplicate JSON id columns, adds the version foreign key, and installs the PostgreSQL trigger, with a downgrade that restores the JSON columns. Upgrade and downgrade were not run: PostgreSQL transaction test = pending infrastructure.

## P. End-to-end chain — PASS

Existing critical-path and API tests still run Observation → indicator → evaluation → evidence → alert → package → snapshot → decision → action → outcome.

## Q. Test coverage — PASS

`py -3 -m pytest` with `PYTHONPATH=src`: 62 passed.

## R. Architecture drift — PASS

No Kafka, microservices, event sourcing, service mesh, or LLM on the rule path.

## S. Human-in-the-loop — PASS

Decision still requires an actor. The critical path does not create a decision or an action. `ACKNOWLEDGED` is not `DECIDED`.

## T. AI isolation — PASS

No agent writes `RuleVersion`, `IndicatorVersion`, thresholds, `Decision`, or `Action`.

## Verdict

PHASE 5 VERIFIED
