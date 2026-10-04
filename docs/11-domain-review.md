# 11 — Domain Review & Freeze (Phase 1.5)

## Status

**Review completed.** Soft freeze recommended for technical architecture design.

| Phase | Status |
|-------|--------|
| Phase 0 — Foundation | COMPLETED |
| Phase 1 — Core Domain Model | COMPLETED |
| Phase 1.5 — Domain Review & Freeze | COMPLETED |
| Phase 2 — Technical Architecture | COMPLETED — see [12-technical-architecture.md](./12-technical-architecture.md) |
| Phase 2.5 — Architecture Review & Freeze | COMPLETED — see [14-architecture-review.md](./14-architecture-review.md) |
| Next — Implementation bootstrap + Data ingestion (roadmap Phase 3) | NOT STARTED |

This document does **not** choose technologies, APIs, databases, or implementations.

---

## 1. Audit verdict (summary)

The domain is **sufficiently defined** to design technical architecture **without expecting fundamental concept churn**, provided architecture treats listed frozen concepts as stable and keeps open questions parameterized.

**Primary question answered:**  
> Can we design technical architecture without later changing fundamental domain concepts?  
> **Yes, with soft freeze** — see §16.

**BLOCKERS for Phase 2 (architecture):** **None** after applying the safe clarifications in this review (Decision-time context freeze elevated to invariant; Observation epistemic nuance clarified).

---

## 2. Glossary audit

### 2.1 Issues found

```text
ISSUE: Observation was described as if it were always a world-FACT.
WHY IT MATTERS: Invalid, delayed, or low-quality observations are still records; equating Observation with truth enables “FACT washing.”
IMPACT: Epistemic confusion in EvidenceItems and DSS.
PROPOSED CHANGE: Clarify Observation = recorded claim/measurement record; FACT label applies to “this was recorded,” not “this is true of the world.” Quality/Uncertainty carry fitness.
STATUS: SAFE TO CHANGE (applied in glossary + invariants clarification)
```

```text
ISSUE: DssPackage freeze-at-Decision was TBD (Q31), weakening “what did the decider see?”
WHY IT MATTERS: Historical reconstruction of human decisions requires a frozen context.
IMPACT: Architecture might omit snapshot/immutability and create unfixable audit debt.
PROPOSED CHANGE: Elevate to Invariant 17 — Decision must reference a frozen DSS context snapshot (ids + versions of alerts, evidence packages, recommendations/options, analyses presented).
STATUS: SAFE TO CHANGE (applied; aligns with Phase 0 lean recommendation)
```

```text
ISSUE: “Condition” used in rules docs but not in glossary.
WHY IT MATTERS: Minor ubiquitous-language gap.
IMPACT: Low.
PROPOSED CHANGE: Add Condition as predicate within RuleVersion (not a standalone root entity).
STATUS: SAFE TO CHANGE (applied in glossary)
```

```text
ISSUE: “Processed Data” in Phase 0 Evidence Chain vs Phase 1 Observation+DataQuality lean.
WHY IT MATTERS: Naming mismatch across docs.
IMPACT: Low if architecture supports transformation provenance on Observations.
PROPOSED CHANGE: Keep lean; treat Processed Data as OPEN QUESTION / NON-BLOCKING (Q15b).
STATUS: NON-BLOCKING
```

```text
ISSUE: IndicatorVersion named in model versioning section but not as first-class glossary heading (unlike RuleVersion).
WHY IT MATTERS: Symmetry / clarity.
IMPACT: Low — pattern already stated.
PROPOSED CHANGE: Note IndicatorVersion = version body of Indicator (same pattern as RuleVersion).
STATUS: SAFE TO CHANGE (applied as glossary note)
```

