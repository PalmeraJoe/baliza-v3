"""EXPERIMENTAL / PHASE 7.6.3. MERMAID association checks.

Not on the operational critical path. A nearby field record is not a local
measurement, and it does not confirm a NOAA value. Degrees are not metres.
"""

from __future__ import annotations

import json
from pathlib import Path

UNKNOWN = "UNKNOWN"
NOT_AUTHORIZED = "NOT_AUTHORIZED"
ACCESS_GAP = "ACCESS_GAP"
NO_COMPATIBLE_RECORD = "NO_COMPATIBLE_RECORD"
MATCH_FOUND = "MATCH_FOUND"

PEOPLE_FIELDS = ("project_admins", "observers", "contact_link", "site_notes", "project_notes", "management_notes")


def redact(row: dict) -> dict:
    """Drop person and note fields. Public coordinates and dates can remain."""
    return {key: value for key, value in row.items() if key not in PEOPLE_FIELDS}


def keep_bleaching_category(category: str | None) -> dict:
    """Keep MERMAID's category. Recently dead is not a mortality percentage."""
    return {
        "bleaching_category": UNKNOWN if category is None else category,
        "mortality_percentage": "NOT_EQUIVALENT",
        "converted": False,
    }


def associate_record(
    spot: dict,
    record: dict,
    *,
    label: str,
    distance_m: float | None = None,
    source_crs: str | None = None,
) -> dict:
    """One MERMAID row against one spot. Synthetic rows must say so in `label`."""
    latitude = record.get("latitude")
    longitude = record.get("longitude")
    survey_date = record.get("survey_date") or record.get("sample_date")
    missing_coordinates = latitude is None or longitude is None
    same_place = (
        not missing_coordinates
        and latitude == spot["geometry"]["latitude"]
        and longitude == spot["geometry"]["longitude"]
        and source_crs not in (None, "", UNKNOWN)
        and source_crs == spot["crs"]
    )
    if same_place or distance_m == 0:
        point_relation = "EXACT"
        local_to_spot = True
    elif distance_m is not None and distance_m > 0 and not missing_coordinates:
        point_relation = "NEAR"
        local_to_spot = False
    else:
        point_relation = UNKNOWN
        local_to_spot = False
    temporal = UNKNOWN
    spot_time = spot.get("reference_time")
    if survey_date and spot_time and spot_time != UNKNOWN:
        temporal = "EXACT_TIME" if survey_date == spot_time else "SAME_DAY" if survey_date[:10] == spot_time[:10] else UNKNOWN
    depth = record.get("depth")
    if depth is None:
        depth = record.get("depth_avg")
    return {
        "label": label,
        "spot_id": spot["spot_id"],
        "source": "MERMAID",
        "record_id": record.get("sample_event_id") or record.get("record_id") or UNKNOWN,
        "site_id": record.get("site_id", UNKNOWN),
        "project_id": record.get("project_id", UNKNOWN),
        "spatial": {
            "association_type": point_relation,
            "distance_m": UNKNOWN if distance_m is None else distance_m,
            "spatial_precision": UNKNOWN if point_relation == UNKNOWN else record.get("spatial_precision", UNKNOWN),
            "source_crs": UNKNOWN if not source_crs else source_crs,
            "spot_crs": spot["crs"],
            "association_method": "Supplied distance or identical coordinates. Degrees are not converted to metres.",
        },
        "temporal": {
            "association_type": temporal,
            "observation_time": UNKNOWN,
            "survey_date": UNKNOWN if not survey_date else survey_date,
            "spot_reference_time": spot.get("reference_time", UNKNOWN),
            "policy": "NOT_DEFINED",
        },
        "spatially_associated": point_relation in {"EXACT", "WITHIN", "NEAR"},
        "temporally_associated": True if temporal in {"EXACT_TIME", "SAME_DAY"} else UNKNOWN,
        "contemporary_evidence": temporal in {"EXACT_TIME", "SAME_DAY"} and point_relation == "EXACT",
        "local_to_spot": local_to_spot,
        "scientific": {
            "layer": "MEASURED" if point_relation == "EXACT" else "EXTERNAL_INDICATOR",
            "epistemic_label": "FACT",
        },
        "variables": _variables(record),
        "bleaching": keep_bleaching_category(record.get("bleaching_category")),
        "depth": UNKNOWN if depth is None else depth,
        "depth_unit": UNKNOWN if depth is None or record.get("depth_unit") is None else record.get("depth_unit"),
        "quality": {"source_quality": UNKNOWN, "association_quality": UNKNOWN},
        "provenance": {
            "source": "MERMAID",
            "dataset": record.get("dataset", UNKNOWN),
            "retrieval_timestamp": record.get("retrieval_timestamp", UNKNOWN),
            "raw_checksum": record.get("raw_checksum", UNKNOWN),
            "status": "CLOSED" if record.get("raw_checksum") else "PARTIAL",
        },
        "model_validated": False,
        "local_estimate": NOT_AUTHORIZED,
        "alert": None,
        "gaps": ["COORDINATE GAP"] if missing_coordinates else [],
    }


