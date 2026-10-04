# 09 — Domain Invariants

## Purpose

Rules that **must always hold** in the BALIZA V3 domain, independent of technology.  
Violations are defects; workarounds that hide violations are forbidden (`AGENTS.md`).

---

## Invariant 1 — Decision requires a responsible Actor

A `Decision` **must** reference an `Actor` accountable as the decision-maker.

- System components and `AgentRun`s are **not** valid Decision actors.
- If multi-party approval is introduced later, each approving party is still an Actor (`TBD` structure).

---

## Invariant 2 — Action is never an implicit Decision

An `Action` **must** reference a pre-existing `Decision`.

- Recording an Action without a Decision is invalid.
- “We just did X in the field” still requires a Decision record (possibly retrospective under explicit policy — policy `TBD`, but Action alone is insufficient).

---

## Invariant 3 — Critical alerts require evidence traceability

A critical `Alert` (severity taxonomy `TBD`, but whatever is designated critical) **must** reference an `EvidencePackage` that can be expanded to underlying items (observations, indicator values, rule evaluations, etc.).

- Alerts must not exist as unexplained narrative.
- Incomplete evidence, if temporarily allowed, must be **explicitly marked** as incomplete/gaps — not silently empty (see also Invariant 9).

---

## Invariant 4 — Rule evaluations preserve version identity

Every `RuleEvaluation` **must** store the `rule_id` **and** `rule_version` used.

- Re-running with a new version creates a new evaluation; it does not rewrite the old one.
- Alerts cite evaluations (and thus versions), not “the rule” without version.

---

## Invariant 5 — AgentRun is not a Decision

`Agent`, `AgentRun`, `Analysis`, and agent-produced `Recommendation` **must not** be treated as `Decision`.

- No status flag on AgentRun may mean “decided.”
- No automatic creation of Decision from AgentRun completion.

---

## Invariant 6 — ACKNOWLEDGED ≠ DECIDED

`AlertStatus = ACKNOWLEDGED` means awareness / receipt by a human workflow — **not** an operational Decision.

- Acknowledgment and Decision are separate records.
- Closing an alert without a Decision may be allowed for non-operational dismissals (`TBD` policy) but must not forge a Decision.

---

## Invariant 7 — Rule (and other definition) history is preserved

Changes to Rules, Thresholds, Protocols, Indicators, and Agent configs that affect outputs **must not** destroy prior published versions.

- Activation creates/points to new versions.
- Past evaluations remain interpretable.

---

## Invariant 8 — Epistemic kinds remain distinguishable

`FACT`, `INFERENCE`, `RECOMMENDATION`, and `DECISION` **must** remain distinguishable in the model (via `EpistemicLabel` or equivalent separation of entity types).

- UI/presentation (later) must not be the only place this distinction exists.
- Storing an inference as if it were an Observation FACT is invalid.

---

## Invariant 9 — Absence of data ≠ absence of risk

Missing observations, failed quality gates, or empty windows **must not** be interpreted automatically as “no risk” / “healthy.”

- Gaps must be representable on EvidencePackages and Uncertainty.
- Rules may explicitly require minimum data; failing that yields no false-green certainty.
- `UNKNOWN`, `INSUFFICIENT_DATA`, and `NOT_TRIGGERED` are distinct rule outcomes. Neither absence nor an undetermined quality is rewritten as not triggered.

---

## Invariant 10 — AI recommendations are labeled as recommendations

Any recommendation originating from AI (`AgentRun` / `Analysis`) **must** be identifiable as `RECOMMENDATION` (and typically not FACT).

- Protocol catalog options presented as suggestions are also recommendations when offered for choice.
- Recommendations must not auto-execute as Actions.
- A DSS situation reading may list options. It must not record a Decision or an Action.

---

## Invariant 11 — Protocols do not auto-execute on Alerts

Creating or updating an `Alert` **must not** by itself create an `Action` or `Decision`.

- Protocol linkage may generate `Recommendation`s inside a `DssPackage` only.

---

## Invariant 12 — Critical thresholds are not LLM-only

Thresholds that drive critical alerting **must** live on versioned `RuleVersion` (or equivalent deterministic configuration), not solely inside prompts or free-text agent instructions.

---

## Invariant 13 — Evidence is structured

`EvidenceItem` / `EvidencePackage` content **must** include references to underlying artifacts (ids/kinds), not only unstructured prose.

- Prose may annotate; it cannot be the sole evidence body for critical paths.

---

## Invariant 14 — Outcomes do not rewrite history

Recording an `Outcome` **must not** mutate prior Observations, RuleEvaluations, Alerts, or Decisions in place.

- Feedback may add links and new evidence; corrections use supersession/compensation patterns.

---

## Invariant 15 — Decision justification is mandatory

A `Decision` **must** carry a justification (structured and/or textual with minimum length/policy `TBD`) plus snapshot of options considered (or explicit custom-path marker).

---

## Invariant 16 — System components are auditable actors of change, not decision-makers

Ingestion jobs, rule engines, and orchestrators may emit `AuditEvent`s as system subjects for what they changed/produced, but **cannot** satisfy Invariant 1 as Decision makers.

---

## Invariant 17 — Decision freezes the DSS context that was considered

A `Decision` **must** reference a first-class immutable `DssContextSnapshot` of the DSS context considered at `decided_at`.

The snapshot **must** be sufficient to reconstruct, without live joins to mutable rows:

- related `Alert` ids and the alert state **as presented**;
- `EvidencePackage` id(s) and `EvidenceItem` id(s) (kind, epistemic label, refs/hashes);
- `RuleVersion` and `RuleEvaluation` id(s) cited;
- `IndicatorVersion` cited via evaluations/values;
- `ProtocolVersion` and options presented;
- `Recommendation`s presented (protocol and/or AI);
- `Analysis` / `AgentRun` outputs **if they were shown**;
- uncertainty, gaps, and missing-data flags as shown;
- relevant timestamps (`frozen_at`, and source clocks as copied).

The live `DssPackage` may continue to evolve afterward. The snapshot is **immutable after Decision**. Reconstructing the Decision solely by re-querying current data is invalid.

Copies of mutable presented state are stored inside the snapshot at freeze: alert status and severity, evidence descriptors (kind, epistemic label, provenance, narrative), thresholds applied, and protocol option text. Later updates to those rows do not change the snapshot. Ids alone are not a substitute for that presented state.

Rationale: enable reconstruction of what BALIZA presented and what the Actor decided upon (Phase 1.5 / 2.5). See ADR-011.

---

## Conflict log

No Phase 0 conflicts requiring human review were introduced by these invariants. They codify Phase 0 principles.

If a future implementation proposal violates an invariant:

```text
CONFLICT
WHY IT MATTERS
PROPOSED RESOLUTION
STATUS: REQUIRES HUMAN REVIEW
```
