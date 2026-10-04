import json
from pathlib import Path

import pytest

from baliza.experimental.phase762.engine import temporal_association
from baliza.experimental.phase763.mermaid import associate_record
from baliza.experimental.phase764.evidence import (
    build_real_evidence,
    classify_pair,
    evidence_completeness,
    freshness,
    make_evidence,
    render_evidence,
    traceability,
    transformation_chain,
    uncertainty_value,
)

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "phase75" / "raw"
PROVENANCE = ROOT / "data" / "phase75" / "provenance.json"
ALLEN = ROOT / "data" / "phase75" / "allen" / "raw" / "benthic_bbox.json"
ALLEN_PROVENANCE = ROOT / "data" / "phase75" / "allen" / "provenance.json"
INQUIRY = ROOT / "data" / "phase763" / "mermaid-inquiry.json"
AUSTRALIA = ROOT / "data" / "phase763" / "mermaid-australia-summary.json"


def _item(**overrides) -> dict:
    base = dict(
        evidence_id="t",
        spot_id="SPOT",
        source="NOAA Coral Reef Watch",
        dataset="dataset",
        product="product",
        product_version="v",
        variable="variable",
        value="1",
        unit="degree_C",
        source_time="2026-09-26T12:00:00Z",
        observation_time=None,
        ingestion_time="2026-10-01",
        spatial_association="UNKNOWN",
        temporal_association="UNKNOWN",
        spatial_precision="GRID",
        temporal_precision="DAY",
        source_quality="UNKNOWN",
        baliza_quality="UNKNOWN",
        association_quality="UNKNOWN",
        quality_basis="UNKNOWN",
        measurement=uncertainty_value("UNKNOWN"),
        spatial_uncertainty=uncertainty_value("UNKNOWN"),
        temporal_uncertainty=uncertainty_value("UNKNOWN"),
        association_uncertainty=uncertainty_value("UNKNOWN"),
        model_uncertainty=uncertainty_value("NOT_APPLICABLE"),
        raw_file="file.csv",
        raw_checksum="abc",
        retrieval_timestamp="2026-10-01",
        source_url="https://example.test",
        request_parameters={},
        chain=transformation_chain("PARSED"),
        gaps=[],
        scientific_layer="EXTERNAL_INDICATOR",
    )
    base.update(overrides)
    return make_evidence(**base)


def _real() -> dict:
    return build_real_evidence(RAW, PROVENANCE, ALLEN, ALLEN_PROVENANCE, INQUIRY, AUSTRALIA)


def test_checksum_present_and_missing_and_broken() -> None:
    complete_parts = _item()
    assert complete_parts["provenance"]["raw_checksum"] == "abc"
    assert complete_parts["provenance"]["integrity"] == "SHA-256"
    missing_checksum = _item(raw_checksum=None)
    assert missing_checksum["traceability"] == "PARTIAL"
    assert "PROVENANCE_GAP" not in missing_checksum["gaps"] or missing_checksum["provenance"]["raw_checksum"] == "UNKNOWN"
    missing_version = _item(product_version=None)
    assert missing_version["product_version"] == "UNKNOWN"
    assert missing_version["traceability"] == "PARTIAL"
    broken = _item(source="UNKNOWN", raw_file=None, raw_checksum=None, product_version=None)
    assert broken["traceability"] == "BROKEN"
    assert broken["usable_in_later_indicator"] is False


def test_quality_layers_stay_separate() -> None:
    item = _item(source_quality="GOOD", baliza_quality="QUESTIONABLE", association_quality="UNKNOWN", quality_basis="SOURCE_PROVIDED")
    assert item["quality"]["source"] == "GOOD"
    assert item["quality"]["baliza"] == "QUESTIONABLE"
    assert item["quality"]["association"] == "UNKNOWN"
    assert item["quality"]["quality_basis"] == "SOURCE_PROVIDED"


def test_freshness_does_not_invent_a_class() -> None:
    present = freshness(reference_time=None, observation_time="2026-09-26T12:00:00Z", ingestion_time="2026-10-01")
    assert present["observation_time"] == "2026-09-26T12:00:00Z"
    assert present["ingestion_time"] == "2026-10-01"
    assert present["ingestion_used_as_observation"] is False
    absent = freshness(reference_time=None, observation_time=None, ingestion_time="2026-10-01")
    assert absent["observation_time"] == "UNKNOWN"
    assert absent["freshness_status"] == "UNKNOWN"
    assert absent["freshness_method"] == "NOT_DEFINED"
    with pytest.raises(ValueError):
        freshness(reference_time="2026-10-01", observation_time="2026-09-26", ingestion_time=None, policy_version="unapproved")


def test_uncertainty_unknown_is_not_zero() -> None:
    unknown = uncertainty_value("UNKNOWN")
    numeric = uncertainty_value("KNOWN_NUMERIC", 0.2)
    zero = uncertainty_value("KNOWN_NUMERIC", 0)
    qualitative = uncertainty_value("QUALITATIVE")
    assert unknown["value"] == "UNKNOWN"
    assert unknown["value"] != 0
    assert numeric["kind"] == "KNOWN_NUMERIC"
    assert zero["kind"] == "KNOWN_NUMERIC"
    assert zero["value"] == 0
    assert qualitative["kind"] == "QUALITATIVE"
    assert qualitative["value"] != 0


