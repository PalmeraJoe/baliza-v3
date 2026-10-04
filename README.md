# BALIZA V3

**Decision Support System (DSS)** for marine/coastal ecosystem management, resorts, and/or marine protected areas (MPAs).

## What it is

BALIZA V3 transforms heterogeneous environmental data, observations, indicators, scientific sources, deterministic rules, and AI-assisted analysis into:

- interpretable information;
- traceable alerts;
- actionable options for a human decision-maker.

The final operational decision always remains under human control.

## Problem it addresses

Managers of marine/coastal zones need to integrate fragmented environmental signals, uncertain evidence, and protocols of action into decisions that are auditable, timely, and scientifically grounded. BALIZA provides structured support for that process.

## What it is NOT

- Not an autonomous predictor.
- Not an automated operational decision-maker.
- Not a system that executes closures, restrictions, or interventions without a human decision.
- Not a substitute for scientific validation of thresholds, rules, or protocols.

## Fundamental principles

1. **Human-in-the-loop** — humans decide; the system supports.
2. **Evidence before inference** — facts and provenance precede interpretation.
3. **Full traceability** — every alert, recommendation, and decision must be reconstructable.
4. **Explicit uncertainty** — unknowns and confidence must be visible.
5. **Deterministic rules for critical thresholds** — critical logic is versioned and auditable; not hidden in AI prompts.
6. **Separation of concerns** — data ≠ evidence ≠ rules ≠ protocols ≠ alerts ≠ DSS ≠ decisions ≠ actions.

## Conceptual chain

```text
DATA → QUALITY/NORMALIZATION → INDICATORS → RULES + AI ANALYSIS
  → EVIDENCE → ALERTS/STATE → DSS → ACTION OPTIONS
  → HUMAN DECISION → ACTION → OUTCOME → NEW EVIDENCE
```

## Current status

**Phase 0 — Foundation — COMPLETED**  
**Phase 1 — Core Domain Model — COMPLETED**  
**Phase 1.5 — Domain Review & Soft Freeze — COMPLETED**  
**Phase 2 — Technical Architecture — COMPLETED**  
**Phase 2.5 — Architecture Review & Freeze — COMPLETED**  
**Phase 3 — Technical foundation & domain core — VERIFIED** after Phase 3.6 (`docs/17-phase3.6-remediation.md`)  
**Phase 4 — Evidence → Alerts → DSS — VERIFIED** after Phase 4.1 (`docs/20-phase4.1-remediation.md`)  
**Phase 5 — Scientific semantics & persistence integrity — VERIFIED** (`docs/21-phase5-implementation.md`, `docs/22-phase5-audit.md`)  
**Phase 6 — Scientific & operational DSS layer — VERIFIED** (`docs/23-phase6-implementation.md`, `docs/24-phase6-audit.md`)  
**Phase 7 — Scientific foundation recorded; models not authorized** (`docs/25-phase7-scientific-foundation.md`, `docs/34-phase7-audit.md`)

Python package under `src/baliza/` (domain / application / infrastructure / interfaces).  
No UI, Redis, LLM, or Kafka.

### Run tests

```text
py -3 -m pip install -e ".[dev]"
py -3 -m pytest
```

### Dev API (in-memory demo only)

```text
py -3 -m uvicorn baliza.interfaces.api.app:app --reload
```

Domain freeze: [docs/11-domain-review.md](./docs/11-domain-review.md)  
Architecture freeze: [docs/14-architecture-review.md](./docs/14-architecture-review.md)  
Technical architecture: [docs/12-technical-architecture.md](./docs/12-technical-architecture.md)

## Documentation

| Document | Purpose |
|----------|---------|
| [AGENTS.md](./AGENTS.md) | Technical constitution for humans and AI agents working on this project |
| [docs/00-foundation.md](./docs/00-foundation.md) | Scope of Phase 0, non-goals, and open architectural questions |
| [docs/01-product-definition.md](./docs/01-product-definition.md) | Problem, users, use cases |
| [docs/02-conceptual-architecture.md](./docs/02-conceptual-architecture.md) | Conceptual layers and boundaries |
| [docs/03-dss-principles.md](./docs/03-dss-principles.md) | DSS behavior and fact/inference/recommendation/decision separation |
| [docs/04-rules-and-protocols.md](./docs/04-rules-and-protocols.md) | Rules, indicators, alerts, protocols, versioning |
| [docs/05-ai-agents.md](./docs/05-ai-agents.md) | AI agent roles, limits, autonomy |
| [docs/06-evidence-and-traceability.md](./docs/06-evidence-and-traceability.md) | Evidence Chain and auditability |
| [docs/07-domain-glossary.md](./docs/07-domain-glossary.md) | Ubiquitous language / term definitions |
| [docs/08-domain-model.md](./docs/08-domain-model.md) | Logical domain model, relations, versioning, domain events |
| [docs/09-domain-invariants.md](./docs/09-domain-invariants.md) | Always-true domain constraints |
| [docs/10-domain-open-questions.md](./docs/10-domain-open-questions.md) | Classified unresolved domain questions |
| [docs/11-domain-review.md](./docs/11-domain-review.md) | Phase 1.5 consistency audit and soft freeze |
| [docs/12-technical-architecture.md](./docs/12-technical-architecture.md) | Phase 2 technical architecture |
| [docs/13-technical-risks.md](./docs/13-technical-risks.md) | Technical risk register |
| [docs/14-architecture-review.md](./docs/14-architecture-review.md) | Phase 2.5 architecture freeze |
| [docs/15-phase3-implementation.md](./docs/15-phase3-implementation.md) | Phase 3 implementation notes |
| [docs/16-phase3-audit.md](./docs/16-phase3-audit.md) | Phase 3.5 audit (historical: needs fixes) |
| [docs/17-phase3.6-remediation.md](./docs/17-phase3.6-remediation.md) | Phase 3.6 remediation and re-audit |
| [docs/18-phase4-implementation.md](./docs/18-phase4-implementation.md) | Phase 4 DSS flow (ready for audit) |
| [docs/architecture/](./docs/architecture/) | ADRs 001–012 |
| [docs/roadmap.md](./docs/roadmap.md) | Phased delivery plan |

## Working rules for contributors

- Do not start Phase 4+ product features (rich indicators, full ingest pipelines, UI, AI) without keeping the frozen critical path intact.
- Do not change FROZEN architecture or domain concepts without an explicit ADR/domain revision.
- Do not place LLMs on the critical alert path.
- Do not reconstruct a Decision from live joins; use `DssContextSnapshot`.
- Do not invent scientific thresholds or present hypotheses as requirements.
- Mark unresolved items as `TBD` / classified open questions.
- Read [AGENTS.md](./AGENTS.md), domain docs, and ADRs before implementing.
