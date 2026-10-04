# Data source → variable → science

This chain is documentation. It is not a rule and not a weight.

## DHW

SRC-SKIRVING-2020 and SRC-NOAA-METHOD define the accumulation. SRC-HUGHES-2017 links spatial patterns of bleaching to spatial patterns of sea temperature, not to a BALIZA threshold.

Mechanism: accumulated warm-season exceedance of the local maximum monthly mean, on CRW's definition.

Variable: `dhw`.

Source and product: NOAA CRW v3.1 Degree Heating Week, 0.05 degree, daily, °C-weeks, 1985–present.

BALIZA observation: none stored yet. A future join would attach the pixel value to a station as an external observation, with pixel id, version, and time.

Model role: hazard candidate for a later RBM specification. Feature candidate for thermal context. Not a target. Not an alert.

## SST to a future downscaled estimate

Mechanism: surface heat is measured coarsely; local depth and habitat may change the water a colony experiences. No transfer function is adopted.

Variable: `sst` as feature, `downscaled_temperature_estimate` as a future target, `depth_local` or `bathymetry` as context if validated.

Sources: NOAA CoralTemp; Allen satellite depth or EMODnet DTM only inside their footprints; local temperature not yet in the schema.

Model role: XGBoost design only. Output is an estimate.

## Reef mask

Mechanism: mapped shallow-reef presence.

Variable: `reef_extent`.

Source: Allen Coral Atlas v2 reef mask, 5 m, map epoch.

Model role: exposure candidate. Not proof of live coral. Not a bleaching target.

## MERMAID bleaching

MERMAID bleaching categories and calculated colony percents are field observations (`sources/mermaid.md`). They can later be a validation target. They are not a NOAA product, not a BALIZA alert, and not evidence that DHW predicts them. That relationship is unevaluated. No threshold connects the two.

## What is refused

CRW Bleaching Alert Area → BALIZA Alert. Refused.

DHW band → RuleVersion. Refused until a separate, sourced, versioned rule is adopted.

Allen class → coral cover. Refused.

Any chain → automatic action. Refused.
