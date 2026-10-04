# 05 — AI Agents

## Purpose

Defines a **minimal conceptual agent architecture** for BALIZA V3: roles, inputs/outputs, limits, autonomy, and traceability.

No agents are implemented in Phase 0. This is a design hypothesis for later phases (roadmap Phase 8, after Evidence and Alert foundations).

---

## Design stance

AI agents in BALIZA are **assistive analysts** inside the DSS and Evidence Layer.

They:

- interpret and contextualize;
- compare and explain;
- detect inconsistencies and gaps;
- help formulate scenarios;

They do **not**:

- take final operational decisions;
- execute closures/restrictions/protocols;
- modify scientific rules or critical thresholds on their own;
- invent evidence;
- hide uncertainty;
- present inferences as facts.

Critical alerting paths remain owned by the **Rule Engine**.

---

## Minimal architecture (hypothesis)

```text
Agent Orchestrator
        │
        ├── Evidence Agent
        ├── Context Agent
        ├── Anomaly Agent
        └── Explanation Agent
```

### Assessment of necessity

| Agent | Keep in v1 hypothesis? | Rationale |
|-------|------------------------|-----------|
| **Orchestrator** | Yes | Routes tasks, enforces structured I/O, applies policy limits, records traces |
| **Evidence Agent** | Yes | Core to “evidence before inference” — assemble/compare sources and gaps |
| **Context Agent** | Yes | Spatial-temporal and operational framing for DSS packages |
| **Anomaly Agent** | Conditional | Useful for soft signals and inconsistency checks; **must not** replace deterministic rules for critical thresholds. May be deferred if early pilots are rule-only |
| **Explanation Agent** | Yes | Translates rule firings + evidence into operator-facing explanations without changing outcomes |

**Possible later agents (not in minimal set):** Literature Agent, Scenario Agent, Protocol-drafting Assistant. All would inherit the same limits. Adding them requires documented need (`TBD`).

**Recommendation:** Start implementation planning with Orchestrator + Evidence + Explanation; add Context early for DSS quality; treat Anomaly as optional until rule coverage is clear.

---

## Shared contract (all agents)

Every agent invocation should produce a structured result including at least:

| Field | Intent |
|-------|--------|
| `agent_id` / `version` | Which agent and config version |
| `task_id` | Correlation id |
| `inputs_ref` | Pointers to data/evidence/alert ids used |
| `outputs` | Typed payload |
| `epistemic_label` | FACT summary refs vs INFERENCE vs RECOMMENDATION draft |
| `confidence` / `limitations` | Explicit uncertainty |
| `sources` | Allowed sources actually used |
| `gaps` | Missing information identified |
| `timestamp` | When produced |
| `trace` | Prompt/tool/config hashes as applicable (`TBD` detail) |

Outputs that lack provenance or label must be rejected by the Orchestrator.

---

## Agent: Orchestrator

### Purpose

Coordinate agent calls for a given alert, investigation, or DSS session; enforce policies; persist traces.

### Inputs

- Task type (e.g., `enrich_alert`, `explain_alert`, `gap_analysis`)
- References to alert / evidence / zone / time window
- Policy profile (what agents may run)

### Outputs

- Ordered agent results package
- Aggregate gaps / warnings
- Orchestration trace

### Autonomy

**Low.** Runs only on explicit system or user-triggered workflows. No self-initiated operational actions.

### May

- Call allowed agents
- Refuse unsafe tasks (e.g., “auto-execute protocol”)
- Normalize outputs into Evidence Layer contributions

### Must not

- Activate rules/protocols
- Create critical alerts solely from LLM judgment (policy lean; final `TBD` in architecture open questions)
- Drop uncertainty fields

### Allowed sources

Only those passed in or registered for the task; no arbitrary web invention presented as project data.

### Traceability

Full task graph: which agents, versions, inputs, outputs, times.

---

## Agent: Evidence Agent

### Purpose

Assemble, compare, and quality-check evidence related to an alert or question; identify missing pieces and conflicts.

### Inputs

- Candidate evidence refs (data, indicators, rule outcomes)
- Alert or investigation scope
- Quality reports

### Outputs

- Evidence synopsis (structured)
- Conflict list
- Gap list
- Confidence notes

### Autonomy

**Low–medium** within analysis only.

### May

