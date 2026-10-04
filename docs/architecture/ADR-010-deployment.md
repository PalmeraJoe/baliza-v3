# ADR-010 — Deployment

## Status

**ACCEPTED** (pilot model)

## Context

Small team, real pilot, portable images, avoid premature Kubernetes complexity.

## Decision

**Pilot topology (Docker Compose or equivalent):**

| Service | Role |
|---------|------|
| `api` | FastAPI modular monolith |
| `worker` | Same image, job consumer |
| `postgres` | System of record |
| `redis` | Job queue / short cache — **not required for RuleEvaluation** |
| `minio` | S3-compatible objects (or managed S3) |
| IdP | External Auth0 **or** Keycloak container |
| `otel-collector` | Optional but recommended before pilot |

**Later:** same container images on ECS/Cloud Run/Kubernetes; managed Postgres/Redis/S3.

**Secrets:** environment / secret manager — never commit secrets.  
**Backups:** automated Postgres + object versioning/replication; restore drill before pilot.

**Version strategy:** immutable image tags per release; DB migrations forward-only in implementation phases.

## Reason

- Matches modular monolith + workers.
- Low ops load; clear promotion path.
- MinIO keeps S3 API without forcing AWS on day one.

## Trade-offs

- Compose is not HA — acceptable for pilot, not multi-region DR.
- Team must not skip backup drills (R-M5).

## Migration / exit

- Move services one-by-one to managed offerings; DNS/config only.
- No proprietary deploy DSL required in Phase 2 (no Terraform authored here).

## NOT in this phase

No Dockerfiles, Compose files, or Terraform are created in Phase 2 documentation-only gate — this ADR defines the **target model** for Phase 3+ bootstrap.

## References

- ADR-001, ADR-003, ADR-004, ADR-005
- [12-technical-architecture.md](../12-technical-architecture.md)
