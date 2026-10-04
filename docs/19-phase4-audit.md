# 19 — Phase 4 Audit

Phase 4.1 addressed the two HIGH findings. The re-audit is in `docs/20-phase4.1-remediation.md`. This file remains the original audit record.

No product code was changed by the audit itself. Phase 5 was not started. AI was not added.

The code under `src/baliza/`, `tests/`, and `alembic/` is the source. `docs/18-phase4-implementation.md` was not taken as evidence.

## A. Audit Result

**PHASE 4 NEEDS FIXES**

The deterministic critical path, human decision boundary, and SQLite reconstruction of one alert chain are real. Two high gaps block verification:

1. `DssContextSnapshot` does not contain enough of the presented context to satisfy Invariant 17 without reading mutable rows.
2. The transactional boundary is optional, and the process that serves HTTP does not bind it or PostgreSQL.

## B. Domain Purity

**PASS**

`src/baliza/domain/` imports the standard library and `baliza.domain` only. `tests/test_import_boundaries.py` forbids FastAPI, SQLAlchemy, Alembic, Redis, S3, OpenAI, Anthropic, and OIDC libraries. `run_critical_path` and `evaluate_rule` do not call an agent, a network client, or a worker.

## C. Observation

**PASS**

`record_observation` stores variable, unit, value, `observed_at`, `processed_at` (clock), `DataQuality`, optional `source_id`, `spatial_ref`, and metadata. Subject is a metadata key, not a separate column. `observation.recorded` is emitted with `system_component="ingestion"`.

Missing values stay `None`. `DataQuality.implies_no_risk()` returns `False` for every facet (`src/baliza/domain/quality.py`).

## D. Data Quality

**PARTIAL**

Facets present: `valid`, `invalid`, `suspect`, `missing`, `insufficient`, `unknown`, plus the older `delayed`, `low_quality`, and `source_unavailable`.

`evaluate_rule` maps `INVALID` to `INVALID_INPUT`. Every other non-usable facet, including `missing`, `suspect`, `insufficient`, and `unknown`, becomes `INSUFFICIENT_DATA`. Nothing becomes `NOT_TRIGGERED` or a safe state.

The facet is copied into `input_snapshot["quality"]`, so the evaluation row still says `unknown` or `suspect`. The outcome enum does not. `unknown` and `insufficient` are therefore collapsed at the decision-relevant outcome, while remaining visible in the snapshot of inputs. That is a semantic loss at the outcome, not a conversion to “no risk”.

## E. Indicators

**PARTIAL**

`IndicatorValue` stores indicator id, version id, version string, source observation ids, `computed_at`, unit, quality, value, and notes. `calculate_from_observations` does not replace a missing member with zero.

SQL writes `indicator_value_observations`. `SqlIndicatorRepository.get_value` rebuilds sources from the JSON column `source_observation_ids`, not from that junction. The foreign keys exist, but the read path does not use them. `alert_chain` follows the same JSON list.

`indicator_versions` can be updated in SQL. There is no insert-only or published-immutable listener, unlike `rule_versions`.

## F. Rule Engine

**PASS**

Operators in `ComparisonOp`: `gt`, `gte`, `lt`, `lte`, `eq`, `between`.

`_compare` is strict for `gt`/`lt` and inclusive for `gte`/`lte`. `between` is inclusive on both ends: `low <= value <= upper`, where `low` is `threshold_name` and `upper` is the threshold named `{threshold_name}_upper`. A missing upper bound returns `INVALID_INPUT` and does not compare. Tests cover an interior point and a point above the range. They do not assert the inclusive endpoints. The code is not ambiguous.

`eq` is float equality. No unit check exists between the indicator unit and the rule. The evaluation stores `rule_version`, `rule_version_id`, `thresholds_applied`, `input_snapshot`, `evaluated_at`, outcome, and reason. There is no LLM call.

## G. Critical Alert Path

**PASS**

