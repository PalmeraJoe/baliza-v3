# 44 — Phase 7.6 spatial association and spot mapping

Protocol only, plus deterministic geometry checks that do not estimate a local value. No interpolation, no downscaling, no model, no new threshold, and no alert. The checks live in `src/baliza/experimental/phase76/` and are not on the critical path.

Associating a source with a spot produces context. It does not produce a local measurement.

## Spot

A spot is the operational place a person asks about. It may later be a point, a station, a polygon, a resort sector, a reef sector, or a management area. It is not assumed to be a point. Whether that object is the same as a Zone remains **OPEN**.

A spot record needs `spot_id`, `geometry`, `geometry_type`, `CRS`, `spatial_precision`, `parent_zone`, `parent_entity`, `valid_from`, and `valid_to`. Geometry types in this protocol are `POINT`, `POLYGON`, `MULTIPOLYGON`, `LINE` / `TRANSECT`, and `UNKNOWN`.

The Phase 0–6 domain has no geometry field and no CRS on Station or Zone. This phase does not add one. Until a spot geometry and a CRS exist, a real association stays `UNKNOWN`.

## CRS

Every association names `source_CRS`, `spot_CRS`, `transformation_method`, and `target_CRS`. Missing CRS or two different CRS values block the coordinate comparison. No datum shift is implemented. Latitude and longitude are not treated as one shared system.

The CRW cell retrieved in Phase 7.5 has no CRS code in the file. The Allen WFS layer declares `urn:ogc:def:crs:EPSG::4326` for the service, while the stored feature JSON has `crs: null` and no geometry. Those are not interchangeable with a resort coordinate.

## Relations

| Type | Meaning | What it does not mean |
|------|---------|------------------------|
| DIRECT | The source is the same place as the spot | A local measurement, or ground truth |
| CONTAINS | The source geometry contains the spot | The source value is the spot's own value |
| INTERSECTS | The geometries overlap, including a point on a shared boundary | A licence to pick one part |
| NEAREST | A nearest feature, only with `distance`, `distance_unit`, and `distance_method` | The default |
| AGGREGATED | An explicit spatial aggregate, with method, source units, and coverage | A silent mean |
| ASSOCIATED | A stated spatial link that is none of the above | A guess |
| UNKNOWN | The relation is not justified | Zero, safety, or `NOT_TRIGGERED` |

`NEAREST` is not used for the NOAA boundary. No nearness distance is approved, so a point that is merely nearby stays `UNKNOWN` with the distance attached. `EXACT` in the point protocol is identity or distance zero in the same CRS. `WITHIN` is a point inside a spot polygon. `NEAR` is not assigned.

## NOAA pixels

Cells use closed footprints. A point on an edge or a corner belongs to every adjacent cell. The result lists `pixel` centers, values when they were actually retrieved, `pixel_count`, and the relation. It does not choose a cell, average, or interpolate. The epistemic class stays `EXTERNAL_INDICATOR`. `spatial_precision` stays `GRID`.

The published heritage coordinate -23.5, 152.0 from NOAA `orig24_names.txt` sits 0.025° from each of the centers -23.475 or -23.525 and 151.975 or 152.025. Only the cell -23.475, 151.975 was retrieved, and only for one day. The other three HotSpot values are **UNKNOWN**. They are not copied from the retrieved cell. Because the grid CRS code is **UNKNOWN**, that point is not given a production association. The four-cell rule is tested on a grid marked `TEST / SYNTHETIC / NON-SCIENTIFIC`. The first reading that uses the published point, without filling the three missing cells, is `docs/45-phase7.6.1-first-real-spot-intelligence.md`. The engine that emits one association per cell, still without a mean, is `docs/46-phase7.6.2-spatial-temporal-association-engine.md`.

A point outside the listed cells is a `SPATIAL GAP` and a `DATA GAP`. It is not zero.

## Polygons, rasters, points, transects

An Allen polygon that contains or intersects a spot is recorded with polygon id, class, intersection area, overlap fraction, and relation, when the geometry and CRS exist. The stored Allen extract has no geometry, so that overlay is not computed here. A benthic class is not a field identification and not a species. Coral/Algae on that map is one map class, not Acropora.

Raster summaries `CELL_VALUE`, `AREA_SUMMARY`, `AREA_FRACTION`, and `CONTEXTUAL_VALUE` are names only. An area summary would be a `DERIVED_INDICATOR` only after a written method. None is authorised. No bilinear sample is computed.

A MERMAID site, a sensor, or a station is `DIRECT` only when it is that spot. A site 150 m away keeps the distance and stays `UNKNOWN` as a membership. Resort files, when they exist, are local records for site calibration and validation, not base-model training and not automatic ground truth. None are in the schema.

A transect keeps its line, endpoints, depth, survey date, and method. Intersection, containment, and the reverse are separate relations. The line is not collapsed to one point. The domain does not store a transect geometry yet.

## Time, precision, uncertainty, conflict

Spatial association does not hide time. Clocks stay `source_time`, `observation_time`, `valid_time`, `processing_time`, `retrieval_time`, and `spot_validity_interval`. A daily product and a spot time that share a UTC date can be `SAME_DAY`. An equal timestamp is `EXACT_TIME`. A monthly composite against one field time is `AGGREGATED_PERIOD`. Anything else, including "close in time", is `UNKNOWN`. No day-count threshold is set.

`spatial_precision` of a 0.05° cell remains `GRID` after association. It does not become `EXACT`.

Uncertainties stay separate: measurement, spatial, temporal, association, and model. A missing uncertainty is `UNKNOWN`. No standard deviation is invented. Model uncertainty stays absent because no local model is authorised.

Two associated sources that disagree are both kept, with a conflict flag. Neither is selected as truth. Coverage outside the product, partial cover, and nodata are gaps, not low values.

Epistemic class is not upgraded by the link. `EXTERNAL_INDICATOR` does not become `DIRECT_OBSERVATION`. `CONTEXT_ONLY` does not become a local measurement. `MODEL_ESTIMATED` does not become observed.

## What a spot reading may show

Geometry, spatial precision, and temporal validity; measured values only when they are actually that place; external NOAA, EMODnet, and Allen context; derived indicators only where a formula already exists; the association and temporal records; quality, freshness, the separate uncertainties, coverage, and gaps. Estimated local values are `NONE`. Alerts and playbook options are unchanged and are not fired by an association.

## Verdict

PHASE 7.6 SPATIAL ASSOCIATION & SPOT MAPPING — LOCAL ESTIMATION / DOWNSCALING / ML NOT AUTHORIZED.
