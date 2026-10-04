# 08 — Domain Model (Conceptual / Logical)

## Status

Technology-independent logical model for BALIZA V3.  
Normative meaning aligns with [07-domain-glossary.md](./07-domain-glossary.md) and [AGENTS.md](../AGENTS.md).

This document does **not** define databases, APIs, frameworks, or deployment architecture.

---

## 1. Modeling principles

1. Prefer **many-to-many** where the real world is many-to-many; do not force a single linear chain.
2. Separate **definition** (Indicator, Rule, Protocol, Agent) from **instance** (IndicatorValue, RuleEvaluation, AgentRun, Alert).
3. Separate **identity** from **version body**.
4. Separate **epistemic kinds**: FACT / INFERENCE / RECOMMENDATION / DECISION.
5. Prefer **append / supersede** over silent mutate for audit-critical records.
6. Mark unresolved cardinality and hierarchy as `TBD` rather than inventing false precision.

---

## 2. Chain (canonical) vs graph (actual)

### Canonical narrative

```text
DATA
 ↓
OBSERVATION
 ↓
INDICATOR (definition) / INDICATOR VALUE (instance)
 ↓
RULE EVALUATION / ANALYSIS
 ↓
EVIDENCE PACKAGE
 ↓
ALERT
 ↓
DSS PACKAGE
 ↓
DECISION
 ↓
ACTION
 ↓
OUTCOME  →  (may yield new OBSERVATIONS / EVIDENCE)
```

### Actual cardinality (required)

| Relation | Cardinality intent |
|----------|-------------------|
| Observations → IndicatorValue | many → one (and one IndicatorValue uses many Observations) |
| IndicatorValues → Alert | many → many (via RuleEvaluations / Evidence) |
| RuleEvaluations → Alert | many → one or many (`TBD` composition) |
| EvidenceItems → EvidencePackage | many → one (packages may share items `TBD`) |
| EvidencePackages → Alert | one or many → one |
| Alerts → Decision | many → one (a Decision may cover several Alerts) |
| Decision → Actions | one → many |
| Action → Outcomes | one → many |
| Alerts related to Alerts | many ↔ many (related/supersedes) |

---

## 3. Core entities (logical)

Attributes below are **conceptual fields**, not a physical schema.

### 3.1 Scope & tenancy

#### System
- Conceptual product boundary (BALIZA V3).

#### Tenant
- `tenant_id`, name, status  
- Optional in early single-org pilots (`TBD`).

#### Deployment
- `deployment_id`, tenant_ref?, label, status  
- Distinct from Tenant (see glossary).

---

### 3.2 Actors & access (logical only)

#### Actor
- `actor_id`, display identity, status  
- May later bind to authentication subjects (Phase 10).  
- **Only Actors create Decisions.**

#### Role
- `role_id`, name, responsibility description  
- Assignments: Actor *many-to-many* Role (`TBD` permission details).

---

### 3.3 Spatial / monitored subjects

#### Entity
- `entity_id`, name, `entity_kind` (resort | mpa | region | habitat | asset | other — enum `TBD`)  
- Optional `tenant_id`  
- May aggregate or relate to Zones

#### Zone
- `zone_id`, name, `entity_id` (or Zone-as-Entity — modeling choice `TBD`)  
- Spatial extent placeholder (`geometry` format `TBD`)  
- Operational/ecological unit for alerts & decisions

#### Station
- `station_id`, name, location placeholder (`TBD`)  
- Associated Zone(s) (`TBD` cardinality)  
- Often linked to DataSources

**Working relation (non-final):**

```text
Tenant?
  └── Entity
        └── Zone*
              └── Station*
```

`*` = zero or more. Hierarchy depth and multiple parents are `TBD`.

---

### 3.4 Data plane

#### DataSource
- `source_id`, kind (sensor | satellite | human | api | scientific_dataset | model | other `TBD`), metadata refs

#### Dataset
- `dataset_id`, source_id?, name, time_range, status

#### Observation
- `observation_id`
- `variable` (conceptual measured quantity name/code)
- `value` + `unit`
- `observed_at` (phenomenon time)
- `processed_at` (ingest/record/quality time; aliases `recorded_at` / `ingested_at`)
- spatial ref: `station_id` and/or `zone_id` and/or `entity_id`
- `source_id`, `dataset_id`?
- `method`?
- `data_quality` ref
- `uncertainty` ref
- provenance identifiers

