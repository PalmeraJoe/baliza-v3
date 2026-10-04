# ADR-006 — Rules Engine

## Status

**ACCEPTED** (strategy); DSL syntax **PROPOSED/OPEN**

## Context

Must support Rule, RuleVersion, Threshold, RuleEvaluation with determinism, versioning, auditability, tests, and future simulation. Critical alerts must not depend on LLMs. No DSL implementation in Phase 2.

## Options

| Approach | Pros | Cons |
|----------|------|------|
| Rules as **code** only | Flexible | Harder for scientists to review; weaker config audit unless careful |
| **Declarative config** (YAML/JSON in DB) + evaluator code | Reviewable, versionable, testable | Expression power limited initially |
| Custom **DSL** | Author UX | Build cost; delay pilot |
| External BRE (Drools, etc.) | Features | Lock-in, ops, impedance with Evidence Chain |

## Decision

**Initial:** Store **RuleVersion** bodies as **declarative documents** (JSON/YAML) in PostgreSQL, including thresholds, conditions, evidence/quality requirements. Evaluate with a **versioned deterministic evaluator** implemented in the Rules module (Python).

**Evolution:** If authors need richer expressions, introduce a constrained DSL or expression subset **without** changing RuleEvaluation identity fields (`rule_id`, `rule_version`, input/threshold snapshots, `evaluated_at`).

**External BRE:** not for pilot.

### Guarantees

- Same inputs + RuleVersion ⇒ same RuleEvaluation outcome.
- Every evaluation persists version + threshold snapshot + input refs.
- `not_triggered` evaluations retained (at least for pilot) to answer “why no alert?”
- Critical Alert creation requires RuleEvaluation + EvidencePackage.

## Reason

- Matches scientific review and Inv 4/7/12.
- Avoids DSL project delaying Phase 5.
- Keeps determinism testable in CI.

## Trade-offs

- Complex temporal logic may push evaluator code updates (version the evaluator engine id on RuleEvaluation too).
- Scientists may want UI builder later (Phase 10+).

## Migration / exit

- Document schema version field on RuleVersion; migrate documents forward.
- Evaluator engine_id allows side-by-side old/new interpreters.

## References

- [04-rules-and-protocols.md](../04-rules-and-protocols.md)
- Invariants 4, 7, 11, 12
