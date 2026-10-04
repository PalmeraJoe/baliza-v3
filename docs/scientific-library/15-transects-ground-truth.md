# Transects and ground truth

BALIZA observations today have a variable, a unit, a time, a quality facet, and an optional opaque `spatial_ref`. They do not have Station, Transect, depth, species, cover, or bleaching percent as typed fields.

A future ground-truth campaign would need: station, transect, coordinates, survey time, depth, observer, method, and the biological variables in the registry. Photographs would be evidence objects, not truth.

Those fields are specified in `dataset-specification.md`. They are not tables.

MERMAID is an external field-observation source (`sources/mermaid.md`). Resort and operator archives are a different channel: site calibration and site validation, not automatic truth and not default base-model training. Accepted shapes include CSV, Excel, JSON, GeoJSON, shapefiles, GPX, databases, sensors, reports, manual logs, photographs, and transects. Normalisation is a later ingestion task (`docs/36-phase7-scientific-data-integration.md`).
