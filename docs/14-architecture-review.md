# 14 — Technical Architecture Review & Freeze (Phase 2.5)

## Status

**Review completed.** Soft freeze recommended for implementation.

| Phase | Status |
|-------|--------|
| Phase 0 — Foundation | COMPLETED |
| Phase 1 — Core Domain Model | COMPLETED |
| Phase 1.5 — Domain Review & Freeze | COMPLETED |
| Phase 2 — Technical Architecture | COMPLETED |
| Phase 2.5 — Architecture Review & Freeze | CURRENT / completing with this document |
| Phase 3 — Implementation bootstrap + Data ingestion | NOT STARTED |

No application code, migrations, APIs, UI, or infrastructure are produced in this phase.

**Primary question:** Can we start implementation without later changing **fundamental** architectural decisions?

**Answer:** **Yes**, after the documentary corrections in this review (DssContextSnapshot as a first-class immutable entity; ports/adapters diagram; canonical clocks; artifact integrity hashes as a design requirement).

**BLOCKING issues remaining:** **None.**

---

## 1. Verdict

The Phase 2 architecture is **sufficiently mature** to implement against, provided implementers treat the **FROZEN** list in §16 as stable and keep **OPEN BUT NON-BLOCKING** items parameterized.

Acceptance criteria A–J from Phase 2 remain satisfied. AI is an **optional capability**. Critical alerts do not depend on LLM/AgentRun.

---

## 2. Architecture freeze classification

### FROZEN (implementation may assume)

| Decision | Notes |
|----------|--------|
| Modular Monolith + async workers | Logical modules; same domain library; not microservices |
| No Event Sourcing as system of record | |
| No Kafka / NATS as MVP dependency | |
| Ports & adapters: UI → Application → Domain ← Ports/Infra | Domain has no PG/Redis/S3/FastAPI/React/LLM/OIDC/cloud imports |
| Workers share the **same domain**; they are not an alternate owner | |
| PostgreSQL 16+ = system of record | |
| S3-compatible object storage for large artifacts | |
| EvidenceItem + EvidencePackage persist; Evidence is conceptual | |
| DssPackage = live context; **DssContextSnapshot** = frozen Decision context | Immutable after Decision |
| Critical alert path: Observation → IndicatorValue → RuleEvaluation → Evidence → Alert | LLM-free |
| Rule / RuleVersion / Threshold / RuleEvaluation | Published versions immutable |
| RuleEvaluation stores version, input refs, threshold snapshot, triggered/not_triggered | Deterministic; no AgentRun |
| AgentRun → Analysis/Recommendation only | Never Decision/Action/Outcome/Rule activation |
| AI optional for MVP | Rules-only DSS is valid |
| Actor ≠ IdP user | OIDC authenticates; BALIZA persists Actor |
| RBAC for pilot | Minimum permissions listed in §15 |
| AuditEvent ≠ logs/metrics/traces | |
| Domain clocks remain distinct | Canonical names in §11 |
| Failure ≠ no risk | `OK \| DEGRADED \| INSUFFICIENT_DATA \| UNKNOWN` |
| Integrity hash on artifacts and snapshots | Algorithm OPEN (lean: SHA-256) |
| Spatial-ready without PostGIS-on-day-one | Opaque geometry today; PostGIS later |
| Python 3.12+ / FastAPI as API+worker runtime | Domain stays framework-free |
| Redis jobs **must not** be required for deterministic RuleEvaluation | Queue failure ≠ cannot evaluate |

### OPEN BUT NON-BLOCKING

| Item | Why non-blocking |
|------|------------------|
| Vite vs Next.js | UI only; does not change domain/backend |
| Keycloak vs Auth0 | Both OIDC; Actor mapping stable |
| ARQ vs other Redis job lib | Behind `JobEnqueuer` port |
| MinIO vs managed S3 | Same S3 API |
| Snapshot embed JSONB vs object_key for large payloads | Same entity; storage split already defined |
| Hash algorithm (SHA-256 vs others) | Requirement frozen; algo configurable |
| Enable PostGIS extension | Spatial-ready columns first; extension when Q7 needs queries |
| Sync vs async **scheduling** of indicator/rule after ingest | Evaluator itself is in-process/sync-capable |
| Pilot ships with or without AI module enabled | Architecture supports both |
| Rule expression richness / future DSL | Evaluator engine_id versioned |
| Exact RBAC matrix beyond minimum | Extra permissions can be added |
| Multi-tenancy isolation | Optional `tenant_id` |
| Offline / edge | Q51; default online |
| Notification channels | Email/webhook later |
| Alembic vs other migrator | Implementation detail |

