# Future dataset

Not a database table. Unit of a future thermal or bleaching table: **station × time**.

Resort and operator histories are a first-class future channel for **site calibration and site validation**, not the default training set of a base scientific model (`docs/36-phase7-scientific-data-integration.md`). They are not automatically true. They pass a later ingestion, validation, normalisation, quality, alignment, and provenance path. The provider does not have to pre-format files. A dataset version used for training, calibration, validation, testing, evaluation, or a scientific analysis is not edited in place. Rows used to calibrate a model are not later presented as an independent validation of that same model.

Each future value carries an epistemic class: `OBSERVED`, `DERIVED`, `INTERPOLATED`, `AGGREGATED`, `MODEL_ESTIMATED`, or `DOWNSCALED`. An estimate is never stored as an observation.

Permission to store resort data is not permission to train. Training permission, owner, licence, retention, and sharing are separate and are not collected in this phase.

A resort with no history still uses external sources. The gap stays visible. It is not zero risk and it is not extra precision.

A future model split is not a random 80/20 of rows. Development data and a sealed final holdout, spatial groups, and forward time splits are specified in `docs/37-phase7.1-ml-validation-protocol.md`. The grouping unit is still open. Learned preprocessing is fit on train only. No candidate in `docs/38-phase7.2-scientific-target-and-spot-resolution.md` is an authorised downscaling label. A spot reading may attach external products and measurements; it may not copy a grid value onto the spot (`docs/39-phase7.3-spot-intelligence-evidence-state-model.md`). Resort rows stay out of the base set. The estimate column is empty. A deterministic baseline may count direct observations and list missing inputs; it may not write a grid value into a local column (`docs/40-phase7.4-spot-scientific-baseline.md`). A retrieved CRW cell stays a grid cell (`docs/41-phase7.5-real-scientific-data-acquisition.md`).

Columns below are names from the variable registry. A column marked absent cannot be filled with a placeholder.

| Column | Kind | Status |
|--------|------|--------|
| station_id, latitude, longitude | identity | Not in the schema |
| timestamp | `survey_time` or grid day, declared per row | Required distinction |
| depth | local context | Absent |
| noaa_sst, noaa_sst_anomaly, noaa_hotspot, noaa_dhw | external predictors or context | Obtainable, not ingested |
| thermal_history | context | Undefined |
| bathymetry, slope, aspect | context | Partial and footprint-limited |
| geomorphology, habitat, turbidity | context | Allen epoch, not a time series |
| coral_cover, species_richness, functional_groups | observation or context | Absent |
| historical_bleaching | context | Must end before forecast origin |
| observed_bleaching | TARGET | Absent. Forbidden as a predictor of bleaching |
| mortality | OUTCOME | Absent. Forbidden as a predictor of mortality |
| disease, recovery | observation or outcome | Absent. Role not chosen |
| data_quality, uncertainty, source_provenance | required metadata | Quality exists for generic observations; these columns do not |

## Leakage

| Kind | Rule |
|------|------|
| Temporal | Features must be available at the forecast origin. DHW's 84-day window and annual turbidity must not include days after that origin if the claim is a forecast. |
| Post-event / future information | A variable for a condition at time `t` cannot include information that existed only after `t`. |
| Repeated station or transect | The same station or transect in both calibration and the reported validation is not an independent test. |
| Spatial | Do not train and report skill on random pixels from the same reef without a spatial block. Nearby pixels share water. |
| Station | Holding out random days from a station that remains in training leaks that station's identity. |
| Survey | A campaign's own cover or photos cannot explain that campaign's bleaching score. |
| Target | `observed_bleaching` is not a feature of a bleaching model. |
| Duplicates | The same NOAA day joined to many replicates of one survey must be one feature row or an explicit replicate weight. It must not be treated as independent days. |

Predictor, context, target, and outcome are the `scientific_role` values in the registry. A column does not change role because it improves a score.
