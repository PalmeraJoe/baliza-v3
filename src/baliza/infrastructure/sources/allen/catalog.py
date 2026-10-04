"""Allen Coral Atlas catalog from verified WFS access only.

Bathymetry, turbidity, and reef mask are not on the verified WFS layers.
"""

from __future__ import annotations

SOURCE = "ALLEN_CORAL_ATLAS"
SOURCE_LABEL = "Allen Coral Atlas"
ENDPOINT = "https://allencoralatlas.org/geoserver/ows"
WFS_VERSION = "2.0.0"
PARSER_VERSION = "phase79-allen-1"
NORMALIZATION_VERSION = "phase79-normalize-1"
SERVICE_DEFAULT_CRS = "urn:ogc:def:crs:EPSG::4326"
ATTRIBUTION = (
    "Allen Coral Atlas (2022). Imagery, maps and monitoring of the world's tropical coral reefs. "
    "https://doi.org/10.5281/zenodo.3833242"
)
LICENSE = (
    "FAQ: maps, bathymetry and map statistics © 2018-2023 Allen Coral Atlas Partnership "
    "and Arizona State University, CC BY 4.0. Website Terms of Use prohibit robot retrieval "
    "of the Site. Global habitat-map reproduction may need written consent."
)

AVAILABLE_LAYERS: dict[str, dict[str, str]] = {
    "coral-atlas:benthic_data_verbose": {
        "product": "benthic_data_verbose",
        "layer": "benthic",
        "file": "benthic_bbox.json",
        "scientific_role": "mapped_benthic_classification",
        "epistemic": "CONTEXT_ONLY",
        "transformation_type": "MODEL_ESTIMATED",
        "transformation_origin": "PROVIDER",
        "note": "Provider map classification. Not a BALIZA estimate and not a field observation.",
    },
    "coral-atlas:geomorphic_data_verbose": {
        "product": "geomorphic_data_verbose",
        "layer": "geomorphic",
        "file": "geomorphic_bbox.json",
        "scientific_role": "mapped_geomorphic_zone",
        "epistemic": "CONTEXT_ONLY",
        "transformation_type": "MODEL_ESTIMATED",
        "transformation_origin": "PROVIDER",
        "note": "Provider map classification. Not a field observation.",
    },
}

NOT_AVAILABLE_PRODUCTS: dict[str, dict[str, str]] = {
    "reef_mask": {
        "status": "NOT_AVAILABLE",
        "reason": "Not present on the verified WFS layers used by BALIZA.",
    },
    "satellite_derived_depth": {
        "status": "NOT_AVAILABLE",
        "reason": "Bathymetry is download-only on the portal; not on the verified WFS.",
    },
    "turbidity": {
        "status": "NOT_AVAILABLE",
        "reason": "Turbidity is not on the verified WFS layers.",
    },
}

REQUEST_BBOX = {
    "min_lat": -23.48,
    "min_lon": 151.97,
    "max_lat": -23.47,
    "max_lon": 151.98,
    "crs": SERVICE_DEFAULT_CRS,
    "bbox_param": "-23.48,151.97,-23.47,151.98",
}

DEMO_SPOT_ID = "DEMO-CRW-ORIG24-HERITAGE-POINT"
DEMO_SPOT = {
    "spot_id": DEMO_SPOT_ID,
    "label": "DEMONSTRATION / RESEARCH TEST SPOT",
    "geometry_type": "POINT",
    "latitude": -23.5,
    "longitude": 152.0,
    "crs": "UNKNOWN",
    "spatial_precision": "UNKNOWN",
}

# Technical test only. Inside the stored WFS bbox. Not a validation of the DEMO Spot.
ALLEN_RESEARCH_TEST_SPOT = {
    "spot_id": "ALLEN-RESEARCH-TEST-SPOT",
    "label": "ALLEN RESEARCH TEST SPOT / NON-SCIENTIFIC DEMO",
    "geometry_type": "POINT",
    "latitude": -23.475,
    "longitude": 151.975,
    "crs": "UNKNOWN",
    "spatial_precision": "UNKNOWN",
    "note": "Placed inside the stored Allen WFS request bbox for pipeline tests. Not the DEMO Spot.",
}
