# 18 — Phase 4 Implementation (Evidence → Alerts → DSS)

## Status

**PHASE 4 READY FOR AUDIT**

Phase 5 has not been started. AI remains off. This document does not replace the frozen architecture.

Demo numbers in tests and `/demo/critical-path` are labeled **DEMO / NON-SCIENTIFIC**. They are not validated scientific thresholds.

## What was implemented

A synchronous, deterministic path:

```text
Observation → DataQuality → IndicatorValue → RuleEvaluation
  → EvidenceItem → EvidencePackage → Alert → DssPackage
  → DssContextSnapshot → Decision → Action → Outcome
```

Protocols contribute recommendation options only. They do not create Actions.

## Use cases

| Use case | Audit action |
| --- | --- |
| `record_observation` | `observation.recorded` |
| `calculate_indicator` | `indicator.calculated` |
| `activate_rule_version` | `rule_version.activated` |
| `evaluate_and_maybe_alert` | `rule.evaluated`, `evidence.package_created`, `alert.created` when triggered |
| `acknowledge_alert` | `alert.acknowledged` |
| `build_dss_package` | `dss.package_opened` |
| `record_human_decision` | `dss_context_snapshot.frozen`, `decision.recorded` |
| `record_human_action` | `action.recorded` |
| `record_human_outcome` | `outcome.recorded` |

Names stay in the existing dotted form. There is no `SAFE` outcome.

## API

FastAPI routes in `src/baliza/interfaces/api/routes.py` call application use cases. They do not use SQLAlchemy.

The process default is an in-memory `Repositories` (`create_app`). PostgreSQL remains the system of record for a deployed process; this phase does not add a production session factory to the HTTP app.

`POST /demo/critical-path` stays an unauthenticated smoke test. `production_ready` is false. `ai_used` is false.

## Persistence

Alembic `0003_phase4` adds `observations.metadata`, `indicator_versions`, action type/metadata, and indexes on `observed_at` and alert status.

`UnitOfWork` is the transaction port. The critical path commits evaluation, evidence, and alert together. If evidence or alert persistence fails, the unit of work rolls back so a critical alert is not left without its package.

SQLite checks foreign keys per statement. Repositories flush a parent row before a child row. PostgreSQL triggers from Phase 3.6 are unchanged and are not executed by the SQLite tests.

## Evidence chain and DSS

`alert_chain` rebuilds Alert → EvidencePackage → RuleEvaluation → IndicatorValue → Observation from repositories.

A `DssPackage` may hold several alerts. Freeze copies that list into the snapshot payload and hash. A later Outcome does not change the hash.

## Human-in-the-loop

Acknowledge updates alert status only. `Alert.is_decision()` is false. `record_action` rejects a missing decision. Protocol recommendations use epistemic label `RECOMMENDATION` and source `protocol`.

## Data quality

Existing facets remain. Phase 4 adds `suspect`, `insufficient`, and `unknown`. None of them make `implies_no_risk()` true. Missing aggregate members are not treated as zero. Unknown or suspect quality does not become `NOT_TRIGGERED`.

`RuleOutcome` stays `triggered | not_triggered | insufficient_data | invalid_input`. There is no `UNKNOWN` or `SAFE` outcome.

## Rule operators

`gt`, `gte`, `lt`, `lte`, `eq`, and `between`. `between` uses `{threshold_name}` and `{threshold_name}_upper`. Published versions stay immutable.

Indicator formulas used: `passthrough`, `subtract_baseline`, `mean`, `min`, `max`, `sum`, `count`.

## Known limits

- The HTTP app is in-memory unless a caller passes SQL repositories into `create_app`.
- Actor has no IdP and no SQL table. Decision stores `actor_id` and the API requires an Actor already registered.
- Protocol catalog is domain-only. The chosen options are stored on the DSS package payload, not in a protocol table.
- No workers on the critical path.
- SQLite tests do not run PostgreSQL immutability triggers.

## Internal review

| Area | Result | Why |
| --- | --- | --- |
| A. Domain purity | PASS | Domain imports do not include FastAPI, SQLAlchemy, or LLM clients. |
| B. Application boundaries | PASS | Use cases and queries call ports. |
| C. Observation / quality | PASS | Missing and invalid values stay non-numeric and never imply no risk. |
| D. Indicator provenance | PASS | Value stores version, sources, time, quality, and notes. |
| E. Rule determinism | PASS | Same inputs and version produce the same outcome class. No LLM. |
| F. Evidence chain | PASS | Rebuilt from repositories after a new SQL session. |
| G. Alert lifecycle | PASS | Open and acknowledged. Acknowledge is not a Decision. |
| H. DSS lifecycle | PASS | Live package, then freeze at decision. Several alerts can share one package. |
| I. Snapshot integrity | PASS | Deep freeze and insert-only behavior from Phase 3.6 still apply. |
| J. Human-in-the-loop | PASS | No automatic Decision or Action. |
| K. Decision integrity | PASS | Actor, snapshot, justification, and `decided_at` remain mandatory. |
| L. Action safety | PASS | Action requires a Decision id. |
| M. Outcome traceability | PASS | Outcome points at Action and Decision and does not change the snapshot hash. |
| N. Audit completeness | PASS | Lifecycle actions listed above are emitted from use cases. |
| O. Persistence integrity | PARTIAL | Chain tables and indicator versions persist. Protocol rows do not. |
| P. Transaction consistency | PASS | Evidence or alert failure rolls back the critical path when a unit of work is bound. |
| Q. API boundaries | PASS | HTTP maps errors and does not contain rule logic. Default app is not a production database boundary. |
| R. Test quality | PASS | Domain, failure, multi-alert, API, and SQLite end-to-end tests. SQLite is not PostgreSQL. |
| S. Architecture drift | PASS | Modular monolith, ports, human Decision, AI off. No Redis, Kafka, UI product, or workers on the critical path. |
