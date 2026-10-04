"""Allen Spot Intelligence from stored WFS extracts.

The DEMO heritage point keeps its coordinates. If it is outside the stored bbox,
Allen coverage is NOT_AVAILABLE for that Spot. A separate research-test Spot may
show that the extract parses, without becoming DEMO validation.
"""

from __future__ import annotations

from pathlib import Path

from baliza.experimental.phase76.association import rectangle_overlap
from baliza.infrastructure.sources.allen.adapter import AllenAdapter
from baliza.infrastructure.sources.allen.catalog import (
    ALLEN_RESEARCH_TEST_SPOT,
    AVAILABLE_LAYERS,
    DEMO_SPOT,
    NOT_AVAILABLE_PRODUCTS,
    REQUEST_BBOX,
    SERVICE_DEFAULT_CRS,
    SOURCE,
)


def _bbox_contains(spot: dict) -> bool:
    return (
        REQUEST_BBOX["min_lat"] <= spot["latitude"] <= REQUEST_BBOX["max_lat"]
        and REQUEST_BBOX["min_lon"] <= spot["longitude"] <= REQUEST_BBOX["max_lon"]
    )


def _load_layers(raw_dir: Path, provenance_path: Path) -> list[dict]:
    adapter = AllenAdapter()
    layers = []
    for type_name in AVAILABLE_LAYERS:
        loaded = adapter.load_stored_layer(raw_dir, provenance_path, type_name)
        layers.append(
            {
                "indicator": loaded["normalized"],
                "provenance": loaded["provenance"],
                "geometry_present_count": loaded["parsed"]["geometry_present_count"],
                "class_counts": loaded["parsed"]["class_counts"],
            }
        )
    return layers