`run_critical_path` is synchronous and only calls `evaluate_rule` plus evidence and alert constructors. `AgentRun` remains a separate type with `is_decision() == False`. Triggered evaluations create an alert. `INSUFFICIENT_DATA` and `NOT_TRIGGERED` do not. The path does not read Redis or an external API.

## H. Atomicity

**PARTIAL**

`evaluate_and_maybe_alert` writes evaluation, items, package, then alert, and commits only if `repos.uow` is set. On exception it rolls that unit of work back. Alert insert is after the package, so a package failure does not insert an alert.

`Repositories.uow` defaults to `None`. `create_app()` uses `memory_repos()`, which does not set a unit of work. In that process, repository writes are immediate and are not rolled back.

`MemoryUnitOfWork` snapshots selected dicts. Tests prove rollback for evidence failure, alert failure, and a failed snapshot insert on that in-memory unit of work. There is no SQLite test that fails evidence persistence and then asserts the session has no evaluation row. `SqlUnitOfWork.begin` is a no-op; rollback is `session.rollback()`. Intermediate `flush()` calls are uncommitted, so rollback works only when that unit of work is actually bound and the caller does not commit earlier.

## I. Evidence Chain

**PARTIAL**

Domain objects link observation → indicator value → evaluation → evidence items → package → alert. Primary evidence must be `FACT` (`src/baliza/domain/evidence.py`).

Persisted foreign keys: indicator value ↔ observation, evaluation → rule version, evaluation ↔ indicator value, package ↔ item, alert → evidence package (`nullable=False`).

`items_for_package` and `get_package` trust `evidence_packages.item_ids` (JSON). The junction `evidence_package_items` is written and then ignored on read. Evidence item `referenced_id` is a string, not a foreign key. That matches the polymorphic reference in the domain model, and it is not referential integrity.

`test_end_to_end_sqlite_chain` reloads the chain in a new session through repositories, so the happy path is reconstructable from SQLite. It does not prove the junction is the source of truth.

## J. Epistemic Labels

**PASS**

Primary evidence cannot be `INFERENCE`. Protocol options are `RECOMMENDATION` with source `protocol`. `record_decision` requires an `Actor`. Acknowledge and `AgentRun` do not construct a `Decision`. The critical path does not create recommendations from a model.

## K. Alerts

**PASS**

An alert stores severity, status, `alerted_at`, evidence package id, evaluation ids, and scope health. Critical construction requires an evidence package in the domain type. `acknowledge` sets `ACKNOWLEDGED` and an audit event. It does not call `record_decision`. `Alert.is_decision()` is false. No use case creates an `Action` from an alert.

Alert rows themselves remain mutable after a decision. See section N.

## L. DSS Package

**PASS**

`DssPackage` is a mutable dataclass. `DssContextSnapshot` is a separate frozen object. `build_dss_package` accepts a list of alerts, copies their evidence package ids and evaluation ids, and can attach protocol recommendations, gaps, and uncertainty notes. `test_multi_alert_decision` puts two alerts into one package and one decision. That test is in memory only.

## M. Protocols

**PASS** for behavior, **PARTIAL** for persistence.

`recommendations_from_protocol` only builds `RecommendationView` values. `test_protocol_options_do_not_create_actions` shows no action is stored. A published `ProtocolVersion.with_options` raises `PublishedVersionImmutable`.

There is no `protocols` table. The option text and `protocol_version` string are copied onto the live package and into the snapshot recommendations. That does not contradict “protocols do not execute”. It does leave published-protocol immutability unenforced in PostgreSQL.

## N. Snapshot

**PARTIAL**

The snapshot object is deep-frozen. `content_hash` is SHA-256 of canonical JSON. ORM listeners and the PostgreSQL trigger reject snapshot updates and deletes. Mutating the live package after freeze does not change the hash (`tests/test_dss.py`). An outcome recorded afterward does not change the hash (`test_multi_alert_decision`, in memory).

Invariant 17 requires the snapshot to reconstruct, without joins to mutable rows, the alert state as presented, evidence item kind and label, the cited rule version, and indicator version. `freeze_dss_package` stores ids for alerts, evidence packages, and evaluations, plus recommendation text, gaps, uncertainty notes, protocol version string, and two timestamps. It does not store alert status or severity, evidence item descriptors, threshold values, or indicator version. `record_human_decision` does not pass those in `extra_snapshot`.

