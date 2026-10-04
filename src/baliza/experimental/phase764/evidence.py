"""EXPERIMENTAL / PHASE 7.6.4. Evidence chain for one spot.

Traceability is not scientific validity. Unknown is not zero.
No interpolation, downscaling, or model estimate is created here.
"""

from __future__ import annotations

import json
from pathlib import Path

from baliza.experimental.phase75.crw_csv import PRODUCTS, parse_crw_griddap_csv
from baliza.experimental.phase761.record import (
    CANDIDATE_CENTERS,
    DATASETS,
    RETRIEVED_CENTER,
    SPOT_ID,
)
from baliza.experimental.phase763.mermaid import real_spot_mermaid

UNKNOWN = "UNKNOWN"
NOT_AUTHORIZED = "NOT_AUTHORIZED"
FORBIDDEN_TRANSFORMS = frozenset({"INTERPOLATED", "MODEL_ESTIMATED", "DOWNSCALED"})
QUALITY_STATES = frozenset({"GOOD", "QUESTIONABLE", "POOR", "MISSING", "UNKNOWN"})
GAP_TYPES = (
    "DATA_GAP",
    "SOURCE_GAP",
    "SPATIAL_GAP",
    "TEMPORAL_GAP",
    "GROUND_TRUTH_GAP",
    "QUALITY_GAP",
    "LICENSE_ACCESS_GAP",
    "PROVENANCE_GAP",
)


def _quality(value: str) -> str:
    if value not in QUALITY_STATES:
        raise ValueError(f"Unknown quality state: {value}")
    return value


def uncertainty_value(kind: str, numeric: float | None = None) -> dict:
    """UNKNOWN is never stored as zero. A numeric zero must be labeled KNOWN_NUMERIC."""
    if kind not in {"KNOWN_NUMERIC", "QUALITATIVE", "UNKNOWN", "NOT_APPLICABLE"}:
        raise ValueError(kind)
    if kind == "UNKNOWN":
        return {"kind": "UNKNOWN", "value": UNKNOWN}
    if kind == "NOT_APPLICABLE":
        return {"kind": "NOT_APPLICABLE", "value": "NOT_APPLICABLE"}
    if kind == "QUALITATIVE":
        return {"kind": "QUALITATIVE", "value": "QUALITATIVE"}
    if numeric is None:
        raise ValueError("A numeric uncertainty needs a supplied number.")
    return {"kind": "KNOWN_NUMERIC", "value": numeric}


def transformation_chain(*steps: str) -> list[str]:
    ordered = []
    for step in steps:
        if step in FORBIDDEN_TRANSFORMS:
            raise ValueError(f"{step} is not authorized in this phase.")
        ordered.append(step)
    return ordered


def freshness(
    *,
    reference_time: str | None,
    observation_time: str | None,
    ingestion_time: str | None,
    policy_version: str | None = None,
) -> dict:
    """No freshness class is assigned unless a versioned policy is supplied. None is authorized."""
    status = UNKNOWN
    if policy_version:
        raise ValueError("This phase has no authorized freshness policy.")
    return {
        "reference_time": reference_time or UNKNOWN,
        "observation_time": observation_time or UNKNOWN,
        "ingestion_time": ingestion_time or UNKNOWN,
        "age": UNKNOWN,
        "freshness_status": status,
        "freshness_method": "NOT_DEFINED",
        "ingestion_used_as_observation": False,
    }


def traceability(item: dict) -> str:
    """COMPLETE is reconstructable. BROKEN cannot name an origin. PARTIAL is the rest."""
    provenance = item["provenance"]
    if not item.get("source") or item["source"] == UNKNOWN:
        if provenance.get("raw_file_reference") in (None, UNKNOWN) and provenance.get("raw_checksum") in (None, UNKNOWN):
            return "BROKEN"
    required = (
        item.get("source"),
        item.get("product"),
        item.get("product_version"),
        provenance.get("raw_file_reference"),
        provenance.get("raw_checksum"),
        provenance.get("retrieval_timestamp"),
        item.get("spatial_association"),
        item.get("transformation_type"),
    )
    if all(part not in (None, "", UNKNOWN) for part in required):
        return "COMPLETE"
    if item.get("source") in (None, UNKNOWN) and provenance.get("raw_checksum") in (None, UNKNOWN):
        return "BROKEN"
    return "PARTIAL"


