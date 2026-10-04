# Phase 3 implementation notes

## Scope delivered

- Domain core (Observation → Decision) with invariants as executable tests.
- Application use cases coordinating the critical path (no LLM, no Redis).
- Ports + in-memory adapters + SQLAlchemy/PostgreSQL schema (Alembic).
- Object storage **port** + in-memory adapter.
- Thin FastAPI health + demo critical-path endpoint (in-memory).

## ORM

SQLAlchemy 2.0 in `infrastructure` only. See `docs/architecture/ADR-012-persistence-orm.md`.

## Clocks persisted

`observed_at`, `processed_at`, `computed_at`, `evaluated_at`, `alerted_at`, `reviewed_at` (alert history), `opened_at`, `frozen_at`, `decided_at`. Action/Outcome clocks exist in domain; tables deferred.

## Not in this phase

UI, Redis/ARQ, LLM/agents, Kafka, GIS, cloud deploy, external Action systems.