def test_real_noaa_chain_keeps_one_cell_and_three_gaps() -> None:
    bundle = _real()
    sst = next(item for item in bundle["evidence"] if item["product"] == "crw_coraltemp_sst")
    hotspot = next(item for item in bundle["evidence"] if item["product"] == "crw_hotspot")
    assert sst["value"] == "22.72"
    assert sst["scientific_layer"] == "EXTERNAL_INDICATOR"
    assert sst["spatial_association"] == "UNKNOWN"
    assert sst["spatial_precision"] == "GRID"
    assert sst["observation_time"] == "UNKNOWN"
    assert sst["source_time"] == "2026-09-26T12:00:00Z"
    assert sst["ingestion_time"] == "2026-10-01"
    assert sst["provenance"]["raw_checksum"]
    assert sst["transformation_chain"] == ["PARSED"]
    assert "DOWNSCALED" not in sst["transformation_chain"]
    assert len(bundle["unretrieved_noaa_cells"]) == 3
    assert hotspot["quality"]["baliza"] == "QUESTIONABLE"
    assert hotspot["quality"]["source"] == "UNKNOWN"
    assert hotspot["quality"]["association"] == "UNKNOWN"
    assert hotspot["uncertainty"]["association"]["value"] != 0
    text = render_evidence(bundle)
    assert "not to a local measurement" in text
    assert "Intersection is not confirmed" in text
    provenance = json.loads(PROVENANCE.read_text(encoding="utf-8"))
    checksums = {item["name"]: item["sha256"] for item in provenance["files"]}
    assert checksums[sst["provenance"]["raw_file_reference"]] == sst["provenance"]["raw_checksum"]


def test_time_relations_and_gaps_and_conflicts() -> None:
    exact = temporal_association(
        source_kind="daily",
        observation_time="2026-09-26T12:00:00Z",
        spot_reference_time="2026-09-26T12:00:00Z",
    )
    same_day = temporal_association(
        source_kind="daily",
        observation_time="2026-09-26T00:00:00Z",
        spot_reference_time="2026-09-26T12:00:00Z",
    )
    mismatch = temporal_association(
        source_kind="daily",
        observation_time="2026-09-20T12:00:00Z",
        spot_reference_time="2026-09-26T12:00:00Z",
    )
    missing = temporal_association(source_kind="daily")
    assert exact["association_type"] == "EXACT_TIME"
    assert same_day["association_type"] == "SAME_DAY"
    assert mismatch["association_type"] == "UNKNOWN"
    assert missing["association_type"] == "UNKNOWN"
    bundle = _real()
    kinds = {gap["kind"] for gap in bundle["gaps"]}
    assert {"SPATIAL_GAP", "TEMPORAL_GAP", "GROUND_TRUTH_GAP", "PROVENANCE_GAP", "LICENSE_ACCESS_GAP", "SOURCE_GAP"} <= kinds
    assert bundle["source_conflict"]["status"] == "SOURCE_CONFLICT"
    assert bundle["source_conflict"]["resolved"] is False
    assert bundle["complementary_evidence"]["status"] == "COMPLEMENTARY_EVIDENCE"
    assert bundle["mermaid"]["summary_sample_event_count"] == 16557
    assert bundle["mermaid"]["usable_spot_observations"] == 0
    assert bundle["mermaid"]["spatial_compatibility"] == "UNKNOWN"
    assert bundle["mermaid"]["count_is_not_usable_observations"] is True
    allen = next(item for item in bundle["evidence"] if item["source"] == "Allen Coral Atlas")
    assert allen["value"] == "UNKNOWN"
    assert "SPATIAL_GAP" in allen["gaps"]
    assert allen["scientific_layer"] == "CONTEXT_ONLY"
    near = associate_record(
        {"spot_id": "SPOT", "geometry": {"latitude": 0, "longitude": 0}, "crs": "TEST-SAME-AXIS", "reference_time": "UNKNOWN"},
        {"record_id": "synthetic-near", "latitude": 1, "longitude": 1, "survey_date": "2026-09-26"},
        label="TEST / SYNTHETIC / NON-SCIENTIFIC",
        distance_m=10,
        source_crs="TEST-SAME-AXIS",
    )
    assert near["spatial"]["association_type"] == "NEAR"
    assert near["local_to_spot"] is False
    assert near["spatial"]["distance_m"] == 10
    with pytest.raises(ValueError):
        transformation_chain("INTERPOLATED")
    assert evidence_completeness("COMPLETE", []) == "COMPLETE"
    assert evidence_completeness("PARTIAL", ["DATA_GAP"]) == "PARTIAL"
    left = {"variable": "sst", "value": "1"}
    right = {"variable": "bleaching", "value": "pale"}
    assert classify_pair(left, right) == "COMPLEMENTARY_EVIDENCE"
    assert "threshold" not in json.dumps(bundle).lower()
    assert bundle["alerts"] == []
    assert bundle["downscaling"] == "NOT_AUTHORIZED"
