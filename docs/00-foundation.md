# 00 — Foundation (Phase 0)

## Purpose of this document

Defines the scope of **Phase 0: Foundation**, what is intentionally out of scope, and the open decisions that later phases must resolve before implementation.

Phase 0 produces **documentation only**. No application runtime exists yet.

---

## In scope (Phase 0)

- Product definition (problem, users, use cases)
- Conceptual architecture (layers and boundaries)
- DSS principles (human-in-the-loop, fact vs inference vs recommendation vs decision)
- Rules vs protocols vs agents vs alerts
- Evidence and traceability strategy (Evidence Chain)
- Project constitution (`AGENTS.md`)
- Roadmap of subsequent phases
- Explicit `TBD` and Open Questions

---

## Explicit non-goals (Phase 0)

Do **not** implement or specify as final:

- Frontend / dashboard UI
- Backend services / API contracts as implementation
- Database schemas as definitive designs
- Docker / deployment
- Authentication / authorization implementation
- Functional AI agents
- Data pipelines / ETL code
- ML models
- External integrations (sensors, APIs, GIS platforms)
- Concrete technology stack choices (language, framework, cloud) except where unavoidable for clarity of concepts

Hypothetical technology mentions, if any, are illustrative only and marked `TBD`.

---

## Product invariant (non-negotiable)

```text
BALIZA supports decisions. Humans make decisions. Actions follow human decisions.
```

No document in this repository may imply that BALIZA automatically:

- closes areas;
- restricts access;
- executes protocols;
- changes operational status without a recorded human decision.

---

## Traceability invariant

At any time, for any important alert or DSS package, the system must be designed to answer:

| Question | Layer |
|----------|-------|
| What occurred? | Alert / state |
| When? | Temporal context |
| Where? | Spatial entity / zone |
| Which data indicate it? | Data / indicators |
| Which evidence was used? | Evidence layer |
| Which rule or analysis produced it? | Rule engine / agents |
| What uncertainty exists? | Quality + confidence |
| What information is missing? | Gap analysis |
| What action options exist? | Protocols / DSS |
| Who decided? | Human decision record |
| What action was taken? | Action record |
| What was the outcome? | Outcome / feedback |

---

## Conceptual chain (canonical)

```text
DATOS
  ↓
CALIDAD / NORMALIZACIÓN
  ↓
INDICADORES
  ↓
REGLAS + ANÁLISIS IA
  ↓
EVIDENCIA
  ↓
ALERTAS / ESTADO
  ↓
DSS
  ↓
OPCIONES DE ACTUACIÓN
  ↓
DECISIÓN HUMANA
  ↓
ACCIÓN
  ↓
OBSERVACIÓN DEL RESULTADO
  ↓
NUEVA EVIDENCIA
```

This chain is the reference for all subsequent design. Layers may be refined; they must not be collapsed in a way that breaks auditability.

---

## Open Questions

These questions are intentionally unresolved in Phase 0:

1. **Deployment context** — single resort, multi-site MPA network, or multi-tenant SaaS? `TBD`
2. **Primary spatial model** — zones, grids, polygons, stations, or hybrid? `TBD`
3. **Primary domains of indicators** — water quality, thermal stress, biodiversity, pollution, human pressure, etc.? Priority set `TBD` (needs domain expert input)
4. **Authority model** — who can approve rule/threshold changes? Scientific board vs operator roles? `TBD`
5. **Offline / degraded mode** — required for field operations? `TBD`
6. **Retention and audit storage** — legal/regulatory requirements for evidence retention? `TBD`
7. **Language / locale** — product UI and scientific content languages? `TBD`
8. **Technology stack** — deferred until after core domain model (Phase 1+) `TBD`

Resolved answers must be documented before they drive implementation.

---

## Consistency check (Phase 0 exit criteria)

Phase 0 documentation exit:

- [x] README, AGENTS.md, and docs set exist
- [x] DSS is human-in-the-loop by design
- [x] Rules ≠ protocols ≠ agents ≠ alerts
- [x] Critical thresholds are not owned by LLMs
- [x] Evidence Chain is defined conceptually
- [x] Open questions are listed, not silently assumed
- [ ] Domain expert review of product definition and rule/protocol concepts (`TBD`)
- [ ] Stakeholder confirmation of user categories and use cases (`TBD`)

**Phase 0 status: COMPLETED** (documentation). Domain modeling continues in Phase 1 (`docs/07`–`10`).
