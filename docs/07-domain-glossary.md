# 07 — Domain Glossary (Ubiquitous Language)

## Purpose

Formal definitions for BALIZA V3 domain terms. This glossary is **normative for meaning**. It is technology-independent.

Related logical structure: [08-domain-model.md](./08-domain-model.md).  
Related constraints: [09-domain-invariants.md](./09-domain-invariants.md).  
Unresolved issues: [10-domain-open-questions.md](./10-domain-open-questions.md).

---

## Conventions

For each term:

| Field | Meaning |
|-------|---------|
| **Definition** | What it is |
| **Purpose** | Why it exists in the domain |
| **Owned by** | Conceptual owner (role/process), not a tech service |
| **References** | Typical related concepts |
| **Lifecycle** | How it is created, changes, ends |
| **Open questions** | Deferred decisions |

`Distinction` sections prevent category errors.

---

## System

**Definition:** The BALIZA V3 Decision Support System as a whole: the bounded product that supports human decisions over marine/coastal entities.

**Purpose:** Name the product boundary; distinguish product behavior from external operational systems that may execute physical actions.

**Owned by:** Product governance.

**References:** Tenant, Deployment, Actor, AuditEvent.

**Lifecycle:** Exists for the product lifetime; configuration evolves via versioned domain objects.

**Open questions:** Single vs multi-deployment product topology (`TBD`).

---

## Tenant

**Definition:** An organizational boundary that isolates configuration, actors, entities, and operational records belonging to one customer/organization.

**Purpose:** Allow future multi-organization operation without forcing it in v1.

**Owned by:** Organizational administrator (authority model `TBD`).

**References:** System, Deployment, Actor, Entity.

**Lifecycle:** Provisioned → active → suspended/retired (`TBD`).

**Open questions:** Required in first pilot? Hierarchy of tenants? (`TBD` — see [10-domain-open-questions.md](./10-domain-open-questions.md)).

---

## Deployment

**Definition:** A concrete running instance or operational context of the System (e.g., a site installation or environment), distinct from the abstract product.

**Purpose:** Separate “product concept” from “where/how an instance operates” without choosing infrastructure.

**Owned by:** Operators / administrators.

**References:** System, Tenant, Entity.

**Lifecycle:** Commissioned → operating → decommissioned.

**Open questions:** Relation Tenant↔Deployment cardinality; env types (pilot/prod) (`TBD`).

### Distinction — Tenant ≠ Deployment

| Tenant | Deployment |
|--------|------------|
| Who owns/configures the organizational slice | Where/which instance of the system runs |
| Organizational isolation concept | Operational instance concept |

---

## Entity

**Definition:** An abstract monitored subject in the domain — anything BALIZA tracks as a first-class object of concern (not limited to a geographic polygon).

**Purpose:** Generalize beyond “everything is a zone”; allow resorts, MPAs, habitats, assets, regions, etc.

**Owned by:** Domain administrators / scientific configuration (`TBD`).

**References:** Zone, Station, Observation, Alert, Decision, Tenant.

**Lifecycle:** Defined → active monitoring → archived.

**Open questions:** Closed type taxonomy; hierarchy rules (`TBD`).

### Distinction — Entity ≠ Zone

| Entity | Zone |
|--------|------|
| Abstract monitored subject (may be spatial or organizational) | Spatial operational/ecological unit |
| May contain or relate to zones | Always spatial in intent |

Working rule: **Zone is a kind of spatial Entity specialization or a spatial facet of an Entity** — exact modeling choice is `TBD` (see domain model).

---

## Zone

**Definition:** A spatial unit used for operations and/or ecology (area of interest for indicators, alerts, decisions).

**Purpose:** Anchor where events occur and where options apply.

**Owned by:** Site/MPA configuration owners.

**References:** Entity, Station, Observation, IndicatorValue, Alert, Decision, Geometry (`TBD` format).

**Lifecycle:** Defined → in use → redefined (new version/identity policy `TBD`) → retired.

**Open questions:** Geometry format; Zone vs Area naming; nesting (`TBD`).

