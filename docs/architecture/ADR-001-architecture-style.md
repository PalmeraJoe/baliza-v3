# ADR-001 — Architecture Style

## Status

**ACCEPTED**

## Context

BALIZA V3 needs Evidence Chain consistency, Decision snapshots, versioned RuleEvaluations, auditability, and a small-team pilot. Alternatives: modular monolith, microservices, hybrid, full event-driven.

## Decision

Adopt a **Modular Monolith** application (single codebase / primary deployable) with **async worker processes** sharing the same domain modules (light hybrid). Use in-process domain events; avoid microservices and Kafka-centric EDA for the pilot.

## Consequences

### Positive

- Transactional integrity across RuleEvaluation → Evidence → Alert → Decision freeze.
- Fast iteration and simpler observability.
- Clear path to extract workers/services later.

### Negative

- Requires module discipline to avoid a “ball of mud.”
- Scaling is primarily vertical + worker horizontal scale.

## Extraction seams

- Packages: `domain / application / infrastructure`.
- Module folders: ingestion, indicators, rules, evidence, alerts, dss, ai, decisions, audit.
- Workers share the **same** domain/application modules as the API; they must not fork an alternate domain model.
- Replace in-proc calls with queue messages at module boundaries when needed (AI, ingest first).

## Alternatives considered

| Option | Why not now |
|--------|-------------|
| Microservices | Ops and consistency cost unjustified for pilot |
| Full EDA + broker | Complexity; domain events ≠ need for Kafka |
| Event sourcing | Strong reason absent; RuleEvaluation/AuditEvent suffice |

## References

- [12-technical-architecture.md](../12-technical-architecture.md)
- [11-domain-review.md](../11-domain-review.md)
