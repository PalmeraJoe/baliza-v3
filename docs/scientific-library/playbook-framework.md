# Playbook — specification

A playbook entry is an option catalog, the same idea as a Protocol: it does not run.

```text
RBM state
  → entry conditions
  → allowed options
  → preconditions
  → monitoring requirements
  → exit conditions
  → outcome (recorded after a human decision and an action)
```

Names reserved as concepts, without entry conditions:

| Concept | Means | Does not mean |
|---------|--------|----------------|
| MONITOR | Keep observing | Start a sensor by itself |
| VERIFY | Check the signal in the field | Declare the signal true |
| INTENSIVE SURVEY | A possible extra survey | A required survey |
| MITIGATION OPTION | A possible human response | An authorised or automatic mitigation |

No entry condition is defined. Defining one would be a threshold or a policy, and neither is adopted in Phase 7.

Options shown to a person stay `RECOMMENDATION`. The outcome of a later action does not rewrite the snapshot or the RBM state that was shown.
