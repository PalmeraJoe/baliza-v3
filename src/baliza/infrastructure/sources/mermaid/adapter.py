"""MERMAID adapter over stored official summary responses.

Does not invent matches. Does not call authenticated observation endpoints.
Raw response bodies were intentionally not stored; hashes and redacted rows remain.
"""

from __future__ import annotations

import json
from pathlib import Path

from baliza.experimental.phase763.mermaid import keep_bleaching_category, redact
from baliza.infrastructure.sources.mermaid.catalog import (
    AVAILABLE_DATASETS,
    ENDPOINT,
    NORMALIZATION_VERSION,
    PARSER_VERSION,
    PARTIAL_OR_BLOCKED,
    PROTOCOL_TO_DATASET,
    SEARCH_STRATEGY,
    SOURCE,
    SOURCE_LABEL,
)


class MermaidAdapterError(ValueError):
    """A MERMAID artifact could not be used. No substitute observation is invented."""


class MermaidAdapter:
    def discover(self, *, live: bool = False) -> dict:
        return {
            "source": SOURCE,
            "endpoint": ENDPOINT,
            "discovery_mode": "VERIFIED_CATALOG" if not live else "LIVE_NOT_RUN",
            "authentication": "Unauthenticated summary reads only. Sites require credentials.",
            "available": [
                {"dataset_id": dataset_id, **meta} for dataset_id, meta in AVAILABLE_DATASETS.items()
            ],
            "partial_or_blocked": [
                {"dataset_id": dataset_id, **meta} for dataset_id, meta in PARTIAL_OR_BLOCKED.items()
            ],
            "search_strategy": SEARCH_STRATEGY,
            "thermal_ground_truth": "NOT_AVAILABLE",
            "note": "Summary protocol names are not observation-level values.",
        }

    def load_inquiry(self, inquiry_path: Path) -> dict:
        if not inquiry_path.is_file():
            raise MermaidAdapterError("MERMAID inquiry file is missing.")
        return json.loads(inquiry_path.read_text(encoding="utf-8"))

    def load_australia_summary(self, path: Path) -> dict:
        if not path.is_file():
            raise MermaidAdapterError("MERMAID Australia summary file is missing.")
        payload = json.loads(path.read_text(encoding="utf-8"))
        if payload.get("http_status") != 200:
            raise MermaidAdapterError("Australia summary was not a successful retrieval.")
        records = [redact(row) for row in payload.get("records") or []]
        return {
            "url": payload["url"],
            "http_status": payload["http_status"],
            "http_date": payload["http_date"],
            "response_sha256": payload["response_sha256"],
            "raw_body_stored": payload.get("raw_body_stored", False),
            "count": payload["count"],
            "returned": payload["returned"],
            "next": payload.get("next"),
            "records": records,
        }

    def validate_summary(self, summary: dict) -> dict:
        if summary["returned"] != len(summary["records"]):
            raise MermaidAdapterError("Returned count does not match stored records.")
        if summary["next"] is not None and summary["count"] != summary["returned"]:
            raise MermaidAdapterError("Incomplete Australia page cannot be treated as complete.")
        return {
            "ok": True,
            "page_complete": summary["next"] is None and summary["count"] == summary["returned"],
            "raw_body_stored": summary["raw_body_stored"],
        }

    def normalize_summary_record(self, record: dict, *, retrieval_timestamp: str, response_sha256: str) -> dict:
        protocols = list(record.get("protocol_names") or [])
        dataset_types = sorted({PROTOCOL_TO_DATASET.get(name, "UNKNOWN") for name in protocols})
        return {
            "source": SOURCE,
            "source_label": SOURCE_LABEL,
            "dataset": "summarysampleevents",
            "dataset_types": dataset_types,
            "survey_methods": protocols,
            "sample_unit": "UNKNOWN",
            "observation_type": "SUMMARY_SAMPLE_EVENT",
            "sample_event_id": record.get("sample_event_id", "UNKNOWN"),
            "site_id": record.get("site_id", "UNKNOWN"),
            "project_id": record.get("project_id", "UNKNOWN"),
            "site_name": record.get("site_name", "UNKNOWN"),
            "country_name": record.get("country_name", "UNKNOWN"),
            "latitude": record.get("latitude"),
            "longitude": record.get("longitude"),
            "survey_date": record.get("sample_date", "UNKNOWN"),
            "observation_time": "UNKNOWN",
            "depth_avg": record.get("depth_avg", "UNKNOWN"),
            "depth_unit": "m" if record.get("depth_avg") is not None else "UNKNOWN",
            "depth_method": "UNKNOWN",
            "source_crs": "UNKNOWN",
            "processing_crs": "UNKNOWN",
            "scientific_layer": "MEASURED",
            "epistemic_label": "FACT",
            "scientific_role": "field_ecological_summary",
            "measured_ecological_observation": True,
            "measured_temperature": False,
            "thermal_ground_truth": False,
            "validates_crw": False,
            "causal_with_crw": False,
            "bleaching": keep_bleaching_category(None),
            "bleaching_categories_present": False,
            "recently_dead_is_mortality_percent": False,
            "estimated": "NONE",
            "quality": {
                "source_quality": "UNKNOWN",
                "baliza_quality": "UNKNOWN",
                "association_quality": "UNKNOWN",
            },
            "uncertainty": {
                "measurement": "UNKNOWN",
                "spatial": "UNKNOWN",
                "temporal": "UNKNOWN",
                "association": "UNKNOWN",
                "methodological": "UNKNOWN",
            },
            "freshness": {
                "retrieval_freshness": retrieval_timestamp,
                "observation_recency": record.get("sample_date", "UNKNOWN"),
                "note": "Retrieval date is not the survey date.",
            },
            "provenance": {
                "source": SOURCE,
                "endpoint": ENDPOINT + "summarysampleevents/",
                "dataset": "summarysampleevents",
                "retrieval_timestamp": retrieval_timestamp,
                "response_sha256": response_sha256,
                "raw_body_stored": False,
                "parser_version": PARSER_VERSION,
                "normalization_version": NORMALIZATION_VERSION,
                "transformation_chain": ["RAW_HASH", "REDACT", "NORMALIZE"],
                "status": "PARTIAL",
            },
            "parser_version": PARSER_VERSION,
            "normalization_version": NORMALIZATION_VERSION,
        }

    def emit_inquiry_provenance(self, inquiry: dict) -> dict:
        return {
            "source": SOURCE,
            "artifact": "mermaid-inquiry.json",
            "spot_id": inquiry.get("spot_id"),
            "queries": inquiry.get("queries", []),
            "mermaid_status": inquiry.get("mermaid_status"),
            "spatial_search_completed": inquiry.get("spatial_search_completed", False),
            "any_coordinate_equals_spot": inquiry.get("any_coordinate_equals_spot", False),
        }
