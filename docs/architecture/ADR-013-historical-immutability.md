# ADR-013 — Historical immutability in persistence

## Status

**ACCEPTED** (Phase 3.6)

## Context

ADR-011 freezes `DssContextSnapshot` after a Decision. Phase 3 enforced that only at the top-level Python mapping. Nested lists stayed mutable, and SQLAlchemy could emit `UPDATE` / `DELETE` for snapshot rows and published `RuleVersion` rows.

## Decision

1. Historical payloads are deep-copied and stored as recursively read-only values: mappings become read-only mappings, sequences become tuples, sets become frozensets.
2. `content_hash` is SHA-256 of canonical JSON (`sort_keys`, compact separators, UTF-8). Sequences serialize as JSON arrays. This is an integrity check, not authentication.
3. `dss_context_snapshots` are insert-only. Application repositories do not update or delete them. SQLAlchemy `before_update` / `before_delete` reject writes. PostgreSQL triggers in Alembic `0002_phase36` reject `UPDATE` and `DELETE` even if the ORM is bypassed.
4. `RuleVersion` may change while `DRAFT`. Once `PUBLISHED`, ORM listeners and a PostgreSQL trigger reject update and delete. A later scientific change is a new `(rule_id, version)` row. `(rule_id, version)` is unique.
5. `rule_evaluations` and `audit_events` are insert-only at the ORM. PostgreSQL triggers for those two tables are not part of this revision.

## Consequences

SQLite tests exercise the ORM listeners and SQL constraints. They do not execute the PostgreSQL trigger functions. A raw `UPDATE` on SQLite can still bypass the listeners; production PostgreSQL cannot for snapshots and published rule versions.
