# 16 — Phase 3 Implementation Audit

## Result

Historical record of the Phase 3.5 audit: **PHASE 3 NEEDS FIXES**.

Phase 3.6 remediation and the re-audit are in `docs/17-phase3.6-remediation.md`. That re-audit concludes **PHASE 3 VERIFIED**. The findings below are kept as the defect list that 3.6 had to close.

The critical alert path is synchronous and LLM-free. Decisions require an Actor and a snapshot. Domain code does not import infrastructure.

The freeze is **not** fully enforced: nested snapshot structures are mutable, SQLAlchemy can update snapshot and published-version rows, and several audit events from the Phase 3 brief are missing.

No product code was changed. Fixes below are `REQUIRES HUMAN REVIEW`.

## Domain purity

**PASS.** `src/baliza/domain/` imports only stdlib and `baliza.domain`.

## Application boundary

**PASS with gaps.** Use cases call ports. They do not import SQLAlchemy. `RecordAction` / `RecordOutcome` / `RuleVersion` activation are domain functions only; they are not application use cases and do not emit audit events.

## Snapshot

`MappingProxyType` blocks replacing the top-level mapping and `with_payload` raises. Nested lists and dicts (`gaps`, `alert_ids`, `recommendations`, `extra`) remain the same objects. `snapshot.payload["gaps"].append(...)` mutates history and does not update `content_hash`.

`SqlDssRepository` has no guard against `UPDATE` of `dss_context_snapshots`.

## Evidence chain (in memory)

Observation id → IndicatorValue.source_observation_ids → RuleEvaluation.input_indicator_value_ids + rule_version → EvidenceItem.referenced_id (primary vs derived) → EvidencePackage.item_ids → Alert.evidence_package_id + rule_evaluation_ids.

SQL: observation ids are JSON, not FKs. `alerts.evidence_package_id` is nullable. No round-trip test of the full chain.

## Rules

Domain `RuleVersion.with_threshold` rejects published mutation. `RuleEvaluation` stores version, thresholds, inputs, outcome, `evaluated_at`. `input_snapshot` dict is still mutable. No DB unique `(rule_id, version)` and no update ban.

## Critical path

`run_critical_path` / `evaluate_rule` do not reference LLM, Agent, AgentRun, or Redis. **PASS.**

## Human-in-the-loop / actions

No path Alert → Decision or AgentRun → Decision/Action. `record_decision` requires Actor, snapshot, justification, `decided_at`. `record_action` requires `decision_id`. **PASS** in domain. Demo HTTP endpoint can record a Decision without auth (explicit demo).

## Audit gaps

Present: observation.recorded, indicator.calculated, alert.created, rule.evaluated (non-trigger), decision.recorded, alert.acknowledged.

Missing: RuleVersion activation, snapshot freeze as its own event, Action, Outcome.

## Temporal

Domain clocks exist. Persisted: observed_at, processed_at, computed_at, evaluated_at, alerted_at, opened_at, frozen_at, decided_at. `reviewed_at` only inside alert history JSON. `acted_at` / `observed_outcome_at` are not in the migration. No domain `created_at` substitute.

## Status

Do not start Phase 4 until snapshot deep-immutability and the SQL update path are reviewed.
