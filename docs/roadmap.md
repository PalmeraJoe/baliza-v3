# Roadmap

## Status

Phases are ordered by **architectural dependency**. Dates and staffing are `TBD`.

- **Phase 0 — Foundation — COMPLETED**
- **Phase 1 — Core Domain Model — COMPLETED**
- **Phase 1.5 — Domain Review & Freeze — COMPLETED** (see `docs/11-domain-review.md`)
- **Phase 2 — Technical Architecture — COMPLETED** (see `docs/12-technical-architecture.md`, `docs/architecture/`)
- **Phase 2.5 — Architecture Review & Freeze — COMPLETED** (see `docs/14-architecture-review.md`)
- **Phase 3 — Technical foundation & domain core — COMPLETED** (see `docs/15-phase3-implementation.md`)
- **Phase 3.5 — Implementation audit — COMPLETED** (see `docs/16-phase3-audit.md`)
- **Phase 3.6 — Remediation & re-audit — COMPLETED** (see `docs/17-phase3.6-remediation.md`). Conclusion: **PHASE 3 VERIFIED**
- **Phase 4 — Evidence → Alerts → DSS — VERIFIED** after Phase 4.1 (`docs/20-phase4.1-remediation.md`)
- **Phase 5 — Scientific semantics & persistence integrity — VERIFIED** (`docs/22-phase5-audit.md`)
- **Phase 6 — Scientific & operational DSS layer — VERIFIED** (`docs/24-phase6-audit.md`)
- **Phase 7 — Coral bleaching scientific foundation — RECORDED, models not authorized** (`docs/34-phase7-audit.md`)
- **Phase 7.11 — Integrated Spot Intelligence — PARTIAL** (`docs/55-phase7.11-integrated-spot-intelligence.md`)
- **Phase 7.12 — End-to-end scientific DSS — DEMONSTRATED** (`docs/56-phase7.12-end-to-end-scientific-dss-integration.md`)
- **Phase 7.13 — Pilot Readiness Review — COMPLETED** (`docs/57-phase7.13-pilot-readiness-review.md`)
- **Phase 7.14 — BALIZA Visual MVP — COMPLETED** (`docs/58-phase7.14-baliza-visual-mvp.md`)
- **Phase 7.15 — Scientific Pilot Preparation / IMR — COMPLETED** (`docs/59-phase7.15-scientific-pilot-imr-specification.md`): meeting-ready data/governance/validation spec; connector not implemented; ML still not authorized
- Next: IMR meeting / answers → choose next state A–E — **not started automatically**
- Phases 8–13 — pending

**Domain and architecture soft freeze** remain in force. Implementation must not violate FROZEN items in `docs/14-architecture-review.md`.

---

## Sequence overview

```text
Phase 0    Foundation (documentation)           ✓ COMPLETED
Phase 1    Core domain model                    ✓ COMPLETED
Phase 1.5  Domain review & soft freeze          ✓ COMPLETED
Phase 2    Technical architecture               ✓ COMPLETED
Phase 2.5  Architecture review & freeze         ✓ COMPLETED
Phase 3    Technical foundation & domain core   ✓ COMPLETED
Phase 3.6  Remediation & re-audit               ✓ PHASE 3 VERIFIED
Phase 4    Evidence → Alerts → DSS              verified after 4.1 (docs/20)
Phase 5    Semantics, canonical links, indicator immutability   verified (docs/22)
Phase 6    Scientific & operational DSS layer   verified (docs/24)
Phase 7    Scientific foundation recorded; ML and RBM not authorized (docs/34)
Phase 7.11 Integrated Spot Intelligence PARTIAL (docs/55)
Phase 7.12 E2E scientific DSS demonstrated on public data (docs/56)
Phase 7.13 Pilot Readiness Review (docs/57) — scientific pilot next; ML after gate only
Phase 7.14 BALIZA Visual MVP (docs/58) — UI presentation of existing DSS
Phase 7.15 Scientific Pilot Preparation / IMR (docs/59) — specification only; await partner answers

Post–Phase 7.13 intended sequence:
BALIZA FOUNDATION → PUBLIC SCIENTIFIC DATA → END-TO-END DSS
  → PILOT READINESS REVIEW → SCIENTIFIC PILOT (IMR)
  → SCIENTIFIC VALIDATION → ML AUTHORIZATION GATE
  → [ONLY IF PASSED] PREDICTIVE MODEL → COMMERCIAL PILOT

# Original outline below is not the next implementation phase.
# Evidence layer, alert engine, DSS capture, AI, UI, auth, QA, pilot.
```

### Roadmap shift note (Phase 1.5)

Previously Phase 2 was “Data ingestion.” Phase 1.5 inserts **Technical Architecture** as Phase 2 and shifts implementation phases by +1 so architecture is designed against the frozen domain before ingestion code.

---

## Rationale for ordering (and one deliberate shift)

### Why Evidence before Alerts before DSS (implementation)

Alerts without evidence packages create uncorrectable audit debt. DSS without alerts/evidence has nothing structured to support.

### Why AI agents after Evidence + Alerts (+ DSS skeleton)

Agents must bind to real evidence and rule traces. A thin DSS can exist without agents; agents enrich it later.

### Why Frontend after DSS conceptual/API surface

UI should consume stable DSS packages.

### Why Auth is late but Actor is early

Actor exists in the domain (Phase 1). Full authn/authz implementation remains before serious pilot.

### Why Testing phase is listed late but practiced early

System-level validation gates come late; unit/domain tests begin as soon as code exists.

