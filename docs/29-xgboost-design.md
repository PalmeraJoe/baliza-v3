# 29 — XGBoost design

Canonical specification: `docs/scientific-library/xgboost-design.md`.

Working hypothesis: local temperature. Phase 7.2 does not adopt it (`docs/38-phase7.2-scientific-target-and-spot-resolution.md`). The exact target stays OPEN. Downscaling is not authorised. Baseline: the NOAA pixel. A future base set may include NOAA, EMODnet, Allen, and MERMAID. Resort history is site calibration and independent site validation, not default base training. Output: an estimate with uncertainty and provenance, never an observation. Not implemented. Validation rules, including a sealed final holdout, are in `docs/37-phase7.1-ml-validation-protocol.md`. See also `docs/36-phase7-scientific-data-integration.md`.