def evidence_completeness(trace: str, gaps: list[str]) -> str:
    if trace == "BROKEN" or "PROVENANCE_GAP" in gaps and trace != "COMPLETE":
        if trace == "BROKEN":
            return "INSUFFICIENT"
    if trace == "COMPLETE" and not gaps:
        return "COMPLETE"
    if trace == "PARTIAL" or gaps:
        return "PARTIAL"
    return UNKNOWN


def classify_pair(left: dict, right: dict) -> str:
    """Same variable with two values is a conflict. Different variables are complementary."""
    if left["variable"] != right["variable"]:
        return "COMPLEMENTARY_EVIDENCE"
    if left["value"] != right["value"]:
        return "SOURCE_CONFLICT"
    return "SAME_VALUE"


def make_evidence(
    *,
    evidence_id: str,
    spot_id: str,
    source: str,
    dataset: str,
    product: str,
    product_version: str | None,
    variable: str | None,
    value: str | None,
    unit: str | None,
    source_time: str | None,
    observation_time: str | None,
    ingestion_time: str | None,
    spatial_association: str,
    temporal_association: str,
    spatial_precision: str,
    temporal_precision: str,
    source_quality: str,
    baliza_quality: str,
    association_quality: str,
    quality_basis: str,
    measurement: dict,
    spatial_uncertainty: dict,
    temporal_uncertainty: dict,
    association_uncertainty: dict,
    model_uncertainty: dict,
    raw_file: str | None,
    raw_checksum: str | None,
    retrieval_timestamp: str | None,
    source_url: str | None,
    request_parameters: dict | None,
    chain: list[str],
    gaps: list[str],
    scientific_layer: str,
) -> dict:
    for gap in gaps:
        if gap not in GAP_TYPES:
            raise ValueError(gap)
    item = {
        "evidence_id": evidence_id,
        "spot_id": spot_id,
        "source": source,
        "dataset": dataset,
        "product": product,
        "product_version": product_version or UNKNOWN,
        "variable": variable or UNKNOWN,
        "value": UNKNOWN if value is None else value,
        "unit": unit or UNKNOWN,
        "scientific_layer": scientific_layer,
        "epistemic_label": "FACT" if value is not None else UNKNOWN,
        "source_time": source_time or UNKNOWN,
        "observation_time": observation_time or UNKNOWN,
        "measurement_time": UNKNOWN,
        "survey_date": UNKNOWN,
        "processing_time": UNKNOWN,
        "publication_time": UNKNOWN,
        "ingestion_time": ingestion_time or UNKNOWN,
        "spatial_association": spatial_association,
        "temporal_association": temporal_association,
        "spatial_precision": spatial_precision,
        "temporal_precision": temporal_precision,
        "quality": {
            "source": _quality(source_quality),
            "baliza": _quality(baliza_quality),
            "association": _quality(association_quality),
            "quality_basis": quality_basis,
            "quality_method": "phase75 hotspot sign check" if baliza_quality == "QUESTIONABLE" else UNKNOWN,
            "quality_timestamp": UNKNOWN,
        },
        "uncertainty": {
            "measurement": measurement,
            "spatial": spatial_uncertainty,
            "temporal": temporal_uncertainty,
            "association": association_uncertainty,
            "model": model_uncertainty,
        },
        "freshness": freshness(
            reference_time=None,
            observation_time=observation_time,
            ingestion_time=ingestion_time,
        ),
        "provenance": {
            "dataset": dataset,
            "raw_file_reference": raw_file or UNKNOWN,
            "raw_checksum": raw_checksum or UNKNOWN,
            "retrieval_timestamp": retrieval_timestamp or UNKNOWN,
            "source_url": source_url or UNKNOWN,
            "request_parameters": request_parameters or {},
            "integrity": "SHA-256" if raw_checksum else UNKNOWN,
        },
        "transformation_type": chain[-1] if chain else UNKNOWN,
        "transformation_chain": chain,
        "downscaled": NOT_AUTHORIZED,
        "interpolated": NOT_AUTHORIZED,
        "model_estimated": NOT_AUTHORIZED,
        "gaps": gaps,
        "local_estimate": NOT_AUTHORIZED,
    }
    item["traceability"] = traceability(item)
    item["evidence_completeness"] = evidence_completeness(item["traceability"], gaps)
    if item["traceability"] == "BROKEN":
        item["usable_in_later_indicator"] = False
    else:
        item["usable_in_later_indicator"] = item["value"] != UNKNOWN
    return item