### BLOCKING

**None.**

---

## 3. Style review — Modular Monolith + Workers

**Confirmed as base architecture (ADR-001).**

| Check | Result |
|-------|--------|
| Modules are **logical** boundaries in one codebase | Pass |
| Not microservices | Pass |
| Workers use the **same domain packages** as the API | Pass — freeze: no worker-local domain fork |
| Event Sourcing not adopted | Pass |
| Kafka not an MVP dependency | Pass |
| Extraction later without rewriting domain | Pass — `domain / application / infrastructure` seams |

Workers may **schedule** ingest, AI, notifications, and heavy recompute. They must **import** domain services, not reimplement RuleEvaluation/Decision semantics.

---

## 4. Dependency rule review

**Required:**

```text
UI
 ↓
Application
 ↓
Domain
 ↓
Ports (interfaces)
 ↓
Infrastructure adapters  (PostgreSQL, Redis, S3, FastAPI, OIDC, LLM, …)
```

### Issue found (documentary)

```text
ISSUE: Context diagram in docs/12 showed Domain → PostgreSQL / Object store.
SOURCE: docs/12-technical-architecture.md §4–5
CONFLICT: Contradicts ports & adapters and ADR-001/002.
PROPOSED RESOLUTION: Diagrams must show Application/Infra adapters owning I/O; Domain remains persistence-ignorant.
STATUS: SAFE TO CHANGE (diagrams corrected in Phase 2.5)
```

**No approved exception.** Domain must not import:

- PostgreSQL / SQLAlchemy / drivers
- Redis / ARQ
- S3 / boto
- FastAPI / Starlette
- React
- LLM provider SDKs
- OIDC / Keycloak / Auth0 SDKs
- Cloud provider SDKs

FastAPI is the **adapter** that calls application services. Workers are another adapter (job runner) calling the same services.

---

## 5. DssPackage vs DssContextSnapshot (mandatory)

### Frozen distinction

```text
DssPackage
    = live / assembled DSS context (may evolve while open)

DssContextSnapshot
    = immutable frozen projection bound to a Decision
```

A Decision **must** reference `DssContextSnapshot` (Inv 17). Reconstructing “what the Actor saw” by **live joins** after the fact is **forbidden**.

### Snapshot must reconstruct (minimum payload)

| Content | How |
|---------|-----|
| Alerts considered | ids + severity/status **as shown** + versions of related evals |
| EvidencePackages | ids + assembler version + gaps/conflicts as shown |
| EvidenceItems | ids + kind + epistemic_label + refs/hashes |
| RuleVersion | rule_id + version |
| RuleEvaluation | evaluation ids + outcome + threshold snapshot refs |
| IndicatorVersion | indicator_id + version (via evals/values cited) |
| ProtocolVersion | protocol_id + version + options presented |
| Recommendations | ids + source (protocol vs AI) + labels |
| Agent outputs | AgentRun/Analysis ids + version + epistemic labels (if presented) |
| Uncertainty / gaps | as presented |
| Timestamps | `opened_at` / `frozen_at` / `decided_at` |
| Actor | bound on Decision (`actor_id`); snapshot records freeze time |

### Immutability

```text
IMMUTABLE AFTER DECISION
```

No update API for an existing snapshot. Corrections ⇒ new Decision + new snapshot (compensation), never mutate the old one.

Storage (already ADR-004, tightened): PostgreSQL row + `content_hash`; oversized payload → immutable object + `object_key` + same hash. Details: [ADR-011](./architecture/ADR-011-dss-snapshot.md).

**Was this a gap?** Snapshot was required (Inv 17) but not a first-class glossary entity with a closed payload list. **Closed for architecture in this review** (SAFE TO CHANGE). Payload **schema encoding** remains OPEN (JSONB shape), payload **meaning** is FROZEN.

---

## 6. Evidence integrity

| Concern | Verdict |
|---------|---------|
| Structured metadata in PostgreSQL | FROZEN |
| Large/binary artifacts in object storage | FROZEN |
| Stable `object_key` (or content-addressed key) | FROZEN |
| EvidenceItem provenance (source, timestamps, versions, kind) | FROZEN |
| Original vs derived via `kind` | FROZEN (enum values OPEN) |
| EvidencePackage reconstructible from item refs | FROZEN |
| Detect substitution/modification | **FROZEN as requirement:** store `content_hash` (and optional size) on artifacts and snapshot payloads |