Observations are primary FACT candidates (measurement facts).

#### DataQuality
- Structured flags/scores/check results  
- Linked to Observation and/or IndicatorValue  
- Assessment method/version recorded  
- Facets may include: missing, invalid, low quality, delayed, source unavailable (see glossary)

---

### 3.4b Temporal fields (must remain distinct)

Architecture must not collapse these clocks. **Canonical names (Phase 2.5):**

| Canonical | Meaning | Typical fields / aliases |
|-----------|---------|--------------------------|
| `observed_at` | Phenomenon time | Observation.`observed_at` |
| `processed_at` | Ingest / quality / transform time | `processed_at`; aliases `recorded_at`, `ingested_at`, DQ assessed_at |
| `evaluated_at` | Rule evaluation time | RuleEvaluation.`evaluated_at` |
| `alerted_at` | Alert first raised | Alert.`alerted_at` (alias: former `created_at` as domain clock) |
| `reviewed_at` | Review / ack / status change | Alert status history timestamps |
| `decided_at` | Human decision | Decision.`decided_at` |
| `acted_at` | Action executed/recorded | Action.`acted_at` |
| `observed_outcome_at` | Outcome / later observation | Outcome.`observed_outcome_at` (alias: `recorded_at`) |

Plus: IndicatorValue.`computed_at` / `time_window`; DssPackage.`opened_at`; DssContextSnapshot.`frozen_at`; AgentRun start/end.

ORM/DB `created_at`/`updated_at` are **technical**, never substitutes for domain clocks.

Late observations **append**; they do not overwrite original `observed_at`. Later evaluations create **new** RuleEvaluations.

---

### 3.5 Indicators

#### Indicator (definition)
- `indicator_id` (identity)
- current/active version pointer (derived; history via versions)
- Per version body: inputs, transformation spec, unit, baseline rules, aggregation period/scope rules, quality expectations  
- Status: draft | active | deprecated | …

#### IndicatorValue (instance)
- `indicator_value_id`
- `indicator_id` + `indicator_version`
- scope: entity/zone/station
- `time_window` / `computed_at`
- `value` + `unit`
- input Observation refs (many)
- `data_quality`, `uncertainty`
- transformation version/refs

**Observation ≠ IndicatorValue** (see glossary).

---

### 3.6 Rules

#### Rule (identity)
- `rule_id`, name, description, status of family

#### RuleVersion (immutable body when published)
- `rule_id` + `version`
- inputs (indicator constraints, quality signals)
- conditions
- `thresholds` (explicit; may be embedded value objects of this version)
- `severity` mapping
- `evidence_requirements`
- `data_quality_requirements`
- `effective_from` / `effective_to`
- status: draft | active | deprecated | retired
- scientific_references / change_rationale

#### Threshold
- Value object **owned by** a RuleVersion (changing thresholds ⇒ new RuleVersion)  
- No standalone silent edit

#### RuleEvaluation
- `evaluation_id`
- `rule_id` + `rule_version` (**mandatory**)
- `evaluated_at`
- scope refs
- input snapshots/refs (IndicatorValues, quality)
- thresholds_applied snapshot
- outcome: not_triggered | candidate_alert | … (`TBD` enum)
- links to EvidenceItems created from this evaluation

**RuleEvaluation may contribute to Alert creation; it never creates a Decision.**

---

### 3.7 Protocols

#### Protocol (identity)
- `protocol_id`, name

#### ProtocolVersion
- `protocol_id` + `version`
- applicability (alert types/severities — linkage `TBD`)
- `options[]` (option_id, label, description, required_roles?)
- `considerations[]`
- status, effective window

**Protocol defines options; Decision selects; Action executes.**

---

### 3.8 Evidence

#### EvidenceItem
- `evidence_item_id`
- `kind`: primary | derived | scientific | contextual | analytical (`TBD` final enum)
- `ref` to underlying object (Observation, IndicatorValue, RuleEvaluation, Analysis, registered reference, …)
- `epistemic_label`
- origin, timestamps, versions, transformation refs
- `data_quality`, `uncertainty`
- **Not free text alone** (narrative optional accessory, never sole content)