def build_real_evidence(
    raw_dir: Path,
    provenance_path: Path,
    allen_path: Path,
    allen_provenance_path: Path,
    mermaid_inquiry: Path,
    mermaid_australia: Path,
) -> dict:
    """One demonstration spot. Checksums come from the stored provenance files."""
    provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
    checksums = {item["name"]: item["sha256"] for item in provenance["files"]}
    unknown_u = uncertainty_value("UNKNOWN")
    model_u = uncertainty_value("NOT_APPLICABLE")
    items = []
    for dataset_id in DATASETS:
        filename = f"{dataset_id}_2026-09-26.csv"
        parsed = parse_crw_griddap_csv((raw_dir / filename).read_text(encoding="utf-8"), dataset_id)[0]
        if (float(parsed.where_latitude), float(parsed.where_longitude)) != RETRIEVED_CENTER:
            raise ValueError("Stored NOAA row is not the retrieved cell.")
        basis = "BALIZA_DERIVED" if parsed.baliza_quality == "QUESTIONABLE" else UNKNOWN
        gaps = ["QUALITY_GAP"] if parsed.source_provided_quality == UNKNOWN else []
        gaps.append("PROVENANCE_GAP")
        items.append(
            make_evidence(
                evidence_id=f"noaa-{dataset_id}",
                spot_id=SPOT_ID,
                source=parsed.source,
                dataset=dataset_id,
                product=parsed.what,
                product_version=PRODUCTS[dataset_id]["version"],
                variable=PRODUCTS[dataset_id]["variable"],
                value=parsed.value,
                unit=parsed.original_unit,
                source_time=parsed.when,
                observation_time=None,
                ingestion_time=provenance["retrieval_calendar_date"],
                spatial_association=UNKNOWN,
                temporal_association=UNKNOWN,
                spatial_precision="GRID",
                temporal_precision="DAY",
                source_quality=UNKNOWN,
                baliza_quality=parsed.baliza_quality if parsed.baliza_quality in QUALITY_STATES else UNKNOWN,
                association_quality=UNKNOWN,
                quality_basis=basis,
                measurement=unknown_u,
                spatial_uncertainty=unknown_u,
                temporal_uncertainty=unknown_u,
                association_uncertainty=unknown_u,
                model_uncertainty=model_u,
                raw_file=filename,
                raw_checksum=checksums[filename],
                retrieval_timestamp=provenance["retrieval_calendar_date"],
                source_url=provenance["endpoint"],
                request_parameters=provenance["request"],
                chain=transformation_chain("PARSED"),
                gaps=gaps,
                scientific_layer="EXTERNAL_INDICATOR",
            )
        )
    allen_prov = json.loads(allen_provenance_path.read_text(encoding="utf-8"))
    allen_checksum = next(item["sha256"] for item in allen_prov["files"] if item["name"] == allen_path.name)
    items.append(
        make_evidence(
            evidence_id="allen-benthic-extract",
            spot_id=SPOT_ID,
            source="Allen Coral Atlas",
            dataset="coral-atlas:benthic_data_verbose",
            product="benthic map extract",
            product_version=None,
            variable="class_name",
            value=None,
            unit=None,
            source_time=None,
            observation_time=None,
            ingestion_time="2026-10-01T07:46:05.256Z",
            spatial_association=UNKNOWN,
            temporal_association=UNKNOWN,
            spatial_precision=UNKNOWN,
            temporal_precision=UNKNOWN,
            source_quality=UNKNOWN,
            baliza_quality=UNKNOWN,
            association_quality=UNKNOWN,
            quality_basis=UNKNOWN,
            measurement=unknown_u,
            spatial_uncertainty=unknown_u,
            temporal_uncertainty=unknown_u,
            association_uncertainty=unknown_u,
            model_uncertainty=model_u,
            raw_file=allen_path.name,
            raw_checksum=allen_checksum,
            retrieval_timestamp="2026-10-01T07:46:05.256Z",
            source_url="https://allencoralatlas.org/geoserver/ows",
            request_parameters={"geometry": "null on stored features"},
            chain=transformation_chain("PARSED"),
            gaps=["SPATIAL_GAP", "PROVENANCE_GAP"],
            scientific_layer="CONTEXT_ONLY",
        )
    )
    mermaid = real_spot_mermaid(mermaid_inquiry, mermaid_australia, {"spot_id": SPOT_ID, "geometry": {"latitude": -23.5, "longitude": 152.0}, "crs": UNKNOWN, "reference_time": UNKNOWN})
    anomalies = [item for item in items if item["product"].startswith("crw_sst_anomaly")]
    return {
        "spot_id": SPOT_ID,
        "label": "DEMONSTRATION / RESEARCH TEST SPOT",
        "evidence": items,
        "unretrieved_noaa_cells": [
            {"latitude": lat, "longitude": lon, "value": UNKNOWN, "gap": "DATA_GAP"}
            for lat, lon in CANDIDATE_CENTERS
            if (lat, lon) != RETRIEVED_CENTER
        ],
        "gaps": [
            {"kind": "DATA_GAP", "detail": "Three documented NOAA cell centers were not retrieved."},
            {"kind": "SOURCE_GAP", "detail": "EMODnet depth was not retrieved. The European DTM does not cover this cell."},
            {"kind": "SPATIAL_GAP", "detail": "The stored Allen features have no geometry, so no polygon was associated."},
            {"kind": "TEMPORAL_GAP", "detail": "The spot has no reference time. NOAA grid time was not used as one."},
            {"kind": "GROUND_TRUTH_GAP", "detail": "No field observation was associated with this spot."},
            {"kind": "QUALITY_GAP", "detail": "NOAA rows have no source quality flag."},
            {"kind": "LICENSE_ACCESS_GAP", "detail": "MERMAID /sites/ returned 401. Summary access is not site verification."},
            {"kind": "PROVENANCE_GAP", "detail": "NOAA retrieval is a calendar date. MERMAID raw bodies were not stored."},
        ],
        "source_conflict": {
            "dimension": "SST anomaly on the retrieved cell",
            "status": classify_pair(anomalies[0], anomalies[1]),
            "resolved": False,
        },
        "complementary_evidence": {
            "pair": "NOAA degree heating week and MERMAID bleaching",
            "status": "COMPLEMENTARY_EVIDENCE",
            "reason": "They are different variables. No MERMAID bleaching value was associated.",
        },
        "mermaid": {
            "official_access": "PARTIAL",
            "sample_event_access": "AVAILABLE",
            "spatial_site_access": "PARTIAL",
            "spatial_compatibility": UNKNOWN,
            "temporal_compatibility": UNKNOWN,
            "summary_sample_event_count": mermaid["summary_sample_event_count"],
            "usable_spot_observations": 0,
            "count_is_not_usable_observations": True,
            "status": mermaid["mermaid_status"],
        },
        "local_estimate": "NONE",
        "downscaling": NOT_AUTHORIZED,
        "alerts": [],
    }