```text
ISSUE: Evidence (umbrella) vs EvidenceItem/Package — persistence TBD (Q30).
WHY IT MATTERS: Implementers might create a redundant Evidence table or lose Items.
IMPACT: Low if architecture persists Item+Package and treats Evidence as concept.
PROPOSED CHANGE: Freeze for architecture: Evidence is conceptual; persisted types are EvidenceItem + EvidencePackage.
STATUS: SAFE TO CHANGE (frozen assumption; Q30 closed for architecture)
```

### 2.2 Synonyms / overlaps (acceptable, not merged)

| Pair | Assessment |
|------|------------|
| RuleEvaluation / “Rule Outcome” | Same concept; alias OK |
| Alert OPEN / CREATED | Synonym states; enum finalization later |
| Recommendation from Protocol vs from Agent | Same entity, different `source`; correct |
| Analysis vs AgentRun output | Distinct: Run = execution; Analysis = analytical product |
| Evidence vs EvidenceItem | Umbrella vs atom; keep both linguistically |
| Entity vs Zone | Overlap risk if Zone-as-Entity; relationship OPEN but non-blocking if hierarchy is flexible |
| Tenant vs Deployment | Distinct; OK |
| Version (pattern) vs RuleVersion | Pattern vs typed version body; OK |

### 2.3 Defined and used — core set

All reviewed core terms are defined and used consistently across 07/08/09:

Entity, Zone, Station, Deployment, Tenant, Observation, Dataset, Indicator, IndicatorValue, Rule, RuleVersion, RuleEvaluation, EvidenceItem, EvidencePackage, Alert, DssPackage, Analysis, Recommendation, Decision, Action, Outcome, Actor, Agent, AgentRun, AuditEvent, Version.

### 2.4 Used elsewhere, lightly defined

| Term | Notes |
|------|-------|
| Condition | Now added to glossary |
| DataQuality | Defined; facets for delay/unavailable strengthened |
| EpistemicLabel | Defined |
| Severity / AlertStatus | Defined; taxonomies OPEN |
| Protocol / ProtocolVersion | Defined |
| Uncertainty | Defined; quantitative model OPEN |

No silent meaning drift detected between Phase 0 principles and Phase 1 model for human-in-the-loop, rules vs protocols, or evidence structure.

---

## 3. Responsibility audit (one sentence each)

| Entity | Why it exists |
|--------|----------------|
| **Observation** | Hold a primary recorded measurement/claim with provenance before derivation. |
| **IndicatorValue** | Hold a derived metric instance computed from observations under a versioned Indicator definition. |
| **RuleEvaluation** | Record a deterministic evaluation of a RuleVersion on specific inputs at a time. |
| **EvidenceItem** | Make one supporting artifact referenceable with kind, epistemic label, quality, uncertainty. |
| **EvidencePackage** | Assemble items (+ gaps/conflicts) for a subject so alerts/DSS are auditable. |
| **Alert** | Signal that attention is required — without deciding or acting. |
| **DssPackage** | Materialize the decision-support context (situation, evidence, options, uncertainty) for a human. |
| **Recommendation** | Propose an option for consideration — never enact it. |
| **Decision** | Record a human Actor’s authorized choice and justification. |
| **Action** | Record what was executed (or explicit non-action) after a Decision. |
| **Outcome** | Link post-hoc observations/evaluations back to Action/Decision without rewriting history. |

**No fusion recommended.** None are duplicates of responsibility.

---

## 4. Evidence chain audit

```text
Raw / Source (DataSource) → Observation → IndicatorValue
  → RuleEvaluation / Analysis → EvidenceItem → EvidencePackage
  → Alert → DssPackage → Recommendation → Decision → Action → Outcome
```

