# 13 — Technical Risks

Risks for BALIZA V3 technical architecture (Phase 2). Domain/scientific risks remain in product docs; this file focuses on **technical / delivery / ops**.

Legend: **P** = probability, **I** = impact.

---

## Critical

### R-C1 — Silent collapse of Evidence Chain in implementation

| | |
|--|--|
| **Risk** | Implementers store alerts without EvidencePackage / skip version on RuleEvaluation / skip Decision snapshot |
| **P** | Medium |
| **I** | Critical (audit & safety failure) |
| **Mitigation** | Enforce invariants in domain services + DB constraints + acceptance tests A–H; code review checklist from Inv 1–17 |
| **When** | From first vertical slice (Phase 3+) |

### R-C2 — LLM placed on critical alert path

| | |
|--|--|
| **Risk** | Shortcut: “let the model decide if we alert” |
| **P** | Medium under schedule pressure |
| **I** | Critical (non-reproducible, non-auditable, violates AGENTS.md) |
| **Mitigation** | Architecture gate: Alerts module rejects creation without RuleEvaluation for critical severity; no AI tools for Alert.create(critical) |
| **When** | ADR-007 compliance; Phase 5–7 and 9 |

---

## High

### R-H1 — Modular monolith becomes unstructured monolith

| | |
|--|--|
| **Risk** | Cross-module imports, domain coupled to FastAPI/SQLAlchemy/LLM |
| **P** | High without discipline |
| **I** | High (blocks extraction, tests fragile) |
| **Mitigation** | Package layers, import linters, domain tests without infra; ADR-001 seams |
| **When** | Phase 3 project bootstrap |

### R-H2 — Decision freeze implemented as live joins only

| | |
|--|--|
| **Risk** | “We can always re-query” — history drifts |
| **P** | Medium |
| **I** | High (cannot answer what user saw) |
| **Mitigation** | Inv 17 + snapshot table/object; tests that mutate live package post-decision and assert snapshot stable |
| **When** | Phase 8 DSS |

### R-H3 — False “all clear” on missing data

| | |
|--|--|
| **Risk** | Dashboards show green when INSUFFICIENT_DATA |
| **P** | Medium |
| **I** | High (operational/safety) |
| **Mitigation** | Health state enum; UI/API contracts; Inv 9 tests |
| **When** | Phase 7–10 |

### R-H4 — IdP or LLM vendor lock-in / outage

| | |
|--|--|
| **Risk** | Hard-coded SDKs; pilot blocked by provider outage |
| **P** | Medium |
| **I** | High for AI features; Medium for auth |
| **Mitigation** | Ports/adapters; rules-only DSS mode; session cache; secondary IdP path documented |
| **When** | Phase 2 design (done) / Phase 9–11 |

### R-H5 — Underestimated scientific configuration burden

| | |
|--|--|
| **Risk** | Architecture ready but no validated RuleVersions → empty pilot |
| **P** | High |
| **I** | High (delivery) |
| **Mitigation** | Parallel scientific track; keep rules in `draft`; Phase 13 not skipped |
| **When** | Ongoing; not solved by tech alone |

---

## Medium

### R-M1 — PostgreSQL used as blob store

| | |
|--|--|
| **Risk** | Large raw files / traces in BYTEA → bloat/backup pain |
| **P** | Medium |
| **I** | Medium |
| **Mitigation** | ADR-004 object store for binaries; size limits in API |
| **When** | Phase 3 |

### R-M2 — Async job races (indicator vs rules)

| | |
|--|--|
| **Risk** | Alert from stale IndicatorValue |
| **P** | Medium |
| **I** | Medium |
| **Mitigation** | Versioned inputs on RuleEvaluation; job ordering; idempotent keys |
| **When** | Phase 4–5 |

### R-M3 — Prompt injection / tool abuse

| | |
|--|--|
| **Risk** | Agent induced to exfiltrate or call forbidden tools |
| **P** | Medium when agents ship |
| **I** | Medium–High |
| **Mitigation** | Allowlisted tools; no Decision/Action tools; output schema validation; least privilege credentials |
| **When** | Phase 9 |

### R-M4 — Observability gap (“why no alert?”)

| | |
|--|--|
| **Risk** | Only log successes; cannot debug non-firing rules |
| **P** | Medium |
| **I** | Medium |
| **Mitigation** | Persist RuleEvaluation even when `not_triggered` (sampled or full for pilot); metrics on eval outcomes |
| **When** | Phase 5 |

### R-M5 — Compose-only habits block production hardening

| | |
|--|--|
| **Risk** | Secrets in files, no backups tested |
| **P** | Medium |
| **I** | Medium–High at go-live |
| **Mitigation** | Backup/restore drill before pilot; secret manager checklist ADR-010 |
| **When** | Before Phase 13 pilot |

### R-M6 — Frontend epistemic mixing

| | |
|--|--|
| **Risk** | UI shows inference as fact |
| **P** | Medium |
| **I** | Medium |
| **Mitigation** | API returns EpistemicLabel; UI components per label; design review |
| **When** | Phase 10 |

---

## Low

### R-L1 — Premature PostGIS / GIS complexity

| | |
|--|--|
| **Risk** | Heavy geo stack before needed |
| **P** | Low if ADR followed |
| **I** | Low–Medium (delay) |
| **Mitigation** | Opaque geometry until Q7 resolved |
| **When** | Only when pilot requires maps |

### R-L2 — Redis unavailability

| | |
|--|--|
| **Risk** | Jobs stall |
| **P** | Low |
| **I** | Low–Medium |
| **Mitigation** | Critical path sync option; queue health alerts; retry/DLQ |
| **When** | Phase 3 workers |

### R-L3 — Over-building notification channels

| | |
|--|--|
| **Risk** | Slack/SMS/multi-channel before need |
| **P** | Low |
| **I** | Low |
| **Mitigation** | Email/webhook only for pilot |
| **When** | Phase 7+ |

---

## Risk summary matrix

| ID | Level | Theme |
|----|-------|-------|
| R-C1 | Critical | Traceability integrity |
| R-C2 | Critical | AI on critical path |
| R-H1 | High | Modular discipline |
| R-H2 | High | Snapshot freeze |
| R-H3 | High | No-data semantics |
| R-H4 | High | Provider dependency |
| R-H5 | High | Scientific readiness |
| R-M1–M6 | Medium | Storage, races, security, observability, ops, UI |
| R-L1–L3 | Low | GIS, Redis, notifications |

---

## Related

- [12-technical-architecture.md](./12-technical-architecture.md)
- [09-domain-invariants.md](./09-domain-invariants.md)
- [AGENTS.md](../AGENTS.md)
