"""EXPERIMENTAL / PHASE 7.6.5. Audit of files already stored.

Does not download, replace a checksum, or invent a version or CRS.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

AUDIT_VERSION = "phase765-1"
UNKNOWN = "UNKNOWN"
NOT_AVAILABLE = "NOT_AVAILABLE"

NOAA_DATASETS = (
    ("noaacrwsstDaily", "crw_coraltemp_sst", "analysed_sst"),
    ("noaacrwsstanomalyDaily", "crw_sst_anomaly_v31", "sea_surface_temperature_anomaly"),
    ("noaacrwsstanomalybaselineDaily", "crw_sst_anomaly_1991_2020", "sea_surface_temperature_anomaly"),
    ("noaacrwhotspotDaily", "crw_hotspot", "hotspot"),
    ("noaacrwdhwDaily", "crw_dhw", "degree_heating_week"),
    ("noaacrwbaa7dDaily", "crw_bleaching_alert_area_7d", "bleaching_alert_area"),
)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compare_checksum(path: Path, stored: str | None) -> dict:
    computed = sha256_file(path) if path.is_file() else None
    if stored in (None, "", UNKNOWN):
        result = NOT_AVAILABLE
    elif computed == stored:
        result = "MATCH"
    else:
        result = "MISMATCH"
    return {
        "checksum_algorithm": "SHA-256" if computed else UNKNOWN,
        "baliza_computed_checksum": computed or UNKNOWN,
        "stored_checksum": stored or UNKNOWN,
        "checksum_source": "BALIZA_COMPUTED" if computed else UNKNOWN,
        "stored_checksum_origin": "BALIZA_RECORDED_AT_ACQUISITION" if stored else NOT_AVAILABLE,
        "comparison": result,
        "provenance_integrity_issue": result == "MISMATCH",
    }


def _attr(info: dict, name: str) -> str:
    for row in info.get("rows") or []:
        if len(row) >= 5 and row[0] == "attribute" and row[2] == name and row[4] not in ("", None):
            return str(row[4])
    return UNKNOWN


def _file_row(
    *,
    dataset_id: str,
    source: str,
    product: str,
    version: str,
    variable: str,
    path: Path,
    file_type: str,
    stored_checksum: str | None,
    retrieval_timestamp: str,
    endpoint: str,
    request: dict,
    spatial_extent: str,
    temporal_extent: str,
    crs: str,
    resolution: str,
    unit: str,
    raw_or_derived: str,
    association: str,
    quality: str,
    uncertainty: str,
    evidence_completeness: str,
    chain: str,
) -> dict:
    exists = path.is_file()
    size = path.stat().st_size if exists else None
    checksum = compare_checksum(path, stored_checksum) if exists else {
        "checksum_algorithm": UNKNOWN,
        "baliza_computed_checksum": UNKNOWN,
        "stored_checksum": stored_checksum or UNKNOWN,
        "checksum_source": UNKNOWN,
        "stored_checksum_origin": NOT_AVAILABLE,
        "comparison": NOT_AVAILABLE,
        "provenance_integrity_issue": False,
    }
    if not exists:
        raw_status = NOT_AVAILABLE if stored_checksum is None else "OPEN"
    elif checksum["comparison"] == "MISMATCH":
        raw_status = "PARTIAL"
    elif checksum["comparison"] == "MATCH" and version != UNKNOWN and crs != UNKNOWN:
        raw_status = "CLOSED"
    elif checksum["comparison"] in {"MATCH", NOT_AVAILABLE} and exists:
        raw_status = "PARTIAL" if version == UNKNOWN or crs == UNKNOWN or checksum["comparison"] == NOT_AVAILABLE else "CLOSED"
    else:
        raw_status = "PARTIAL"
    readable = exists
    return {
        "dataset_id": dataset_id,
        "source": source,
        "product": product,
        "product_version": version,
        "variable": variable,
        "file_reference": str(path).replace("\\", "/"),
        "file_type": file_type,
        "file_size": size if size is not None else UNKNOWN,
        "raw_exists": exists,
        "raw_readable": readable,
        "raw_status": raw_status,
        "checksum": checksum,
        "retrieval_timestamp": retrieval_timestamp,
        "source_endpoint": endpoint,
        "request_parameters": request,
        "authentication": "none stored",
        "spatial_extent": spatial_extent,
        "temporal_extent": temporal_extent,
        "crs": crs,
        "resolution": resolution,
        "unit": unit,
        "original_unit": unit,
        "canonical_unit": UNKNOWN,
        "conversion_applied": False,
        "raw_or_derived": raw_or_derived,
        "source_transformation": "Provider product. Not produced by BALIZA.",
        "baliza_transformation": "PARSE only, where a parser was run. No interpolation or downscaling.",
        "association": association,
        "quality": quality,
        "uncertainty": uncertainty,
        "freshness_status": UNKNOWN,
        "evidence_completeness": evidence_completeness,
        "chain_integrity": chain,
        "status": raw_status,
    }


def build_audit(root: Path) -> dict:
    raw = root / "data" / "phase75" / "raw"
    provenance = json.loads((root / "data" / "phase75" / "provenance.json").read_text(encoding="utf-8"))
    stored = {item["name"]: item["sha256"] for item in provenance["files"]}
    allen_prov = json.loads((root / "data" / "phase75" / "allen" / "provenance.json").read_text(encoding="utf-8"))
    allen_stored = {item["name"]: item["sha256"] for item in allen_prov["files"]}
    inquiry = json.loads((root / "data" / "phase763" / "mermaid-inquiry.json").read_text(encoding="utf-8"))
    australia = json.loads((root / "data" / "phase763" / "mermaid-australia-summary.json").read_text(encoding="utf-8"))
    datasets = []
    for dataset_id, product, variable in NOAA_DATASETS:
        info_path = raw / "metadata" / f"{dataset_id}.info.json"
        info = json.loads(info_path.read_text(encoding="utf-8")) if info_path.is_file() else {}
        version = _attr(info, "product_version")
        csv_path = raw / f"{dataset_id}_2026-09-26.csv"
        unit = UNKNOWN
        if csv_path.is_file():
            lines = csv_path.read_text(encoding="utf-8").splitlines()
            if len(lines) >= 2:
                unit = lines[1].split(",")[-1] or UNKNOWN
        quality = "QUESTIONABLE" if dataset_id == "noaacrwhotspotDaily" else UNKNOWN
        datasets.append(
            _file_row(
                dataset_id=dataset_id,
                source="NOAA Coral Reef Watch",
                product=product,
                version=version,
                variable=variable,
                path=csv_path,
                file_type="CSV",
                stored_checksum=stored.get(csv_path.name),
                retrieval_timestamp=provenance["retrieval_calendar_date"],
                endpoint=provenance["endpoint"],
                request=provenance["request"],
                spatial_extent="One cell center -23.475, 151.975. Four candidate centers documented. Three not retrieved.",
                temporal_extent="Grid time 2026-09-26T12:00:00Z. Not relabeled as an observation time.",
                crs=UNKNOWN,
                resolution=_attr(info, "geospatial_lat_resolution"),
                unit=unit,
                raw_or_derived="RAW_SUBSET",
                association="UNKNOWN. Four centers listed. One value stored. No average.",
                quality=quality,
                uncertainty=UNKNOWN,
                evidence_completeness="PARTIAL",
                chain="PARTIAL",
            )
        )
    allen_root = root / "data" / "phase75" / "allen" / "raw"
    for name, product in (
        ("benthic_bbox.json", "benthic_data_verbose"),
        ("geomorphic_bbox.json", "geomorphic_data_verbose"),
        ("mapping_maps.json", "mapping maps catalogue"),
    ):
        datasets.append(
            _file_row(
                dataset_id=f"allen-{name}",
                source="Allen Coral Atlas",
                product=product,
                version=UNKNOWN,
                variable="class_name" if name != "mapping_maps.json" else UNKNOWN,
                path=allen_root / name,
                file_type="JSON",
                stored_checksum=allen_stored.get(name),
                retrieval_timestamp=allen_prov["response_timestamps"].get(name, allen_prov["retrieval_http_date"]),
                endpoint=allen_prov["endpoint"],
                request=allen_prov["request"] if name != "mapping_maps.json" else {},
                spatial_extent="Request bbox only. Feature geometry is null." if name != "mapping_maps.json" else UNKNOWN,
                temporal_extent=UNKNOWN,
                crs=UNKNOWN,
                resolution=UNKNOWN,
                unit=UNKNOWN,
                raw_or_derived="RAW_EXTRACT",
                association="Not associated. Not a field observation.",
                quality=UNKNOWN,
                uncertainty=UNKNOWN,
                evidence_completeness="PARTIAL",
                chain="PARTIAL",
            )
        )
    for name in ("wfs-capabilities-2.0.0.xml", "benthic-describe-feature-type.xml", "geomorphic-describe-feature-type.xml"):
        datasets.append(
            _file_row(
                dataset_id=f"allen-{name}",
                source="Allen Coral Atlas",
                product="WFS service description",
                version=UNKNOWN,
                variable=UNKNOWN,
                path=allen_root / name,
                file_type="XML",
                stored_checksum=None,
                retrieval_timestamp=UNKNOWN,
                endpoint=allen_prov["endpoint"],
                request={},
                spatial_extent=UNKNOWN,
                temporal_extent=UNKNOWN,
                crs="Service DefaultCRS was recorded in Phase 7.5.2. This audit does not copy it onto feature files.",
                resolution=UNKNOWN,
                unit=UNKNOWN,
                raw_or_derived="RAW_METADATA",
                association="Not a spot association.",
                quality=UNKNOWN,
                uncertainty=UNKNOWN,
                evidence_completeness="PARTIAL",
                chain="PARTIAL",
            )
        )
    datasets.append(
        {
            "dataset_id": "emodnet-bathymetry",
            "source": "EMODnet",
            "product": "European DTM",
            "product_version": UNKNOWN,
            "variable": "depth",
            "file_reference": NOT_AVAILABLE,
            "file_type": NOT_AVAILABLE,
            "file_size": NOT_AVAILABLE,
            "raw_exists": False,
            "raw_readable": False,
            "raw_status": NOT_AVAILABLE,
            "checksum": {"comparison": NOT_AVAILABLE, "provenance_integrity_issue": False},
            "retrieval_timestamp": NOT_AVAILABLE,
            "source_endpoint": "https://ows.emodnet-bathymetry.eu/wms",
            "request_parameters": {"documented_call": "GetCapabilities HTTP 200. Body not stored."},
            "spatial_extent": "Documented footprint does not include this cell. No depth value was stored.",
            "temporal_extent": UNKNOWN,
            "crs": UNKNOWN,
            "resolution": UNKNOWN,
            "unit": UNKNOWN,
            "conversion_applied": False,
            "raw_or_derived": "NOT_RETRIEVED",
            "documented_is_not_retrieved": True,
            "association": NOT_AVAILABLE,
            "quality": UNKNOWN,
            "uncertainty": UNKNOWN,
            "freshness_status": UNKNOWN,
            "evidence_completeness": "INSUFFICIENT",
            "chain_integrity": "BROKEN",
            "usable_in_later_indicator": False,
            "status": NOT_AVAILABLE,
        }
    )
    datasets.append(
        {
            "dataset_id": "mermaid-summarysampleevents",
            "source": "MERMAID",
            "product": "summarysampleevents",
            "product_version": UNKNOWN,
            "variable": UNKNOWN,
            "file_reference": "data/phase763/mermaid-inquiry.json",
            "file_type": "JSON",
            "raw_exists": False,
            "raw_readable": False,
            "raw_status": "PARTIAL",
            "checksum": {
                "comparison": NOT_AVAILABLE,
                "reason": "Response hashes were stored. Response bodies were not, so they cannot be recomputed.",
                "provenance_integrity_issue": False,
            },
            "retrieval_timestamp": australia["http_date"],
            "source_endpoint": "https://api.datamermaid.org/v1/summarysampleevents/",
            "summary_sample_event_count": next(q["count"] for q in inquiry["queries"] if q["name"] == "summary_sample_events_page"),
            "usable_spot_observations": 0,
            "official_access": "PARTIAL",
            "sample_event_access": "AVAILABLE",
            "spatial_site_access": "PARTIAL",
            "spatial_compatibility": UNKNOWN,
            "temporal_compatibility": UNKNOWN,
            "spot_result": "NO_MATCH_WITH_DEMO_SPOT",
            "australia_summary_count": australia["count"],
            "association": "None. The Australia page has no identical coordinate.",
            "quality": UNKNOWN,
            "uncertainty": UNKNOWN,
            "freshness_status": UNKNOWN,
            "evidence_completeness": "PARTIAL",
            "chain_integrity": "PARTIAL",
            "status": "PARTIAL",
        }
    )
    datasets.append(
        {
            "dataset_id": "resort",
            "source": "Resort",
            "product": NOT_AVAILABLE,
            "product_version": NOT_AVAILABLE,
            "file_reference": NOT_AVAILABLE,
            "raw_exists": False,
            "raw_status": NOT_AVAILABLE,
            "role": "SITE_SPECIFIC_CALIBRATION and SITE_SPECIFIC_VALIDATION in a later phase. Not base-model training.",
            "base_model_training": False,
            "status": NOT_AVAILABLE,
        }
    )
    issues = [row["dataset_id"] for row in datasets if row.get("checksum", {}).get("provenance_integrity_issue")]
    return {
        "audit_version": AUDIT_VERSION,
        "spot_id": "DEMO-CRW-ORIG24-HERITAGE-POINT",
        "noaa_pixel_count": 4,
        "noaa_valued_cells": 1,
        "noaa_averaged_value": None,
        "local_estimate": "NONE",
        "downscaling": "NOT_AUTHORIZED",
        "interpolated": "NOT_AUTHORIZED",
        "model_estimated_by_baliza": "NOT_AUTHORIZED",
        "alerts": [],
        "datasets": datasets,
        "provenance_integrity_issues": issues,
        "gaps": [
            {"gap_id": "G1", "source": "NOAA", "dataset": "three unretrieved cells", "gap_type": "DATA_GAP", "description": "Three of four documented centers have no file.", "impact": "No four-value comparison.", "known_reason": "Only one cell was requested.", "next_possible_resolution": "A later authorized retrieval of the other three cells."},
            {"gap_id": "G2", "source": "EMODnet", "dataset": "European DTM", "gap_type": "SOURCE_GAP", "description": "No depth file is stored.", "impact": "No depth evidence.", "known_reason": "The documented European footprint does not include this cell, and the capabilities body was not saved.", "next_possible_resolution": "None inside this footprint."},
            {"gap_id": "G3", "source": "Allen", "dataset": "benthic and geomorphic extracts", "gap_type": "SPATIAL_GAP", "description": "Feature geometry is null.", "impact": "No overlap.", "known_reason": "The request omitted geometry.", "next_possible_resolution": "A later request that asks for geometry, still not a field observation."},
            {"gap_id": "G4", "source": "NOAA", "dataset": "retrieved cell", "gap_type": "TEMPORAL_GAP", "description": "The spot has no reference time.", "impact": "Temporal association stays unknown.", "known_reason": "No spot clock was defined.", "next_possible_resolution": "A recorded spot reference time."},
            {"gap_id": "G5", "source": "MERMAID", "dataset": "summarysampleevents", "gap_type": "GROUND_TRUTH_GAP", "description": "No field row was associated with the spot.", "impact": "No ground truth for this spot.", "known_reason": "No identical coordinate, and site access is unauthorized.", "next_possible_resolution": "An authorized site read. Not a claim that MERMAID has no data."},
            {"gap_id": "G6", "source": "NOAA", "dataset": "retrieved rows", "gap_type": "QUALITY_GAP", "description": "No source quality flag is in the CSV.", "impact": "Source quality stays unknown.", "known_reason": "The ERDDAP row has no flag.", "next_possible_resolution": "A source flag, if one is published."},
            {"gap_id": "G7", "source": "MERMAID", "dataset": "sites", "gap_type": "LICENSE_ACCESS_GAP", "description": "Sites returned HTTP 401.", "impact": "Observation rows were not read.", "known_reason": "No credential was sent.", "next_possible_resolution": "An authorized project membership. Not a bypass."},
            {"gap_id": "G8", "source": "NOAA", "dataset": "retrieval clock", "gap_type": "PROVENANCE_GAP", "description": "Retrieval is a calendar date.", "impact": "The chain is partial.", "known_reason": "The downloader did not store a sub-second clock.", "next_possible_resolution": "Keep the date. Do not invent a clock."},
        ],
    }


def render_audit(audit: dict) -> str:
    lines = [
        "BALIZA REAL DATASET AUDIT",
        f"Spot: {audit['spot_id']}",
        "NOAA: six CSV subsets exist. Stored SHA-256 values are checked against the files. Product version is taken from the ERDDAP metadata attribute when that attribute is present. CRS is unknown. Four cell centers are listed and one value is stored. No average was calculated.",
        "Allen: benthic, geomorphic, and map-catalogue JSON files exist with stored checksums. Feature geometry is null. Classes are not a field observation. Service XML files exist without a stored checksum.",
        "EMODnet: the capabilities call was documented. No depth file is stored. Documented is not retrieved.",
        "MERMAID: public summary access is partial. The summary count is not a count of observations of this spot. No match with the demonstration spot was verified. This is not a statement that MERMAID has no data.",
        "Resort: not available. Resort history is not base-model training.",
        "Freshness status remains unknown. No risk state was produced.",
        f"NOAA cells: {audit['noaa_pixel_count']}. Valued: {audit['noaa_valued_cells']}. Averaged value: none.",
    ]
    if audit["provenance_integrity_issues"]:
        lines.append("PROVENANCE INTEGRITY ISSUE: " + ", ".join(audit["provenance_integrity_issues"]))
    return "\n".join(lines)
