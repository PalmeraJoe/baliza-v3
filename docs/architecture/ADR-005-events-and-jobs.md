# ADR-005 — Events and Jobs

## Status

**ACCEPTED**

## Context

Need async work (ingest, AgentRun, notifications) without confusing Domain Events, Integration Events, and AuditEvents, and without mandating event sourcing or a heavy broker for MVP.

## Decision

| Mechanism | MVP choice |
|-----------|------------|
| **Domain Events** | In-process publish/subscribe inside the monolith (same transaction when possible) |
| **Integration Events** | Optional **outbox table** in PostgreSQL → worker polls / publishes to job queue |
| **AuditEvents** | Append-only **PostgreSQL** table; written explicitly by application services — **not** equated to domain events |
| **Jobs** | **Redis** + **ARQ** (or equivalent Redis queue) for worker tasks |
| **Broker (Kafka/NATS)** | **Not required** for pilot |

**Event sourcing:** **NOT** adopted as system of record. State lives in domain tables; events notify and audit.

### MVP necessity

- **Must:** AuditEvent persistence; async jobs for non-blocking AI/ingest.
- **Should:** Outbox if workers must not miss emissions after commit.
- **Later:** External event bus if multiple extracted services appear.

## Reason

- Preserves transactional Evidence Chain.
- Small-team ops (Redis vs Kafka).
- Clear semantic separation of event kinds.

## Trade-offs

- In-process domain events do not survive process crash mid-notify — mitigate with outbox for critical integrations.
- Redis becomes an ops dependency — **critical path (Observation persist + RuleEvaluation) must still run sync without Redis**. Redis outage must not be interpreted as “no risk” and must not block deterministic evaluation.

## Migration / exit

- Swap ARQ for another queue behind a `JobEnqueuer` port.
- Promote integration events to a broker without changing AuditEvent model.

## References

- ADR-001, [08-domain-model.md](../08-domain-model.md) domain events list
