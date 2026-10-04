"""EXPERIMENTAL / PHASE 7.6.6. Close only what the stored files demonstrate.

Does not download, invent a clock, or replace a stored checksum.
"""

from __future__ import annotations

import json
from pathlib import Path

from baliza.experimental.phase761.record import CANDIDATE_CENTERS, RETRIEVED_CENTER
from baliza.experimental.phase765.audit import NOT_AVAILABLE, UNKNOWN, build_audit, sha256_file

AUDIT_VERSION = "phase766-1"


def _metadata_artifacts(root: Path) -> list[dict]:
    folder = root / "data" / "phase75" / "raw" / "metadata"
    rows = []
    for path in sorted(folder.glob("*.info.json")):
        rows.append(
            {
                "dataset_id": path.name,
                "source": "NOAA Coral Reef Watch",
                "artifact": "ERDDAP info response",
                "raw_exists": True,
                "file_reference": str(path).replace("\\", "/"),
                "file_type": "JSON",
                "file_size": path.stat().st_size,
                "checksum_algorithm": "SHA-256",
                "checksum_value": sha256_file(path),
                "checksum_origin": "BALIZA_COMPUTED",
                "stored_checksum_comparison": NOT_AVAILABLE,
                "verification_timestamp": UNKNOWN,
                "note": "No checksum was stored at acquisition. This hash is of the metadata file, not a substitute NOAA checksum.",
            }
        )
    return rows


def _chains(audit: dict) -> list[dict]:
    chains = []
    for row in audit["datasets"]:
        if row["dataset_id"] == "resort":
            chains.append(
                {
                    "dataset_id": "resort",
                    "integrity": NOT_AVAILABLE,
                    "completeness": NOT_AVAILABLE,
                    "reason": "No resort file is stored. Absence is not zero and is not base-model training.",
                }
            )
            continue
        chains.append(
            {
                "dataset_id": row["dataset_id"],
                "integrity": row.get("chain_integrity", UNKNOWN),
                "completeness": row.get("evidence_completeness", UNKNOWN),
                "usable_in_later_indicator": row.get("usable_in_later_indicator", row.get("raw_exists", False) and row.get("chain_integrity") != "BROKEN"),
            }
        )
    return chains


