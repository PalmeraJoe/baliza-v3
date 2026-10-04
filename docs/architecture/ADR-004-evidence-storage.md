# ADR-004 — Evidence Storage

## Status

**ACCEPTED**

## Context

EvidenceItems and EvidencePackages must be structured and auditable. Raw datasets, documents, and agent traces can be large. Need clear split: metadata vs binaries.

## Decision

| Content | Store |
|---------|--------|
| EvidenceItem, EvidencePackage, gaps, conflicts, epistemic labels, FK refs, version ids | **PostgreSQL** |
| Raw ingest files, scientific PDFs, large series dumps, AgentRun trace bundles, optional bulky snapshot blobs | **S3-compatible object storage** (MinIO for pilot; AWS S3 or equivalent in prod) |

EvidenceItem always carries: `kind`, `ref` (domain id and/or `object_key`), `epistemic_label`, quality/uncertainty, timestamps, versions, and **`content_hash` when an artifact or payload is stored**.

**Integrity:** Every object-store object and every DssContextSnapshot payload has a `content_hash` (algorithm OPEN; lean SHA-256) so substitution/modification is detectable. Hashing is a **design requirement**, not an optional later extra.

**Decision snapshots (Inv 17 / ADR-011):** PostgreSQL row with JSONB projection + `content_hash`; if payload large, JSONB stub + `object_key` to an **immutable** object with the same hash.

## Reason

- Critical path queries and FKs stay relational.
- Object store scales for artifacts without DB bloat.
- S3 API is portable (MinIO ↔ cloud).

## Trade-offs

- Two systems to backup (coordinate restore).
- Must prevent “evidence = free text only” in API validation.

## Migration / exit

- Object keys opaque; change bucket/provider via config.
- Metadata remains in PG for continuity.

## Alternatives

- All-in-Postgres BYTEA — rejected for size/backup.
- All-in-document DB — rejected as primary (ADR-003).

## References

- [06-evidence-and-traceability.md](../06-evidence-and-traceability.md)
- Invariant 3, 13, 17