### Why Scientific validation / pilot is last among listed phases

Operational pilot needs working chain + auth + UX + agreed indicators/rules. Thresholds must not go `active` without scientific process even if tooling exists earlier in `draft`.

---

## Phase details

### Phase 0 — Foundation

**Status:** **COMPLETED**  
**Deliverables:** `README.md`, `AGENTS.md`, `docs/00`–`06`, initial roadmap.

---

### Phase 1 — Core domain model

**Status:** **COMPLETED**  
**Deliverables:** `docs/07`–`10` (glossary, model, invariants, open questions).

---

### Phase 1.5 — Domain review & freeze

**Goal:** Consistency audit; classify open questions; soft-freeze domain for architecture.

**Status:** **COMPLETED**  
**Deliverables:** `docs/11-domain-review.md`; updates to 07–10; Inv 17 (Decision context freeze).

**Exit criteria:** No BLOCKERS for architecture; frozen concepts listed; READY FOR PHASE 2 declared in review.

---

### Phase 2 — Technical architecture

**Goal:** Design technical architecture **against the soft-frozen domain** — modular boundaries, data flow, persistence strategy, ADRs — without implementing application code.

**Status:** **COMPLETED**

**Deliverables:**

- `docs/12-technical-architecture.md`
- `docs/13-technical-risks.md`
- `docs/architecture/ADR-001` … `ADR-010`

**Exit criteria:** Acceptance A–J satisfied by design; modular monolith + workers chosen; critical path LLM-free; READY FOR PHASE 3 (gated by Phase 2.5 freeze).

---

### Phase 2.5 — Architecture review & freeze

**Goal:** Verify architecture can be implemented without structural ambiguity; freeze vs open classification.

**Status:** **COMPLETED**

**Deliverables:** `docs/14-architecture-review.md`; `ADR-011-dss-snapshot.md`; documentary corrections (snapshot entity, clocks, ports diagrams, hashing, RBAC minimum).

**Exit criteria:** No BLOCKERS; DssContextSnapshot first-class and immutable; AI optional; critical path LLM-free.

---

### Phase 3 — Technical foundation & domain core

**Goal:** Create repository/module skeleton, domain primitives, persistence ports, PostgreSQL schema, AuditEvent, then ingest Observations with provenance.

**Depends on:** Phase 2.5 architecture freeze.

**Does not include:** UI, production agents, DSL, scientific thresholds.

**Status:** **COMPLETED**

**Deliverables:** `src/baliza/` domain/application/infrastructure/interfaces; Alembic `0001_phase3`; pytest suite; ADR-012.

**Exit criteria:** Domain tests without infra; critical path sync without LLM/Redis; Decision requires Actor + DssContextSnapshot; ACKNOWLEDGED ≠ DECISION.

**Internal order:** see `docs/14-architecture-review.md` §20 (structure → domain → ports → schema → audit → observations before workers/AI/UI).

---

### Phase 4 — Indicators

**Goal:** Indicator registry, computation from quality-aware inputs, versioned definitions.

---

### Phase 5 — Rules engine

**Goal:** Deterministic evaluation of versioned rules; persist RuleEvaluations with threshold snapshots; no protocol auto-execution.

**Note:** No scientifically unvalidated thresholds marked `active` without scientific process.

---

### Phase 6 — Evidence layer

**Goal:** EvidencePackage assembly, gaps/conflicts, chain links.

---

### Phase 7 — Alert engine

**Goal:** Alert lifecycle, linkage to evidence and rules, history.

---

### Phase 8 — DSS

**Goal:** DSS package assembly; options from protocols; decision capture with **context freeze**; FACT/INFERENCE/RECOMMENDATION/DECISION separation; outcome hooks.

**Note:** Usable without AI agents.

---

### Phase 9 — AI agents

**Goal:** Orchestrator + Evidence/Explanation/(Context) agents; optional Anomaly agent; structured I/O and hard limits.

---

### Phase 10 — Frontend / dashboard

**Goal:** Operator/manager interfaces; epistemic labeling in UX.

---

### Phase 11 — Authentication / permissions

**Goal:** Real authn/authz aligned with Actor/Role.

**Pilot blocker:** Serious pilot should not proceed without this (or approved interim control).

---

### Phase 12 — Testing / validation (engineering)

**Goal:** Coverage gates, deterministic replay, audit tests, agent epistemic guardrails.

---

### Phase 13 — Scientific validation / pilot

**Goal:** Domain expert validation of indicators/thresholds/protocols; controlled pilot; feedback into rule versions.

---

## Explicitly out of roadmap detail (for now)

- Multi-region HA
- Mobile offline field app (unless Q51 forces earlier)
- Public open data portal
- ML predictive models as primary alerting

---

## Open Questions

See classified list in [10-domain-open-questions.md](./10-domain-open-questions.md) and freeze in [11-domain-review.md](./11-domain-review.md).

1. Compress frontend + auth for a closed pilot? `TBD`
2. First pilot indicator/rule scope? `TBD`
3. Parallel tracks after architecture? Acceptable if frozen domain holds. `TBD`

---

## Related documents

- [00-foundation.md](./00-foundation.md)
- [07-domain-glossary.md](./07-domain-glossary.md)
- [08-domain-model.md](./08-domain-model.md)
- [09-domain-invariants.md](./09-domain-invariants.md)
- [10-domain-open-questions.md](./10-domain-open-questions.md)
- [14-architecture-review.md](./14-architecture-review.md)
- [11-domain-review.md](./11-domain-review.md)
