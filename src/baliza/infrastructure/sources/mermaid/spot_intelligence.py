"""MERMAID Spot Intelligence from stored official summary artifacts.

DEMO Spot coordinates are never changed. Absence of a match is not no bleaching.
"""

from __future__ import annotations

from pathlib import Path

from baliza.infrastructure.sources.mermaid.adapter import MermaidAdapter
from baliza.infrastructure.sources.mermaid.catalog import DEMO_SPOT, SEARCH_STRATEGY, SOURCE


def build_mermaid_spot_intelligence(
    inquiry_path: Path,
    australia_path: Path,
    *,
    spot_id: str | None = None,
) -> dict:
    adapter = MermaidAdapter()
    discovery = adapter.discover(live=False)
    inquiry = adapter.load_inquiry(inquiry_path)
    summary = adapter.load_australia_summary(australia_path)
    validation = adapter.validate_summary(summary)
    if spot_id not in (None, DEMO_SPOT["spot_id"]):
        raise KeyError(spot_id)
    spot = DEMO_SPOT
    identical = [
        row
        for row in summary["records"]
        if row.get("latitude") == spot["latitude"] and row.get("longitude") == spot["longitude"]
    ]
    normalized = [
        adapter.normalize_summary_record(
            row,
            retrieval_timestamp=summary["http_date"],
            response_sha256=summary["response_sha256"],
        )
        for row in summary["records"]
    ]
    protocol_presence = {
        "BLEACHING": any("BLEACHING" in row["dataset_types"] for row in normalized),
        "BENTHIC": any("BENTHIC" in row["dataset_types"] for row in normalized),
        "FISH_BELT": any("FISH_BELT" in row["dataset_types"] for row in normalized),
        "HABITAT_COMPLEXITY": any("HABITAT_COMPLEXITY" in row["dataset_types"] for row in normalized),
    }
    heron = next((q for q in inquiry["queries"] if q["name"] == "site_name_heron_island"), {})
    sites = next((q for q in inquiry["queries"] if q["name"] == "sites"), {})
    return {
        "spot": spot,
        "source": SOURCE,
        "discovery": discovery,
        "search_strategy": SEARCH_STRATEGY,
        "demo_spot_coordinates_unchanged": True,
        "mermaid_access": "PARTIAL",
        "mermaid_real_data": "PARTIAL",
        "mermaid_spatial_compatibility": "UNKNOWN",
        "mermaid_temporal_compatibility": "UNKNOWN",
        "mermaid_ecological_observation": "PARTIAL",
        "mermaid_thermal_ground_truth": "NOT_AVAILABLE",
        "ground_truth_availability": "UNVERIFIED",
        "demo_spot_match": "NO_MATCH",
        "identical_coordinates": len(identical),
        "usable_spot_observations": 0,
        "field_observations_for_spot": [],
        "external_indicators": [],
        "measured": [],
        "estimated": "NONE",
        "downscaling": "NOT_AUTHORIZED",
        "ml_implementation": "NOT_AUTHORIZED",
        "local_estimation": "NOT_AUTHORIZED",
        "alerts": [],
        "australia_summary": {
            "count": summary["count"],
            "returned": summary["returned"],
            "page_complete": validation["page_complete"],
            "raw_body_stored": summary["raw_body_stored"],
            "response_sha256": summary["response_sha256"],
            "retrieval_timestamp": summary["http_date"],
            "protocol_presence_in_page": protocol_presence,
            "note": "These records exist in Australia. They are not observations of this DEMO Spot.",
        },
        "normalized_records_available_elsewhere": len(normalized),
        "spatial_association": {
            "association_type": "UNKNOWN",
            "comparison_performed": False,
            "distance_m": "UNKNOWN",
            "near_promoted_to_measured": False,
            "reason": (
                "No identical coordinate. CRS is unknown. The Australia filter is not a proximity search. "
                "NEAR was not assigned."
            ),
        },
        "temporal_association": {
            "association_type": "UNKNOWN",
            "spot_reference_time": spot["reference_time"],
            "policy": "NOT_DEFINED",
            "reason": "The Spot has no reference time, and no matched survey date was selected.",
        },
        "quality": {"source_quality": "UNKNOWN", "baliza_quality": "UNKNOWN", "association_quality": "UNKNOWN"},
        "freshness": {
            "retrieval_freshness": summary["http_date"],
            "observation_recency": "UNKNOWN",
            "note": "A recent retrieval does not make an old survey current.",
        },
        "uncertainty": {
            "measurement": "UNKNOWN",
            "spatial": "UNKNOWN",
            "temporal": "UNKNOWN",
            "association": "UNKNOWN",
            "methodological": "UNKNOWN",
        },
        "evidence": [],
        "evidence_completeness": "PARTIAL",
        "data_gaps": [
            {
                "kind": "SPATIAL_GAP",
                "detail": "No MERMAID coordinate equals the DEMO Spot. Spatial compatibility stays UNKNOWN.",
            },
            {
                "kind": "TEMPORAL_GAP",
                "detail": "No temporally associated MERMAID row was selected for the DEMO Spot.",
            },
            {
                "kind": "LICENSE_ACCESS_GAP",
                "detail": f"sites endpoint HTTP {sites.get('http_status')}. Observation-level rows were not read.",
            },
            {
                "kind": "GROUND_TRUTH_GAP",
                "detail": "No compatible field observation for this Spot. Absence is not 'healthy' or 'no bleaching'.",
            },
            {
                "kind": "PROVENANCE_GAP",
                "detail": "Summary response bodies were not stored; only SHA-256 and redacted fields remain.",
            },
            {
                "kind": "DATA_GAP",
                "detail": f"Heron Island name query count {heron.get('count')}.",
            },
        ],
        "cross_source": {
            "crw": "Independent EXTERNAL_INDICATOR. No automatic validation or causality.",
            "allen": "Independent CONTEXT_ONLY. Not fused with MERMAID.",
        },
        "baliza_alert_separation": {
            "mermaid_is_baliza_alert": False,
            "note": "MERMAID provides field evidence. It does not create a BALIZA alert.",
        },
        "inquiry_provenance": adapter.emit_inquiry_provenance(inquiry),
        "bleaching_semantics": {
            "categories_preserved": True,
            "recently_dead_is_mortality_percent": False,
            "bleaching_is_temperature": False,
            "bleaching_is_thermal_ground_truth": False,
        },
    }
