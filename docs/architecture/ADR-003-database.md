# ADR-003 — Database

## Status

**ACCEPTED**

## Context

BALIZA needs relational integrity across Observations, IndicatorValues, RuleEvaluations, EvidenceItems/Packages, Alerts, Dss snapshots, Decisions, Actions, Outcomes, AuditEvents, and versioned definitions. Temporal queries and optional geospatial later.

## Options considered

| Option | Pros | Cons |
|--------|------|------|
| **PostgreSQL** | ACID, FKs, JSONB for flexible payloads, rich querying, PostGIS, mature | Ops care for backups |
| Document DB (Mongo, etc.) | Flexible docs | Weak multi-entity integrity for Evidence Chain |
| Dual primary (PG + doc) | Polyglot | Premature complexity |
| Only object store | Cheap blobs | Not a system of record for relations |

## Decision

**PostgreSQL 16+** as the **system of record** for structured domain data. Use **JSONB** where schemaless projections help (e.g., snapshot payload, rule condition docs) **with** relational keys for identity and FKs.

**PostGIS:** **OPEN BUT NON-BLOCKING.** Architecture is **spatial-ready**: Entity/Zone/Station hold opaque geometry now. Enable PostGIS when spatial queries are required (Q7). Do not require rich GIS on day one. Do not pick a non-spatial-capable primary store.

**Version strategy:** Prefer managed PG 16+; pin major; migrations tool chosen at implementation (e.g., Alembic) — not in this phase.

## Reason

- Maps directly to many-to-many Evidence Chain and Inv 17 snapshots.
- Transactions for Alert+EvidencePackage and Decision+snapshot.
- AuditEvent append + query by actor/time/target.

## Trade-offs

- Not ideal for huge binary artifacts → object store (ADR-004).
- Schema evolution requires migrations discipline.

## Migration / exit

- Standard SQL dump/restore; avoid proprietary PG extensions beyond PostGIS optionally.
- Logical module schemas ease future split databases if ever extracted.

## References

- [08-domain-model.md](../08-domain-model.md)
- ADR-004