#### EvidencePackage
- `evidence_package_id`
- `subject` (alert_id / investigation_id / zone+time / …)
- `items[]` (EvidenceItem refs)
- `conflicts[]`, `gaps[]`
- package-level `uncertainty` notes
- `assembler` (component + version)
- `created_at` (+ package version if immutable versions used)

#### Evidence
- Conceptual umbrella only for architecture soft freeze.
- **Persisted types:** EvidenceItem + EvidencePackage (Q30 closed for architecture).

---

### 3.9 Alerts

#### Alert
- `alert_id`
- scope: `entity_id` / `zone_id` (required spatial or entity scope — exact rules `TBD`)
- `severity`
- `status` (AlertStatus)
- `alerted_at` (domain clock; do not use technical `created_at` as substitute)
- `phenomenon_time_range`?
- `rule_evaluation_ids[]` (many)
- `indicator_value_ids[]` (many; denormalized convenience — source of truth via evidence/rules)
- `evidence_package_id` (required for critical alerts — see invariants)
- `uncertainty`
- related_alert_ids[]?
- status_history[]

#### AlertStatus (conceptual enum)
- `OPEN` / `CREATED`
- `UNDER_REVIEW`
- `ACKNOWLEDGED`  ← awareness only
- `ESCALATED` (optional)
- `RESOLVED` / `CLOSED`
- `RETRACTED` / `SUPERSEDED` (optional)

**ACKNOWLEDGED ≠ Decision.**

#### Severity
- Categorical levels (`TBD` taxonomy). Prioritization only.

**Why was this alert created?** must be answerable via RuleEvaluation(s) + EvidencePackage + versions + scope + timestamps + uncertainty.

---

### 3.10 DSS, AI, recommendations

#### DssPackage
- `dss_package_id`
- `alert_ids[]` (one or many)
- `evidence_package_ids[]`
- situation summary refs (FACT)
- `analysis_ids[]` (INFERENCE)
- `recommendation_ids[]` / protocol options presented
- considerations, gaps, uncertainty
- opened_by / opened_at
- **Live** — may evolve. Not the historical record of a Decision.

#### DssContextSnapshot
- `snapshot_id`
- `dss_package_id` (origin, informational)
- `frozen_at`
- `content_hash`
- payload: alerts, evidence packages/items, rule/indicator/protocol versions, RuleEvaluation ids, recommendations, analyses/agent runs **as shown**, uncertainty, gaps, timestamps
- optional `object_key` if payload stored as immutable object
- **Immutable after Decision bind**

See Invariant 17 and ADR-011.

#### Agent
- `agent_id`, name, purpose, limits, allowed_sources policy  
- versioned configuration

#### AgentRun
- `agent_run_id`, `agent_id` + `agent_version`
- inputs_ref, outputs, epistemic labels, sources, confidence, gaps, timestamps, trace refs

#### Analysis
- `analysis_id`
- producer: AgentRun and/or Actor
- structured findings, epistemic_label (usually INFERENCE)
- links to EvidenceItems
- uncertainty / limitations

#### Recommendation
- `recommendation_id`
- epistemic_label = RECOMMENDATION
- source: ProtocolVersion.option and/or Analysis/AgentRun
- text/structured proposal
- explicitly identifiable as recommendation (Invariant 10)

**None of Agent, AgentRun, Analysis, Recommendation is a Decision.**

---

### 3.11 Human decision loop

#### Decision
- `decision_id`
- **`actor_id` (mandatory)**
- `decided_at`
- **`dss_context_snapshot_id` (mandatory — Inv 17 / ADR-011)**
- `dss_package_id` (optional live origin)
- `alert_ids[]`, `evidence_package_ids[]` (copied into snapshot; snapshot is source of historical truth)
- `options_presented[]` (also in snapshot)
- `selected_option` OR `custom_action_description` (policy `TBD`)
- `justification` (mandatory)
- `status`
- must not reference AgentRun as the deciding actor

#### Action
- `action_id`
- **`decision_id` (mandatory)** — Action cannot stand as implicit Decision
- what was done / explicit non-action
- scope (zone/entity)
- `status`, `acted_at`
- external_ref? (`TBD`)
- recorded_by Actor?

