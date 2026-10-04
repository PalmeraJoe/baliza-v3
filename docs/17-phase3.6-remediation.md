# 17 — Phase 3.6 Remediation & Re-Audit

## Result

**PHASE 3 VERIFIED**

Phase 4 has not been started.

The Phase 3.5 findings in `docs/16-phase3-audit.md` are corrected in domain code, application use cases, SQLAlchemy listeners, Alembic `0002_phase36`, and tests. Verification is from inspection of those paths, not from a green test count alone.

## Original issues

| Issue | Disposition |
| --- | --- |
| HIGH snapshot nested mutation | **FIXED.** `freeze_value` deep-copies into read-only mappings, tuples, and frozensets before `content_hash`. |
| HIGH snapshot UPDATE/DELETE | **FIXED** for the ORM on every backend, and for raw SQL on PostgreSQL via trigger. SQLite tests do not run that trigger. |
| MEDIUM evidence chain FKs | **FIXED.** `alerts.evidence_package_id` is NOT NULL. Junction tables link observations, indicator inputs, and package items. JSON id lists remain a denormalized copy, not the only link. |
| MEDIUM RuleVersion constraints | **FIXED.** `UNIQUE(rule_id, version)`. Published rows cannot be updated or deleted. A new version can coexist. |
| MEDIUM AuditEvents | **FIXED.** Use cases emit `rule_version.activated`, `dss_context_snapshot.frozen`, `action.recorded`, `outcome.recorded`. |
| LOW `input_snapshot` mutation | **FIXED.** Same recursive freeze as the DSS snapshot, including `thresholds_applied`. |

## Re-audit

A. **Audit result.** Critical and high invariants checked below are enforced. No critical leftover.

B. **Domain purity.** `src/baliza/domain/` still imports only the standard library and `baliza.domain`.

C. **Application boundary.** Use cases call ports. They do not import SQLAlchemy. Audit events are emitted from use cases, not ORM hooks.

D. **Snapshot immutability.** Nested list, nested mapping, deeper structures, the source object, and the frozen payload cannot be edited in place. Hash stays equal to the canonical form. Tests: `test_nested_snapshot_cannot_be_mutated`, `test_snapshot_is_insert_only_and_survives_reload`.

E. **Evidence chain.** Persistence test creates Observation, IndicatorValue, RuleEvaluation, EvidenceItem, EvidencePackage, and Alert, commits, opens a new session, and reads the links back. An alert row with a null evidence package is rejected.

F. **Rule integrity.** Duplicate `(rule_id, version)` raises `IntegrityError`. Published update and delete raise `ImmutablePersistenceError`. Version `1.1.0` inserts beside `1.0.0`.

G. **Critical alert path.** Unchanged: synchronous, deterministic, no LLM.

H. **Human-in-the-loop.** `record_decision` rejects missing Actor, snapshot, blank justification, and naive `decided_at`. SQL `decisions` requires actor, snapshot, justification, and `decided_at`. `AgentRun.is_decision()` is false. Acknowledge remains separate from Decision.

I. **Action safety.** `actions.decision_id` and `outcomes.action_id` / `outcomes.decision_id` are non-null foreign keys. Use cases record them only after a Decision.

J. **Audit.** New events listed above. `AuditEvent` is still a stored row, not a log line and not OpenTelemetry.

K. **Temporal model.** Persisted clocks: `observed_at`, `processed_at`, `computed_at`, `evaluated_at`, `alerted_at`, `opened_at`, `frozen_at`, `decided_at`, `reviewed_at` (alert column, also copied in history), `acted_at`, `observed_outcome_at`. Technical ORM timestamps were not added as substitutes.

L. **Persistence integrity.** See ORM notes below. Alembic `0002_phase36` adds the unique constraint, evaluation→version FK, alert evidence NOT NULL, junction tables, action/outcome tables, and PostgreSQL triggers.

M. **Test quality.** Domain tests cover freeze and decision preconditions. Application test covers audit emission. Persistence tests use SQLite in-memory (timezone-naive datetimes are converted to UTC on read; PostgreSQL triggers are not executed). Integration test rebuilds the evidence chain across sessions. Action and Outcome persistence exists; the chain test stops at Alert because Decision/Action are covered by separate use-case and schema tests.

N. **Architecture drift.** Modular monolith, ports, PostgreSQL as system of record, and the human Decision boundary are unchanged. No Redis, Kafka, UI, operational LLM, OIDC, PostGIS, or event sourcing.

## ORM safety

No `cascade="all"` and no `delete-orphan` on historical rows.

`session.delete` and attribute changes that flush to `UPDATE` are rejected for snapshots, published rule versions, rule evaluations, and audit events by `before_update` / `before_delete` listeners.

`merge()` is not used by repositories.

Live `DssPackage` JSON may be updated. Snapshot JSON is written once via `canonical_for_hash` and is not a `MutableDict`.

SQLite foreign keys are enabled on connect. Composite junction inserts are flushed after their parent rows because SQLite checks foreign keys per statement and SQLAlchemy can insert a junction before its parents in one flush.

## Security boundary

`POST /demo/critical-path` remains an unauthenticated in-memory demo. It is not a production boundary. It still calls the same use cases, so it cannot record a Decision without an Actor and a snapshot. `Actor` stays a domain identity, independent of an IdP.

## Canonical hash

`canonical_for_hash` sorts mapping keys, turns tuples and lists into JSON arrays, and sorts sets. `sha256_canonical` hashes that JSON with `sort_keys=True`, separators `(',', ':')`, and UTF-8. The same logical payload always yields the same digest.