---

## Station

**Definition:** A point-like (or discrete) observation location — typically where sensors or field observations are taken.

**Purpose:** Distinguish sampling/observation points from areal operational units.

**Owned by:** Monitoring configuration owners.

**References:** Zone, Entity, Observation, DataSource.

**Lifecycle:** Installed/defined → active → relocated (history preserved) → decommissioned.

**Open questions:** Can a Station belong to multiple Zones? (`TBD`).

### Distinction — Zone ≠ Station

| Zone | Station |
|------|---------|
| Area / spatial unit of management or ecology | Point/discrete observation location |
| Alerts and decisions often scoped here | Observations often originate here |

---

## Observation

**Definition:** A primary **recorded** measurement or observation claim at a time and place (or spatial reference), with provenance.

**Purpose:** Represent atomic empirical inputs before indicator derivation.

**Owned by:** Data ingestion / observers (human or system actors).

**References:** DataSource, Dataset, DataQuality, Uncertainty, Station, Zone, Entity, IndicatorValue.

**Lifecycle:** Recorded → (optionally) corrected via append/supersession → retained per policy (`TBD`).

**Open questions:** Observation vs “raw file record” granularity (`TBD`).

### Distinction — Observation ≠ world-truth FACT

| Observation | “True of the world” |
|-------------|---------------------|
| A durable record that a value/claim was captured | May be wrong, delayed, invalid, or low quality |
| FACT label (when used) means “this recording exists with this provenance” | Fitness-for-use lives in DataQuality + Uncertainty |

Invalid or missing-capable records remain Observations (or gaps); they must not be silently treated as proof of safety (Invariant 9).

### Distinction — Observation ≠ Indicator / IndicatorValue

| Observation | IndicatorValue |
|-------------|----------------|
| Primary recorded measurement/claim (e.g., temperature = 28.4°C) | Derived metric from one or more observations (e.g., thermal_anomaly = +2.7°C) |
| Record-level empirical input | Derived computation instance (still not an alert) |

---

## Dataset

**Definition:** A named grouping of related observations or data artifacts sharing provenance, campaign, or ingest batch context.

**Purpose:** Organize bulk data and common metadata without replacing individual Observation identity.

**Owned by:** Data managers / ingestion process.

**References:** Observation, DataSource, DataQuality.

**Lifecycle:** Open/collecting → closed/versioned → archived.

**Open questions:** Dataset versioning vs Observation immutability (`TBD`).

---

## DataSource

**Definition:** The origin classification and identity of data (sensor, satellite, human observation, external API, scientific dataset, model output, etc.).

**Purpose:** Provenance and trust differentiation at the source level.

**Owned by:** Integration / scientific data stewards.

**References:** Observation, Dataset, EvidenceItem.

**Lifecycle:** Registered → active → deprecated.

**Open questions:** Closed enumeration of source kinds for pilot (`TBD`).

### Distinction — DataSource ≠ Observation

| DataSource | Observation |
|------------|-------------|
| Where/what kind of origin | A specific recorded value/event from a source |

---

## DataQuality

**Definition:** Structured assessment of fitness-for-use of data or derived products (flags, scores, checks performed) — not a free-text opinion alone.

**Purpose:** Gate or downgrade use in indicators/rules; make quality visible in evidence.

**Owned by:** Quality assessment process (deterministic preferred for gates).

**References:** Observation, IndicatorValue, Rule, EvidenceItem, Uncertainty.

**Lifecycle:** Assessed at ingest/transform time; may be reassessed with new methods (new assessment version; history kept).

**Open questions:** Scoring model; minimum quality for critical rules (`TBD`).

**Conceptual facets (non-exhaustive, non-final):** missing; invalid; low quality; delayed / high latency; source unavailable; failed range/consistency checks. Absence of usable data must not be encoded as “no risk.”

---

## Indicator

**Definition:** A versioned **definition** of a derived metric: inputs, transformation, units, temporal/spatial scope rules, baseline rules (if any).

**Purpose:** Make derived quantities explicit, reviewable, and reproducible.

