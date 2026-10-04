# 04 — Rules and Protocols

## Purpose

Defines the conceptual vocabulary for **rules**, **indicators**, **alerts**, **protocols**, **thresholds**, **conditions**, and **evidence requirements**, including versioning and audit expectations.

Nothing in this document is a validated scientific parameter set. Numeric examples are illustrative only and marked as such.

---

## Definitions

### Indicator

A **defined, versioned metric** derived from normalized data (and possibly other indicators).

- Has a clear formula or computation specification.
- Has units, temporal aggregation, and spatial scope.
- Is **not** by itself an alert.

**TBD:** Formal indicator specification language / registry format.

---

### Threshold

A **explicit boundary value or set of boundaries** used in conditions (e.g., critical/warning levels).

- Thresholds that drive operational alerts are **critical configuration**.
- Must be versioned and auditable.
- Must **not** live only inside LLM prompts.

Scientific validity of any specific threshold is `TBD` pending domain expert validation.

---

### Condition

A **boolean (or multi-valued) predicate** over indicators, data quality, duration, spatial scope, or combinations thereof.

Example (illustrative, **not** a real scientific rule):

```text
IF temperature_anomaly > threshold
AND duration >= X
AND data_quality >= minimum
THEN rule_outcome = candidate_alert("thermal_stress")
```

---

### Rule

A **deterministic, explicit, versioned specification** that, given inputs and conditions, produces a reproducible outcome (typically a candidate alert or state signal) plus provenance.

| Property | Requirement |
|----------|-------------|
| Deterministic | Same inputs + same rule version → same outcome |
| Explicit | Conditions and thresholds visible to authorized reviewers |
| Auditable | Changes leave an audit trail |
| Versioned | `rule_id` + `version` identity |
| Bounded | Does not execute protocols or human decisions |

**A rule is not a protocol.**

---

### Alert

A **traceable system output** representing a condition of concern (or informational state) for an entity/zone.

An alert should be associable with:

- entity/zone;
- timestamp (event and detection);
- variables / indicators;
- rule(s) and versions;
- evidence package;
- data quality;
- severity / level;
- uncertainty;
- explanation (structured; may include agent narrative as INFERENCE);
- status / lifecycle;
- history.

**An alert does not automatically execute a protocol.**

---

### Protocol

A **documented set of possible actions** that may be considered when certain alerts or states occur.

| Protocol is | Protocol is not |
|-------------|-----------------|
| A catalog of options and considerations | An automatic script the system runs on alert |
| Linked to alert types / severities (`TBD` linkage model) | A substitute for human decision |
| Versionable guidance | A hidden rule threshold |

**A protocol is not a rule.**

---

### Evidence (in this context)

Structured support attached to rule outcomes, alerts, and DSS packages: references to data, indicators, quality, sources, and optional agent analyses. See [06-evidence-and-traceability.md](./06-evidence-and-traceability.md).

---

## Conceptual structure of a rule (proposal)

This YAML-like sketch is a **conceptual proposal**, not a final schema.

```yaml
rule_id: "thermal_stress_candidate"   # stable identifier
version: "0.0.0"                      # semver or equivalent TBD
name: "Thermal stress candidate"      # human label
description: >
  Illustrative only. Detects sustained temperature anomaly
  under minimum data quality. NOT scientifically validated.

inputs:
  - indicator_id: "sst_anomaly"       # TBD real indicators
    version_constraint: ">=1.0.0"     # TBD
  - quality_signal: "sst_quality"

conditions:
  all:
    - "sst_anomaly.value > thresholds.anomaly_high"
    - "sst_anomaly.duration_hours >= thresholds.min_duration_hours"
    - "sst_quality.score >= thresholds.min_quality"

thresholds:
  anomaly_high: null                  # TBD — scientific validation required
  min_duration_hours: null            # TBD
  min_quality: null                   # TBD

severity: "warning"                   # enumeration TBD

evidence_requirements:
  - "include_raw_series_window"
  - "include_indicator_snapshot"
  - "include_quality_report"

data_quality_requirements:
  min_score: null                     # TBD
  allow_partial: null                 # TBD

effective_from: null                  # TBD
effective_to: null                    # TBD
status: "draft"                       # draft | active | deprecated | retired

# metadata
owners: []                            # TBD authority model
change_rationale: null
scientific_references: []             # required before activation — TBD process
```

**No numeric thresholds are asserted as product truth in Phase 0.**

---

## Conceptual structure of a protocol (proposal)

```yaml
protocol_id: "response_thermal_stress"
version: "0.0.0"
name: "Response options for thermal stress alerts"
applies_to_alerts:
  - rule_id: "thermal_stress_candidate"
    min_severity: "warning"           # TBD
options:
  - option_id: "monitor_intensify"
    label: "Intensify monitoring"
    description: "..."
    requires_roles: []                # TBD
  - option_id: "restrict_access"
    label: "Temporary access restriction"
    description: "..."
    requires_roles: []                # TBD
    notes: "Requires human authority; never auto-executed"
  - option_id: "no_action"
    label: "Monitor / no operational change"
    description: "..."
considerations:
  - "Guest/operations impact"         # domain-specific TBD
  - "Ecological risk"
  - "Data confidence"
status: "draft"
```

---

## Versioning principles

1. **Immutable published versions.** Editing an active rule creates a new version; history is preserved.
2. **Effective windows.** `effective_from` / `effective_to` (or equivalent) define when a version applies to evaluations.
3. **Evaluation stamps.** Every rule outcome stores `rule_id`, `version`, and evaluation timestamp.
4. **Protocols version independently** from rules, with explicit linkage versions where needed.
5. **Indicators version independently**; rules declare compatible indicator versions.

Exact versioning scheme (semver vs calver vs monotonic) is `TBD`.

---

## Audit of changes

Any change to rules, thresholds, indicators (definitions), or protocols should record:

| Field | Intent |
|-------|--------|
| Who | User / role identity |
| When | Timestamp |
| What | Diff or replacement version |
| Why | Change rationale (mandatory for scientific activation) |
| From → To | Previous and new version ids |
| Approval | Approver identity if dual-control (`TBD`) |
| References | Scientific or operational basis |

**Draft** changes must not affect production evaluations until activated under the governance process (`TBD`).

---

## Governance (conceptual)

```text
Propose change → Review → (Scientific validation if needed) → Approve → Activate version → Audit log
```

Who holds approval rights is `TBD` (see Open Questions).

AI agents may **draft** proposed rule text or explanations of impacts; they must **not** activate versions or alter thresholds autonomously.

---

## Interaction with AI

| Allowed | Forbidden |
|---------|-----------|
| Explain why a rule fired | Change thresholds silently |
| Suggest missing evidence checks | Encode critical thresholds only in prompts |
| Help authors draft rule documentation | Auto-activate rules |
| Flag inconsistency between protocol and alert type | Execute protocol options |

---

## Open Questions

1. Rule expression language (DSL vs typed UI builder vs code modules)? `TBD`
2. Dual-control approval for threshold changes? `TBD`
3. Can multiple rules contribute to one alert, and how is severity composed? `TBD`
4. Hysteresis / cooldown to prevent alert flapping — policy owner? `TBD`
5. Localization of protocol text for operators? `TBD`
6. Which alert types are “critical” and therefore forbidden from AI-only paths? `TBD` pending risk assessment

---

## Related documents

- [02-conceptual-architecture.md](./02-conceptual-architecture.md)
- [03-dss-principles.md](./03-dss-principles.md)
- [05-ai-agents.md](./05-ai-agents.md)
- [AGENTS.md](../AGENTS.md)
