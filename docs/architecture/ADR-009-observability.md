# ADR-009 — Observability

## Status

**ACCEPTED**

## Context

Must investigate “why this alert?” and “why no alert?” Distinguish business audit from technical telemetry.

## Decision

| Layer | Tooling / artifact |
|-------|---------------------|
| **Business audit** | `AuditEvent` table + domain records (RuleEvaluation, Decision, AgentRun) |
| **Logs** | Structured **JSON** logs (correlation ids: request_id, alert_id, agent_run_id, rule_evaluation_id) |
| **Traces** | **OpenTelemetry** spans across API and workers |
| **Metrics** | OTel metrics / Prometheus: ingest lag, eval counts (triggered/not), job failures, LLM latency/errors, alert lifecycle counts |
| **Rule “why not”** | Persist RuleEvaluation with outcome `not_triggered` (+ reason codes where applicable) for pilot |
| **Agent** | AgentRun record + optional trace object; never substitute for AuditEvent of decisions |

### Questions

- **Why alert?** → Alert → EvidencePackage → RuleEvaluation(s) → IndicatorValues → Observations (+ versions).
- **Why no alert?** → RuleEvaluations not_triggered / quality gates / INSUFFICIENT_DATA health — not absence of logs alone.

## Reason

- Separates compliance-grade audit from ops debugging.
- OTel is vendor-neutral.

## Trade-offs

- Volume of not_triggered evaluations — may sample in production later; full for pilot recommended.
- Collector optional in smallest dev setup; required before serious pilot.

## Migration / exit

- Change APM backend (Jaeger/Grafana/etc.) without domain changes.

## References

- [13-technical-risks.md](../13-technical-risks.md) R-M4
- ADR-005
