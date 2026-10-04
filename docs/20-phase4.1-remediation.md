# 20 — Phase 4.1 Remediation

## Problem

Phase 4 audit (`docs/19-phase4-audit.md`) found two HIGH gaps.

The snapshot stored alert, package, and evaluation ids. Alert status, evidence descriptors, and thresholds stayed on rows that can change later. Invariant 17 requires the snapshot itself to show what the decider saw.

`UnitOfWork` existed, but `Repositories.uow` defaulted to empty and the HTTP process did not bind it. A failure midway through evaluation, evidence, and alert could leave a partial critical path.

## Snapshot

`presented_context_payload` copies, at freeze time:

| Field | Contents |
| --- | --- |
| `alerts_at_freeze` | id, status, severity, `alerted_at`, `reviewed_at`, health, evidence package id, evaluation ids |
| `evidence_descriptors_at_freeze` | item id, kind, epistemic label, referenced type and id, narrative, `created_at`, content hash |
| `evidence_packages_at_freeze` | package id, subject, item ids, gaps, incomplete flag |
| `thresholds_at_freeze` | evaluation id, rule id, rule version id and label, threshold map, indicator unit when known, outcome, reason |
| `protocol_options_at_freeze` | option texts with source `protocol` |

`freeze_dss_package` writes those keys after any extra payload, then hashes the whole document. `DssContextSnapshot` still deep-freezes the payload. Later acknowledge, evidence narrative edits, raw threshold updates, live package edits, and outcomes do not change the hash.

Invariant 17 now states that those copies are required and that ids alone are not enough. The invariant was not weakened.

## Transaction

`evaluate_and_maybe_alert` refuses to run without a `UnitOfWork`. It begins, writes evaluation, evidence items, evidence package, and alert, then commits. Any exception, including a failed commit, rolls the unit of work back.

In-memory repositories bind `MemoryUnitOfWork` in `memory_repos()` and in the test fixture. SQL repositories bind `SqlUnitOfWork` on the request session.

`create_app(database_url=..., create_schema=False)` opens that URL. SQLite uses a shared pool so one process can see its own rows. Credentials are not hardcoded. Set `database_url` from the environment at the process boundary. The default `app` stays in memory when no URL is passed. `POST /demo/critical-path` still uses a private in-memory repository, still goes through the use cases, and still does not turn an alert into a decision by itself. The scripted demo calls `record_human_decision` only as an explicit operator step.

## Tests

SQLite: after freeze, a new session shows alert status `OPEN`, the original evidence narrative, and threshold `2.0` even though the alert row, the evidence narrative, and the evaluation JSON were changed.

SQLite rollback: evidence failure, alert failure, and commit failure each leave zero evaluation, evidence item, evidence package, and alert rows in a new session.

HTTP: `TestClient` against `create_app(database_url="sqlite://", create_schema=True)` persists an observation through the SQL repositories.

## PostgreSQL

`PostgreSQL transaction test = pending infrastructure`

`SqlUnitOfWork` is a SQLAlchemy session commit/rollback. That session works with the PostgreSQL dialect. No test in this repository connects to PostgreSQL, so SQLite does not stand in for it.

## Re-audit

| Check | Result |
| --- | --- |
| A. Snapshot completeness | PASS |
| B. Snapshot immutability | PASS |
| C. Hash integrity | PASS. New historical keys are inside the hashed payload. |
| D. Evidence descriptors | PASS |
| E. Alert state at freeze | PASS |
| F. Thresholds at freeze | PASS |
| G. Protocol options at freeze | PASS |
| H. UnitOfWork | PASS. The critical-path use case requires it. |
| I. Atomicity | PASS for evaluation, evidence, and alert. |
| J. Rollback | PASS on SQLite for evidence, alert, and commit failures. |
| K. HTTP transaction path | PASS. SQL mode opens a session per request, binds `SqlUnitOfWork`, and commits on success. |
| L. SQL persistence | PASS on SQLite, including a new session after freeze. |
| M. PostgreSQL compatibility | PARTIAL. The unit of work is dialect-neutral. No PostgreSQL server was available to run the same tests. |
| N. End-to-end reconstruction | PASS. Decision → snapshot reloads the frozen status, narrative, thresholds, and options without using the mutated rows. |
| O. Architecture drift | PASS. Same monolith, ports, and human decision. No LLM, Redis, Kafka, or workers. |

Medium items from the Phase 4 audit that were out of scope remain: live reads of evidence and indicator links still prefer JSON lists beside junction tables; published indicator versions have no SQL write guard; `unknown` and `insufficient` still share `INSUFFICIENT_DATA` while the facet stays on the evaluation input snapshot. They are not the two HIGH findings.

## Verdict

PHASE 4 VERIFIED