def build_allen_spot_intelligence(
    raw_dir: Path,
    provenance_path: Path,
    *,
    spot_id: str | None = None,
) -> dict:
    adapter = AllenAdapter()
    discovery = adapter.discover(live=False)
    layers = _load_layers(raw_dir, provenance_path)

    if spot_id in (None, DEMO_SPOT["spot_id"]):
        spot = DEMO_SPOT
        covered = _bbox_contains(spot)
        return {
            "spot": spot,
            "source": SOURCE,
            "discovery": discovery,
            "allen_spatial_coverage": "NOT_AVAILABLE" if not covered else "PARTIAL",
            "class_attached_to_spot": False,
            "field_observation": False,
            "external_indicators": [],
            "context_layers_available_elsewhere": layers,
            "measured": [],
            "estimated": "NONE",
            "downscaling": "NOT_AUTHORIZED",
            "ml_implementation": "NOT_AUTHORIZED",
            "local_estimation": "NOT_AUTHORIZED",
            "alerts": [],
            "spatial_association": {
                "association_type": "UNKNOWN",
                "comparison_performed": False,
                "overlap_fraction": "UNKNOWN",
                "reason": (
                    "The stored Allen WFS bbox does not contain this DEMO Spot. "
                    "Coordinates were not changed. Feature geometry is null, so no polygon overlay exists."
                    if not covered
                    else "Feature geometry is null, so no class is attached to the Spot."
                ),
            },
            "temporal_association": {
                "association_type": "UNKNOWN",
                "temporal_semantics": "MAP_EPOCH",
                "map_epoch": "UNKNOWN",
                "observation_time": "UNKNOWN",
                "map_epoch_is_observation_time": False,
            },
            "quality": {"source_quality": "UNKNOWN", "baliza_quality": "UNKNOWN", "association_quality": "UNKNOWN"},
            "freshness": {
                "retrieval_freshness": layers[0]["provenance"]["retrieval_timestamp"] if layers else "UNKNOWN",
                "scientific_temporal_currency": "UNKNOWN",
                "note": "A recent retrieval does not make a map epoch current.",
            },
            "uncertainty": {
                "measurement": "UNKNOWN",
                "spatial": "UNKNOWN",
                "temporal": "UNKNOWN",
                "association": "UNKNOWN",
                "model": "UNKNOWN",
            },
            "evidence": [],
            "data_gaps": _gaps(covered=False),
            "baliza_alert_separation": {
                "allen_is_baliza_alert": False,
                "note": "Allen provides mapped context. It does not create a BALIZA alert.",
            },
            "demo_spot_coordinates_unchanged": True,
        }

    if spot_id != ALLEN_RESEARCH_TEST_SPOT["spot_id"]:
        raise KeyError(spot_id)

    spot = ALLEN_RESEARCH_TEST_SPOT
    covered = _bbox_contains(spot)
    # Attributes exist for the request bbox. Geometry is still null, so no class is the Spot's class.
    synthetic_box = (
        REQUEST_BBOX["min_lon"],
        REQUEST_BBOX["min_lat"],
        REQUEST_BBOX["max_lon"],
        REQUEST_BBOX["max_lat"],
    )
    spot_box = (spot["longitude"] - 0.001, spot["latitude"] - 0.001, spot["longitude"] + 0.001, spot["latitude"] + 0.001)
    overlap = rectangle_overlap(
        spot_box,
        synthetic_box,
        spot_crs="TEST-SAME-AXIS",
        feature_crs="TEST-SAME-AXIS",
    )
    evidence = []
    indicators = []
    for layer in layers:
        indicators.append(
            {
                **layer["indicator"],
                "applies_to": "stored WFS request bbox attributes only",
                "class_selected_for_spot": None,
                "nearest_selected": False,
                "interpolated": False,
                "spatial_association": {
                    "association_type": "UNKNOWN",
                    "wfs_filter_relation": "INTERSECTS" if covered else "UNKNOWN",
                    "overlap_fraction": "UNKNOWN",
                    "geometry_overlay": False,
                    "reason": (
                        "Feature geometry is null. Class counts describe the request bbox extract, "
                        "not a polygon attached to this Spot."
                    ),
                    "test_axis_aligned_bbox_relation": overlap.association_type,
                    "test_label": "TEST / SYNTHETIC axis-aligned boxes. Not a geodesic Allen geometry.",
                },
            }
        )
        evidence.append(
            {
                "evidence_id": f"allen-{layer['indicator']['layer']}",
                "scientific_layer": layer["indicator"]["scientific_layer"],
                "epistemic_label": "FACT",
                "raw_file": layer["provenance"]["raw_file"],
                "raw_checksum_sha256": layer["provenance"]["raw_checksum_sha256"],
                "product": layer["provenance"]["product"],
                "version": layer["provenance"]["version"],
                "epoch": layer["provenance"]["epoch"],
                "transformation_chain": layer["provenance"]["transformation_chain"],
                "evidence_completeness": "PARTIAL",
                "measured": False,
                "field_observation": False,
            }
        )
    return {
        "spot": spot,
        "source": SOURCE,
        "discovery": discovery,
        "allen_spatial_coverage": "PARTIAL",
        "class_attached_to_spot": False,
        "field_observation": False,
        "external_indicators": indicators,
        "measured": [],
        "estimated": "NONE",
        "downscaling": "NOT_AUTHORIZED",
        "ml_implementation": "NOT_AUTHORIZED",
        "local_estimation": "NOT_AUTHORIZED",
        "alerts": [],
        "spatial_association": {
            "association_type": "UNKNOWN",
            "comparison_performed": False,
            "overlap_fraction": "UNKNOWN",
            "service_default_crs": SERVICE_DEFAULT_CRS,
            "feature_crs": "UNKNOWN",
            "reason": "Attributes were retrieved for a bbox containing this research-test point. Geometry is null.",
        },
        "temporal_association": {
            "association_type": "UNKNOWN",
            "temporal_semantics": "MAP_EPOCH",
            "map_epoch": "UNKNOWN",
            "observation_time": "UNKNOWN",
            "map_epoch_is_observation_time": False,
        },
        "quality": {"source_quality": "UNKNOWN", "baliza_quality": "UNKNOWN", "association_quality": "UNKNOWN"},
        "freshness": {
            "retrieval_freshness": layers[0]["provenance"]["retrieval_timestamp"] if layers else "UNKNOWN",
            "scientific_temporal_currency": "UNKNOWN",
            "note": "A recent retrieval does not make a map epoch current.",
        },
        "uncertainty": {
            "measurement": "UNKNOWN",
            "spatial": "UNKNOWN",
            "temporal": "UNKNOWN",
            "association": "UNKNOWN",
            "model": "UNKNOWN",
        },
        "evidence": evidence,
        "data_gaps": _gaps(covered=True),
        "baliza_alert_separation": {
            "allen_is_baliza_alert": False,
            "note": "Allen provides mapped context. It does not create a BALIZA alert.",
        },
        "not_a_validation_of_demo_spot": True,
    }


def _gaps(*, covered: bool) -> list[dict]:
    gaps = [
        {
            "kind": "SOURCE_GAP",
            "detail": product_id,
            "reason": meta["reason"],
        }
        for product_id, meta in NOT_AVAILABLE_PRODUCTS.items()
    ]
    gaps.extend(
        [
            {
                "kind": "SPATIAL_GAP",
                "detail": "Feature geometry is null in the stored extracts. Polygon→Spot overlay is not available.",
            },
            {
                "kind": "PROVENANCE_GAP",
                "detail": "product_version and map_epoch are UNKNOWN on the stored features.",
            },
            {
                "kind": "QUALITY_GAP",
                "detail": "No source quality or classification confidence is in the attribute extract.",
            },
        ]
    )
    if not covered:
        gaps.insert(
            0,
            {
                "kind": "SPATIAL_GAP",
                "detail": "ALLEN_SPATIAL_COVERAGE = NOT_AVAILABLE for the DEMO Spot. Coordinates were not moved.",
            },
        )
    return gaps
