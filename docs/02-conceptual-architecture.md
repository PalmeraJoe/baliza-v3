# 02 — Conceptual Architecture

## Status

This document describes a **conceptual** architecture. It is **not** a technology stack decision and **not** a definitive service topology.

Technology choices (languages, databases, message buses, GIS, LLM providers) are `TBD` and deferred until the domain model and layer contracts are clearer.

---

## Layer diagram

```text
DATA SOURCES
     ↓
DATA INGESTION
     ↓
QUALITY / NORMALIZATION
     ↓
INDICATORS
     ↓
RULE ENGINE ──────────┐
                      │
AI AGENTS ────────────┤
                      ↓
              EVIDENCE LAYER
                      ↓
               ALERT ENGINE
                      ↓
                    DSS
                      ↓
             HUMAN DECISION
                      ↓
                   ACTION
                      ↓
             OUTCOME / FEEDBACK
```

Rules and AI agents both contribute to the evidence layer, but with different guarantees:

- **Rule Engine** — deterministic, versioned, auditable.
- **AI Agents** — interpretive/analytical assistance; structured outputs; never sole owners of critical thresholds.

---

## Layer responsibilities and boundaries

### 1. Data Sources

**Responsibility:** Origin of raw signals (sensors, manual observations, files, remote APIs, literature metadata, etc.).

**Limits:** Sources are not trusted blindly. They do not create alerts directly.

**TBD:** Catalog of required source types for the first pilot.

---

### 2. Data Ingestion

**Responsibility:** Acquire, timestamp, associate to spatial entities, and store immutable or append-only raw records with provenance (source id, acquisition time, ingest time).

**Limits:** No business alerting logic here. No silent “fixing” of values without recording transformations.

---

### 3. Quality / Normalization

**Responsibility:** Assess fitness for use (missingness, range checks, sensor status, temporal consistency) and normalize units/formats into a consistent representation.

**Outputs:** Quality flags/scores and normalized datasets that downstream layers can reference.

**Limits:** Quality gates may **block or downgrade** use of data in rules; they do not invent replacement scientific values presented as real measurements.

**TBD:** Quality scoring model and minimum thresholds for rule evaluation.

---

### 4. Indicators

**Responsibility:** Compute defined metrics from normalized data (e.g., anomaly vs baseline, rolling statistics, indices). Indicators are first-class, versioned definitions.

**Limits:** An indicator is not an alert and not a protocol. Indicator formulas that encode critical policy thresholds should be reviewable and versioned like rules (`TBD` boundary with Rule Engine).

---

### 5. Rule Engine

**Responsibility:** Evaluate explicit, versioned conditions against indicators/data/quality to produce **rule outcomes** (candidates for alerts/state changes) with full provenance.

**Limits:**

- Does not execute protocols.
- Does not record human decisions.
- Critical thresholds live here (or in linked threshold objects), **not** only in AI prompts.

See [04-rules-and-protocols.md](./04-rules-and-protocols.md).

---

### 6. AI Agents

**Responsibility:** Interpret, contextualize, compare, explain, detect inconsistencies, and surface missing information—producing structured contributions to the Evidence Layer and DSS.

**Limits:**

- No final operational decisions.
- No silent modification of rules/thresholds.
- No invented evidence.
- Not a replacement for the Rule Engine on critical paths.

See [05-ai-agents.md](./05-ai-agents.md).

---

### 7. Evidence Layer

**Responsibility:** Assemble structured evidence objects linking data, indicators, rule outcomes, agent outputs, sources, quality, and uncertainty into an auditable package.

**Limits:** Evidence is not a decision. Conflicting evidence must be representable.

See [06-evidence-and-traceability.md](./06-evidence-and-traceability.md).

---

### 8. Alert Engine

**Responsibility:** Create, update, escalate, acknowledge, and close **alerts** as traceable system outputs, based on rule outcomes and evidence requirements.

**Limits:**

- An alert is not an automatic protocol execution.
- Alert lifecycle policies (deduplication, hysteresis) are `TBD` but must remain deterministic and auditable where they affect severity.

---

### 9. DSS

**Responsibility:** Present situation, evidence, context, uncertainty, interpretations, action options, and considerations to a human. Support investigation workflows.

**Limits:** The DSS must not auto-select and enact an option. It may rank or suggest (`TBD` whether ranking is allowed and how it is labeled as recommendation).

See [03-dss-principles.md](./03-dss-principles.md).

---

### 10. Human Decision

**Responsibility:** Capture who decided, when, on which alert/context, which option (or custom action), and justification.

**Limits:** Only authorized humans. Agents cannot substitute this record.

---

### 11. Action

**Responsibility:** Record the action taken (or explicit non-action) linked to the decision. May reference external operational systems (`TBD`).

**Limits:** BALIZA records and supports; physical execution may be outside BALIZA.

---

### 12. Outcome / Feedback

**Responsibility:** Link subsequent observations and indicators to prior decisions/actions, feeding the Evidence Chain for learning and audit.

**Limits:** Outcomes do not automatically rewrite rules. Rule changes require governed versioning.

---

## Cross-cutting concerns (conceptual)

| Concern | Intent | Status |
|---------|--------|--------|
| Identity & access | Who can view alerts, decide, edit rules | Phase 10; model `TBD` |
| Spatial-temporal context | Every relevant object has where/when | Required conceptually; model `TBD` |
| Versioning | Rules, indicators, protocols, agent configs | Required conceptually |
| Observability | Logs/metrics/traces for pipelines | Engineering principle; stack `TBD` |
| Security | Protect sensitive operational and personal data | Principles only in Phase 0 |

---

## What this architecture deliberately avoids (for now)

- Microservices vs monolith decision
- Event-driven vs request-driven topology
- Choice of LLM vendor
- Choice of time-series or geospatial database
- Exact API surface

Those are implementation decisions for later phases, after the domain model exists.

---

## Open Questions

1. Should indicator computation and rule evaluation share one “evaluation runtime” or remain separate services/modules? `TBD`
2. Are agent outputs allowed to **raise** alerts by themselves, or only enrich evidence for rule/DSS use? **Lean recommendation:** agents do not create critical alerts alone; they may propose “soft signals” that require rule or human confirmation. Final decision `TBD`.
3. How is spatial hierarchy modeled (site → zone → station)? `TBD`
4. Is there a distinct “State” object separate from “Alert” (e.g., continuous condition levels)? `TBD`
5. Feedback loop automation: how much automated suggestion of rule revision is allowed vs human-only scientific process? `TBD`

---

## Related documents

- [00-foundation.md](./00-foundation.md)
- [04-rules-and-protocols.md](./04-rules-and-protocols.md)
- [05-ai-agents.md](./05-ai-agents.md)
- [06-evidence-and-traceability.md](./06-evidence-and-traceability.md)
