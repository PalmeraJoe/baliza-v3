# 10 — Domain Open Questions

## Purpose

Explicit list of questions **not resolved** as product/scientific truth.  
Do not invent answers. Architecture may **parametrize** ARCHITECTURE-RELEVANT items.

Classification (Phase 1.5):

| Class | Meaning |
|-------|---------|
| **BLOCKER** | Must resolve before technical architecture |
| **ARCHITECTURE-RELEVANT** | Conditions tech design; keep parameterized |
| **DOMAIN** | Later domain refinement without base architecture rewrite |
| **SCIENTIFIC** | Needs scientific validation |
| **PRODUCT** | Product decision |
| **PILOT** | Depends on first pilot scope |
| **LEGAL** | Legal/compliance |
| **LATER** | Can wait |
| **CLOSED** | Resolved for architecture soft freeze (see notes) |

Full audit: [11-domain-review.md](./11-domain-review.md).

**BLOCKERS:** none after Phase 1.5.

---

## Tenancy & deployment

1. **PILOT / PRODUCT** — Is multi-tenant required for the first pilot, or single-organization only?
2. **ARCHITECTURE-RELEVANT** — Cardinality and isolation rules for `Tenant` vs `Deployment`? (Design with optional `tenant_id`.)
3. **ARCHITECTURE-RELEVANT** — Are “environments” (pilot/staging/prod) Deployments or a separate concept?

---

## Spatial model & entity hierarchy

4. **DOMAIN / PILOT** — Final `Entity` kind taxonomy?
5. **ARCHITECTURE-RELEVANT** — Is `Zone` a subtype of `Entity`, a child, or a spatial facet? (Support flexible hierarchy; keep Zone ≠ Station.)
6. **DOMAIN** — Zone vs Area vs Site naming?
7. **ARCHITECTURE-RELEVANT** — Geometry representation? (Opaque spatial payload until chosen.)
8. **DOMAIN** — Station membership: one Zone only or many?
9. **DOMAIN** — Nested / overlapping zones allowed?
10. **DOMAIN / LATER** — Separate continuous **State** object beside **Alert**?

---

## Cardinalities & identity

11. **ARCHITECTURE-RELEVANT** — EvidenceItem↔EvidencePackage sharing?
12. **ARCHITECTURE-RELEVANT** — One EvidencePackage per Alert vs version chain?
13. **DOMAIN** — Multi-RuleEvaluation severity merge policy?
14. **DOMAIN** — May one Decision cover alerts across multiple Entities/Zones?
15. **ARCHITECTURE-RELEVANT** — Observation identity granularity?
15b. **DOMAIN** — **Processed Data** as first-class entity vs Observation + DataQuality + transform refs? **Lean kept:** latter unless pilot requires distinct type.

---

## Severity, status, workflow

16. **DOMAIN / PRODUCT** — Final Severity taxonomy?
17. **DOMAIN** — Final AlertStatus enum?
18. **PRODUCT / DOMAIN** — Close alerts without Decision? Reason codes?
19. **PRODUCT** — Acknowledgment reason code required?
20. **DOMAIN** — Deduplication / hysteresis policy?

---

## Rules & indicators (scientific / technical)

21. **ARCHITECTURE-RELEVANT** — Rule expression language? (Pluggable evaluator later.)
22. **ARCHITECTURE-RELEVANT** — Indicator specification language?
23. **DOMAIN / SCIENTIFIC** — Boundary between Indicator formulas and Rule thresholds?
24. **SCIENTIFIC / PILOT** — Minimum viable indicator set?
25. **SCIENTIFIC** — Threshold validation process and owners? (**No numeric thresholds approved.**)
26. **PRODUCT / SCIENTIFIC** — Dual-control for RuleVersion activation?

---

## Uncertainty & quality

27. **SCIENTIFIC / ARCHITECTURE-RELEVANT** — Quantitative uncertainty vs structured facets? (Support facet structure now.)
28. **SCIENTIFIC / ARCHITECTURE-RELEVANT** — DataQuality scoring / minima for critical rules?
29. **PRODUCT / LATER** — How to present “no data” without implying safety?

---

## Evidence & DSS