Alert status is mutable (`SqlAlertRepository.save`). After acknowledge, the only status in `alerts` is the new one. The snapshot cannot show that the decision saw `OPEN`. Evidence items and evidence packages have no immutability listener, so they are mutable rows. Reading them to complete the decision context violates Invariant 17.

Rule evaluations are insert-only, so joining them for thresholds is a join to an immutable row. The snapshot still does not carry those thresholds itself.

## O. Decision

**PASS** in domain and application. **PARTIAL** in SQL nullability of the live package link.

`record_decision` rejects a missing actor, a missing snapshot, a blank justification, and a naive `decided_at`. The API looks up `Actor` and returns 400 if it is absent. `POST /decisions` and `POST /dss/packages/{id}/freeze` both call `record_human_decision`. There is no route from an alert id, an agent run, or a recommendation to a decision.

`decisions.actor_id`, `dss_context_snapshot_id`, `justification`, and `decided_at` are NOT NULL. `dss_package_id` is a foreign key and is nullable in the model. There is no `actors` table, so `actor_id` is not a foreign key.

## P. Action

**PASS**

`record_action` raises `ActionWithoutDecision` when `decision_id` is missing. `POST /actions` loads the decision and returns 400 if it is missing. `actions.decision_id` is a non-null foreign key. No code path creates an action from an alert, an agent run, a recommendation, or a protocol.

## Q. Outcome

**PASS**

`Outcome` stores `action_id` and `decision_id`, both non-null foreign keys. `record_human_outcome` inserts a new row and an audit event. It does not write the decision, snapshot, evidence, evaluation, or alert. The in-memory multi-alert test checks the snapshot hash after the outcome. The SQLite end-to-end test checks that the loaded outcome points at the decision. It does not re-read the hash after a second session mutation attempt.

## R. Audit Events

**PASS**

Use cases emit `observation.recorded`, `indicator.calculated`, `rule.evaluated`, `evidence.package_created`, `alert.created`, `alert.acknowledged`, `dss.package_opened`, `dss_context_snapshot.frozen`, `decision.recorded`, `action.recorded`, `outcome.recorded`, and `rule_version.activated`.

Human steps carry `actor_id`. System steps carry `system_component`. The SQLite end-to-end test loads `audit_events` in a new session and requires that set. These rows are not log lines. `audit_events` are insert-only at the ORM. There is no OpenTelemetry exporter on this path.

## S. Persistence

**PARTIAL**

Enforced and tested on SQLite via the ORM: unique `(rule_id, version)`, published rule update/delete rejected, snapshot update/delete rejected, evaluation and audit insert-only, alert evidence package NOT NULL, decision actor/snapshot/justification/`decided_at` NOT NULL, action and outcome foreign keys.

Not enforced: published `indicator_versions` immutability, evidence item/package immutability, protocol versions, actor foreign key. `decisions.dss_package_id` and `dss_context_snapshots.dss_package_id` are nullable. Cascades are not `all, delete-orphan` on historical rows. PostgreSQL triggers from `0002_phase36` still cover snapshots and published rule versions only when that migration runs on PostgreSQL.

## T. PostgreSQL vs SQLite

**PARTIAL**

| Invariant | Where it is proven |
| --- | --- |
| Domain outcomes, quality, operators, acknowledge ≠ decision | Domain tests, no database |
| Snapshot nested immutability and hash | Domain tests |
| Snapshot and published rule ORM rejection | SQLite + SQLAlchemy listeners |
| Snapshot and published rule rejection under raw SQL | PostgreSQL trigger in `0002_phase36`, not executed by tests |
| Full chain reload | One SQLite session-reopen test |
| HTTP persistence | Not tested; default app has no database |

SQLite is not treated as PostgreSQL. No test in `tests/` connects to PostgreSQL.

## U. API