**Owned by:** Scientific/configuration governance.

**References:** IndicatorValue, Observation, Rule, Version.

**Lifecycle:** draft → reviewed → active → deprecated → retired.

**Open questions:** Indicator specification language (`TBD`).

---

## IndicatorValue

**Definition:** A concrete computed instance of an Indicator for a scope (entity/zone/station), time window, and Indicator version.

**Purpose:** Provide inputs to rules and evidence without conflating definition and instance.

**Owned by:** Indicator computation process.

**References:** Indicator, Observation, DataQuality, Uncertainty, RuleEvaluation.

**Lifecycle:** Calculated → superseded by newer calculation for same key (policy `TBD`) → retained for audit.

**Open questions:** Recompute vs append strategy (`TBD`).

---

## Rule

**Definition:** Stable identity of a deterministic evaluation specification (the “rule family”), independent of any single version body.

**Purpose:** Allow version history under one conceptual rule.

**Owned by:** Scientific/operational rule governance.

**References:** RuleVersion, Threshold, Alert, EvidencePackage.

**Lifecycle:** Created → versions accumulate → may be retired as a family.

**Open questions:** Rule naming taxonomy (`TBD`).

---

## RuleVersion

**Definition:** An immutable published body of a Rule: inputs, conditions, thresholds, evidence/quality requirements, severity mapping, effective window, status.

**Purpose:** Reproducible evaluation; audit of what logic produced a signal.

**Owned by:** Rule governance (activation requires authority `TBD`).

**References:** Rule, Threshold, RuleEvaluation, AuditEvent.

**Lifecycle:** draft → approved → active (within effective window) → superseded/deprecated. **Published versions are not silently overwritten.**

**Open questions:** Expression language; dual-control activation (`TBD`).

### Distinction — Rule ≠ Protocol

| Rule / RuleVersion | Protocol / ProtocolVersion |
|--------------------|----------------------------|
| Detects/evaluates conditions → candidate signals | Catalog of possible actions/procedures |
| Deterministic evaluation | Guidance for humans |
| Does not choose operational action | Does not fire alerts by itself |

---

## Threshold

**Definition:** Explicit boundary value(s) used in RuleVersion conditions (warning/critical/etc. as defined by that version).

**Purpose:** Keep critical boundaries auditable and outside LLM-only prompts.

**Owned by:** Same governance as RuleVersion (scientific validation required before `active`).

**References:** RuleVersion, IndicatorValue, DataQuality.

**Lifecycle:** Bound to a RuleVersion; changing thresholds ⇒ new RuleVersion.

**Open questions:** Any specific numeric thresholds — **none asserted** (`TBD` scientific validation).

---

## Protocol

**Definition:** Stable identity of a catalog of possible action options and considerations for classes of situations/alerts.

**Purpose:** Structure DSS options without auto-execution.

**Owned by:** Operational + scientific protocol governance (`TBD`).

**References:** ProtocolVersion, Recommendation, Decision, Alert.

**Lifecycle:** Created → versions accumulate → retired.

**Open questions:** Linkage model Protocol↔Alert type/severity (`TBD`).

---

## ProtocolVersion

**Definition:** Immutable published body of a Protocol: options, considerations, applicability, required roles (conceptual), status.

**Purpose:** Versioned guidance presented by the DSS.

**Owned by:** Protocol governance.

**References:** Protocol, Recommendation, Decision, AuditEvent.

**Lifecycle:** draft → active → superseded. No silent overwrite of published versions.

**Open questions:** Whether options require role gates in v1 (`TBD`).

---

## Evidence

**Definition:** The domain concept of **structured, referenced support** for a claim, alert, analysis, or decision context — never merely unstructured prose pretending to be proof.

**Purpose:** Anchor “evidence before inference.”

**Owned by:** Evidence assembly process / investigators contributing structured items.

**References:** EvidenceItem, EvidencePackage, Observation, Analysis, DataSource.

**Lifecycle:** Accumulates as items; packaged for subjects (alerts, investigations).

