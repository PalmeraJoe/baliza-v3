"""Build a characterization report. EXPERIMENTAL / PHASE 7.5."""

from __future__ import annotations

from baliza.experimental.phase75.crw_csv import CanonicalRecord


def grid_cell_report(records: list[CanonicalRecord]) -> dict[str, object]:
    if not records:
        raise ValueError("No records. An empty source is not filled.")
    return {
        "label": "DEMONSTRATION / RESEARCH TEST AREA",
        "subject": "CRW grid cell, not a resort and not a BALIZA spot",
        "estimated": "NONE",
        "downscaling": "NOT AUTHORIZED",
        "spatial_relation": "UNKNOWN",
        "records": [
            {
                "what": record.what,
                "value": record.value,
                "original_unit": record.original_unit,
                "when": record.when,
                "where_latitude": record.where_latitude,
                "where_longitude": record.where_longitude,
                "transformation_type": record.transformation_type,
                "spatial_precision": record.spatial_precision,
                "baliza_quality": record.baliza_quality,
                "spatial_relation": record.spatial_relation,
            }
            for record in records
        ],
    }
