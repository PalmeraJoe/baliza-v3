# 03 — DSS Principles

## Purpose

Defines how the Decision Support System (DSS) must behave conceptually: what it shows, what it must never do, and how it separates **facts**, **inferences**, **recommendations**, and **decisions**.

---

## Core statement

> The DSS helps a responsible human understand a situation and choose among options.  
> The DSS does **not** decide for the human.  
> The DSS does **not** execute operational actions by itself.

---

## Alert → decision flow (conceptual)

```text
ALERTA
  ↓
EVIDENCIA
  ↓
CONTEXTO
  ↓
INCERTIDUMBRE
  ↓
INTERPRETACIONES
  ↓
OPCIONES
  ↓
CONSIDERACIONES
  ↓
DECISIÓN HUMANA
  ↓
RESULTADO
```

Each step must remain distinguishable in the information model and in the UI narrative (UI design is later; the conceptual separation applies now).

---

## What the DSS presents

For a given alert or investigation context, the DSS package should include:

| Element | Description | Epistemic label |
|---------|-------------|-----------------|
| **Situation** | What alert/state is active, where, when, severity | Primarily FACT (system state) |
| **Evidence** | Linked data, indicators, rule hits, sources | FACT + provenance |
| **Context** | Spatial-temporal and operational framing | FACT and/or curated reference |
| **Uncertainty** | Quality, confidence, conflicts, gaps | Explicit uncertainty objects |
| **Interpretations** | Possible readings of the evidence | INFERENCE (must be labeled) |
| **Action options** | Protocol-linked or documented alternatives | RECOMMENDATION (catalog + guidance) |
| **Considerations** | Trade-offs, constraints, missing info | Mixed; must cite basis |
| **Decision capture** | Form for human choice + justification | DECISION (human-authored) |
| **Outcome linkage** | Later results tied back | FACT relative to observations |

---

## Mandatory epistemic separation

These four must **never** be mixed in storage or presentation without clear labeling:

### FACT

Observable or deterministically derived statements with provenance.

Examples:

- “Sensor S1 recorded SST = … at timestamp T (quality = …).”
- “Rule `thermal_stress` v3.2 evaluated TRUE.”
- “Alert A-123 is OPEN since …”

### INFERENCE

Interpretive statements that go beyond deterministic rule outputs, typically from agents or human analysts.

Examples:

- “Patterns are consistent with a short-lived thermal anomaly rather than a seasonal shift.”
- “Literature suggests similar events were associated with …”

Inferences must carry: basis, confidence, limitations, and must not be shown as facts.

### RECOMMENDATION

Suggested options or prioritizations for human consideration (from protocols, playbooks, or advisory agents).

Examples:

- “Option P1: increase monitoring frequency.”
- “Option P2: temporary access restriction (requires human authority).”

Recommendations must not auto-execute.

### DECISION

A recorded human choice: who, when, what option/action, why.

Only humans (authorized roles) create decisions. Agents may draft a suggested justification text; the decision act remains human (`TBD` whether draft justifications are allowed).

---

## DSS behavioral rules

1. **No silent automation of choices.** If the system ranks options, ranking is labeled as recommendation, not decision.
2. **No hiding of empty evidence.** If evidence is thin, the DSS must say so.
3. **No collapsing uncertainty into a single green/red without access to detail.**
4. **Always link back** to Evidence Chain identifiers.
5. **Distinguish rule-fired alerts from agent commentary.**
6. **Protocols are options, not triggers.** Alert ≠ execute protocol.
7. **“Do nothing / monitor” must be a valid decision path** when appropriate.
8. **Post-decision,** the DSS should support attaching outcomes without rewriting history.

---

## Alert lifecycle vs DSS

The Alert Engine owns alert state transitions (open, acknowledged, escalated, resolved — exact states `TBD`).

The DSS owns the **decision-support presentation and decision capture** around alerts.

Acknowledging an alert (operator awareness) is **not** the same as an operational decision to enact a protocol. Both should be recorded separately.

---

## Minimal DSS session (logical)

1. Open alert / zone context  
2. Show facts (data, indicators, rule outcomes)  
3. Show evidence package + quality  
4. Show uncertainty and gaps  
5. Show labeled inferences (if any)  
6. Show action options from applicable protocols  
7. Capture human decision + justification  
8. Record action status  
9. Later: attach outcome observations  

---

## Anti-patterns (forbidden)

- “Auto-resolve by applying recommended protocol.”
- “AI decided to close the beach.”
- Showing only a chatbot answer without Evidence Chain links.
- Embedding critical thresholds only in explanatory text.
- Presenting a single option as if no alternative exists when protocols define several.

---

## Open Questions

1. May the DSS propose a **default highlighted option**? If yes, labeling and liability implications `TBD`.
2. Multi-party decisions (e.g., scientist + manager co-approval) — required for some protocols? `TBD`
3. Time-bounded decisions (review-by date) — needed in v1? `TBD`
4. How to present conflicting scientific interpretations without inducing alert fatigue? `TBD` (UX later; information model must allow conflict)
5. Should “acknowledgment” require a reason code? `TBD`

---

## Related documents

- [01-product-definition.md](./01-product-definition.md)
- [04-rules-and-protocols.md](./04-rules-and-protocols.md)
- [05-ai-agents.md](./05-ai-agents.md)
- [06-evidence-and-traceability.md](./06-evidence-and-traceability.md)
