# 56 — Phase 7.12 end-to-end scientific DSS integration

Demonstrates that BALIZA can run as an auditable DSS on **real public scientific
data** already integrated in Phases 7.8–7.11, without ML, downscaling, local
estimation, IMR, or resort training data.

## What is demonstrated

```text
PUBLIC SCIENTIFIC DATA (CRW + Allen + MERMAID via Spot Intelligence)
        ↓
SPOT INTELLIGENCE
        ↓
EVIDENCE (CRW EXTERNAL_INDICATOR observations)
        ↓
INDICATORS (DEMO passthrough of CoralTemp SST)
        ↓
RULE EVALUATION (DEMO / NON-SCIENTIFIC threshold)
        ↓
ALERT
        ↓
DSS PACKAGE + protocol options (RECOMMENDATION)
        ↓
FROZEN DssContextSnapshot
        ↓
HUMAN DECISION
        ↓
ACTION
        ↓
OUTCOME
```

Entry point: `baliza.application.phase712_scientific_dss.run_e2e_scientific_dss`.

Spot: `DEMO-CRW-ORIG24-HERITAGE-POINT` at `-23.5, 152.0` (unchanged).

## Real public data used

| Source | Role in E2E |
|--------|-------------|
| NOAA CRW | Six stored products ingested as `EXTERNAL_INDICATOR` observations |
| Allen Coral Atlas | CONTEXT_ONLY gap (not attached to DEMO Spot) |
| MERMAID | DATA EXISTS BUT NO COMPATIBLE MATCH (explicit data gap) |

CRW values are **not** presented as `LOCAL_MEASURED_TEMPERATURE`. Production
spatial association remains UNKNOWN.

## DEMO / NON-SCIENTIFIC parts

| Item | Status |
|------|--------|
| Indicator `demo_crw_coraltemp_passthrough` | `DEMO_ONLY=true` |
| Rule `demo_crw_external_sst_watch` | `DEMO_ONLY=true` |
| Threshold `demo_sst_watch = 20.0` | `SCIENTIFICALLY_VALIDATED=false` |
| Protocol options | Catalog RECOMMENDATIONs; no auto-execution |

These exist only to exercise the DSS critical path. They are **not** BALIZA
scientific bleaching thresholds.

A second DEMO path evaluates CRW DHW against `demo_dhw_watch=4.0` and yields
`NOT_TRIGGERED` (distinct from `UNKNOWN`).

## What remains PARTIAL / NOT_AVAILABLE / NOT_AUTHORIZED

| Item | Status |
|------|--------|
| CRW production spatial association | PARTIAL / UNKNOWN |
| Allen Spot coverage | PARTIAL / NOT_AVAILABLE for DEMO |
| MERMAID compatible field observation | NOT_AVAILABLE for DEMO |
| Thermal ground truth | NOT_AVAILABLE |
| Local estimation | NOT_AUTHORIZED |
| Downscaling | NOT_AUTHORIZED |
| ML implementation | NOT_AUTHORIZED |
| IMR dependency | NONE |

## How to reproduce

```bash
# from repository root
set PYTHONPATH=src
py -3 -m pytest tests/test_phase712_e2e_scientific_dss.py -q
```

Artifacts written by the main E2E test:

- `data/phase712/e2e-brief.txt`
- `data/phase712/e2e-summary.json`

## Evidence chain verification

Audit events expected on the happy path:

```text
observation.recorded
indicator.calculated
rule.evaluated
evidence.package_created
alert.created
dss.package_opened
recommendation.presented
dss_context_snapshot.frozen
decision.recorded
action.recorded
outcome.recorded
```

Snapshot payload includes Spot Intelligence contract version, DEMO threshold
labels, thermal-ground-truth / ML / downscaling flags, and CRW-not-local flag.

## Human decision boundary

Verified by tests:

- `Alert.is_decision() is False`
- `ACKNOWLEDGED ≠ DECISION` (existing Phase 6 behaviour retained)
- `AgentRun.is_decision() is False`; Decision requires Actor
- Action requires Decision (`ActionWithoutDecision` without it)
- Recommendation cannot create Action without Decision
- Decision requires Actor + Snapshot + non-empty justification
- Snapshot hash stable after post-freeze mutation of live package gaps

## API (reused; no parallel surface)

```text
GET /scientific/spots/{spot_id}/intelligence
GET /alerts/{id}/context
GET /dss/packages/{id}/brief
GET /dss/packages/{id}/evidence
GET /dss/packages/{id}/options
GET /dss/packages/{id}/snapshots
```

## What this phase does **not** claim

BALIZA does **not** yet predict local bleaching. It **does** integrate public
evidence, evaluate a deterministic DEMO rule, open a DSS package, freeze
context, and record a human decision → action → outcome with explicit
uncertainty and data gaps.

## Next logical milestone

**Pilot Readiness Review**, then scientific pilot with IMR (out of scope here).

```text
PHASE 7.12 END-TO-END SCIENTIFIC DSS INTEGRATION
ESTIMATED = NONE
DOWNSCALING = NOT_AUTHORIZED
ML_IMPLEMENTATION = NOT_AUTHORIZED
LOCAL_ESTIMATION = NOT_AUTHORIZED
IMR_DEPENDENCY = NONE
```
