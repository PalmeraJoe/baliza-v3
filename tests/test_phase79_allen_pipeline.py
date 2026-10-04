import hashlib
import json
from pathlib import Path

from fastapi.testclient import TestClient

from baliza.infrastructure.sources.allen.adapter import AllenAdapter
from baliza.infrastructure.sources.allen.catalog import (
    ALLEN_RESEARCH_TEST_SPOT,
    AVAILABLE_LAYERS,
    DEMO_SPOT,
    NOT_AVAILABLE_PRODUCTS,
    REQUEST_BBOX,
)
from baliza.infrastructure.sources.allen.spot_intelligence import build_allen_spot_intelligence
from baliza.infrastructure.sources.crw.raw_store import RawOverwriteError, preserve_raw
from baliza.interfaces.api.app import app

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "phase75" / "allen" / "raw"
PROVENANCE = ROOT / "data" / "phase75" / "allen" / "provenance.json"
client = TestClient(app)


def test_discover_lists_wfs_layers_and_unavailable_products() -> None:
    discovery = AllenAdapter().discover(live=False)
    assert discovery["source"] == "ALLEN_CORAL_ATLAS"
    assert discovery["service_type"] == "WFS"
    names = {item["type_name"] for item in discovery["available"]}
    assert names == set(AVAILABLE_LAYERS)
    unavailable = {item["product_id"] for item in discovery["not_available"]}
    assert unavailable == set(NOT_AVAILABLE_PRODUCTS)
    assert "reef_mask" in unavailable
    assert "satellite_derived_depth" in unavailable
    assert "turbidity" in unavailable


def test_raw_checksums_and_no_overwrite(tmp_path: Path) -> None:
    provenance = json.loads(PROVENANCE.read_text(encoding="utf-8"))
    for item in provenance["files"]:
        digest = hashlib.sha256((RAW / item["name"]).read_bytes()).hexdigest()
        assert digest == item["sha256"]
    payload = (RAW / "benthic_bbox.json").read_bytes()
    first = preserve_raw(tmp_path, "benthic_bbox.json", payload)
    assert first["written"] is True
    second = preserve_raw(tmp_path, "benthic_bbox.json", payload)
    assert second["status"] == "ALREADY_PRESENT"
    try:
        preserve_raw(tmp_path, "benthic_bbox.json", b"other")
        raise AssertionError("overwrite should fail")
    except RawOverwriteError:
        pass


def test_parse_normalize_epistemic_and_epoch_semantics() -> None:
    loaded = AllenAdapter().load_stored_layer(RAW, PROVENANCE, "coral-atlas:benthic_data_verbose")
    row = loaded["normalized"]
    assert row["scientific_layer"] == "CONTEXT_ONLY"
    assert row["epistemic_label"] == "FACT"
    assert row["measured"] is False
    assert row["field_observation"] is False
    assert row["estimated"] == "NONE"
    assert row["transformation_type"] == "MODEL_ESTIMATED"
    assert row["transformation_origin"] == "PROVIDER"
    assert row["map_epoch_is_observation_time"] is False
    assert row["observation_time"] == "UNKNOWN"
    assert row["epoch"] == "UNKNOWN"
    assert row["product_version"] == "UNKNOWN"
    assert row["feature_crs"] == "UNKNOWN"
    assert row["uncertainty"]["measurement"] == "UNKNOWN"
    assert row["uncertainty"]["measurement"] != 0
    assert loaded["parsed"]["geometry_present_count"] == 0
    assert "Coral/Algae" in loaded["parsed"]["class_counts"]
    assert loaded["provenance"]["raw_checksum_sha256"]
    assert loaded["provenance"]["crs"]["transformation_method"] == "NONE"


def test_demo_spot_keeps_coordinates_and_has_no_allen_coverage() -> None:
    package = build_allen_spot_intelligence(RAW, PROVENANCE, spot_id=DEMO_SPOT["spot_id"])
    assert package["spot"]["latitude"] == -23.5
    assert package["spot"]["longitude"] == 152.0
    assert package["demo_spot_coordinates_unchanged"] is True
    assert package["allen_spatial_coverage"] == "NOT_AVAILABLE"
    assert package["class_attached_to_spot"] is False
    assert package["external_indicators"] == []
    assert package["evidence"] == []
    assert package["estimated"] == "NONE"
    assert package["alerts"] == []
    assert package["baliza_alert_separation"]["allen_is_baliza_alert"] is False
    assert not (
        REQUEST_BBOX["min_lat"] <= DEMO_SPOT["latitude"] <= REQUEST_BBOX["max_lat"]
        and REQUEST_BBOX["min_lon"] <= DEMO_SPOT["longitude"] <= REQUEST_BBOX["max_lon"]
    )
    kinds = {gap["kind"] for gap in package["data_gaps"]}
    assert "SPATIAL_GAP" in kinds
    assert "SOURCE_GAP" in kinds


def test_research_test_spot_parses_without_becoming_measured() -> None:
    package = build_allen_spot_intelligence(RAW, PROVENANCE, spot_id=ALLEN_RESEARCH_TEST_SPOT["spot_id"])
    assert package["not_a_validation_of_demo_spot"] is True
    assert package["class_attached_to_spot"] is False
    assert package["field_observation"] is False
    assert package["estimated"] == "NONE"
    assert package["downscaling"] == "NOT_AUTHORIZED"
    assert package["ml_implementation"] == "NOT_AUTHORIZED"
    assert len(package["external_indicators"]) == 2
    for item in package["external_indicators"]:
        assert item["scientific_layer"] == "CONTEXT_ONLY"
        assert item["measured"] is False
        assert item["class_selected_for_spot"] is None
        assert item["nearest_selected"] is False
        assert item["interpolated"] is False
        assert item["map_epoch_is_observation_time"] is False
        assert item["spatial_association"]["geometry_overlay"] is False
    assert all(item["evidence_completeness"] == "PARTIAL" for item in package["evidence"])
    text = json.dumps(package)
    assert "xgboost" not in text.lower()
    assert "HotSpot >" not in text


def test_allen_api_endpoints() -> None:
    discovery = client.get("/scientific/allen/discovery")
    assert discovery.status_code == 200
    assert discovery.json()["source"] == "ALLEN_CORAL_ATLAS"
    demo = client.get(f"/scientific/spots/{DEMO_SPOT['spot_id']}/allen")
    assert demo.status_code == 200
    assert demo.json()["allen_spatial_coverage"] == "NOT_AVAILABLE"
    assert demo.json()["spot"]["latitude"] == -23.5
    research = client.get(f"/scientific/spots/{ALLEN_RESEARCH_TEST_SPOT['spot_id']}/allen")
    assert research.status_code == 200
    assert research.json()["not_a_validation_of_demo_spot"] is True
    missing = client.get("/scientific/spots/NOT-A-SPOT/allen")
    assert missing.status_code == 404
