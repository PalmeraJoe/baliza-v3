# 58 — Phase 7.14 BALIZA Visual MVP

Visual presentation of the existing scientific DSS. No new science, ML, IMR
connector, or commercial features.

## Scope

React + TypeScript + Vite frontend under `frontend/` that consumes the BALIZA
API. Backend remains the source of truth.

Happy path:

```text
Overview → DEMO Spot → Indicators / Evidence / Gaps
        → Alert (DEMO rule) → DSS options
        → Human Decision → Action → Outcome
```

## Screens

| Route | Purpose |
|-------|---------|
| `/` | Overview, metrics, map, bootstrap DEMO session |
| `/spots` | Spot list |
| `/spots/:id` | Spot Intelligence detail |
| `/alerts`, `/alerts/:id` | Alerts + deterministic “why” |
| `/dss`, `/dss/:id` | DSS brief, options, decision form |
| `/decisions`, `/decisions/:id` | Decision, Action, Outcome |

## APIs used

```text
GET  /scientific/spots
GET  /scientific/spots/{id}/intelligence
POST /scientific/mvp/bootstrap
GET  /scientific/mvp/session
GET  /alerts
GET  /alerts/{id}
GET  /alerts/{id}/context
GET  /dss/packages
GET  /dss/packages/{id}/brief|evidence|options|snapshots
POST /decisions
GET  /decisions
GET  /decisions/{id}
POST /actions
GET  /actions/{id}
POST /outcomes
GET  /outcomes/{id}
```

Bootstrap runs Phase 7.12 through DSS only (`through="dss"`), so the human
records the Decision in the UI.

## Real vs DEMO

| Layer | Status |
|-------|--------|
| CRW / Allen / MERMAID Spot Intelligence | REAL scientific data (with known gaps) |
| `demo_sst_watch` rule / threshold | DEMO / NON-SCIENTIFIC · not scientifically validated |
| Decision / Action / Outcome | Human-recorded via existing domain APIs |

## Visible scientific limits

- CRW = EXTERNAL INDICATOR (not local measured temperature)
- Allen = CONTEXT ONLY; DEMO coverage may be NOT_AVAILABLE
- MERMAID no-match ≠ no bleaching / healthy
- Thermal ground truth = NOT_AVAILABLE
- Local estimation / downscaling / ML = NOT_AUTHORIZED
- AI analysis panel = “Not enabled in MVP”

## Run

```text
# API (repo root)
$env:PYTHONPATH = "src"
py -3 -m uvicorn baliza.interfaces.api.app:app --reload --port 8000

# UI
cd frontend
npm install
npm run dev
```

UI proxies `/api` → `http://127.0.0.1:8000`.

```text
cd frontend
npm test
```

Backend:

```text
py -3 -m pytest -q
```

## Not implemented

Billing, users, orgs, IMR, ML, notifications, automated actions, commercial
packaging, invented reef polygons, risk scores.

## Acceptance

A non-developer can open BALIZA and follow public data → Spot Intelligence →
evidence → alert → DSS → options → human decision without the UI inventing
science or hiding gaps.
