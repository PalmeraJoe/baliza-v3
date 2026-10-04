# Thermal downscaling — design only

No model is trained. No library is added. The output, if a later phase builds it, is a `DownscaledTemperatureEstimate`: an estimate with uncertainty and model provenance. It is not a measured temperature and not a bleaching observation.

## Target

The exact target remains **OPEN** (`docs/36-phase7-scientific-data-integration.md`, `docs/38-phase7.2-scientific-target-and-spot-resolution.md`). The working hypothesis is local water temperature at a station and depth, at `observation_time`, from a local sensor or survey. Phase 7.2 does not authorise that hypothesis. No local series is in the system of record. That label is not in the schema. NOAA SST is a coarse input, not that label, and not the same quantity as an in-situ temperature or as this estimate. Using NOAA SST as both feature and target would not be downscaling. A future base set may use NOAA, EMODnet, Allen, and MERMAID where each value is allowed and versioned. Resort histories are not in that base set by default. Their first role is site calibration, then an independent site validation. Calibration method, weights, and correction factors are undefined.

## Features allowed to be discussed

From the registry, as candidates only: CoralTemp SST and its anomaly, HotSpot, DHW, MMM, Allen or EMODnet depth where the footprint exists, slope, geomorphic class, benthic class, turbidity. Each feature needs the clocks in `spatial-temporal-model.md`.

Biological cover and bleaching percent are not features of a temperature model.

## Baseline

The baseline is the NOAA 0.05° pixel value sampled at the station, with no statistical model. A later model must beat that baseline on held-out local temperatures. The metric and the holdout are not chosen here, because no local series exists to justify a number.

## Training and validation

The protocol is `docs/37-phase7.1-ml-validation-protocol.md`. Development data and a sealed final holdout are separate. The initial ratio is 80/20 and the split is not random. Spatial groups and forward time splits are required. The grouping unit is not chosen until the real hierarchy is written. Hyperparameters and learned preprocessing stay inside development data. Resort rows are not in the base training set.

Missing features stay missing. No imputed scientific value. The model version, feature list, training period, and code hash would be provenance on the estimate.

## Uncertainty and fallback

The estimate carries a stated uncertainty method. Until that method exists, the uncertainty is `UNKNOWN` and the fallback is the NOAA pixel labeled as 5 km surface temperature, not as local truth.

## Explainability

A later model may report which features it used. That report is not evidence strength and not a cause.

## What this design refuses

A temperature estimate does not create an alert, a decision, or an action. It does not bypass a future RBM constraint.