30. **CLOSED (architecture)** — `Evidence` is conceptual; persist `EvidenceItem` + `EvidencePackage`.
31. **CLOSED** — Freeze DSS context at Decision time is **mandatory**. Entity = `DssContextSnapshot` (Immutable). Remaining OPEN: JSON encoding and object-store size threshold only (ADR-011).
32. **PRODUCT** — May DSS highlight a default Recommendation?
33. **PRODUCT / DOMAIN** — Free-form Decisions vs protocol-option-only?
34. **PRODUCT / DOMAIN** — Multi-party / co-signature Decisions?
35. **PRODUCT / LATER** — Time-bounded Decisions?

---

## AI agents

36. **ARCHITECTURE-RELEVANT** — Confirm hard ban: agents cannot create critical Alerts alone? **Frozen lean assumption: yes.** Formal product sign-off still welcome.
37. **PRODUCT / ARCHITECTURE-RELEVANT** — Auto-enrich every alert vs on-demand?
38. **PRODUCT** — May Explanation Agent draft Decision justifications?
39. **LEGAL / ARCHITECTURE-RELEVANT** — Prompt/trace retention and privacy?
40. **ARCHITECTURE-RELEVANT / LEGAL** — Model hosting / data residency?

---

## Governance, permissions, legal

41. **PRODUCT / LATER** — Role permission matrix (Actor/Role exist; matrix later / Phase 10).
42. **PRODUCT / LATER** — Version governance SLAs?
43. **LEGAL** — Retention periods?
44. **LEGAL** — E-signature requirements for Decisions?
45. **LEGAL / PILOT** — Regulatory constraints by jurisdiction?
46. **PRODUCT / LEGAL** — Public vs internal alert visibility?

---

## Outcomes & integrations

47. **ARCHITECTURE-RELEVANT** — External systems of record for Action execution?
48. **DOMAIN** — Formal Outcome evaluation method?
49. **DOMAIN** — Outcomes → proposed rule revisions without auto-changing rules?

---

## Product scope

50. **PILOT / PRODUCT** — First pilot vertical?
51. **PILOT / ARCHITECTURE-RELEVANT** — Offline / degraded mode required?
52. **PRODUCT / PILOT** — Locale / languages?

---

## Intentionally out of domain resolution

Do **not** close by inventing technology:

- Programming language, frameworks, databases, cloud providers
- API / UI designs
- ORM / DDL
- LLM / GIS vendors

---

## Phase 5 closures

32. **CLOSED** — Structural relations (indicator value ↔ observation, rule evaluation ↔ indicator value, evidence package ↔ item, alert ↔ rule evaluation) are canonical in junction tables. JSON keeps metadata, scientific payload, and frozen snapshots.
33. **CLOSED** — A published `IndicatorVersion` is immutable, same policy as a published `RuleVersion`. A formula change is a new version.
34. **CLOSED** — `RuleOutcome.UNKNOWN` is distinct from `INSUFFICIENT_DATA`. Missing or undetermined inputs are `UNKNOWN` (`required_input_absent` or `quality_not_determinable`). Data that exists but misses the minimum sample or quality is `INSUFFICIENT_DATA`. Neither becomes `NOT_TRIGGERED`. Alerts are still created only for `TRIGGERED`.

---

35. **CLOSED** — Phase 6 presents a situation reading (signal, evidence posture, data gaps, qualitative uncertainty, protocol options) without creating a Decision. `DataGap` is a value in that reading, not a new alert type.
36. **OPEN / PRODUCT** — Should `UNKNOWN` or `INSUFFICIENT_DATA` open a non-critical data-limitation alert? Phase 6 does not.
37. **OPEN** — `ScopeHealth` has no `CONFLICTING_EVIDENCE` value. Conflicts are uncertainty statements on the evidence package.
38. **OPEN** — The protocol catalog is not a SQL table. Presented options are copied into the DSS package payload and the snapshot. A catalog table is still required before published protocol immutability is enforced in PostgreSQL.
39. **OPEN** — `Actor` still has no SQL table. A future identity provider must map onto the domain Actor and must not replace it.

---

40. **OPEN / SCIENTIFIC** — Which thermal, depth, habitat, and biological variables are valid inputs to a later downscaling or risk reading? The current record is `docs/scientific-library/variable-registry.yaml` and `docs/33-phase7-open-scientific-questions.md`. Unanswered items stay open. They are not thresholds.

---

## How to resolve

1. Record the decision here or in an ADR-style note.
2. Update glossary/model/invariants if meaning changes.
3. Changes to **FROZEN FOR ARCHITECTURE** concepts ([11-domain-review.md](./11-domain-review.md)) require explicit revision; human-in-the-loop / evidence integrity changes → `REQUIRES HUMAN REVIEW`.