**Open questions:** Whether “Evidence” is only a conceptual umbrella or also a persisted root type — **CLOSED for architecture:** umbrella only; persist EvidenceItem + EvidencePackage (Phase 1.5).

### Distinction — Evidence ≠ free text

Evidence must resolve to EvidenceItems (and packages) with origin, references, quality, and uncertainty. Narrative alone is not sufficient.

---

## EvidenceItem

**Definition:** Atomic structured evidence unit pointing to a source artifact (observation, indicator value, rule evaluation, analysis, scientific reference, contextual record) with epistemic label, quality, uncertainty, timestamps, and versions.

**Purpose:** Make each supporting piece independently auditable.

**Owned by:** Producer of the item (ingestion, rule engine, agent run, human attach).

**References:** EvidencePackage, Observation, IndicatorValue, RuleEvaluation, Analysis, Uncertainty, EpistemicLabel (FACT/INFERENCE/…).

**Lifecycle:** Created → optionally superseded → retained.

**Open questions:** Closed enum of item kinds (`TBD`).

**Kinds (conceptual, non-final):** primary (observations); derived (indicators, rule evaluations); scientific (registered references); contextual (history, site config); analytical (Analysis/AgentRun outputs labeled INFERENCE unless purely referential).

---

## EvidencePackage

**Definition:** Assembled, versioned collection of EvidenceItems for a subject (alert candidate, alert, investigation, decision context), including conflicts, gaps, and package-level uncertainty notes.

**Purpose:** Answer “what evidence supports this?” as one auditable object.

**Owned by:** Evidence assembly component (conceptual).

**References:** EvidenceItem, Alert, DssPackage, Decision, Uncertainty.

**Lifecycle:** Created → amended via new package version or linked packages (immutability policy `TBD`) → retained.

**Open questions:** Single mutable package vs immutable versions per amendment (`TBD`).

---

## Alert

**Definition:** Traceable system-generated signal that a condition requires human attention for an Entity/Zone (or related scope), backed by evidence and rule evaluations (and optionally analyses).

**Purpose:** Surface situations into the DSS without deciding actions.

**Owned by:** Alert lifecycle process; created from rule outcomes under policy (`TBD` soft signals).

**References:** AlertStatus, Severity, EvidencePackage, RuleVersion, IndicatorValue, Zone, Entity, Uncertainty, Decision.

**Lifecycle:** See AlertStatus. History of status changes is retained.

**Open questions:** Deduplication; multi-rule composition; agent-only soft alerts (`TBD`).

### Distinction — Alert ≠ Decision

| Alert | Decision |
|-------|----------|
| System-generated signal requiring attention | Human-authorized operational choice |
| Does not execute protocols | May select a protocol option or custom action |
| May be acknowledged without deciding | Requires responsible Actor |

---

## AlertStatus

**Definition:** Lifecycle state of an Alert.

**Purpose:** Separate awareness workflow from operational decision-making.

**Owned by:** Alert lifecycle process + Actors who transition states under policy.

**References:** Alert, Actor, AuditEvent.

**Lifecycle (conceptual, non-final):**

```text
CREATED / OPEN
    ↓
UNDER_REVIEW
    ↓
ACKNOWLEDGED          ← awareness only; NOT a Decision
    ↓
RESOLVED / CLOSED
```

Optional branches: `ESCALATED`, `RETRACTED`/`SUPERSEDED` (`TBD` exact enum).

### Distinction — ACKNOWLEDGED ≠ DECIDED

| ACKNOWLEDGED | Decision recorded |
|--------------|-------------------|
| “A human has seen / taken ownership of awareness” | “A human chose an operational option (or explicit no-action)” |
| AlertStatus transition | Separate Decision entity |

---

## Severity

**Definition:** Ordinal or categorical level of an Alert (and possibly rule outcomes) indicating urgency/importance.

**Purpose:** Prioritization aid — not an automatic action trigger.

**Owned by:** Defined by RuleVersion mapping / alert policy.

**References:** Alert, RuleVersion, ProtocolVersion (applicability).

**Lifecycle:** Set at creation/update per deterministic policy; changes audited.

