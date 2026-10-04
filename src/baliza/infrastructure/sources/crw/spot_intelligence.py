"""Build Spot Intelligence from stored CRW products.

CRW cells remain EXTERNAL_INDICATOR. Four candidate cells are listed.
No average, nearest pick, interpolation, estimate, or BALIZA alert is created.
"""

from __future__ import annotations

from pathlib import Path

from baliza.experimental.phase76.association import GridSpec, associate_point_to_grid
from baliza.infrastructure.sources.crw.adapter import CrwAdapter
from baliza.infrastructure.sources.crw.catalog import (
    AVAILABLE_PRODUCTS,
    CANDIDATE_CENTERS,
    DEMO_SPOT,
    GRID_TIME,
    NOT_AVAILABLE_PRODUCTS,
    RETRIEVED_CENTER,
    SOURCE,
)


def build_crw_spot_intelligence(
    raw_dir: Path,
    provenance_path: Path,
    *,
    reference_time: str | None = None,
) -> dict:
    adapter = CrwAdapter()
    discovery = adapter.discover(live=False)
    products = []
    for dataset_id in AVAILABLE_PRODUCTS:
        loaded = adapter.load_stored_product(raw_dir, provenance_path, dataset_id)
        row = loaded["normalized"][0]
        products.append(
            {
                "dataset_id": dataset_id,
                "indicator": row,
                "provenance": loaded["provenance"],
                "metadata": loaded["metadata"],
                "applies_to": "retrieved cell only",
                "cell": {
                    "latitude": row["where"]["latitude"],
                    "longitude": row["where"]["longitude"],
                },
                "spatial_association": {
                    "association_type": "UNKNOWN",
                    "reason": "Spot CRS and grid CRS are both UNKNOWN. Coordinates are not compared.",
                    "comparison_performed": False,
                },
                "temporal_association": {
                    "association_type": "UNKNOWN",
                    "source_time": row["when"],
                    "spot_reference_time": reference_time or "UNKNOWN",
                    "policy": "NOT_DEFINED",
                    "ingestion_time": loaded["provenance"]["retrieval_timestamp"],
                    "observation_time": "UNKNOWN",
                    "note": "Grid time is not relabeled as an observation time.",
                },
            }
        )

    pixels = []
    for lat, lon in CANDIDATE_CENTERS:
        pixels.append(
            {
                "latitude": lat,
                "longitude": lon,
                "retrieved": (lat, lon) == RETRIEVED_CENTER,
                "values": "see external_indicators" if (lat, lon) == RETRIEVED_CENTER else "UNKNOWN",
                "scientific_layer": "EXTERNAL_INDICATOR",
            }
        )

    # Regression geometry for the four-pixel boundary under a shared TEST CRS only.
    test_grid = GridSpec(
        crs="TEST-SAME-AXIS",
        lat_centers=(-23.475, -23.525),
        lon_centers=(151.975, 152.025),
        half_lat=0.025,
        half_lon=0.025,
        label="TEST / SYNTHETIC CRS. Not the NOAA production CRS.",
    )
    four = associate_point_to_grid(
        DEMO_SPOT["latitude"],
        DEMO_SPOT["longitude"],
        test_grid,
        spot_crs="TEST-SAME-AXIS",
        values={
            (-23.475, 151.975): "retrieved",
            (-23.475, 152.025): None,
            (-23.525, 151.975): None,
            (-23.525, 152.025): None,
        },
    )

    return {
        "spot": DEMO_SPOT,
        "source": SOURCE,
        "discovery": discovery,
        "external_indicators": products,
        "measured": [],
        "estimated": "NONE",
        "downscaling": "NOT_AUTHORIZED",
        "ml_implementation": "NOT_AUTHORIZED",
        "alerts": [],
        "playbook_options": [],
        "quality": [item["indicator"]["quality"] for item in products],
        "freshness": {
            "product_time": GRID_TIME,
            "retrieval_time": products[0]["provenance"]["retrieval_timestamp"] if products else "UNKNOWN",
            "reference_time": reference_time or "UNKNOWN",
            "freshness_status": "UNKNOWN",
            "note": "No freshness cutoff is authorized in this phase.",
        },
        "uncertainty": {
            "measurement": "UNKNOWN",
            "spatial": "UNKNOWN",
            "temporal": "UNKNOWN",
            "association": "UNKNOWN",
            "model": "NOT_APPLICABLE",
        },
        "evidence": [
            {
                "evidence_id": f"crw-{item['dataset_id']}",
                "scientific_layer": "EXTERNAL_INDICATOR",
                "epistemic_label": "FACT",
                "raw_file": item["provenance"]["raw_file"],
                "raw_checksum_sha256": item["provenance"]["raw_checksum_sha256"],
                "product_version": item["provenance"]["product_version"],
                "transformation_chain": item["provenance"]["transformation_chain"],
                "baliza_alert": item["indicator"]["baliza_alert"],
            }
            for item in products
        ],
        "spatial_associations": {
            "production": {
                "pixel_count": 4,
                "valued_cells": 1,
                "averaged_value": None,
                "nearest_selected": False,
                "interpolated": False,
                "association_type": "UNKNOWN",
                "pixels": pixels,
                "note": "Four documented centers. One retrieved. CRS unknown, so intersection is not confirmed.",
            },
            "test_four_pixel_boundary": {
                "label": four.note,
                "association_type": four.association_type,
                "hit_count": len(four.hits),
                "local_estimate": four.local_estimate,
                "averaged_value": None,
                "values": [hit.value for hit in four.hits],
            },
        },
        "data_gaps": [
            {"kind": "DATA_GAP", "detail": "Three of four documented NOAA cell centers were not retrieved."},
            *[
                {"kind": "SOURCE_GAP", "detail": product_id, "reason": meta["reason"]}
                for product_id, meta in NOT_AVAILABLE_PRODUCTS.items()
            ],
            {"kind": "TEMPORAL_GAP", "detail": "Spot has no reference time. Temporal association stays UNKNOWN."},
            {"kind": "SPATIAL_GAP", "detail": "Grid CRS is UNKNOWN. Production association stays UNKNOWN."},
            {"kind": "GROUND_TRUTH_GAP", "detail": "No in-situ measurement at this spot."},
            {"kind": "PROVENANCE_GAP", "detail": "Retrieval timestamp is a calendar date without a sub-second clock."},
        ],
        "source_conflicts": _anomaly_conflict(products),
        "baliza_alert_separation": {
            "crw_bleaching_alert_area_is_baliza_alert": False,
            "note": "CRW Bleaching Alert Area remains EXTERNAL_INDICATOR. Only an existing BALIZA RuleVersion may create a BALIZA alert.",
        },
    }


def _anomaly_conflict(products: list[dict]) -> list[dict]:
    anomalies = [
        item
        for item in products
        if item["indicator"]["what"].startswith("crw_sst_anomaly")
    ]
    if len(anomalies) < 2:
        return []
    values = {item["indicator"]["value"] for item in anomalies}
    return [
        {
            "dimension": "SST anomaly on the retrieved cell",
            "conflict": len(values) > 1,
            "resolved": False,
            "products": [item["indicator"]["what"] for item in anomalies],
            "values": [item["indicator"]["value"] for item in anomalies],
        }
    ]
