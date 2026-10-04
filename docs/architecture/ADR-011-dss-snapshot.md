# ADR-011 — DSS Context Snapshot

## Status

**ACCEPTED** (Phase 2.5)

## Context

Invariant 17 requires a frozen DSS context at Decision time. Phase 2 named `dss_context_snapshot_ref` but did not define `DssContextSnapshot` as a first-class immutable entity. Implementers could reconstruct context via live joins, violating auditability.

## Decision

```text
DssPackage          = live assembled DSS context (mutable while open)
DssContextSnapshot  = immutable freeze bound 1:N from Decision (typically 1:1)
```

### Rules

1. Recording a `Decision` **creates** a `DssContextSnapshot` (or binds an already-frozen snapshot produced in the same use case).
2. After bind, the snapshot is **IMMUTABLE**. No updates.
3. Historical reconstruction **must** read the snapshot, not only current Alert/Evidence rows.
4. Payload **meaning** is frozen (alerts, evidence packages/items, rule/indicator/protocol versions, evaluations, recommendations, agent outputs if shown, uncertainty, gaps, timestamps). JSON encoding is an implementation detail.
5. Persist in PostgreSQL with `content_hash`. If payload exceeds a size threshold, store bytes in object storage (`object_key`) and keep hash + pointer in PostgreSQL.
6. Live `DssPackage` may continue to change after Decision.

### Non-goals

- Exact JSON schema (OPEN).
- Hash algorithm (OPEN; lean SHA-256).

## Consequences

- DSS and Decision modules own snapshot creation inside one application transaction with the Decision.
- Tests must mutate the live package after Decision and prove the snapshot is unchanged.

## References

- Invariant 17
- [14-architecture-review.md](../14-architecture-review.md)
- ADR-004
