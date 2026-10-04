"""EXPERIMENTAL / PHASE 7.6.1. One demonstration spot from files already stored.

Does not download, estimate, or alert.
"""

from __future__ import annotations

import json
from pathlib import Path

from baliza.experimental.phase75.crw_csv import PRODUCTS, parse_crw_griddap_csv

SPOT_ID = "DEMO-CRW-ORIG24-HERITAGE-POINT"
# Published in NOAA orig24_names.txt. Not a surveyed resort coordinate.
PUBLISHED_LAT = -23.5
PUBLISHED_LON = 152.0
# Centers 0.025 degrees from that point. Only one of them was retrieved.
CANDIDATE_CENTERS = (
    (-23.475, 151.975),
    (-23.475, 152.025),
    (-23.525, 151.975),
    (-23.525, 152.025),
)
RETRIEVED_CENTER = (-23.475, 151.975)
ALLEN_BBOX = (-23.48, 151.97, -23.47, 151.98)  # min_lat, min_lon, max_lat, max_lon

DATASETS = (
    "noaacrwsstDaily",
    "noaacrwsstanomalyDaily",
    "noaacrwsstanomalybaselineDaily",
    "noaacrwhotspotDaily",
    "noaacrwdhwDaily",
    "noaacrwbaa7dDaily",
)


def _allen_bbox_contains_published_point() -> bool:
    min_lat, min_lon, max_lat, max_lon = ALLEN_BBOX
    return min_lat <= PUBLISHED_LAT <= max_lat and min_lon <= PUBLISHED_LON <= max_lon


def build_spot_record(raw_dir: Path, provenance_path: Path) -> dict:
    provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
    checksums = {item["name"]: item["sha256"] for item in provenance["files"]}
    indicators = []
    for dataset_id in DATASETS:
        filename = f"{dataset_id}_2026-09-26.csv"
        text = (raw_dir / filename).read_text(encoding="utf-8")
        record = parse_crw_griddap_csv(text, dataset_id)[0]
        if (float(record.where_latitude), float(record.where_longitude)) != RETRIEVED_CENTER:
            raise ValueError("Retrieved row is not the stored cell.")
        indicators.append(
            {
                "statement_kind": "FACT",
                "scientific_layer": "EXTERNAL_INDICATOR",
                "source": record.source,
                "product": record.what,
                "dataset": dataset_id,
                "value": record.value,
                "unit": record.original_unit,
                "source_resolution": "0.05 degree grid as documented; file attribute is a binary 0.05",
                "source_crs": "UNKNOWN",
                "valid_time": record.when,
                "source_time": record.when,
                "observation_time": None,
                "retrieval_time": provenance["retrieval_calendar_date"],
                "temporal_relation": "UNKNOWN",
                "association_type": "UNKNOWN",
                "association_method": "Not compared. Spot CRS and grid CRS are both UNKNOWN.",
                "source_precision": "GRID",
                "applies_to": "retrieved cell only",
                "cell_latitude": record.where_latitude,
                "cell_longitude": record.where_longitude,
                "source_quality": record.source_provided_quality,
                "baliza_quality": record.baliza_quality,
                "quality_basis": "BALIZA_DERIVED" if record.baliza_quality == "QUESTIONABLE" else "UNKNOWN",
                "raw_file": filename,
                "sha256": checksums[filename],
                "source_version": PRODUCTS[dataset_id]["version"],
                "transformation": record.transformation_type,
            }
        )
    anomaly_values = [
        item["value"] for item in indicators if item["product"].startswith("crw_sst_anomaly")
    ]
    pixels = []
    for lat, lon in CANDIDATE_CENTERS:
        pixels.append(
            {
                "latitude": lat,
                "longitude": lon,
                "retrieved": (lat, lon) == RETRIEVED_CENTER,
                "values": "see external_indicators" if (lat, lon) == RETRIEVED_CENTER else "UNKNOWN",
            }
        )
    return {
        "label": "DEMONSTRATION / RESEARCH TEST SPOT",
        "spot_id": SPOT_ID,
        "geometry": {"type": "POINT", "latitude": PUBLISHED_LAT, "longitude": PUBLISHED_LON},
        "geometry_type": "POINT",
        "crs": "UNKNOWN",
        "spatial_precision": "UNKNOWN",
        "valid_from": "UNKNOWN",
        "valid_to": "UNKNOWN",
        "temporal_validity": "UNKNOWN",
        "coordinate_note": (
            "Latitude -23.5 and longitude 152.0 are the heritage 50 km station "
            "coordinates NOAA published in orig24_names.txt. This is not a BALIZA resort."
        ),
        "measured": [],
        "external_indicators": indicators,
        "derived_indicators": [],
        "estimated": [],
        "downscaling": "NOT AUTHORIZED",
        "spatial_associations": [
            {
                "source": "NOAA Coral Reef Watch",
                "statement_kind": "INFERENCE",
                "association_type": "UNKNOWN",
                "pixel_count_if_axes_match": 4,
                "confirmed_intersection": False,
                "pixels": pixels,
                "reason": (
                    "The published point is 0.025 degrees from four documented cell centers. "
                    "The grid CRS is UNKNOWN, so those centers are not confirmed as intersections. "
                    "Values exist for one retrieved cell only. The other three were not retrieved."
                ),
            }
        ],
        "temporal_associations": [
            {
                "source": "NOAA Coral Reef Watch",
                "source_time": "2026-09-26T12:00:00Z",
                "spot_time": "UNKNOWN",
                "relation": "UNKNOWN",
            }
        ],
        "quality": [
            {
                "product": item["product"],
                "source_quality": item["source_quality"],
                "baliza_quality": item["baliza_quality"],
                "quality_basis": item["quality_basis"],
            }
            for item in indicators
        ],
        "freshness": {
            "data_timestamp": "2026-09-26T12:00:00Z",
            "retrieval_timestamp": provenance["retrieval_calendar_date"],
            "age": "UNKNOWN",
            "freshness_status": "UNKNOWN",
            "note": "No freshness cutoff is approved. The retrieval clock has no sub-second time.",
        },
        "uncertainty": {
            "measurement_uncertainty": "UNKNOWN",
            "spatial_uncertainty": "UNKNOWN",
            "temporal_uncertainty": "UNKNOWN",
            "association_uncertainty": "UNKNOWN",
            "model_uncertainty": "UNKNOWN",
        },
        "data_gaps": [
            {"kind": "GROUND TRUTH GAP", "detail": "No in-situ measurement at this point."},
            {"kind": "DATA GAP", "detail": "Three of the four candidate NOAA cells were not retrieved."},
            {"kind": "SPATIAL GAP", "detail": "Allen WFS bbox does not contain this point. Classes are not attached."},
            {"kind": "SOURCE GAP", "detail": "EMODnet depth was not retrieved. The European DTM does not cover this cell."},
            {"kind": "LICENSE / ACCESS GAP", "detail": "MERMAID sites were not authorized. No survey row is stored."},
            {"kind": "QUALITY GAP", "detail": "NOAA rows carry no source quality flag. HotSpot is QUESTIONABLE."},
            {"kind": "PROVENANCE GAP", "detail": "NOAA retrieval has a calendar date and no sub-second clock."},
        ],
        "source_conflicts": [
            {
                "dimension": "SST anomaly on the retrieved cell, not on the spot",
                "conflict": len(set(anomaly_values)) > 1,
                "resolved": False,
                "products": [item for item in indicators if item["product"].startswith("crw_sst_anomaly")],
            }
        ],
        "allen_associated": _allen_bbox_contains_published_point(),
        "alerts": [],
        "playbook_options": [],
        "local_estimate": "NONE",
    }