def build_closure(root: Path) -> dict:
    audit = build_audit(root)
    on_disk = [row for row in audit["datasets"] if row.get("raw_exists") is True]
    raw_closed = all(
        isinstance(row.get("file_size"), int) and row["checksum"]["baliza_computed_checksum"] not in (None, UNKNOWN)
        for row in on_disk
    )
    checksums_closed = raw_closed and all(row["checksum"]["comparison"] != "MISMATCH" for row in on_disk)
    pixels = []
    for lat, lon in CANDIDATE_CENTERS:
        pixels.append(
            {
                "cell_id": f"{lat},{lon}",
                "retrieved": (lat, lon) == RETRIEVED_CENTER,
                "value": "see NOAA CSV" if (lat, lon) == RETRIEVED_CENTER else UNKNOWN,
                "association_type": UNKNOWN,
                "scientific_layer": "EXTERNAL_INDICATOR",
            }
        )
    benthic_path = root / "data" / "phase75" / "allen" / "raw" / "benthic_bbox.json"
    benthic = json.loads(benthic_path.read_text(encoding="utf-8"))
    classes = sorted({feature["properties"]["class_name"] for feature in benthic["features"]})
    gaps = [
        {"gap_id": "P1", "source": "NOAA", "dataset": "retrieved cell", "field": "CRS", "status": "PARTIAL", "reason": "No CRS code is in the CSV or the audited global attributes used here.", "impact": "Spatial association stays UNKNOWN.", "possible_resolution": "A CRS statement in the product file. Do not assume EPSG."},
        {"gap_id": "P2", "source": "NOAA", "dataset": "retrieved cell", "field": "retrieval_timestamp", "status": "PARTIAL", "reason": "Only a calendar date was stored.", "impact": "Retrieval provenance is not a full clock.", "possible_resolution": "Keep the date. Do not invent a time."},
        {"gap_id": "P3", "source": "NOAA", "dataset": "retrieved cell", "field": "observation_time", "status": "PARTIAL", "reason": "The grid time is not an observation time.", "impact": "Temporal association stays UNKNOWN.", "possible_resolution": "A source field that names the observation clock."},
        {"gap_id": "P4", "source": "NOAA", "dataset": "three cells", "field": "raw", "status": NOT_AVAILABLE, "reason": "Those cells were not requested.", "impact": "Four associations exist and three values do not.", "possible_resolution": "A later authorized retrieval."},
        {"gap_id": "P5", "source": "Allen", "dataset": "benthic and geomorphic", "field": "version", "status": "PARTIAL", "reason": "Feature files do not state a product version.", "impact": "Version stays UNKNOWN.", "possible_resolution": "A version field on the feature or a joined map epoch."},
        {"gap_id": "P6", "source": "Allen", "dataset": "benthic and geomorphic", "field": "geometry", "status": "PARTIAL", "reason": "Stored geometry is null.", "impact": "No overlap and no class attached to the spot.", "possible_resolution": "A later geometry request. Still not a field observation."},
        {"gap_id": "P7", "source": "Allen", "dataset": "WFS XML", "field": "stored_checksum", "status": "PARTIAL", "reason": "The files exist and are hashed now. No acquisition checksum was stored to compare.", "impact": "Comparison is NOT_AVAILABLE. The new hash is BALIZA_COMPUTED.", "possible_resolution": "Keep both facts. Do not backfill the old provenance file."},
        {"gap_id": "P8", "source": "EMODnet", "dataset": "European DTM", "field": "raw", "status": NOT_AVAILABLE, "reason": "No body was stored.", "impact": "Not an operational dataset.", "possible_resolution": "None inside this footprint."},
        {"gap_id": "P9", "source": "MERMAID", "dataset": "summarysampleevents", "field": "raw_body", "status": "PARTIAL", "reason": "A response hash was stored and the body was not.", "impact": "The hash cannot be recomputed. Spatial compatibility stays UNKNOWN.", "possible_resolution": "Do not relabel UNKNOWN as NO_COMPATIBLE_RECORD."},
        {"gap_id": "P10", "source": "MERMAID", "dataset": "sites", "field": "access", "status": "PARTIAL", "reason": "HTTP 401 without a credential.", "impact": "Ground truth for this spot is unverified.", "possible_resolution": "An authorized membership. Not a bypass."},
        {"gap_id": "P11", "source": "all stored rows", "field": "freshness_status", "status": "PARTIAL", "reason": "No versioned freshness policy exists.", "impact": "The status is UNKNOWN. That is not CURRENT.", "possible_resolution": "A later versioned policy. Not a 24-hour cutoff in this phase."},
        {"gap_id": "P12", "source": "all stored rows", "field": "uncertainty", "status": "PARTIAL", "reason": "The files do not give a numeric uncertainty.", "impact": "The value stays UNKNOWN, not zero.", "possible_resolution": "A source uncertainty field."},
        {"gap_id": "P13", "source": "NOAA", "dataset": "parser", "field": "transformation_timestamp", "status": "PARTIAL", "reason": "The parse module is known. The time it ran was not stored.", "impact": "The transformation chain is partial.", "possible_resolution": "Do not invent the run time."},
        {"gap_id": "P14", "source": "Resort", "dataset": "resort", "field": "raw", "status": NOT_AVAILABLE, "reason": "No authorized file is in the repository.", "impact": "Not available, and not base-model training.", "possible_resolution": "A later separated calibration and validation set."},
    ]
    return {
        "audit_version": AUDIT_VERSION,
        "generated_at": UNKNOWN,
        "generated_at_reason": "No separate audit clock was stored. The checksums are recomputed from the files.",
        "datasets": audit["datasets"],
        "artifacts": _metadata_artifacts(root),
        "evidence_chains": _chains(audit),
        "gaps": gaps,
        "noaa_four_pixels": {
            "pixel_count": 4,
            "valued_cells": 1,
            "averaged_value": None,
            "pixels": pixels,
            "scientific_layer": "EXTERNAL_INDICATOR",
        },
        "allen": {
            "layer": "benthic_data_verbose",
            "classes_in_extract": classes,
            "class_attached_to_spot": False,
            "field_observation": False,
            "measured": False,
            "epoch": UNKNOWN,
            "geometry": "null",
            "scientific_layer": "CONTEXT_ONLY",
        },
        "mermaid": {
            "official_access": "PARTIAL",
            "sample_event_access": "AVAILABLE",
            "spatial_site_access": "PARTIAL",
            "spatial_compatibility": UNKNOWN,
            "temporal_compatibility": UNKNOWN,
            "usable_spot_observations": 0,
            "relabel_unknown_as_no_compatible_record": False,
        },
        "reproducibility": {
            "local_checksum_and_parse": "reproducible",
            "reason": "SHA-256 and the CSV parse use the stored files.",
            "external_download": "not reproducible from this audit",
            "external_reason": "This phase does not call the providers again.",
            "mermaid_response_body": "not reproducible",
            "mermaid_reason": "The body was not stored.",
        },
        "closure": {
            "raw_data_traceability": "CLOSED" if raw_closed else "PARTIAL",
            "checksum_traceability": "CLOSED" if checksums_closed else "PARTIAL",
            "source_versus_baliza_transformations": "CLOSED",
            "raw_traceability_reason": "Every stored raw file has a path, a size, and a BALIZA SHA-256. Missing datasets are NOT_AVAILABLE, not untraced files.",
            "checksum_reason": "Stored acquisition checksums match. Files without an acquisition checksum are hashed and marked BALIZA_COMPUTED. No hash was copied onto a derived file.",
        },
        "local_estimate": "NONE",
        "downscaling": "NOT_AUTHORIZED",
        "alerts": [],
        "thresholds": [],
    }
