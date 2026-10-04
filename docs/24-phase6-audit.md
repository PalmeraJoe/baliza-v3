# 24 — Phase 6 audit

Evidence is the code in `src/baliza/domain/situation.py`, the freeze path in `dss.py`, and `tests/test_phase6.py`. Phase 7 was not started.

## A. Scientific context — PASS

`SignalReading` carries indicator version, value, rule, rule version, thresholds from the evaluation, outcome, and quality. `tests/test_phase6.py::test_triggered_reading_keeps_version_threshold_and_clocks`.

## B. Operational context — PASS

Alert status, severity, and scope health are attached only when an alert exists. The reading's `decision` field is null. Acknowledge remains a separate use case.

## C. Evidence synthesis — PASS

Primary and derived items are supports. `data_quality` items are limits. Conflicts are listed as contradictory. The evidence route returns that split.

## D. DataGap semantics — PASS

Gaps are derived from rule reasons and package gap text. They are not alerts. `not_triggered` is excluded. Unknown input becomes `missing_observation`, not `NOT_TRIGGERED`.

## E. Uncertainty semantics — PASS

Types are `known`, `unknown`, `insufficient`, `conflicting`, and `suspect`. No confidence float is written by `interpret_situation`.

## F. Protocol semantics — PASS

`Protocol` and `ProtocolVersion` stay distinct from rules and from decisions. Published versions reject option edits in the domain. SQL catalog persistence is not in this phase (open question 38); the snapshot stores the option text that was shown.

## G. Option semantics — PASS

`ProtocolOption` keeps description, preconditions, and constraints supplied by the caller. The test option is not executed: the action repository stays unused until a human decision exists.

## H. Recommendation semantics — PASS

Recommendations use epistemic label `RECOMMENDATION`. `recommendation.presented` is an audit event. `is_decision` on the API option payload is false.

## I. DSS Package — PASS

The live package still collects multiple alerts, evidence ids, evaluations, gaps, and recommendations, and remains mutable after open.

## J. Snapshot — PASS

Freeze copies gaps, uncertainty, signal readings, and evidence synthesis in addition to the Phase 4.1 fields. The hash is the canonical hash of that payload.

## K. Historical reconstruction — PASS

After freeze, acknowledging the stored alert, replacing an evidence narrative, and editing live recommendation text leave the snapshot hash unchanged. Outcome recording leaves it unchanged.

## L. Multi-alert context — PASS

Two triggered alerts produce two signal readings and two alert ids on one snapshot, then one decision.

## M. Temporal context — PASS

The reading keeps `observed_at`, `evaluated_at`, and `alerted_at` as separate fields. `decided_at` remains on the decision.

## N. Spatial compatibility — PASS

`spatial_ref` is copied from the alert or the observation when present. Entity, Zone, and Station are not collapsed and no GIS model was added.

## O. API architecture — PASS

New routes call `alert_situation` and `package_situation`. They do not import SQLAlchemy.

## P. Auditability — PASS

Package open, recommendation presented, snapshot frozen, and decision recorded are audit events. They are `AuditEvent` records, not logs.

## Q. Failure states — PASS

Unknown, insufficient, and conflicting inputs produce a reading with `decision` null. Existing `ScopeHealth` values are reused. `CONFLICTING_EVIDENCE` was not added to that enum.

## R. Human-in-the-loop — PASS

Decision still requires an actor, a snapshot, and a justification. The situation reading does not create one.

## S. AI isolation — PASS

`ai_used` is false on the new routes. No agent writes rules, thresholds, indicator versions, decisions, or actions.

## T. Persistence — PASS

New fields are inside the existing DSS package payload and snapshot payload. Junction tables from Phase 5 are unchanged. SQLite end-to-end tests from Phase 4 still pass.

## U. Migration integrity — PASS

No schema change. Alembic was not given an empty revision. PostgreSQL transaction test = pending infrastructure remains the Phase 4.1/5 limit for triggers, not a new Phase 6 schema gap.

## V. Test coverage — PASS

`py -3 -m pytest` with `PYTHONPATH=src`: 68 passed, including `tests/test_phase6.py`.

## W. Architecture drift — PASS

Modular monolith, application ports, PostgreSQL as the system of record. No Kafka, microservices, event sourcing, or LLM on the rule path.

## X. Scientific integrity — PASS

No new scientific threshold, score, or species parameter. Demo numbers stay labeled `DEMO / NON-SCIENTIFIC`.

## Verdict

PHASE 6 VERIFIED
