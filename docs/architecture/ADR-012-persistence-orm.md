# ADR-012 — Persistence ORM (Phase 3)

## Status

**ACCEPTED**

## Context

Phase 3 needs a PostgreSQL adapter without leaking persistence into the domain. Options: SQLAlchemy 2.x, SQLModel, raw SQL, Tortoise.

## Decision

Use **SQLAlchemy 2.0** (imperative/mapped tables in `infrastructure` only) and **Alembic** for migrations. Domain entities remain pure dataclasses.

**Tests:** domain/application tests use in-memory repositories (no DB). Persistence tests may use SQLite via SQLAlchemy for CI without Docker; production dialect is PostgreSQL (`psycopg` v3).

## Reason

- Mature, widely supported, matches ADR-003.
- Clear session/unit-of-work boundary.
- Alembic is the de-facto companion.

## Trade-offs

- SQLite in tests is not 100% PostgreSQL (JSONB ≈ JSON). Critical invariants are tested in-domain, not via dialect quirks.
- Must never import SQLAlchemy from `baliza.domain`.

## Migration / exit

- Repositories sit behind ports; ORM can be replaced without domain changes.
