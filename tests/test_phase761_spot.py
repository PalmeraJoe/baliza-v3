import hashlib
import json
from pathlib import Path

from baliza.experimental.phase761.record import build_spot_record, render_spot

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "phase75" / "raw"
PROVENANCE = ROOT / "data" / "phase75" / "provenance.json"
ALLEN_RAW = ROOT / "data" / "phase75" / "allen" / "raw" / "benthic_bbox.json"


def _record() -> dict:
    return build_spot_record(RAW, PROVENANCE)


def test_measured_is_empty_and_nothing_is_estimated() -> None:
    record = _record()
    assert record["measured"] == []
    assert record["estimated"] == []
    assert record["derived_indicators"] == []
    assert record["downscaling"] == "NOT AUTHORIZED"
    assert record["alerts"] == []
    assert record["local_estimate"] == "NONE"
    text = render_spot(record)
    assert "local measurement" in text
    assert "ESTIMATED\nNone" in text
    assert "Not authorized" in text


def test_only_one_noaa_cell_has_values_and_four_are_named() -> None:
    record = _record()
    association = record["spatial_associations"][0]
    assert association["association_type"] == "UNKNOWN"
    assert association["confirmed_intersection"] is False
    assert association["pixel_count_if_axes_match"] == 4
    retrieved = [pixel for pixel in association["pixels"] if pixel["retrieved"]]
    missing = [pixel for pixel in association["pixels"] if not pixel["retrieved"]]
    assert len(retrieved) == 1
    assert len(missing) == 3
    assert all(pixel["values"] == "UNKNOWN" for pixel in missing)
    hotspot = next(item for item in record["external_indicators"] if item["product"] == "crw_hotspot")
    assert hotspot["value"] == "-4.39"
    assert hotspot["applies_to"] == "retrieved cell only"
    assert hotspot["association_type"] == "UNKNOWN"
    assert hotspot["scientific_layer"] == "EXTERNAL_INDICATOR"


def test_allen_classes_are_not_attached_to_this_point() -> None:
    record = _record()
    assert record["allen_associated"] is False
    assert "Not associated" in render_spot(record)
    assert "Coral/Algae" not in render_spot(record)
    payload = json.loads(ALLEN_RAW.read_text(encoding="utf-8"))
    assert payload["numberMatched"] == 47


def test_gaps_conflicts_and_unknown_uncertainty() -> None:
    record = _record()
    kinds = {gap["kind"] for gap in record["data_gaps"]}
    assert "GROUND TRUTH GAP" in kinds
    assert "SPATIAL GAP" in kinds
    assert "LICENSE / ACCESS GAP" in kinds
    assert record["source_conflicts"][0]["conflict"] is True
    assert record["source_conflicts"][0]["resolved"] is False
    assert set(record["uncertainty"].values()) == {"UNKNOWN"}
    assert record["freshness"]["freshness_status"] == "UNKNOWN"
    assert record["temporal_associations"][0]["relation"] == "UNKNOWN"
    assert "threshold" not in json.dumps(record).lower()


def test_raw_checksums_are_unchanged() -> None:
    provenance = json.loads(PROVENANCE.read_text(encoding="utf-8"))
    for item in provenance["files"]:
        digest = hashlib.sha256((RAW / item["name"]).read_bytes()).hexdigest()
        assert digest == item["sha256"]
    record = _record()
    for item in record["external_indicators"]:
        assert item["sha256"]
        assert item["raw_file"].endswith(".csv")
