# 23 — Phase 6 implementation

## 1. Objective

Phase 6 turns the verified chain into a situation a responsible person can read: what was detected, which evidence supports or limits it, what is missing, which rule and indicator version were used, which options exist, and which context was frozen for the decision.

BALIZA still does not choose or execute an option.

## 2. Scientific context

`interpret_situation` builds one `SignalReading` per rule evaluation. It copies the indicator value and version, the rule id and version, the thresholds stored on that evaluation, the outcome, the quality facet, and the clocks `observed_at`, `evaluated_at`, and `alerted_at`.

Demo thresholds stay labeled `DEMO / NON-SCIENTIFIC` on the API. The reading does not add a scientific meaning to those numbers.

## 3. Operational context

An alert remains an operational event. The reading attaches alert status, severity, and scope health when an alert exists. `ACKNOWLEDGED` is still not a decision. A package may hold several alerts; one decision freezes that package.

## 4. DataGap

`DataGap` is a value object, not a table and not an alert. Kinds come from existing outcomes:

| Source | Kind |
|--------|------|
| `UNKNOWN` / `required_input_absent` | `missing_observation` |
| `UNKNOWN` / `quality_not_determinable` | `unknown_quality` |
| `insufficient_sample` | `insufficient_coverage` |
| other `INSUFFICIENT_DATA` | `below_minimum_quality` |
| other evidence-package gap text | `stated_gap` |

The placeholder gap `not_triggered` is not treated as missing data.

## 5. Uncertainty

`UncertaintyStatement` uses `known`, `unknown`, `insufficient`, `conflicting`, or `suspect`. It stores a reason and the source evaluation or evidence package. It does not store a confidence number.

`EvidencePackage.conflicts` becomes `conflicting`. It does not become `NOT_TRIGGERED` and it does not create a decision.

## 6. Evidence synthesis

Existing evidence kinds are grouped:

- `primary` and `derived` support the signal
- `data_quality` limits it
- `contextual` is listed separately
- package conflicts are the contradictory list
- data gaps are the missing list

Quality posture is one of three sentences: evidence supports the signal, evidence is limited, or the state cannot be determined reliably.

## 7. Protocol and options

`ProtocolOption` carries a code, a description, preconditions, and constraints when those strings are supplied. The catalog does not invent consequences or resource claims.

A published `ProtocolVersion` still rejects `with_options` and `with_option_details` in the domain. Presented options become `RecommendationView` records with epistemic label `RECOMMENDATION`.

## 8. Recommendation semantics

Opening a package that has recommendations writes `recommendation.presented`. That event does not write a Decision or an Action. Options stay visible together; none is selected by the system.

## 9. DSS package

`DssPackage` remains the live context: alerts, evidence packages, evaluations, gaps, and recommendations. It can change after it is opened.

## 10. Snapshot

Freeze now also copies data gaps, uncertainty statements, signal readings (including clocks, quality, versions, thresholds, and spatial reference), and the evidence synthesis. The hash covers those fields. Later edits to the live alert, evidence narrative, package recommendations, or protocol draft do not change the hash. An outcome does not change it.

## 11. Multi-alert decisions

Several alerts can be placed on one package. The snapshot stores each alert id and each signal reading. The decision points at that snapshot, not at the current alert row.

## 12. Temporal context

Observation time, evaluation time, and alert time stay on the reading. Decision time stays on `Decision.decided_at`. Action and outcome keep their own clocks.

## 13. API

New read routes, all through application queries:

- `GET /alerts/{id}/context`
- `GET /dss/packages/{id}/brief`
- `GET /dss/packages/{id}/evidence`
- `GET /dss/packages/{id}/options`
- `GET /dss/packages/{id}/snapshots`

They follow the existing `/dss/packages` path. Responses set `decision` to null and `ai_used` to false. Thresholds are marked demo.

## 14. Testing

`tests/test_phase6.py` covers a triggered reading, unknown versus insufficient, conflicting evidence, a two-alert freeze that survives later mutation, decision preconditions, and the read API.

## 15. Limitations

- No PostgreSQL migration was required: new reading fields live in the existing snapshot and package JSON.
- Protocol versions are not stored in a SQL catalog. Immutability of a published protocol is enforced in the domain object, and the presented text is what the snapshot keeps.
- `Actor` has no SQL table. Identity provider mapping remains future work and must not replace the domain Actor.
- `ScopeHealth` was not given a conflicting-evidence value.
- No GIS. `spatial_ref` is an opaque string. Entity, Zone, and Station stay distinct and are not implemented as tables here.
- No uncertainty alert policy was added.

## 16. Open questions

See items 36–39 in `docs/10-domain-open-questions.md`.
