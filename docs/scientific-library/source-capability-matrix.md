# Source capability matrix

Status values: `AVAILABLE`, `PARTIAL`, `UNKNOWN`, `NOT_AVAILABLE`.

`PARTIAL` means the provider has a related product whose footprint, resolution, or definition does not match the variable as needed for a reef station.

| Variable | NOAA CRW | EMODnet | Allen Coral Atlas | MERMAID | BALIZA local |
|----------|----------|---------|-------------------|---------|--------------|
| SST | AVAILABLE, daily, 0.05°, global, 1985–present, °C | PARTIAL, in situ only, footprint of series unknown | NOT_AVAILABLE | NOT_AVAILABLE | NOT_AVAILABLE |
| SST anomaly | AVAILABLE, daily, 0.05°, °C | NOT_AVAILABLE | NOT_AVAILABLE | NOT_AVAILABLE | NOT_AVAILABLE |
| HotSpot | AVAILABLE, daily, 0.05°, °C | NOT_AVAILABLE | NOT_AVAILABLE | NOT_AVAILABLE | NOT_AVAILABLE |
| DHW | AVAILABLE, daily, 0.05°, °C-weeks | NOT_AVAILABLE | NOT_AVAILABLE | NOT_AVAILABLE | NOT_AVAILABLE |
| MMM climatology | AVAILABLE, static per version, 0.05°, °C | NOT_AVAILABLE | NOT_AVAILABLE | NOT_AVAILABLE | NOT_AVAILABLE |
| 7-day SST trend | AVAILABLE, daily, 0.05° | NOT_AVAILABLE | NOT_AVAILABLE | NOT_AVAILABLE | NOT_AVAILABLE |
| Bleaching Alert Area | AVAILABLE, categorical, not a BALIZA alert | NOT_AVAILABLE | NOT_AVAILABLE | NOT_AVAILABLE | NOT_AVAILABLE |
| Thermal duration, frequency, onset, history | PARTIAL, derivable only after a definition | NOT_AVAILABLE | NOT_AVAILABLE | NOT_AVAILABLE | NOT_AVAILABLE |
| Bathymetry | NOT_AVAILABLE | PARTIAL, 2024 DTM 1/16' on listed European seas | PARTIAL, 10 m satellite depth | NOT_AVAILABLE | NOT_AVAILABLE |
| Local depth | NOT_AVAILABLE | NOT_AVAILABLE | NOT_AVAILABLE | PARTIAL, transect depth (m) on fish, benthic, and habitat forms | NOT_AVAILABLE |
| Slope | NOT_AVAILABLE | PARTIAL, derivative of the DTM | PARTIAL, used in mapping | NOT_AVAILABLE | NOT_AVAILABLE |
| Aspect | NOT_AVAILABLE | UNKNOWN | UNKNOWN | NOT_AVAILABLE | NOT_AVAILABLE |
| Geomorphology | NOT_AVAILABLE | PARTIAL, EUSeaMap | AVAILABLE, 5 m, < 15 m | PARTIAL, site fields reef type, zone, exposure. Not Allen classes | NOT_AVAILABLE |
| Reef extent | NOT_AVAILABLE | NOT_AVAILABLE | AVAILABLE, 5 m mask | NOT_AVAILABLE | NOT_AVAILABLE |
| Benthic habitat | NOT_AVAILABLE | PARTIAL, EUSeaMap | AVAILABLE, 5 m, < 10 m | PARTIAL, PIT, LIT, and photo-quadrat attributes | NOT_AVAILABLE |
| Turbidity | NOT_AVAILABLE | UNKNOWN | AVAILABLE, annual FNU | NOT_AVAILABLE | NOT_AVAILABLE |
| Currents | NOT_AVAILABLE | PARTIAL, in situ catalogue | NOT_AVAILABLE | PARTIAL, optional current field, not a velocity product | NOT_AVAILABLE |
| Waves | NOT_AVAILABLE | PARTIAL, in situ catalogue | PARTIAL, mapping covariate | NOT_AVAILABLE | NOT_AVAILABLE |
| Coral cover | NOT_AVAILABLE | UNKNOWN | NOT_AVAILABLE | PARTIAL, percent cover where a benthic or bleaching sample exists and policy allows it | NOT_AVAILABLE |
| Richness | NOT_AVAILABLE | UNKNOWN | NOT_AVAILABLE | UNKNOWN. Taxa are recorded. A richness metric was not verified | NOT_AVAILABLE |
| Bleaching percent | NOT_AVAILABLE | NOT_AVAILABLE | NOT_AVAILABLE | PARTIAL, colony categories and calculated percents on bleaching samples | NOT_AVAILABLE |
| Mortality percent | NOT_AVAILABLE | NOT_AVAILABLE | NOT_AVAILABLE | PARTIAL, recently dead is a colony category, not a later mortality percent | NOT_AVAILABLE |
| Disease | NOT_AVAILABLE | NOT_AVAILABLE | NOT_AVAILABLE | NOT_AVAILABLE | NOT_AVAILABLE |

A source cell is not a selected model feature.

Quality notes sit in `sources/`. NOAA thermal coverage is global at 5 km. Allen coverage is shallow reef mapped optically. EMODnet European products do not cover the Indo-Pacific. MERMAID coverage is the set of submitted project sites, further limited by each method's data-sharing policy. It is not a continuous layer.