| Question | Answer | Gap? |
|----------|--------|------|
| Why was an alert created? | Via RuleEvaluation(s) + EvidencePackage + scope/time/severity | No fundamental gap |
| Which rule version? | RuleEvaluation stores rule_id + rule_version (Inv 4) | No |
| What evidence existed then? | EvidencePackage at alert; **Decision-time freeze** now required (Inv 17) | Gap closed for architecture |
| Original vs derived evidence? | EvidenceItem.kind (primary \| derived \| …) | Enum finalization OPEN, concept OK |
| What did the decider see? | Frozen DssPackage snapshot on Decision (Inv 17) | Closed as domain requirement |
| What was AI-generated? | AgentRun / Analysis / Recommendation with producer + epistemic labels | Trace retention depth OPEN |
| Reconstruct Decision later? | Decision + Actor + justification + frozen context + Actions/Outcomes | Yes, conceptually |

---

## 5. Epistemological audit

| Separation | Status |
|------------|--------|
| FACT / INFERENCE / RECOMMENDATION / DECISION | Enforced by EpistemicLabel + entity types + Inv 8 |
| Observation ≠ world-truth Fact | Clarified (record vs truth) |
| Analysis ≠ Fact | OK (usually INFERENCE) |
| AgentRun ≠ Decision | Inv 5 |
| Recommendation ≠ Decision | Distinctions + Inv 10 |
| Alert ≠ Decision | Distinctions + Inv 6/11 |
| Protocol ≠ Action | Protocol = options catalog; Action follows Decision |

**Residual risk:** UI could still mis-present labels — mitigated by requiring labels in the **model**, not only UI (Inv 8).

---

## 6. AI audit

```text
Agent (capability) → AgentRun (execution) → Analysis / Recommendation
                         ✗ cannot jump to Action
Recommendation → Human Decision → Action
```

AgentRun auditability fields (conceptual): agent identity, version/config, inputs_ref, timestamp, outputs, sources, epistemic labels, confidence/gaps, context refs, trace refs (`TBD` retention).

**Impossible by invariants** for AgentRun to become automatic operational Action without Decision.

---

## 7. Rules audit

| Concept | Role |
|---------|------|
| Rule | Identity of the rule family |
| RuleVersion | Immutable published logic body |
| Threshold | Boundaries owned by a RuleVersion |
| RuleEvaluation | Concrete run with input/threshold snapshots |
| Alert | Possible downstream signal — not the evaluation itself |

Reconstruction: “which rule, version, inputs, thresholds” is supported by RuleEvaluation. **No DSL invented.**

---

## 8. Versioning audit

Published bodies must be immutable for: RuleVersion, ProtocolVersion, Indicator versions, Agent config versions, relevant transforms, Analysis schema versions.

**Forbidden pattern:** mutate Rule v1 in place. **Required:** new version + activation audit.

Past evaluations keep cited version ids (Inv 4, 7).

---

## 9. Decision loop audit

```text
Alert (“system detected”) 
 → DssPackage (“context for human”)
 → Recommendation(s) (“consider…”)
 → Decision (“Actor chooses”)
 → Action (“executed / recorded”)
 → Outcome (“what happened later”)
```

ACKNOWLEDGED ≠ DECISION — confirmed.  
Recommendation ≠ Decision — confirmed.

---

## 10. Missing / degraded data audit

Representable via DataQuality + Uncertainty + EvidencePackage.gaps + rule quality gates + Inv 9.

| Situation | Representation |
|-----------|----------------|
| Missing | gaps / missingness facets; no auto “healthy” |
| Invalid | DataQuality flags |
| Low quality | scores/flags; may block RuleEvaluation |
| Delayed | DataQuality facet / latency metadata (clarified) |
| Source unavailable | DataSource status + gaps |
| Insufficient evidence | EvidencePackage.gaps; incomplete markers |
| High uncertainty | Uncertainty on items/packages/alerts |

**No Data ≠ No Risk** is an invariant (Inv 9). Residual risk is **presentation** (Q29 PRODUCT/LATER), not domain absence.

---

## 11. Spatial audit

| Concept | Clear enough for architecture? |
|---------|--------------------------------|
| Entity vs Zone vs Station | **Yes** as distinct concepts; hierarchy shape OPEN |
| Geometry format | OPEN QUESTION — non-blocking (opaque spatial ref) |
| Tenant / multi-tenancy | OPEN — architecture can use optional tenant_id |
| Deployment | Distinct from Tenant — OK |