**Open questions:** Final taxonomy (info/warning/critical/…) (`TBD`).

---

## Uncertainty

**Definition:** Explicit representation of doubt, confidence limits, data gaps, conflicts, or quality limitations associated with a domain object.

**Purpose:** Prevent false certainty; support DSS honesty.

**Owned by:** Producers of the associated object (quality process, rules, agents, humans).

**References:** Observation, IndicatorValue, Analysis, EvidenceItem, EvidencePackage, Alert, Recommendation.

**Lifecycle:** Attached at creation; may be updated with new assessments (history preserved).

**Open questions:** Quantitative model vs structured qualitative facets (`TBD` — no universal formula in Phase 1).

---

## Analysis

**Definition:** Structured analytical result (often from an AgentRun, sometimes from a human analyst) that interprets or compares evidence — typically labeled INFERENCE unless it is a pure citation bundle.

**Purpose:** Hold interpretive products without conflating them with Facts or Decisions.

**Owned by:** Analyst Actor or AgentRun producer.

**References:** AgentRun, EvidenceItem, Recommendation, Uncertainty.

**Lifecycle:** Produced → referenced → superseded by newer analysis (link, don’t erase).

**Open questions:** Human Analysis vs Agent Analysis unified type? (`TBD` lean: unified with `producer` discriminant).

---

## Agent

**Definition:** A named logical capability (e.g., Evidence Agent, Explanation Agent) with versioned configuration and hard behavioral limits.

**Purpose:** Assist interpretation/explanation; never own critical thresholds alone.

**Owned by:** AI/product governance under `AGENTS.md` constraints.

**References:** AgentRun, Analysis, Recommendation.

**Lifecycle:** Defined → versioned configs → deprecated.

**Open questions:** Final agent set for pilot (`TBD`).

---

## AgentRun

**Definition:** One concrete execution of an Agent (or orchestrated set) with inputs refs, outputs, epistemic labels, sources, confidence, gaps, timestamps, agent version.

**Purpose:** Auditability of AI assistance.

**Owned by:** Orchestration process.

**References:** Agent, Analysis, Recommendation, AuditEvent, EvidenceItem.

**Lifecycle:** Started → completed/failed → retained.

**Open questions:** Retention of prompts/traces (`TBD`).

### Distinction — AgentRun ≠ Decision

| AgentRun | Decision |
|----------|----------|
| Execution of assistive analysis | Human operational choice |
| May produce Analysis/Recommendation | Requires human Actor authorization |
| Cannot enact protocols | May lead to Action via Decision |

---

## Recommendation

**Definition:** A proposed option or prioritization for human consideration (from Protocol options, playbooks, or advisory AgentRun/Analysis), explicitly labeled RECOMMENDATION.

**Purpose:** Present choices without selecting them.

**Owned by:** DSS assembly / protocol catalog / agent advisory outputs.

**References:** ProtocolVersion, Analysis, AgentRun, Decision, DssPackage.

**Lifecycle:** Generated → presented → accepted/rejected/ignored via Decision (recommendation itself is not the decision).

**Open questions:** Ranking/default highlighting (`TBD`).

### Distinction — Recommendation ≠ Decision ≠ Action

| Recommendation | Decision | Action |
|----------------|----------|--------|
| “Consider reducing access” | Manager selects temporary restriction | Restriction activated at Zone X |
| Proposal | Human choice record | What was executed / recorded as done |

---

## Decision

**Definition:** Human-authorized operational choice recorded in the DSS context: who, when, on which alerts/context, which option (protocol option or justified custom), justification, status, and mandatory **`DssContextSnapshot`**.

**Purpose:** Keep final authority human and auditable; enable reconstruction of what was considered.

**Owned by:** Responsible human Actor (roles `TBD`).

**References:** Actor, Alert, EvidencePackage, Recommendation, ProtocolVersion, Action, AuditEvent, DssPackage.

**Lifecycle:** Recorded with frozen context → (optional) amended only via compensated new Decision / correction event — no silent rewrite (`TBD` amendment policy) → linked to Actions/Outcomes.