def _variables(record: dict) -> dict:
    kept = {}
    for key in ("site_name", "country_name", "method", "transect", "habitat_complexity"):
        if key in record and record[key] is not None:
            kept[key] = record[key]
    return kept


def classify_retrieval(*, http_status: int | None, spatial_search_completed: bool, compatible_count: int) -> str:
    """An empty authorized search is not an access failure. A returned row is not yet a match."""
    if http_status is None or http_status >= 400 or not spatial_search_completed:
        return ACCESS_GAP
    if compatible_count == 0:
        return NO_COMPATIBLE_RECORD
    return MATCH_FOUND


def deduplicate(records: list[dict]) -> dict:
    seen: dict[str, dict] = {}
    copies = 0
    for record in records:
        key = str(record.get("sample_event_id") or record.get("record_id") or id(record))
        if key in seen:
            copies += 1
            continue
        seen[key] = record
    return {"records": list(seen.values()), "duplicate_count": copies}


def real_spot_mermaid(inquiry_path: Path, australia_path: Path, spot: dict) -> dict:
    """The heritage spot against the MERMAID reads already stored."""
    inquiry = json.loads(inquiry_path.read_text(encoding="utf-8"))
    australia = json.loads(australia_path.read_text(encoding="utf-8"))
    unique = deduplicate(australia["records"])
    identical = [
        row
        for row in unique["records"]
        if row.get("latitude") == spot["geometry"]["latitude"] and row.get("longitude") == spot["geometry"]["longitude"]
    ]
    return {
        "spot_id": spot["spot_id"],
        "mermaid_status": ACCESS_GAP,
        "mermaid_records_found": UNKNOWN,
        "australia_summary_count": australia["count"],
        "australia_summary_returned": australia["returned"],
        "australia_page_complete": australia["next"] is None and australia["count"] == australia["returned"],
        "identical_coordinates_in_australia_summary": len(identical),
        "mermaid_candidates": [],
        "mermaid_spatial_associations": [],
        "mermaid_temporal_associations": [],
        "mermaid_ground_truth_status": "UNVERIFIED",
        "mermaid_data_gap": ACCESS_GAP,
        "reason": (
            "The unauthenticated Australia summary page was complete and contains no identical coordinate. "
            "That page is not a proximity search. The spot CRS and the MERMAID CRS are unknown, so no row "
            "was promoted to a spatial association. /sites/ is unauthorized. A global bbox was not available."
        ),
        "name_query_heron_island_count": _query_count(inquiry, "site_name_heron_island"),
        "sites_http_status": _query_status(inquiry, "sites"),
        "summary_sample_event_count": _query_count(inquiry, "summary_sample_events_page"),
        "mermaid_provenance": {
            "status": "PARTIAL",
            "raw_body_stored": False,
            "australia_response_sha256": australia["response_sha256"],
            "retrieval_timestamp": australia["http_date"],
            "dataset": "https://api.datamermaid.org/v1/summarysampleevents/",
        },
        "duplicate_count": unique["duplicate_count"],
        "model_validated": False,
        "local_estimate": NOT_AUTHORIZED,
        "alerts": [],
        "complementary_evidence": "NOT_ASSESSED",
    }


def render_real(result: dict) -> str:
    return "\n".join(
        [
            "MERMAID",
            f"Spot: {result['spot_id']}",
            "Status: ACCESS GAP",
            (
                f"The public summary sample-event list reports {result['summary_sample_event_count']} events. "
                f"The unauthenticated Australia filter returned {result['australia_summary_count']} events, "
                "and that page was complete."
            ),
            "None of those coordinates is this spot's published point.",
            "No spatial association was created. Both CRS values are unknown, and the Australia filter is not a proximity search.",
            f"The site name Heron Island returned count {result['name_query_heron_island_count']}.",
            f"The sites endpoint returned HTTP {result['sites_http_status']}.",
            "This is an access gap for this spot. It is not a statement that MERMAID has no data.",
            "No local measurement, estimate, or alert was created.",
        ]
    )


def _query_count(inquiry: dict, name: str) -> int | None:
    for query in inquiry["queries"]:
        if query["name"] == name:
            return query["count"]
    return None


def _query_status(inquiry: dict, name: str) -> int | None:
    for query in inquiry["queries"]:
        if query["name"] == name:
            return query["http_status"]
    return None