#### Outcome
- `outcome_id`
- `action_id` and/or `decision_id`
- `observed_outcome_at` (alias: former `recorded_at`)
- linked `observation_ids[]` / `indicator_value_ids[]`
- structured evaluation (with epistemic labels)
- may spawn new EvidenceItems

---

### 3.12 Cross-cutting

#### Uncertainty
- Attachable structure: facets such as confidence, missingness, conflict flags, qualitative notes, method refs  
- **No universal formula in Phase 1**

#### AuditEvent
- `audit_event_id`
- actor_or_system_component
- action_type
- target_ref + target_versions
- timestamp
- rationale?
- correlation ids (alert, decision, agent_run, …)

#### Version (pattern)
- Applied to: Indicator, Rule, Protocol, Agent config, evidence transformations, Analysis schema  
- Published bodies immutable; activation audited

---

## 4. Relationships (logical diagram)

Corrected relative to a naive linear tree — reflects multi-links:

```text
Tenant?
 └── Entity
      ├── Zone
      │    ├── Station
      │    ├── Observation ★
      │    ├── IndicatorValue ★
      │    └── Alert ★
      ├── Decision ★
      └── Action / Outcome (scoped)

DataSource ──► Observation ──► Dataset?
Observation ★★──► IndicatorValue
Indicator (def) ──► IndicatorValue
IndicatorValue ★★──► RuleEvaluation
Rule + RuleVersion ──► RuleEvaluation
RuleEvaluation ★★──► EvidenceItem ──► EvidencePackage
AgentRun / Analysis ──► EvidenceItem (analytical)
EvidencePackage ──► Alert
Alert ★★──► DssPackage
ProtocolVersion ──► Recommendation (options)
Analysis / AgentRun ──► Recommendation
DssPackage ──► Recommendation (presented)
DssPackage ──► DssContextSnapshot (at Decision)
Decision ──► DssContextSnapshot (mandatory, immutable)
Decision ──► Action ★
Action ──► Outcome ★
Outcome ──► Observation / IndicatorValue (feedback)

★ = many possible
```

### Association table (summary)

| From | To | Nature |
|------|----|--------|
| Zone | Station | 1-to-many (many-to-many `TBD`) |
| Station/Zone | Observation | 1-to-many |
| Observation | IndicatorValue | many-to-many |
| IndicatorValue | RuleEvaluation | many-to-many |
| RuleVersion | RuleEvaluation | 1-to-many |
| RuleEvaluation | Alert | many-to-many |
| EvidenceItem | EvidencePackage | many-to-many or many-to-one (`TBD`) |
| EvidencePackage | Alert | 1-to-1 or 1-to-many versions |
| Alert | Alert | related / supersedes |
| Alert | DssPackage | many-to-many |
| DssPackage | Decision | 1-to-many over time via snapshots |
| Decision | DssContextSnapshot | many-to-one (typically 1:1); snapshot immutable |
| Decision | Alert | many-to-many (historical ids also in snapshot) |
| Decision | Action | 1-to-many |
| Action | Outcome | 1-to-many |
| Actor | Decision | 1-to-many |
| Actor | AuditEvent | 1-to-many |
| Agent | AgentRun | 1-to-many |

---

## 5. Versioning strategy (conceptual)

### Identity vs version

```text
Rule (identity)  →  RuleVersion v1, v2, v3 (immutable published bodies)
Protocol         →  ProtocolVersion …
Indicator        →  IndicatorVersion …  (naming: body versions under Indicator)
Agent            →  AgentConfigVersion …
Transformation   →  TransformVersion …
AnalysisSchema   →  SchemaVersion …
```

### Rules

1. Editing an active definition creates a **new version**, does not overwrite the old body.
2. Evaluations and EvidenceItems store **version ids used**.
3. Activation/deprecation emits AuditEvent + domain events.
4. Past Alerts/RuleEvaluations remain interpretable under the versions they used.
5. Threshold changes are RuleVersion changes.

Governance workflow (propose → review → approve → activate) is required conceptually; authority matrix is `TBD`.

---

## 6. Domain events (conceptual only)

Not an event-sourcing mandate — names for domain language and future audit/integration.