**No spatial BLOCKER.** Architecture should support: optional tenancy; Entity with zero-or-more Zones; Zones with zero-or-more Stations; Observations scoped to Station and/or Zone and/or Entity; geometry as opaque payload until chosen.

---

## 12. Temporal audit

| Instant | Domain field (conceptual) | Status |
|---------|---------------------------|--------|
| Observation phenomenon time | `observed_at` | Present |
| Record / ingest time | `recorded_at` / `ingested_at` | Present |
| Indicator computation | `computed_at` + `time_window` | Present |
| Rule evaluation | `evaluated_at` | Present |
| Alert creation | `created_at` (+ phenomenon range?) | Present |
| DSS open | `opened_at` | Present |
| Decision | `decided_at` | Present |
| Action | action timestamps | Present (status lifecycle) |
| Outcome | `recorded_at` | Present |
| AgentRun | run timestamps | Present |
| Processing/transform time | via transform version + assessment time on DataQuality | Adequate if transforms versioned |

**No temporal BLOCKER.** Architecture must persist these distinct clocks; do not collapse to a single `updated_at`.

---

## 13. Historical reconstruction (“what did BALIZA / the user know?”)

| Question | After Inv 17 |
|----------|----------------|
| What did BALIZA know at Decision time? | Frozen refs to EvidencePackages, RuleEvaluations, IndicatorValues, Analyses as of snapshot |
| What did the user see? | Frozen DssPackage content (alerts, evidence, recommendations/options, gaps, uncertainty, analyses presented) |

Still OPEN (non-blocking): exact snapshot payload richness (full embed vs content-addressed refs); prompt retention for AgentRuns.

---

## 14. Classification of open questions

Source: [10-domain-open-questions.md](./10-domain-open-questions.md) (updated with classes).

| # | Class | Notes |
|---|-------|-------|
| 1 | PILOT / PRODUCT | Multi-tenant need |
| 2 | ARCHITECTURE-RELEVANT | Parametrize Tenant↔Deployment |
| 3 | ARCHITECTURE-RELEVANT | Env vs Deployment |
| 4 | DOMAIN / PILOT | Entity kinds |
| 5 | ARCHITECTURE-RELEVANT | Zone↔Entity shape — flexible hierarchy OK |
| 6 | DOMAIN | Naming |
| 7 | ARCHITECTURE-RELEVANT | Geometry opaque until chosen |
| 8–9 | DOMAIN | Station/zone topology |
| 10 | DOMAIN / LATER | State vs Alert |
| 11–12 | ARCHITECTURE-RELEVANT | Evidence sharing/versioning — support both |
| 13 | DOMAIN | Severity merge |
| 14 | DOMAIN | Cross-entity decisions |
| 15 | ARCHITECTURE-RELEVANT | Observation granularity |
| 15b | DOMAIN | Processed Data lean kept |
| 16–20 | DOMAIN / PRODUCT | Severity/status workflow |
| 21–22 | ARCHITECTURE-RELEVANT | Expression languages — pluggable later |
| 23 | DOMAIN / SCIENTIFIC | Indicator vs Rule policy boundary |
| 24–26 | SCIENTIFIC / PRODUCT | Indicators, thresholds, governance |
| 27–28 | SCIENTIFIC / ARCHITECTURE-RELEVANT | Uncertainty/quality models as facets |
| 29 | PRODUCT / LATER | UX of no-data |
| 30 | **CLOSED for architecture** | Evidence = concept; Item+Package persist |
| 31 | **CLOSED** | Freeze mandatory (Inv 17) |
| 32–35 | PRODUCT / DOMAIN | DSS decision UX policies |
| 36 | ARCHITECTURE-RELEVANT | Lean: ban agent critical alerts — freeze as assumption |
| 37–40 | PRODUCT / ARCHITECTURE-RELEVANT / LEGAL | Agent ops |
| 41–42 | PRODUCT / LATER | Permissions detail (Actor/Role exist) |
| 43–46 | LEGAL / PRODUCT | Retention, e-sign, visibility |
| 47–49 | ARCHITECTURE-RELEVANT / DOMAIN | External actions, outcomes |
| 50–52 | PILOT / PRODUCT | Scope, offline, locale |