**Open questions:** Multi-party approval; free-form vs protocol-only (`TBD`).

---

## Action

**Definition:** What was actually carried out (or explicitly recorded as non-action) **after** a Decision — may occur inside or outside BALIZA, but is linked to the Decision.

**Purpose:** Separate choosing from doing; enable outcome evaluation.

**Owned by:** Operational executors; recorded by Actor/system integration (`TBD`).

**References:** Decision, Outcome, Zone, Entity, AuditEvent.

**Lifecycle:** Planned/recorded → in progress → completed/cancelled/failed.

**Open questions:** External system linkage (`TBD`).

### Distinction — Action ≠ Decision

| Decision | Action |
|----------|--------|
| Choice and justification | Execution record (or explicit no-op execution) |
| Must exist before Action (Invariant) | Cannot imply a Decision by itself |

---

## Outcome

**Definition:** Structured post-action (or post-decision) observed result: linked later observations/indicator values, evaluation notes with epistemic labeling, timestamps — not a mere opinion blob.

**Purpose:** Close the feedback loop into new evidence without rewriting history.

**Owned by:** Evaluators (human) with linked empirical refs; system may attach observation links.

**References:** Action, Decision, Observation, IndicatorValue, EvidenceItem, Alert.

**Lifecycle:** Recorded → may be updated with additional linked observations → retained.

**Open questions:** Formal outcome scoring (`TBD`).

---

## Actor

**Definition:** Identity of a person (or accountable human identity) who interacts with the System — capable of acknowledgment, decision, configuration proposals, audit review.

**Purpose:** Accountability for decisions and governed changes. Enables later authn/authz without defining them here.

**Owned by:** Identity administration (`TBD` Phase 10 implementation).

**References:** Role, Decision, AuditEvent, AlertStatus transitions.

**Lifecycle:** Provisioned → active → deactivated.

**Open questions:** Human-only vs service accounts as Actors (`TBD` — lean: system components are not Decision Actors).

### Distinction — Actor ≠ Agent

| Actor | Agent |
|-------|-------|
| Accountable human identity | Software analytical capability |
| Can create Decisions | Cannot create Decisions |

---

## Role

**Definition:** Named set of responsibilities/permissions conceptually assigned to Actors (manager, scientist, operator, admin, auditor, …).

**Purpose:** Express authority boundaries without implementing authz yet.

**Owned by:** Governance / admin.

**References:** Actor, Decision, RuleVersion activation, Protocol options.

**Lifecycle:** Defined → assigned → revised (assignments audited).

**Open questions:** Final role catalog and permission matrix (`TBD` Phase 10).

---

## AuditEvent

**Definition:** Durable record that someone/something did something to a domain object at a time, for a reason, citing versions involved.

**Purpose:** Reconstruct who/what/when/to what/why/which version.

**Owned by:** System audit process.

**References:** Actor, AgentRun, RuleVersion, ProtocolVersion, Alert, Decision, Action.

**Lifecycle:** Append-only conceptually; retention `TBD`.

**Open questions:** Completeness vs volume tradeoffs (`TBD`).

---

## Version

**Definition:** Explicit revision identity of a versioned domain definition (Rule, Protocol, Indicator, Agent config, transformation schema, etc.), distinguishing **identity** from **version body**.

**Purpose:** History preservation and reproducible evaluation.

**Owned by:** Governance of the versioned artifact.

**References:** RuleVersion, ProtocolVersion, Indicator, Agent, AuditEvent.

**Lifecycle:** Issued → effective → superseded. Identity remains; bodies accumulate.

### Distinction — Entity identity vs Entity version

| Identity (e.g., Rule) | Version (e.g., RuleVersion) |
|-----------------------|-----------------------------|
| Stable “which rule family” | Immutable “which logic body” |
| Survives across revisions | Never silently overwritten when published |

---

## Additional glossary terms (required for precision)

### RuleEvaluation (Rule Outcome)

**Definition:** Recorded result of evaluating a RuleVersion against inputs at a time: pass/fail/candidate signal, snapshot of inputs/thresholds, quality gates, links to EvidenceItems.