| Event | Meaning | Affects | Minimum information | Auditable? |
|-------|---------|---------|---------------------|------------|
| `ObservationRecorded` | New primary observation accepted | Observation, Dataset? | id, source, time, space, variable, quality ref | Yes |
| `DataQualityAssessed` | Quality result attached/updated | DataQuality, Observation/IndicatorValue | target id, method/version, result | Yes |
| `IndicatorCalculated` | IndicatorValue produced | IndicatorValue | indicator+version, scope, window, inputs refs | Yes |
| `RuleEvaluated` | RuleVersion run | RuleEvaluation | rule+version, inputs, outcome, time | Yes |
| `EvidenceItemCreated` | Atomic evidence unit created | EvidenceItem | kind, ref, epistemic label | Yes |
| `EvidencePackageCreated` | Package assembled | EvidencePackage | subject, item ids, gaps/conflicts | Yes |
| `AlertCreated` | Alert opened | Alert | scope, severity, rule evals, evidence package | Yes |
| `AlertReviewed` | Moved to under review | Alert, AlertStatus | alert id, actor, time | Yes |
| `AlertAcknowledged` | Awareness acknowledgment | Alert | alert id, actor, time (**not** a Decision) | Yes |
| `AlertResolved` / `AlertClosed` | Lifecycle end states | Alert | alert id, actor, reason? | Yes |
| `AlertRetracted` | Alert invalidated with reason | Alert | alert id, reason, actor | Yes |
| `AgentRunCompleted` | Agent execution finished | AgentRun, Analysis? | agent+version, inputs, outputs meta | Yes |
| `RecommendationGenerated` | Recommendation created/presented | Recommendation, DssPackage | source, label RECOMMENDATION | Yes |
| `DssPackageOpened` | DSS context assembled | DssPackage | alert ids, evidence refs | Yes (optional volume) |
| `DecisionRecorded` | Human decision captured | Decision | **actor**, alerts, option, justification, time | Yes |
| `ActionRecorded` | Action linked to Decision | Action | decision id, what, status, time | Yes |
| `OutcomeRecorded` | Outcome linked | Outcome | action/decision, observation/indicator refs | Yes |
| `RuleVersionActivated` | Version becomes effective | RuleVersion | rule id, version, actor, rationale | Yes |
| `ProtocolVersionActivated` | Protocol version effective | ProtocolVersion | protocol id, version, actor | Yes |
| `IndicatorVersionActivated` | Indicator definition activated | Indicator | indicator id, version, actor | Yes |

All listed events are **historically meaningful** and should be representable as or mirrored by AuditEvents where governance requires.

---

## 7. Epistemic labeling (model rule)

Every EvidenceItem, Analysis, Recommendation, and Decision carries or implies an EpistemicLabel:

| Label | Typical carriers |
|-------|------------------|
| FACT | Observation **as a recording** (not necessarily world-truth), RuleEvaluation result record, Alert status-as-recorded, IndicatorValue-as-computed |
| INFERENCE | Analysis, many AgentRun outputs |
| RECOMMENDATION | Recommendation, ranked protocol options as suggestions |
| DECISION | Decision only |

Mixing without labels violates invariants.

---

## 8. Conflicts with Phase 0?

None requiring silent override. Alignments:

- Human-only Decision — preserved.
- ACKNOWLEDGED ≠ Decision — preserved and strengthened.
- Rules versioned; thresholds not prompt-only — preserved.
- Agents assist; do not decide — preserved.
- Evidence structured — preserved via EvidenceItem/Package.

Open architecture questions from Phase 0 (State vs Alert, agent soft alerts, geometry, tenancy) remain open in [10-domain-open-questions.md](./10-domain-open-questions.md).

### Phase 6 reading

`SituationReading` is a projection over alerts, evaluations, evidence, indicator values, and protocol recommendations. `DataGap` and `UncertaintyStatement` describe missing context and qualitative uncertainty. They are not alerts, risks, or decisions. A recommendation keeps the label `RECOMMENDATION`. The historical source for a decision remains `DssContextSnapshot`.

---

## 9. Related documents

- [07-domain-glossary.md](./07-domain-glossary.md)
- [09-domain-invariants.md](./09-domain-invariants.md)
- [10-domain-open-questions.md](./10-domain-open-questions.md)
- [02-conceptual-architecture.md](./02-conceptual-architecture.md)
- [06-evidence-and-traceability.md](./06-evidence-and-traceability.md)