def render_evidence(bundle: dict) -> str:
    sst = next(item for item in bundle["evidence"] if item["product"] == "crw_coraltemp_sst")
    lines = [
        "BALIZA EVIDENCE CHAIN",
        f"Spot: {bundle['spot_id']}",
        "",
        "NOAA CoralTemp SST:",
        f"{sst['value']} {sst['unit']}. Grid time {sst['source_time']}.",
        "This value belongs to the retrieved cell, not to a local measurement.",
        "Four documented cell centers are listed. Intersection is not confirmed, because the CRS is unknown.",
        "Three cell values were not retrieved and stay unknown.",
        f"The retrieved file is {sst['provenance']['raw_file_reference']}.",
        f"SHA-256 {sst['provenance']['raw_checksum']}.",
        "No local temperature was calculated.",
        "",
        "MERMAID:",
        "Public sample-event summaries were read.",
        f"The reported summary count is {bundle['mermaid']['summary_sample_event_count']}.",
        "That count is not a count of usable observations of this spot.",
        "Spatial and temporal compatibility stay UNKNOWN. This is not a statement that MERMAID has no data.",
        "",
        "Freshness status: UNKNOWN. No freshness policy is authorized.",
        "Uncertainty is unknown, not zero.",
        "Downscaling is not authorized.",
    ]
    return "\n".join(lines)