**Purpose:** Answer “which rule version produced this signal?”

**Owned by:** Rule evaluation process.

**References:** RuleVersion, IndicatorValue, Alert, EvidenceItem.

**Lifecycle:** Created at evaluation; immutable thereafter.

**Open questions:** Store full input snapshots vs hashes+refs (`TBD`).

### DssPackage

**Definition:** Assembled **live** decision-support view for a human session/context: situation (alerts), evidence, uncertainty, labeled inferences, recommendations/options, considerations — ready for Decision capture.

**Purpose:** Materialize DSS principles as a domain object (not a UI widget). May change while the investigation remains open.

**Owned by:** DSS assembly process.

**References:** Alert, EvidencePackage, Recommendation, ProtocolVersion, Analysis, Decision, DssContextSnapshot.

**Lifecycle:** Opened/created → may update while open → at Decision, a **DssContextSnapshot** is created and bound (Invariant 17). The live package may continue to evolve afterward.

**Open questions:** UX of live updates during an open session (`TBD`).

### Distinction — DssPackage ≠ DssContextSnapshot

| DssPackage | DssContextSnapshot |
|------------|--------------------|
| Live / assembled context | Frozen projection at Decision time |
| Mutable while open | **Immutable after Decision** |
| Not sufficient alone for historical reconstruction | Required to reconstruct what the Actor saw |

### DssContextSnapshot

**Definition:** Immutable structured freeze of the DSS context bound to a `Decision`, including alerts, evidence packages/items, rule/indicator/protocol versions, evaluations, recommendations, optional agent outputs as shown, uncertainty, gaps, and timestamps.

**Purpose:** Answer “what information was available when this Decision was taken?” without depending on later mutations.

**Owned by:** Decision capture use case (DSS + Decisions modules).

**References:** Decision, DssPackage, Alert, EvidencePackage, EvidenceItem, RuleEvaluation, Recommendation, Analysis, AgentRun, AuditEvent.

**Lifecycle:** Created at Decision → retained forever (per retention policy) → never updated.

**Open questions:** JSON encoding; size threshold for object-store offload (`TBD`). Hash **requirement** is frozen; algorithm is OPEN (lean SHA-256).

### Condition

**Definition:** A predicate (boolean or multi-valued) inside a `RuleVersion` over indicators, quality, duration, spatial scope, or combinations thereof.

**Purpose:** Express deterministic rule logic explicitly.

**Owned by:** Contained in RuleVersion (not a standalone root aggregate).

**References:** RuleVersion, Threshold, IndicatorValue, DataQuality.

**Lifecycle:** Versioned only as part of RuleVersion publication.

**Open questions:** Expression language (`TBD`).

### IndicatorVersion

**Definition:** Immutable published body of an `Indicator` definition (inputs, transformation, units, baseline/aggregation rules), analogous to `RuleVersion` for rules.

**Purpose:** Symmetry of versioning; reproducible IndicatorValue computation.

**Owned by:** Indicator governance.

**References:** Indicator, IndicatorValue, Version, AuditEvent.

**Lifecycle:** draft → active → superseded; published bodies not silently overwritten.

### EpistemicLabel

**Definition:** Classifier: FACT | INFERENCE | RECOMMENDATION | DECISION (and possibly CONTEXT_REF `TBD`).

**Purpose:** Prevent mixing claims of different epistemic status.

**Owned by:** Producers must set; validators enforce.

**References:** EvidenceItem, Analysis, Recommendation, Decision, Alert explanations.

---

## Global distinction map (quick reference)

```text
DssPackage   ≠  DssContextSnapshot
Observation  ≠  IndicatorValue  ≠  Alert
Rule         ≠  Protocol
Alert        ≠  Decision
ACKNOWLEDGED ≠  DECIDED
Recommendation ≠ Decision ≠ Action
Agent / AgentRun ≠ Actor / Decision
Evidence     ≠  free text
Analysis     ≠  Decision
Outcome      ≠  proof that a Decision was “correct”
```