def render_spot(record: dict) -> str:
    lines = [
        "BALIZA SPOT INTELLIGENCE",
        "DEMONSTRATION / RESEARCH TEST SPOT",
        f"Spot: {record['spot_id']}",
        "Geometry: POINT",
        f"Latitude: {record['geometry']['latitude']}",
        f"Longitude: {record['geometry']['longitude']}",
        "CRS: UNKNOWN",
        "Spatial precision: UNKNOWN",
        "",
        "MEASURED",
        "None",
        "",
        "EXTERNAL INDICATORS",
        "These values belong to one retrieved NOAA cell, not to the spot.",
        "Cell: -23.475, 151.975",
        "Association to the spot: UNKNOWN",
        "Interpretation: external gridded indicator. Not a local measurement.",
        "",
    ]
    for item in record["external_indicators"]:
        lines.append(
            f"{item['product']}: {item['value']} {item['unit']} at {item['valid_time']} "
            f"quality={item['baliza_quality']}"
        )
    lines.extend(
        [
            "",
            "NOAA cells at 0.025 degrees from the published point: 4",
            "Confirmed intersection: no",
            "Values retrieved: 1 cell",
            "Values not retrieved: 3 cells, left UNKNOWN",
            "No cell was chosen. No mean was calculated.",
            "",
            "ALLEN CORAL ATLAS",
            "Not associated with this spot.",
            "The stored WFS bbox does not contain this point.",
            "No benthic class is stated for the spot.",
            "",
            "EMODNET",
            "DATA GAP / SOURCE GAP",
            "",
            "MERMAID",
            "LICENSE / ACCESS GAP",
            "No field observation.",
            "",
            "DERIVED INDICATORS",
            "None",
            "",
            "ESTIMATED",
            "None",
            "",
            "DOWNSCALING",
            "Not authorized",
            "",
            "ALERT",
            "None",
            "",
            "PLAYBOOK OPTIONS",
            "None selected",
            "",
            "SOURCE CONFLICT",
            "Two SST-anomaly products on the retrieved cell differ. Neither is selected.",
        ]
    )
    return "\n".join(lines) + "\n"
