# 21 — Phase 5 implementation

## 1. Objectives

Close the three limitations left by the Phase 4 audit:

1. One canonical store for structural relations.
2. Published `IndicatorVersion` immutability, matching published `RuleVersion`.
3. `UNKNOWN` distinct from `INSUFFICIENT_DATA`, and neither rewritten as `NOT_TRIGGERED`.

Architecture stays a modular monolith with PostgreSQL as the system of record. No Phase 6 work.

## 2. Decisions

- Junction tables are the operational source for indicator observations, rule-evaluation inputs, evidence-package membership, and alert evaluations.
- JSON remains for notes, thresholds, input snapshots, alert history, the live DSS package payload, and the frozen DSS context snapshot.
- Publication states stay `DRAFT`, `PUBLISHED`, `DEPRECATED`. A formula change is a new version. `DEPRECATED` is also not editable through `with_formula` / `with_baseline`.
- Missing required input and undetermined quality map to `UNKNOWN`. Data that exists but misses the minimum sample or usable quality maps to `INSUFFICIENT_DATA`.
- Alerts are still created only when the outcome is `TRIGGERED`. Uncertainty is recorded as evidence and package gaps, not as a new critical-alert policy.

## 3. Domain changes

`RuleOutcome.UNKNOWN` (`unknown`).

`EvidenceKind.DATA_QUALITY` (`data_quality`) for limitation evidence. The narrative is the evaluation reason. Epistemic label stays `FACT`.

Deterministic mapping in `evaluate_rule`:

| Condition | Outcome | Reason |
|-----------|---------|--------|
| Numeric value usable and comparison holds | `TRIGGERED` | comparison text |
| Numeric value usable and comparison fails | `NOT_TRIGGERED` | comparison text |
| Facet `INSUFFICIENT`, including a null value | `INSUFFICIENT_DATA` | `insufficient_sample` |
| Facet `UNKNOWN` | `UNKNOWN` | `quality_not_determinable` |
| Missing indicator, null value, `MISSING`, `SOURCE_UNAVAILABLE` | `UNKNOWN` | `required_input_absent` |
| `SUSPECT`, `LOW_QUALITY`, `DELAYED` | `INSUFFICIENT_DATA` | `below_minimum_quality:<facet>` |
| `INVALID` or missing threshold | `INVALID_INPUT` | existing reasons |

`IndicatorVersion.with_formula` rejects any non-draft version with `PublishedVersionImmutable`.

The decision snapshot payload records `indicator_version` and `input_quality` beside the frozen thresholds.

## 4. Persistence

Canonical links:

| Relation | Table |
|----------|--------|
| IndicatorValue → Observation | `indicator_value_observations` |
| RuleEvaluation → IndicatorValue | `rule_evaluation_inputs` |
| EvidencePackage → EvidenceItem | `evidence_package_items` |
| Alert → RuleEvaluation | `alert_evaluations` |

`indicator_values.indicator_version_id` references `indicator_versions.id`.

Removed as operational columns: `source_observation_ids`, `input_indicator_value_ids`, `evidence_packages.item_ids`, `alerts.rule_evaluation_ids`.

ORM `before_update` / `before_delete` reject a published indicator version. Alembic `0004_phase5` adds the same PostgreSQL trigger, backfills junctions from the JSON lists, then drops those columns.

## 5. UNKNOWN vs INSUFFICIENT_DATA

`UNKNOWN` means the result cannot be determined. `INSUFFICIENT_DATA` means data exists and fails an explicit minimum. Neither is `NOT_TRIGGERED` and neither means no risk.

## 6. IndicatorVersion immutability

Draft versions can change formula or baseline. Published versions cannot be updated or deleted. A later version can be inserted beside the old one. `IndicatorValue` keeps the version id and version string used at calculation time.

## 7. Canonical relational sources

Reads of membership go through the junction rows ordered by `position`. Changing `notes` JSON does not change observation links. Frozen snapshot JSON is historical context, not the live membership store. Live DSS package membership stays in the single package payload document.

## 8. Snapshot implications

Freeze still copies alert state, evidence descriptors, thresholds, and protocol option text, and now also the presented indicator version and input quality. The hash covers that payload. An outcome does not rewrite the snapshot.

## 9. Tests

`tests/test_phase5.py` covers outcome separation, published indicator update/delete rejection, a new version, version reference on the value, and junction reads after a notes change and a new session.

Existing suites were updated where a missing input was previously asserted as `INSUFFICIENT_DATA`. That case is now `UNKNOWN`.

## 10. Limitations

- PostgreSQL upgrade, downgrade, and the indicator trigger have not been executed here. There is no PostgreSQL server in the test environment. Phrase: PostgreSQL transaction test = pending infrastructure.
- No uncertainty-alert policy was added.
- Demo thresholds remain `DEMO / NON-SCIENTIFIC`.
- Actor still has no SQL table.

## 11. Open decisions

Whether `UNKNOWN` or `INSUFFICIENT_DATA` should later open a non-critical data-limitation alert is still a product decision. Phase 5 does not create that alert.

## 12. Roadmap impact

Phase 5 is closed by `docs/22-phase5-audit.md`. Phase 6 is not started.