**Hash algorithm:** OPEN BUT NON-BLOCKING (lean recommendation: SHA-256). Do not skip hashing in the design.

Agents **must not** modify historical EvidenceItems/Packages in place; they may only **add** new analytical items (Inv 14 analogue).

---

## 7. Rule engine freeze

```text
Rule (identity)
 ↓
RuleVersion (immutable when published)
 ↓
Threshold (owned by that version)
 ↓
RuleEvaluation (deterministic; stores version + inputs + thresholds applied)
 ↓
Evidence → Alert  (critical path; no LLM)
```

| Check | Result |
|-------|--------|
| Published RuleVersion immutable | FROZEN |
| Evaluation stores exact version | FROZEN |
| Input refs + threshold snapshot | FROZEN |
| `triggered` and `not_triggered` persisted | FROZEN (pilot: full, not sampled) |
| Deterministic; no LLM/AgentRun | FROZEN |
| DSL | OPEN (evaluator code + declarative JSON/YAML now) |
| Evaluator engine id on evaluation | FROZEN (so interpreter upgrades don’t rewrite history) |

---

## 8. Critical alert path

```text
Observation
     ↓
IndicatorValue
     ↓
RuleEvaluation
     ↓
EvidenceItem / EvidencePackage
     ↓
Critical Alert
```

**Not required** on this path:

```text
LLM
Agent
AgentRun
Recommendation
Analysis
```

**BLOCKING if violated.** Current ADRs do **not** violate this. Freeze: Alerts module **rejects** critical Alert creation without RuleEvaluation + EvidencePackage.

---

## 9. AI boundary

Valid path only:

```text
AgentRun → Analysis / Recommendation → Human review → Decision → Action → Outcome
```

| Forbidden | Frozen |
|-----------|--------|
| AgentRun → Decision | Yes |
| AgentRun → Action | Yes |
| AgentRun → Outcome | Yes |
| Agent modifies RuleVersion / activates rules | Yes |
| Agent creates Decision | Yes |
| Agent executes Actions | Yes |
| Agent mutates historical Evidence | Yes |
| Agent hides uncertainty | Yes |
| Agent unaudited | No — AgentRun + AuditEvent required |

**AI = optional capability.** MVP/pilot can run rules-only DSS. Later enable Evidence / Explanation / Context / Anomaly agents without changing the critical path.

---

## 10. Temporal model (canonical clocks)

**FROZEN:** do not collapse to a single `created_at`. Technical ORM timestamps may exist **in addition**, never as substitutes.

| Canonical domain clock | Meaning | Typical owner |
|------------------------|---------|----------------|
| `observed_at` | Phenomenon time | Observation |
| `processed_at` | Ingest/quality/transform assessment time | Ingestion / DataQuality |
| `evaluated_at` | Rule evaluation time | RuleEvaluation |
| `alerted_at` | Alert created / first raised | Alert |
| `reviewed_at` | Review/ack/status-change times | Alert status history |
| `decided_at` | Human Decision time | Decision |
| `acted_at` | Action executed/recorded | Action |
| `observed_outcome_at` | Outcome / later observation time | Outcome / linked Observation |

Late observations and later evaluations **append**; they do not overwrite original `observed_at` / `evaluated_at`.

Aliases already used in Phase 1 docs (`recorded_at`, `ingested_at`, Alert.`created_at`) map onto this table — implementation should persist **canonical names** (or both with documented mapping). Corrected in domain/architecture docs in this review.

---

## 11. PostgreSQL / PostGIS

| Decision | Class |
|----------|--------|
| PostgreSQL as primary store | **FROZEN** |
| Enable PostGIS on day one | **OPEN BUT NON-BLOCKING** |
| Spatial-ready from the start | **FROZEN** |

**Spatial-ready means:** Entity / Zone / Station carry an opaque spatial field (GeoJSON/WKT/`geometry` bytes TBD) so later PostGIS enablement does **not** require re-modeling identity. Rich GIS queries, tiles, and topology are **LATER**.

Do **not** choose a primary database that cannot add spatial later. PostgreSQL satisfies this.

---

## 12. Object storage placement

| Live in PostgreSQL | May live in object storage |
|--------------------|----------------------------|
| EvidenceItem / EvidencePackage metadata | Raw ingest files / datasets |
| ids, kinds, labels, FKs, gaps, conflicts | Scientific PDFs / large documents |
| RuleVersion documents (declarative JSON) | AgentRun large traces |
| DssContextSnapshot metadata + hash (+ JSONB if small) | Oversized snapshot payload |
| AuditEvent | |

