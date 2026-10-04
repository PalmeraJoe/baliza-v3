# 06 — Evidence and Traceability

## Purpose

Defines the conceptual strategy so that any important system output can be reconstructed end-to-end: from raw data to human decision and outcome.

Traceability is a **product invariant**, not an optional logging feature.

---

## Design goals

1. **Reconstructability** — answer what/when/where/data/evidence/rule/uncertainty/gaps/options/who/action/outcome.
2. **Non-repudiation of process** — important state changes leave durable records (technical mechanism `TBD`).
3. **Epistemic honesty** — FACT / INFERENCE / RECOMMENDATION / DECISION remain separable along the chain.
4. **Version awareness** — evaluations cite the versions of indicators, rules, protocols, and agents involved.
5. **No broken chains** — UI and APIs (future) should not present alerts without evidence references, except explicitly marked incomplete states.

---

## Evidence Chain (canonical)

```text
Raw Data
   ↓
Processed Data
   ↓
Indicator
   ↓
Rule / Agent Output
   ↓
Evidence
   ↓
Alert
   ↓
DSS
   ↓
Decision
   ↓
Action
   ↓
Outcome
```

Each arrow implies stored references (ids), not only narrative text.

---

## What must be linkable

| Object | Must reference (as applicable) |
|--------|--------------------------------|
| **Raw data record** | source id, acquisition time, ingest time, spatial ref, payload checksum/hash (`TBD`) |
| **Processed data** | raw record ids, transformation id/version, quality flags |
| **Indicator value** | processed inputs, indicator definition version, time window, spatial scope |
| **Rule outcome** | rule id+version, input snapshots, thresholds applied, evaluation time |
| **Agent output** | agent id+version, inputs_ref, epistemic label, sources, confidence, gaps |
| **Evidence package** | set of the above + assembler version + conflicts/gaps |
| **Alert** | evidence package id(s), rule outcomes, entity/zone, severity, status history |
| **DSS package** | alert id, evidence, options (protocol versions), interpretations labeled |
| **Decision** | user id, time, alert/DSS refs, option selected, justification |
| **Action** | decision id, action type/status, external refs (`TBD`) |
| **Outcome** | action/decision ids, subsequent observations/indicators, assessment notes |

---

## Evidence package (conceptual)

An **Evidence package** is a structured object, not a free-text blob. Conceptually:

```text
EvidencePackage
  id
  created_at
  subject (alert candidate / zone / question)
  items[]
    kind: raw | processed | indicator | rule_outcome | agent_output | reference
    ref_id
    epistemic_label: fact | inference | ...
    quality_summary
  conflicts[]
  gaps[]
  overall_uncertainty_notes
  assembler (system component / version)
```

Exact schema is `TBD` (Phase 5).

---

## Traceability questions → chain mapping

| Question | Primary anchors |
|----------|-----------------|
| What occurred? | Alert + rule outcomes |
| When? | Event time, detection time, evaluation time |
| Where? | Entity/zone spatial refs on data and alert |
| Which data? | Raw/processed ids in evidence items |
| Which evidence? | EvidencePackage id |
| Which rule/analysis? | rule_id+version and/or agent_id+version |
| Uncertainty? | quality flags, confidence, conflicts |
| Missing info? | gaps[] |
| Options? | protocol version + option ids in DSS |
| Who decided? | Decision.user |
| What action? | Action record |
| What result? | Outcome + linked new observations |

---

## Immutability and corrections

Conceptual rules:

1. **Do not rewrite history.** Corrections append new versions or correction events linked to prior records.
2. **Supersession is explicit.** If an alert is retracted, the retraction references prior evidence and reason.
3. **Rule changes do not mutate past evaluations.** Past outcomes keep the version they used.

Storage technology for immutability (append-only store, WORM, event log) is `TBD`.

---

## Human and machine actors

Every mutation of alert status, decision, rule activation, or protocol activation must record an **actor**:

- human user id, or
- system component id (ingestion job, rule engine, orchestrator),

never an ambiguous “AI decided.” Agent outputs are actor=`agent_id` producing **inference/recommendation artifacts**, not decisions.

---

## Minimum viable audit events (conceptual)

Examples of event types (names `TBD`):

- `data.ingested`
- `data.quality_assessed`
- `indicator.computed`
- `rule.evaluated`
- `evidence.assembled`
- `alert.created` / `alert.updated` / `alert.acknowledged`
- `agent.completed`
- `dss.opened` (optional)
- `decision.recorded`
- `action.recorded`
- `outcome.linked`
- `rule.version_activated`
- `protocol.version_activated`

---

## Failure modes to design against

| Failure | Risk | Mitigation principle |
|---------|------|----------------------|
| Alert without evidence refs | Unauditable operations | Reject or mark `incomplete` visibly |
| Threshold only in prose/prompt | Non-reproducible | Thresholds in versioned rule objects |
| Agent citation without source id | Hallucination accepted as fact | Orchestrator rejects unsourced scientific claims |
| Decision without user id | Accountability break | Mandatory actor on decisions |
| Silent data repair | False confidence | Transformations versioned and linked |

---

## Relation to testing

Traceability supports later scientific and operational validation: replaying a case with stored inputs and versions should reproduce deterministic rule outcomes. Agent outputs may vary; their **inputs and versions** must still be recorded for audit even when text differs (`TBD` reproducibility policy for agents).

---

## Open Questions

1. Retention period for raw data vs evidence packages vs decisions? `TBD` (legal/ops)
2. Cross-export format for external auditors (PDF pack vs machine-readable bundle)? `TBD`
3. Cryptographic hashing / signing of evidence packages? Needed or overkill for v1? `TBD`
4. PII in observation notes — redaction strategy? `TBD`
5. How much raw payload is inlined vs pointed to cold storage? `TBD`

---

## Related documents

- [00-foundation.md](./00-foundation.md)
- [02-conceptual-architecture.md](./02-conceptual-architecture.md)
- [03-dss-principles.md](./03-dss-principles.md)
- [04-rules-and-protocols.md](./04-rules-and-protocols.md)
- [05-ai-agents.md](./05-ai-agents.md)
