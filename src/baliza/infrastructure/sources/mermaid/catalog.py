"""MERMAID catalog from verified unauthenticated API reads only."""

from __future__ import annotations

SOURCE = "MERMAID"
SOURCE_LABEL = "MERMAID"
ENDPOINT = "https://api.datamermaid.org/v1/"
PARSER_VERSION = "phase710-mermaid-1"
NORMALIZATION_VERSION = "phase710-normalize-1"

DEMO_SPOT = {
    "spot_id": "DEMO-CRW-ORIG24-HERITAGE-POINT",
    "label": "DEMONSTRATION / RESEARCH TEST SPOT",
    "geometry_type": "POINT",
    "latitude": -23.5,
    "longitude": 152.0,
    "crs": "UNKNOWN",
    "spatial_precision": "UNKNOWN",
    "reference_time": "UNKNOWN",
}

AVAILABLE_DATASETS: dict[str, dict[str, str]] = {
    "summarysampleevents": {
        "endpoint": "summarysampleevents/",
        "status": "AVAILABLE",
        "access": "unauthenticated summary",
        "epistemic": "MEASURED",
        "note": "Site/date aggregates when policy allows. Not observation-level rows.",
        "scientific_role": "field_ecological_summary",
    },
}

PARTIAL_OR_BLOCKED: dict[str, dict[str, str]] = {
    "sites": {
        "endpoint": "sites/",
        "status": "ACCESS_GAP",
        "http_status": "401",
        "reason": "Unauthenticated client received HTTP 401.",
    },
    "projects": {
        "endpoint": "projects/",
        "status": "PARTIAL",
        "http_status": "200",
        "reason": "Endpoint answered with count 0 for this client.",
    },
    "summarysites": {
        "endpoint": "summarysites/",
        "status": "ACCESS_GAP",
        "http_status": "404",
        "reason": "Path did not resolve on the verified call.",
    },
    "beltfish_observations": {
        "status": "NOT_AVAILABLE",
        "reason": "Observation views require project membership or public policy; not retrieved.",
    },
    "benthic_observations": {
        "status": "NOT_AVAILABLE",
        "reason": "Observation-level benthic rows were not retrieved.",
    },
    "bleaching_observations": {
        "status": "NOT_AVAILABLE",
        "reason": "Observation-level bleaching rows were not retrieved. Summary protocol names only.",
    },
    "habitat_complexity_observations": {
        "status": "NOT_AVAILABLE",
        "reason": "Observation-level habitat complexity rows were not retrieved.",
    },
}

PROTOCOL_TO_DATASET = {
    "colonies_bleached": "BLEACHING",
    "quadrat_benthic_percent": "BENTHIC",
    "benthicpit": "BENTHIC",
    "benthiclits": "BENTHIC",
    "beltfish": "FISH_BELT",
    "habitatcomplexity": "HABITAT_COMPLEXITY",
}

BLEACHING_CATEGORIES = (
    "normal",
    "pale",
    "0-20%",
    "21-50%",
    "51-80%",
    "81-100%",
    "recently_dead",
)

SEARCH_STRATEGY = {
    "query_area": "Unauthenticated Australia summary page and Heron Island name filters. Not a geodesic bbox search.",
    "query_time_window": "Not constrained for the complete Australia page. Grid-day filter returned HTTP 502.",
    "spatial_tolerance": "NOT_DEFINED",
    "temporal_window": "NOT_DEFINED",
    "filters": ["country_name=Australia", "site_name=Heron Island", "site_name=Heron"],
    "dataset": "summarysampleevents",
    "retrieval_time": "2026-10-01",
}