Every object: stable key + `content_hash` + size + content-type.

---

## 13. Async jobs (Redis + ARQ)

| Process | Async allowed? | Notes |
|---------|----------------|-------|
| Ingestion of files/APIs | Yes | SHOULD |
| Data quality / processing | Yes | after durable Observation |
| Indicator recompute (heavy) | Yes | |
| **RuleEvaluation (critical path)** | **Must remain possible in-process / sync** | Queue may *schedule* a job; evaluator must not *require* Redis |
| Evidence + critical Alert persist | Same transaction as evaluation when creating critical alerts | |
| AI AgentRun | Yes | optional |
| Notifications | Yes | |
| Reports / background validation | Yes | LATER |

**FROZEN:** Redis/ARQ outage must **not** prevent recording an Observation or running a RuleEvaluation when the API process can reach PostgreSQL. Jobs are an optimization and a decoupling mechanism, not the source of truth.

ARQ vs equivalent: OPEN behind a port.

---

## 14. Identity / RBAC (pilot minimum)

```text
IdP authenticates a subject
     ↓
BALIZA maps sub → Actor (domain identity)
     ↓
RBAC on Actor
```

**Actor ≠ Identity Provider user.** Audit uses `actor_id`.

### Minimum permissions (conceptual)

| Permission | Intent |
|------------|--------|
| `decision.record` | Create Decision + bind snapshot |
| `action.record` | Record Action after Decision |
| `rule.activate` | Activate published RuleVersion |
| `protocol.activate` | Activate ProtocolVersion |
| `evidence.manage` | Attach/assemble evidence (not mutate history) |
| `alert.acknowledge` | Awareness only ≠ Decision |

Roles (working labels): operator, manager, scientist, admin, auditor. Fine matrix = OPEN. Authn product (Keycloak/Auth0) = OPEN.

Pilot **MUST** enforce `decision.record` and `rule.activate`. Full IdP productization can land with Phase 11 but a real Decision in a pilot **cannot** skip Actor+RBAC.

---

## 15. Audit vs observability

| Business audit | Technical observability |
|----------------|-------------------------|
| AuditEvent | JSON logs |
| Decision, Action | Metrics (OTel/Prometheus) |
| RuleVersion activation | Traces (OTel) |
| Alert / Evidence lifecycle records | Worker/DB/LLM failures, latency |
| RuleEvaluation / AgentRun as **domain records** | |

**FROZEN:** logs do not replace AuditEvent. LLM latency is observability, not a Decision.

---

## 16. Failure semantics

**FROZEN:** `No Data ≠ No Risk`.

Scope health: `OK | DEGRADED | INSUFFICIENT_DATA | UNKNOWN`.

| Failure | Representation |
|---------|----------------|
| Source outage | INSUFFICIENT_DATA / gaps; no false green |
| Invalid data | DataQuality invalid; excluded from critical rules |
| Stale data | quality/latency facet; rule quality gates |
| Indicator failure | DEGRADED; no silent OK |
| Rule failure | AuditEvent; no Alert from failed eval |
| Database outage | API cannot persist Decision; fail closed |
| LLM outage | AI section DEGRADED/UNKNOWN; **rules path continues** |
| Contradictory evidence | EvidencePackage.conflicts |

---

## 17. AI-optional pilot

**FROZEN:** BALIZA MVP **can function fully without AI**.

AI is a **capability flag**. Enabling Evidence / Explanation / Context / Anomaly agents later must not modify Observation → … → Critical Alert.

---

## 18. Frontend

**Vite vs Next.js = OPEN BUT NON-BLOCKING.**

No domain or backend architectural reason to close this before Phase 3. UI remains a client of the application layer.

---

## 19. ADR consistency

| Check | Result |
|-------|--------|
| ADR-001 vs domain freeze | Aligned |
| ADR-002 domain vs FastAPI | Aligned if adapters only |
| ADR-003 vs Evidence Chain | Aligned |
| ADR-004 vs Inv 3/13/17 | Aligned; hashing tightened in 2.5 |
| ADR-005 vs no event sourcing / no Kafka | Aligned |
| ADR-006 vs no LLM on rules | Aligned |
| ADR-007 vs optional AI | Aligned |
| ADR-008 vs Actor | Aligned; permissions list completed in 2.5 |
| ADR-009 audit ≠ logs | Aligned |
| ADR-010 Compose vs no IaC in Phase 2 | Aligned |

