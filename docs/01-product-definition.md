# 01 — Product Definition

## Problem

Managers of marine and coastal ecosystems (including resorts adjacent to sensitive habitats and marine protected areas) face decisions under:

- **heterogeneous data** (sensors, observations, remote sensing, reports);
- **uneven quality and coverage**;
- **scientific uncertainty**;
- **time pressure** when conditions change;
- **need for auditability** (what was known, when, and why a decision was made).

Without a structured system, alerts may be informal, evidence incomplete, thresholds opaque, and decisions poorly documented.

**BALIZA V3** addresses this by providing a Decision Support System that:

1. structures data into indicators;
2. evaluates deterministic, versioned rules;
3. attaches evidence and uncertainty;
4. produces traceable alerts;
5. presents options of action (protocols) to a human responsible party;
6. records decisions, actions, and outcomes for learning and audit.

BALIZA does **not** decide or act autonomously.

---

## Users (initial categories)

Names and permission models are **not** finalized. Categories below are working labels.

| Category | Primary need | Notes |
|----------|--------------|-------|
| **Resort / site manager** | Timely situational awareness and clear action options for guest/operations impact | May not be a domain scientist |
| **MPA / coastal manager** | Conservation-oriented monitoring, alerts, protocol options | Regulatory context `TBD` |
| **Scientist / domain expert** | Validate indicators, rules, thresholds, evidence quality | May propose rule versions; approval authority `TBD` |
| **Operator** | Day-to-day monitoring, acknowledge alerts, gather observations | Limited decision authority `TBD` |
| **Administrator** | Configure entities, users, integrations, non-scientific settings | Must not silently change scientific thresholds |
| **Auditor / compliance reviewer** | Reconstruct Evidence Chain for past alerts and decisions | Read-focused |

Additional roles (e.g., regulator, guest-facing communicator) are `TBD` and out of scope until justified.

---

## Primary use cases

Justified by the product problem. Implementation details are out of scope.

### UC-01 — Monitor a zone

A user reviews the current state of a defined spatial entity (zone/site/area) over a time window: indicators, recent observations, open alerts, data quality summary.

### UC-02 — Detect change

The system (via rules and/or analysis) identifies a condition that may warrant attention relative to baselines, thresholds, or prior state. Detection produces candidates for evidence and alerts; it does not execute actions.

### UC-03 — Receive an alert

A responsible user is notified of a new or updated alert with severity, location, time, and links to supporting evidence. Notification channels are `TBD`.

### UC-04 — Investigate an alert

The user opens the alert and inspects associated variables, indicators, rule firings, agent analyses (if any), quality flags, and history.

### UC-05 — Review evidence

The user examines the Evidence Chain: sources, transformations, confidence, gaps, and conflicting signals. Facts and inferences are visually/ structurally separated.

### UC-06 — Consult action options

The DSS presents protocol-linked options appropriate to the alert/state, plus considerations and missing information. Options are suggestions for human consideration, not commands.

### UC-07 — Make a decision

A authorized human records a decision: selected option (or custom action), justification, timestamp, and identity. The system does not auto-select.

### UC-08 — Register the action

The decided action (or “no action”) is recorded with status and relevant operational metadata. Execution outside BALIZA may occur; linkage is `TBD`.

### UC-09 — Evaluate the outcome

After a period or new observations, outcomes are linked back to the decision and original alert, enriching evidence for future review.

---

## Non-goals (product)

- Autonomous operational control of physical systems.
- Guaranteed prediction of future ecological outcomes.
- Replacement of scientific judgment or regulatory process.
- Unvalidated “AI-only” alerting for critical thresholds.

---

## Success criteria (conceptual)

A successful BALIZA deployment would allow a manager to:

1. see what is happening in a zone with provenance;
2. understand why an alert exists;
3. see uncertainty and gaps;
4. choose among documented options;
5. leave an auditable record of decision and outcome.

Quantitative KPIs (time-to-acknowledge, false alert rates, etc.) are `TBD`.

---

## Open Questions

1. Priority vertical for first pilot: resort coastal zone vs MPA vs both? `TBD`
2. Minimum viable indicator set for pilot? `TBD` (requires scientific input)
3. Must decisions always reference a protocol option, or can free-form decisions be first-class? `TBD` (lean: allow both, with mandatory justification)
4. Multi-organization tenancy needed in v1? `TBD`
5. Legal identity / e-signature requirements for decisions? `TBD`
6. Public vs internal-only visibility of alerts? `TBD`

---

## Related documents

- [00-foundation.md](./00-foundation.md)
- [03-dss-principles.md](./03-dss-principles.md)
- [roadmap.md](./roadmap.md)