**PASS** as a use-case adapter. **PARTIAL** as a production boundary.

Routes call application functions. They do not import SQLAlchemy or `evaluate_rule`. Validation errors from the domain become HTTP 400. A missing actor or decision becomes 400.

`POST /demo/critical-path` builds a private in-memory repository, labels `threshold_status` as `DEMO / NON-SCIENTIFIC`, sets `ai_used` false and `production_ready` false, and still goes through `record_human_decision`. It does not skip actor, snapshot, or justification. It is not the persistence path.

`POST /dss/packages/{id}/freeze` does not freeze alone. It records a decision, which freezes inside `record_human_decision`.

## V. API → Persistence

**PARTIAL**

`create_app(repos)` can receive any `Repositories`, including SQL ones. The module-level `app` calls `memory_repos()` and never opens PostgreSQL. No HTTP test writes a row and reads it back from SQLite or PostgreSQL. `test_api_observation_roundtrip` uses `create_app()` memory only.

The application path and the HTTP path share use cases. They do not share a system of record unless a host injects one. That injection is not implemented in `app.py`.

## W. End-to-End Persistence

**PASS** for a single SQLite chain. **PARTIAL** against the full invariant set.

`test_end_to_end_sqlite_chain` commits, opens a new `Session`, and reloads observation, indicator value, thresholds, rule version string, evidence package, alert, snapshot hash, decision, outcome, and audit actions. It does not go through HTTP. It uses one alert. Actor storage is `InMemoryActorRepository` beside SQL repositories.

## X. Multi-Alert DSS

**PARTIAL**

`test_multi_alert_decision` checks two alert ids inside the in-memory snapshot payload. No persistence test reloads a two-alert snapshot from SQLite or PostgreSQL.

## Y. Failure Modes

**PARTIAL**

Covered: missing and invalid observations do not imply no risk; suspect quality is `INSUFFICIENT_DATA`; missing input is not `NOT_TRIGGERED`; not-triggered and triggered outcomes exist; in-memory unit of work rolls back evidence failure, alert failure, and a failed snapshot insert; action without decision fails; blank decision justification fails in domain tests.

Not covered: those persistence failures on SQLite/PostgreSQL; `unknown` and `insufficient` facets as distinct outcomes; BETWEEN endpoints; a committed alert that later loses its evidence package.

No failure path returns a `SAFE` outcome. That label does not exist.

## Z. Test Quality

**PARTIAL**

| Kind | What exists |
| --- | --- |
| Domain | `test_rules.py`, `test_invariants.py`, `test_evidence.py`, operator and quality cases in `test_phase4.py` |
| Application | Audit emission, acknowledge, protocol options, multi-alert decision, in-memory rollback |
| Persistence | SQLite observation, snapshot immutability, rule uniqueness, one full chain |
| API | `/health`, demo critical path, one observation POST/GET in memory |

The rollback tests replace repository methods and restore dict snapshots. They do not open a database transaction. The end-to-end test does not fail a step on purpose. Pytest being green does not exercise PostgreSQL triggers or the default HTTP composition.

## AA. Architecture Drift

| Item | Class |
| --- | --- |
| Modular monolith, ports, no LLM on the critical path | Matches frozen architecture |
| Snapshot payload omits alert state, evidence descriptors, and thresholds required by Invariant 17 and ADR-011 | **ARCHITECTURAL DRIFT** |
| Read models follow JSON id lists while junction tables exist | **BUG** in the read path relative to the stated foreign-key chain |
| HTTP process uses memory, PostgreSQL is the declared system of record | **DOCUMENTATION GAP** already stated in `docs/18`; still true in code |
| Extra quality facets `suspect`, `insufficient`, `unknown` | **INTENTIONAL** extension; outcome collapse is a semantic issue, not a silent rename of old facets |
| No protocol table | **DOCUMENTATION GAP** relative to `docs/08`; behavior matches Invariant 11 |
| `POST /demo/critical-path` | **INTENTIONAL** demo, already marked non-production |

## AB. Security

**PARTIAL**

