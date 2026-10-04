# 26 — Scientific variable registry

Canonical machine registry: `docs/scientific-library/variable-registry.yaml`.

Readable index and the fifteen-question map: `docs/scientific-library/variable-registry.md`.

Roles used: HAZARD, EXPOSURE, VULNERABILITY, CONSEQUENCE, CONTEXT, OBSERVATION, TARGET, OUTCOME, UNCERTAINTY. No variable is marked VULNERABILITY. Mortality is OUTCOME and only a consequence candidate. Bleaching percent is TARGET. Downscaled temperature does not exist yet; it is the only XGBoost target candidate.

Random Forest is `not_authorized` on every variable. Playbook activation is `not_authorized` on every variable.