### Issues (non-fundamental)

```text
ISSUE: docs/12 context diagram Domain → DB
SOURCE: docs/12 §4–5 vs ADR-001/002
CONFLICT: Dependency rule
PROPOSED RESOLUTION: Correct diagrams
STATUS: SAFE TO CHANGE (done)
```

```text
ISSUE: DssContextSnapshot not a first-class glossary type
SOURCE: Inv 17 + Decision.dss_context_snapshot_ref vs docs/07
CONFLICT: Ambiguity for implementers (live join vs freeze)
PROPOSED RESOLUTION: First-class entity + ADR-011
STATUS: SAFE TO CHANGE (done)
```

```text
ISSUE: Temporal field aliases (created_at / recorded_at) vs canonical clocks
SOURCE: docs/08 vs Phase 2.5 clock list
CONFLICT: Naming only, not meaning
PROPOSED RESOLUTION: Canonical mapping table
STATUS: SAFE TO CHANGE (done)
```

No `REQUIRES HUMAN REVIEW` product conflicts detected.

---

## 20. Implementation boundary (Phase 3 conceptual order)

Roadmap Phase 3 is titled **Data ingestion**, but ingestion **must not** be the first commit. Hidden debt otherwise: schema without invariants, ingest without Actor/Audit.

**Justified order** (bootstrap **inside** Phase 3, then ingest):

```text
1.  Repository / project structure (domain / application / infrastructure)
2.  Domain primitives (ids, EpistemicLabel, clocks, Uncertainty)
3.  Domain entities (subset: Actor, Observation, … growing)
4.  Domain invariants as executable tests (even if persistence is fake)
5.  Application layer (use cases / services)
6.  Persistence ports
7.  Database schema + migrations (PostgreSQL)
8.  Audit foundation (AuditEvent)
9.  Observation + DataQuality persistence (ingestion vertical)
10. Rule evaluation foundation (can be stub evaluator + immutable RuleVersion)
11. Evidence foundation
12. Alert foundation (critical path, no AI)
13. DSS foundation (DssPackage)
14. Decision + DssContextSnapshot foundation
15. Workers (ingest/jobs) — after sync path works
16. AI capability — optional, later (roadmap Phase 9)
17. UI — later (roadmap Phase 10)
```

**Why change vs “ingest code first”:** Evidence Chain and Inv 17 cannot be bolted on after a naive ingest table. Ingestion remains the **first operational vertical**, after the skeleton exists.

Do **not** implement items 16–17 in Phase 3.

---

## 21. Technical debt check

| Risk | Assessment |
|------|------------|
| Premature microservices | Avoided |
| Excessive eventing / Kafka | Avoided |
| Excessive async on critical path | Mitigated (sync RuleEvaluation required) |
| Provider lock-in | Mitigated (ports) |
| Mutable history | Mitigated if snapshot+versions enforced |
| Hidden LLM on alerts | Mitigated by module rules |
| Ball-of-mud monolith | **Residual** — enforce packages/linters (R-H1) |
| Snapshot-as-live-join | **Residual** — tests required (R-H2) |
| Redis as hidden SPOF | **Residual** — documented independence |
| Hashing skipped “for later” | **Residual** — now a frozen requirement |

No new structural over-engineering introduced in Phase 2.

---

## 22. Changes applied in Phase 2.5

- This document (`docs/14-architecture-review.md`)
- `ADR-011-dss-snapshot.md`
- Glossary + domain model: `DssContextSnapshot`; canonical clocks
- Invariant 17 payload list completed
- `docs/12` diagrams and clocks
- ADR-004 hashing; ADR-008 permissions; ADR-005 critical-path independence
- Roadmap / README status

---

## 23. Freeze statement

> Modular Monolith + workers, PostgreSQL + S3-compatible storage, LLM-free critical alerts, immutable DssContextSnapshot, ports/adapters, and optional AI are **stable enough to implement**.  
> Changing a FROZEN item requires an explicit ADR revision. Human-in-the-loop or Evidence Chain changes require **human review**.

---

## Related documents

- [12-technical-architecture.md](./12-technical-architecture.md)
- [13-technical-risks.md](./13-technical-risks.md)
- [architecture/ADR-011-dss-snapshot.md](./architecture/ADR-011-dss-snapshot.md)
- [09-domain-invariants.md](./09-domain-invariants.md)
- [roadmap.md](./roadmap.md)