**BLOCKER count after review:** 0.

---

## 15. Domain freeze declaration

### FROZEN FOR ARCHITECTURE

Architecture **may assume** these stable:

1. BALIZA is a DSS; humans decide; no automatic operational Action from Alert/AgentRun/Recommendation.
2. Core entity set and responsibilities in §3.
3. Evidence chain shape in §4 (graph cardinalities, not forced 1:1).
4. Rule / RuleVersion / Threshold / RuleEvaluation separation; published versions immutable.
5. Protocol / ProtocolVersion ≠ Rule; options only.
6. EvidenceItem + EvidencePackage as persisted evidence structures; Evidence conceptual.
7. Alert ≠ Decision; ACKNOWLEDGED ≠ DECIDED.
8. Agent / AgentRun / Analysis / Recommendation ≠ Decision.
9. Decision requires Actor + justification; Action requires Decision; Outcome does not rewrite history.
10. EpistemicLabel FACT | INFERENCE | RECOMMENDATION | DECISION.
11. Invariants 1–17.
12. Distinct temporal fields (observation / compute / evaluate / alert / decide / act / outcome).
13. Optional Tenant; Deployment ≠ Tenant.
14. Entity, Zone, Station are distinct concepts; Zone ≠ Station.
15. Critical thresholds live on RuleVersion, not LLM-only.
16. Decision freezes DSS context snapshot (Inv 17).
17. Absence of data must not imply absence of risk (Inv 9).
18. Lean assumption: agents do not alone create **critical** alerts (pending formal product confirmation — architecture still designs rule-owned critical path).

### OPEN BUT NON-BLOCKING

All classified open questions except closed 30/31; geometry; tenancy mode; severity enums; DSL; scientific thresholds; legal retention; pilot vertical; etc.

### BLOCKING

**None** for starting technical architecture design.

---

## 16. Soft freeze statement

> These entities, relationships, and invariants are sufficiently stable to design technical architecture.  
> Changes that alter frozen concepts require an explicit domain revision (and human review if they touch human-in-the-loop or evidence integrity).  
> Open questions remain open and must be parameterized, not invented away.

---

## 17. Roadmap note (Phase 2 naming)

```text
ISSUE: Prior roadmap labeled Phase 2 as “Data ingestion”; this review gate refers to Phase 2 as Technical Architecture.
WHY IT MATTERS: Sequencing clarity for the next step.
IMPACT: Contributors might start ingestion before architecture.
PROPOSED CHANGE: Insert Phase 1.5; set Phase 2 = Technical Architecture; shift Data ingestion to Phase 3; renumber subsequent phases.
STATUS: SAFE TO CHANGE (roadmap updated)
```

---

## 18. Changes applied in this review

See final response section C and git-less file updates:

- Invariant 17 (Decision context freeze)
- Glossary: Observation epistemic nuance; Condition; IndicatorVersion note; DataQuality delay/unavailable; DssPackage freeze no longer TBD
- Domain model: freeze mandatory; temporal note; Evidence persistence freeze for architecture
- Open questions: classification + Q30/Q31 closed notes
- Roadmap / README status updates

---

## 19. Related documents

- [07-domain-glossary.md](./07-domain-glossary.md)
- [08-domain-model.md](./08-domain-model.md)
- [09-domain-invariants.md](./09-domain-invariants.md)
- [10-domain-open-questions.md](./10-domain-open-questions.md)
- [roadmap.md](./roadmap.md)
- [AGENTS.md](../AGENTS.md)
