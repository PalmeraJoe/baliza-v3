import json
from pathlib import Path

from baliza.experimental.phase766.closure import build_closure

ROOT = Path(__file__).resolve().parents[1]


def test_operational_closure_accounts_for_every_remaining_gap() -> None:
    closure = build_closure(ROOT)
    assert closure["generated_at"] == "UNKNOWN"
    assert closure["closure"]["raw_data_traceability"] == "CLOSED"
    assert closure["closure"]["checksum_traceability"] == "CLOSED"
    assert closure["closure"]["source_versus_baliza_transformations"] == "CLOSED"
    sst = next(row for row in closure["datasets"] if row["dataset_id"] == "noaacrwsstDaily")
    assert sst["checksum"]["comparison"] == "MATCH"
    assert sst["product_version"] == "3.1"
    assert sst["crs"] == "UNKNOWN"
    assert sst["chain_integrity"] == "PARTIAL"
    assert "2026-09-26T12:00:00Z" in sst["temporal_extent"]
    assert "2026-10-01" in sst["retrieval_timestamp"]
    assert sst["retrieval_timestamp"] != "2026-09-26T12:00:00Z"
    xml = next(row for row in closure["datasets"] if row["dataset_id"] == "allen-wfs-capabilities-2.0.0.xml")
    assert xml["checksum"]["baliza_computed_checksum"] != "UNKNOWN"
    assert xml["checksum"]["comparison"] == "NOT_AVAILABLE"
    assert xml["checksum"]["checksum_source"] == "BALIZA_COMPUTED"
    allen = next(row for row in closure["datasets"] if row["dataset_id"] == "allen-benthic_bbox.json")
    assert allen["product_version"] == "UNKNOWN"
    assert closure["allen"]["class_attached_to_spot"] is False
    assert closure["allen"]["field_observation"] is False
    assert closure["allen"]["measured"] is False
    assert "Coral/Algae" in closure["allen"]["classes_in_extract"]
    pixels = closure["noaa_four_pixels"]
    assert pixels["pixel_count"] == 4
    assert len(pixels["pixels"]) == 4
    assert pixels["averaged_value"] is None
    assert pixels["scientific_layer"] == "EXTERNAL_INDICATOR"
    assert sum(1 for pixel in pixels["pixels"] if pixel["value"] == "UNKNOWN") == 3
    assert closure["mermaid"]["spatial_compatibility"] == "UNKNOWN"
    assert closure["mermaid"]["relabel_unknown_as_no_compatible_record"] is False
    assert closure["mermaid"]["usable_spot_observations"] == 0
    emodnet = next(row for row in closure["datasets"] if row["dataset_id"] == "emodnet-bathymetry")
    assert emodnet["chain_integrity"] == "BROKEN"
    assert emodnet["usable_in_later_indicator"] is False
    resort = next(row for row in closure["datasets"] if row["dataset_id"] == "resort")
    assert resort["base_model_training"] is False
    assert closure["artifacts"]
    assert all(item["checksum_origin"] == "BALIZA_COMPUTED" for item in closure["artifacts"])
    assert all(item["verification_timestamp"] == "UNKNOWN" for item in closure["artifacts"])
    fields = {gap["field"] for gap in closure["gaps"]}
    assert {"CRS", "observation_time", "freshness_status", "uncertainty", "raw_body"} <= fields
    text = json.dumps(closure)
    assert "overall_quality_score" not in text
    assert closure["alerts"] == []
    assert closure["thresholds"] == []
    assert closure["downscaling"] == "NOT_AUTHORIZED"
    assert "password" not in text.lower()
    assert closure["reproducibility"]["local_checksum_and_parse"] == "reproducible"
    assert closure["reproducibility"]["mermaid_response_body"] == "not reproducible"