No OIDC, as required. Decision and action routes refuse a missing actor or a missing decision. They do not authenticate the caller: any client who can hit the process and who knows an in-memory actor id can record a decision. The demo route creates its own actor. Neither path bypasses domain checks. That is acceptable only as a non-production adapter.

## AC. Open Issues

| Declared issue | Classification |
| --- | --- |
| HTTP app does not open PostgreSQL | **REQUIRES FIX BEFORE PHASE 5**. Not an architectural blocker: `create_app(repos)` already accepts SQL repositories. The shipped `app` does not use them. |
| Actor has no table and no IdP | **ACCEPTABLE FOR PHASE 4**. ADR-008 keeps Actor independent of the IdP. SQL still cannot prove the actor existed. |
| PostgreSQL triggers are not tested on SQLite | **ACCEPTABLE FOR PHASE 4** as a known test limit. It is not proof that the triggers are wrong. It is not coverage. |
| Protocol catalog has no table | **ACCEPTABLE FOR PHASE 4** because the options shown are copied onto the package and snapshot. **REQUIRES FIX BEFORE PHASE 5** if published protocol versions must be immutable in the system of record. |

## AD. Issues Found

1. **HIGH — Snapshot is immutable but incomplete (Invariant 17).** `freeze_dss_package` in `src/baliza/domain/dss.py` stores alert, package, and evaluation ids, not alert state, evidence item kind/label, rule thresholds, or indicator version. `alerts` stay updatable. A later acknowledge changes the only stored alert status. The decision record cannot show the state that was presented without reading that mutable row.

2. **HIGH — Critical-path atomicity is not on by default.** `evaluate_and_maybe_alert` rolls back only when `repos.uow` is set. `create_app` / `memory_repos` leave it unset. A failure after `add_evaluation` or `add_item` then leaves partial history in the default process. SQLite failure rollback is not tested; only `MemoryUnitOfWork` is.

3. **MEDIUM — Evidence and indicator reads ignore junction tables.** `items_for_package` and indicator `get_value` use JSON id lists. Junction rows are written and not consulted. Two sources of truth can diverge without the read model noticing.

4. **MEDIUM — `unknown` and `insufficient` collapse to `INSUFFICIENT_DATA`.** The facet survives in `input_snapshot`, not in `RuleOutcome`. Callers that branch only on the outcome cannot tell those facets apart.

5. **MEDIUM — Published indicator versions are mutable in SQL.** `indicator_versions` has a unique `(indicator_id, version)` and no update/delete guard.

6. **MEDIUM — Multi-alert freeze is not reloaded from a database.** The two-alert assertion never leaves process memory.

7. **LOW — `decisions.dss_package_id` and snapshot `dss_package_id` are nullable.** Domain decisions always carry a package id. The table does not.

8. **LOW — `between` inclusivity and float `eq` are implemented and thinly tested.** Endpoints of the closed interval are not asserted. Units are not compared.

## AE. Recommended Fixes

Do not treat this section as authorization to change code inside the audit.

1. Copy into the snapshot, before hashing, the presented alert status and severity, evidence item id/kind/label/reference, rule version id, thresholds, and indicator version. Add a persistence test that acknowledges the alert after the decision and shows the snapshot payload unchanged and still sufficient without reading the updated alert row.
2. Bind a unit of work in every composition root, including `create_app`. Add a SQLite test where evidence insert fails and the new session contains neither the evaluation nor the alert.
3. Read package items and indicator sources from the junction tables. Keep JSON only as a denormalized copy if it is still required.
4. Either keep distinct outcomes for `unknown` versus other insufficient facets, or document the collapse in the domain model and require readers to use `input_snapshot`. Do not invent a `SAFE` outcome.
5. Apply the published-version write guard to `indicator_versions`.
6. Persist a two-alert decision and reload the snapshot in a new session.
7. Wire the HTTP app to the SQL repositories behind an explicit configuration flag when Phase 5 needs a real process. Until then, do not describe the default `app` as the system of record.

## AF. Final Verdict

PHASE 4 NEEDS FIXES
