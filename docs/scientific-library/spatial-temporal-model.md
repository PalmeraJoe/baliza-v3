# Spatial and temporal model

Conceptual only. No join has been implemented.

Sources are not one homogeneous base. External scientific sources are NOAA CRW, EMODnet, Allen Coral Atlas, and MERMAID. Resort history is a separate site channel. A later alignment layer is the Reef Data Fabric in `docs/36-phase7-scientific-data-integration.md`. The key is where, when, what, source, resolution, method, quality, and provenance. A shared reef and date do not make NOAA SST, a local temperature, and a model estimate the same observation. A regional cell is not a local observation. Resampling, interpolation, aggregation, spatial matching, and downscaling, if ever done, are provenance, not silent replacement.

Ingestion time does not replace observation time. Also keep the start and end of the value's window, acquisition date, publication date, and ingestion date.

## Places

The glossary already separates Entity, Zone, and Station. Phase 7 adds Transect as a survey line inside a Station, and keeps Observation as the recorded measurement.

```text
Resort      — an Entity: the managed place
Zone        — management or ecological unit
Spot        — the operational place a manager asks about; not an ML cluster
Station     — a named place with coordinates
Transect    — a survey geometry at a station, on a date
Observation — one recorded value, with its own time
Reef area   — ecological extent, not a Zone
```

`Spot` is defined in `docs/38-phase7.2-scientific-target-and-spot-resolution.md`. Whether it is the same object as a Zone is OPEN. It is not a NOAA pixel. Evidence attached to a spot keeps its scale (`GLOBAL` through `TRANSECT`) and a spatial relation (`DIRECT`, `CONTAINS`, `INTERSECTS`, `NEAREST`, `AGGREGATED`, `ASSOCIATED`, or `UNKNOWN`). Until a join rule is written, the relation is `UNKNOWN` (`docs/39-phase7.3-spot-intelligence-evidence-state-model.md`). Permitted relations per source, and the ban on treating a cell as the spot, are in `docs/40-phase7.4-spot-scientific-baseline.md`. One retrieved cell sits 0.025° from a published heritage station coordinate that is equally close to four centers, so that point has no unique cell (`docs/41-phase7.5-real-scientific-data-acquisition.md`). The association protocol does not pick one cell and does not compare coordinates when the CRS is unknown (`docs/44-phase7.6-spatial-association-spot-mapping.md`).

A NOAA pixel, an EMODnet cell, and an Allen pixel are external grids. They are not Stations. A CRW Regional Virtual Station is not a BALIZA Station.

## Joins that a later pipeline would have to declare

- Point-in-pixel from station coordinates to the NOAA 0.05° grid. Pixel center convention is documented. CRS code is `UNKNOWN` until the NetCDF is read.
- Point-in-polygon or point sample on Allen 5 m classes. The class is map context, not a new observation of cover.
- Overlay on EMODnet only after the station is inside the product footprint. Otherwise the join result is `NOT_AVAILABLE`, not a filled value.
- Transect to station: many observations, one campaign time.

Resolution mismatch is a first-class gap. A 5 km SST value does not describe a 10 m transect. Sampling the pixel is allowed only as an external observation with that footprint stored. Interpolation onto the transect is not authorised; the risk is invented sub-pixel temperature.

Raster and vector stay in object storage or a later GIS store. This phase does not add a geometry column.

## Clocks

| Clock | Meaning |
|-------|---------|
| `observation_time` | When the local measurement was made |
| `acquisition_time` | When the satellite scene was taken |
| `processing_time` | When the provider or BALIZA produced the grid value |
| `valid_from`, `valid_to` | Interval a map or climatology version applies |
| `survey_time` | When a transect campaign was in the water |

NOAA daily values are UTC days, often published one day later. Allen habitat is an epoch (2018–2020), not a survey day. A weekly feature built from daily SST must list the days included. A monthly feature must not be labeled as the survey-day temperature.

Do not align a survey to "the same week" without writing the rule. An unstated nearest-neighbour in time is a leakage risk.

A future evaluation must hold out whole spatial groups and later time periods (`docs/37-phase7.1-ml-validation-protocol.md`). Nearby stations are not independent test points merely because their identifiers differ. The grouping unit is chosen only after the real hierarchy is written.
