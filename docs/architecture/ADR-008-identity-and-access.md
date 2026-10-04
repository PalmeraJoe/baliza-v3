# ADR-008 — Identity and Access

## Status

**ACCEPTED** (model); **IdP product choice PROPOSED**

## Context

Actor is mandatory on Decision (Inv 1). Pilot needs authentication and authorization without building a custom IdP. Multi-tenant hard isolation is not required for first pilot.

## Decision

| Concern | Choice |
|---------|--------|
| Authentication | **OIDC** Authorization Code + PKCE for UI; token validation at API |
| Domain identity | Persist **Actor** linked to IdP `sub` |
| Authorization | **RBAC** roles: operator, manager, scientist, admin, auditor (names align product docs) |
| Permissions (pilot minimum) | `alert.acknowledge`, `decision.record`, `action.record`, `rule.propose`, `rule.activate`, `protocol.activate`, `evidence.manage`, `audit.read` |
| Tenancy | Optional `tenant_id`; single-tenant default |
| ABAC | **Later** if attribute rules needed |
| Deployment | Distinct from Tenant (ops instance) |

### IdP options (pick at implementation)

| Option | Fit |
|--------|-----|
| **Keycloak** (self-host) | Lower lock-in; more ops |
| **Auth0 / similar managed** | Faster pilot; exit via OIDC standard |

**STATUS on vendor:** **PROPOSED** — either is compatible; prefer OIDC-standard claims mapping.

### Pilot MUST vs LATER

| MUST for pilot | LATER |
|----------------|-------|
| Login + Actor sync | Fine-grained ABAC |
| RBAC blocking Decision | Multi-tenant isolation |
| Protect rule activation | Advanced break-glass flows |

## Reason

- Separates authn product from domain Actor.
- Enforces human Decision without implementing full IAM in Phase 2 code.
- Portable via OIDC.

## Trade-offs

- IdP outage affects login — mitigate session TTL/cache carefully; break-glass admin procedure documented at deploy time.
- Role matrix still PRODUCT open (Q41) — start with minimal set.

## Migration / exit

- Change IdP; keep Actor ids stable via remapping table if `sub` changes.

## References

- Invariants 1, 16
- [10-domain-open-questions.md](../10-domain-open-questions.md) Q1, Q41
