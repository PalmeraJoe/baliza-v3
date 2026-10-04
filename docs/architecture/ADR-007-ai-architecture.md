# ADR-007 — AI Architecture

## Status

**ACCEPTED**

## Context

Agents assist Evidence/DSS (Analysis, Recommendation, explanation). They must not own critical alert thresholds or create Decisions/Actions. Provider must be replaceable (acceptance I).

## Decision

```text
AI Orchestrator (application service)
    → Agent + AgentVersion (config, prompts, tool allowlist, model params)
        → AgentRun (durable record)
            → Analysis / Recommendation (structured, EpistemicLabel)
                → optional EvidenceItem (analytical)
                → DssPackage enrichment
```

**LLM Gateway port:** interface in domain/application; adapters for OpenAI-compatible APIs, Anthropic, etc. (e.g., LiteLLM-style or thin custom adapters).

**Not on critical path:**

```text
Rule Engine → RuleEvaluation → Evidence → Alert (critical)
AI ↛ Alert(critical), Decision, Action
```

**Guardrails:** structured output schemas; require sources for scientific claims; tool allowlist excludes decision/action/rule-activation; timeouts/token budgets; treat LLM failure as DEGRADED AI section.

**Versioning:** AgentVersion includes prompt hash/config; AgentRun stores agent_id+version, inputs_ref, outputs, sources, confidence, gaps, timestamps, optional trace object_key.

**Retrieval / scientific sources:** only registered corpora / Evidence refs — no unaudited web invention presented as project evidence.

## Reason

- Aligns with AGENTS.md and frozen lean ban on agent-only critical alerts.
- Replaceable providers without domain rewrite.
**Pilot can ship with AI disabled** (rules-only DSS). Enabling agents later must not change the critical alert path. This is a **frozen** architecture property (Phase 2.5).

## Trade-offs

- Async enrichment means UI must show pending/degraded AI.
- Prompt/trace retention may have LEGAL constraints (Q39).

## Migration / exit

- New adapter implements gateway port.
- Disable AI module via config; DSS remains functional.

## Alternatives

- Embed LLM calls inside Rules — **rejected**.
- Agent framework lock-in without gateway — **rejected**.

## References

- [05-ai-agents.md](../05-ai-agents.md)
- Invariants 5, 10, 12