- Rank source completeness (as recommendation/inference about coverage, not truth of ecology)
- Flag contradictions between sensors/indicators
- Request (via orchestrator) additional registered sources

### Must not

- Fabricate measurements or citations
- Mark inferences as FACT
- Alter underlying data

### Allowed sources

Ingested data, indicator snapshots, rule outcomes, registered scientific references metadata (`TBD` corpus).

### Traceability

Every claim linked to `source_id` / record ids.

---

## Agent: Context Agent

### Purpose

Provide spatial, temporal, and operational context for DSS presentation (what else is known about this zone/time).

### Inputs

- Entity/zone id
- Time window
- Related alerts/decisions history (read-only)
- Relevant protocol metadata (read-only)

### Outputs

- Context brief (structured sections)
- Related historical events (referenced)
- Operational constraints notes if available from registered configs

### Autonomy

**Low.**

### May

- Summarize prior similar alerts with links
- Highlight seasonal/calendar context if data exists

### Must not

- Invent site history
- Issue operational orders
- Override alert severity

### Allowed sources

System registries, historical alerts/decisions, authorized reference layers (`TBD`).

### Traceability

Context statements with refs; unknowns listed explicitly.

---

## Agent: Anomaly Agent

### Purpose

Help detect unusual patterns, inconsistencies, or soft anomalies that may warrant human or rule attention.

### Inputs

- Indicator series / quality series for a scope
- Baselines if defined
- Rule outcomes (to avoid contradicting without note)

### Outputs

- Soft signals / hypotheses (INFERENCE)
- Suggested checks (gaps)
- Explicit “not a rule firing” label

### Autonomy

**Low.** Advisory only.

### May

- Propose follow-up analyses
- Suggest that a scientist review a pattern
- Note disagreement with a rule outcome for human review

### Must not

- Unilaterally create critical operational alerts (`TBD` hard prohibition recommended)
- Adjust thresholds
- Present soft signals as deterministic rule results

### Allowed sources

Registered time series and indicator definitions; no fabricated baselines.

### Traceability

Method notes, windows, versions; clear epistemic labeling.

### Deferral note

If early pilots rely solely on deterministic rules, this agent can be postponed without blocking DSS value.

---

## Agent: Explanation Agent

### Purpose

Produce human-readable explanations of why an alert exists, what evidence supports it, and what remains uncertain—without changing the alert outcome.

### Inputs

- Alert record
- Rule evaluation traces
- Evidence package
- Optional agent analyses

### Outputs

- Structured explanation (sections: what fired, support, uncertainty, gaps)
- Plain-language summary labeled as assistance, not as new evidence of measurements

### Autonomy

**Low.**

### May

- Rephrase rule logic faithfully
- Highlight missing evidence_requirements

### Must not

- Add unsupported causal claims
- Hide failed quality gates
- Recommend protocol execution as if decided

### Allowed sources

The provided alert/evidence/rule package only (plus registered glossary `TBD`).

### Traceability

Explanation tied to alert id, rule versions, evidence ids.

---

## Autonomy summary

| Agent | Autonomy | Can decide operationally? | Can change rules? |
|-------|----------|---------------------------|-------------------|
| Orchestrator | Low | No | No |
| Evidence | Low–medium (analysis) | No | No |
| Context | Low | No | No |
| Anomaly | Low (advisory) | No | No |
| Explanation | Low | No | No |

---

## Placement in roadmap

Agents should be introduced **after** Evidence Layer and Alert Engine exist (see [roadmap.md](./roadmap.md)), so explanations have real artifacts to bind to. Building agents before evidence invites ungrounded narratives.

---

## Open Questions

1. Hard ban on agent-originated critical alerts — confirm as policy? **Recommended yes.** `TBD` formal approval
2. Human-triggered vs automatic enrichment on every alert? `TBD` (cost, latency, audit volume)
3. Model providers, on-prem vs cloud, data residency? `TBD`
4. Evaluation harness for hallucinations and epistemic mislabeling? Required before production use — design `TBD`
5. Multilingual explanations? `TBD`
6. May Explanation Agent draft decision justifications for humans to edit? `TBD` (risk of rubber-stamping)

---

## Related documents

- [AGENTS.md](../AGENTS.md)
- [02-conceptual-architecture.md](./02-conceptual-architecture.md)
- [03-dss-principles.md](./03-dss-principles.md)
- [06-evidence-and-traceability.md](./06-evidence-and-traceability.md)
