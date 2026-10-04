# AGENTS.md — Technical Constitution of BALIZA V3

This document is binding for humans and AI coding agents working on BALIZA V3.
If a proposed change conflicts with this constitution, the change must be rejected or escalated for explicit authorization.

---

## 1. Product principles

1. **BALIZA is a Decision Support System (DSS).** It supports human decisions; it does not replace them.
2. **Human-in-the-loop is mandatory.** No operational decision (closures, restrictions, interventions, protocol execution) may be enacted by the system alone.
3. **Evidence before inference.** Facts with provenance take precedence over model-generated interpretations.
4. **Full traceability.** Any important output must answer: what, when, where, which data, which evidence, which rule/analysis, what uncertainty, what is missing, which options, who decided, what action, what outcome.
5. **Uncertainty must be explicit.** Confidence, data gaps, and conflicting signals must be visible; never silently omitted.
6. **Reproducibility.** Given the same inputs, rule versions, and configurations, deterministic parts of the system must reproduce the same outputs.
7. **Rules must be versioned.** Critical scientific and operational thresholds live in versioned rule definitions, not in ephemeral prompts.
8. **Strict separation:** facts ≠ inferences ≠ recommendations ≠ decisions ≠ actions ≠ outcomes.

---

## 2. AI principles

1. AI agents **do not** take final operational decisions.
2. AI agents **must not** invent evidence, fabricate citations, or present unsupported claims as facts.
3. AI agents **must not** hide uncertainty or present inferences as verified facts.
4. Every scientifically relevant claim produced by an agent must be traceable to an allowed source (data, indicator, rule output, literature reference, or explicit human input).
5. Critical rules and thresholds **must not** depend exclusively on LLMs. Deterministic rule engines own critical logic.
6. Agent outputs must be **structured and auditable** (typed fields, references, confidence, limitations).
7. Agents may assist the DSS (explain, contextualize, compare, flag gaps); they may not execute actions or silently alter domain state that implies an operational decision.

---

## 3. Engineering principles

1. **Modular architecture** — clear boundaries between domain concepts (data, indicators, rules, evidence, alerts, DSS, decisions).
2. **Separation of domain and infrastructure** — domain logic must not be tightly coupled to a specific DB, cloud, or UI framework.
3. **Tests** — domain rules, transformations, and critical paths require automated tests; tests must not be deleted to force a green build.
4. **Observability** — important pipelines and decisions must be loggable/auditable.
5. **Versioning** — rules, protocols, schemas, and agent configurations that affect outputs should be versioned.
6. **Security** — least privilege; no secrets in docs or code; access control for sensitive operational data (`TBD` in Phase 0).
7. **Minimal coupling** — prefer explicit interfaces between layers over shared mutable state.
8. **Documentation before major architectural decisions** — important structural choices must be written down before implementation.

---

## 4. Forbidden behavior (without explicit authorization)

An agent (coding or domain AI) MUST NOT, without documented human authorization:

| Forbidden action | Why |
|------------------|-----|
| Introduce major dependencies without justification and review | Architecture and supply-chain risk |
| Change the base conceptual architecture unilaterally | Breaks product invariants |
| Modify scientific rules or critical thresholds | Scientific and audit integrity |
| Embed critical thresholds only inside LLM prompts | Non-auditable, non-reproducible |
| Remove or weaken traceability / audit fields | Breaks DSS accountability |
| Delete or skip tests to make an implementation pass | False confidence |
| Convert DSS recommendations into automatic actions | Violates human-in-the-loop |
| Use AI where a deterministic rule is required | Undermines auditability |
| Introduce fictional data as if it were real | Corrupts evidence chain |
| Invent scientific parameters, species thresholds, or literature claims | Integrity risk |
| Silently merge FACT / INFERENCE / RECOMMENDATION / DECISION | Misleads operators |
| Execute closures, restrictions, or protocols automatically | Operational safety |
| Modify protocol definitions as if they were executable rules | Category error |
| Bypass quality gates or evidence requirements | Unsafe alerts |

---

## 5. Required separation of domain concepts

| Concept | Role | Must not be confused with |
|---------|------|---------------------------|
| **Data** | Raw or processed observations/measurements | Evidence, decisions |
| **Indicator** | Derived, defined metric over data | Rule, alert |
| **Rule** | Deterministic, versioned condition → alert/state candidate | Protocol, AI prompt |
| **Protocol** | Catalog of possible actions given states/alerts | Automatic execution, rule |
| **Evidence** | Structured, referenced support for a claim or alert | Inference without sources |
| **Alert** | Traceable system output about a condition | Decision or action |
| **DSS package** | Situation + evidence + options for a human | Final decision |
| **Human decision** | Recorded choice by a responsible user | Agent recommendation |
| **Action** | What was done after a decision | Alert itself |
| **Outcome** | Observed result after action | Proof that the decision was correct |

---

## 6. Escalation

If a task requires violating any principle above, the agent must:

1. stop;
2. document the conflict;
3. ask for explicit human authorization;
4. not proceed with a workaround that hides the violation.

---

## 7. Document authority

- Product and architecture docs under `docs/` define intent.
- This file defines constraints.
- In case of conflict between convenience and these principles, **principles win**.
- Open questions are marked `TBD` in docs; agents must not silently resolve them as requirements.
