import hashlib
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from baliza.experimental.phase76.association import GridSpec, associate_point_to_grid
from baliza.infrastructure.sources.crw.adapter import CrwAdapter, CrwAdapterError
from baliza.infrastructure.sources.crw.catalog import (
    AVAILABLE_PRODUCTS,
    CANDIDATE_CENTERS,
    DEMO_SPOT,
    NOT_AVAILABLE_PRODUCTS,
    RETRIEVED_CENTER,
)
from baliza.infrastructure.sources.crw.raw_store import RawOverwriteError, preserve_raw, verify_stored_checksums
from baliza.infrastructure.sources.crw.spot_intelligence import build_crw_spot_intelligence
from baliza.interfaces.api.app import app

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "phase75" / "raw"
PROVENANCE = ROOT / "data" / "phase75" / "provenance.json"
client = TestClient(app)


def test_discover_lists_verified_and_unavailable_products() -> None:
    discovery = CrwAdapter().discover(live=False)
    ids = {item["dataset_id"] for item in discovery["available"]}
    assert ids == set(AVAILABLE_PRODUCTS)
    assert "crw_mmm_climatology" in NOT_AVAILABLE_PRODUCTS
    assert discovery["not_available"]
    assert discovery["discovery_mode"] == "VERIFIED_CATALOG"


def test_raw_checksums_match_and_overwrite_is_refused(tmp_path: Path) -> None:
    rows = verify_stored_checksums(RAW, PROVENANCE)
    assert rows and all(row["match"] for row in rows)
    payload = (RAW / "noaacrwsstDaily_2026-09-26.csv").read_bytes()
    first = preserve_raw(tmp_path, "cell.csv", payload)
    assert first["written"] is True
    second = preserve_raw(tmp_path, "cell.csv", payload)
    assert second["written"] is False
    assert second["status"] == "ALREADY_PRESENT"
    with pytest.raises(RawOverwriteError):
        preserve_raw(tmp_path, "cell.csv", b"different-bytes")


def test_parse_normalize_provenance_and_epistemic_labels() -> None:
    loaded = CrwAdapter().load_stored_product(RAW, PROVENANCE, "noaacrwsstDaily")
    row = loaded["normalized"][0]
    assert row["scientific_layer"] == "EXTERNAL_INDICATOR"
    assert row["epistemic_label"] == "FACT"
    assert row["measured"] is False
    assert row["estimated"] == "NONE"
    assert row["value"] == "22.72"
    assert row["original_unit"] == "degree_C"
    assert row["canonical_unit"] == "degC"
    assert row["conversion"] == "identity"
    assert row["quality"]["source_quality"] == "UNKNOWN"
    assert row["quality"]["baliza_quality"] == "UNKNOWN"
    assert row["uncertainty"] == "UNKNOWN"
    assert loaded["provenance"]["raw_checksum_sha256"]
    assert loaded["provenance"]["product_version"] == "CoralTemp-v3.1"
    assert loaded["metadata"]["global_attributes"]["product_version"] == "3.1"
    hotspot = CrwAdapter().load_stored_product(RAW, PROVENANCE, "noaacrwhotspotDaily")["normalized"][0]
    assert hotspot["value"] == "-4.39"
    assert hotspot["quality"]["baliza_quality"] == "QUESTIONABLE"
    assert hotspot["quality"]["source_quality"] == "UNKNOWN"
    baa = CrwAdapter().load_stored_product(RAW, PROVENANCE, "noaacrwbaa7dDaily")["normalized"][0]
    assert baa["baliza_alert"] == "NO"
    assert baa["scientific_role"] == "external_noaa_alert_area_indicator"


def test_four_pixel_boundary_keeps_all_cells_without_average() -> None:
    grid = GridSpec(
        crs="TEST-SAME-AXIS",
        lat_centers=(-23.475, -23.525),
        lon_centers=(151.975, 152.025),
        half_lat=0.025,
        half_lon=0.025,
        label="TEST / SYNTHETIC / NON-SCIENTIFIC",
    )
    association = associate_point_to_grid(
        -23.5,
        152.0,
        grid,
        spot_crs="TEST-SAME-AXIS",
        values={
            (-23.475, 151.975): "-4.39",
            (-23.475, 152.025): None,
            (-23.525, 151.975): None,
            (-23.525, 152.025): None,
        },
    )
    assert association.association_type == "INTERSECTS"
    assert len(association.hits) == 4
    assert association.local_estimate == "NOT_AUTHORIZED"
    values = [hit.value for hit in association.hits]
    assert values.count("-4.39") == 1
    assert values.count(None) == 3
    package = build_crw_spot_intelligence(RAW, PROVENANCE)
    production = package["spatial_associations"]["production"]
    assert production["pixel_count"] == 4
    assert production["valued_cells"] == 1
    assert production["averaged_value"] is None
    assert production["nearest_selected"] is False
    assert production["interpolated"] is False
    assert production["association_type"] == "UNKNOWN"
    assert len(CANDIDATE_CENTERS) == 4
    assert RETRIEVED_CENTER in CANDIDATE_CENTERS


def test_spot_intelligence_keeps_estimated_none_and_no_baliza_alert() -> None:
    package = build_crw_spot_intelligence(RAW, PROVENANCE)
    assert package["spot"]["spot_id"] == DEMO_SPOT["spot_id"]
    assert package["estimated"] == "NONE"
    assert package["downscaling"] == "NOT_AUTHORIZED"
    assert package["ml_implementation"] == "NOT_AUTHORIZED"
    assert package["alerts"] == []
    assert package["measured"] == []
    assert len(package["external_indicators"]) == 6
    assert all(item["indicator"]["scientific_layer"] == "EXTERNAL_INDICATOR" for item in package["external_indicators"])
    assert package["freshness"]["freshness_status"] == "UNKNOWN"
    assert package["uncertainty"]["measurement"] == "UNKNOWN"
    assert package["uncertainty"]["measurement"] != 0
    assert package["baliza_alert_separation"]["crw_bleaching_alert_area_is_baliza_alert"] is False
    conflict = package["source_conflicts"][0]
    assert conflict["conflict"] is True
    assert conflict["resolved"] is False
    kinds = {gap["kind"] for gap in package["data_gaps"]}
    assert "SOURCE_GAP" in kinds
    assert "DATA_GAP" in kinds
    text = json.dumps(package)
    assert "xgboost" not in text.lower()
    assert package["alerts"] == []
    assert "24h" not in text
    assert "HotSpot >" not in text
    assert "DHW >" not in text
    for item in package["evidence"]:
        digest = hashlib.sha256((RAW / item["raw_file"]).read_bytes()).hexdigest()
        assert digest == item["raw_checksum_sha256"]


def test_unknown_dataset_and_api_endpoints() -> None:
    with pytest.raises(CrwAdapterError):
        CrwAdapter().retrieve("not-a-dataset", time="2026-09-26T12:00:00Z", latitude=0, longitude=0, live=False)
    discovery = client.get("/scientific/crw/discovery")
    assert discovery.status_code == 200
    assert discovery.json()["source"] == "NOAA_CORAL_REEF_WATCH"
    missing = client.get("/scientific/spots/NOT-A-SPOT/crw")
    assert missing.status_code == 404
    ok = client.get(f"/scientific/spots/{DEMO_SPOT['spot_id']}/crw")
    assert ok.status_code == 200
    body = ok.json()
    assert body["estimated"] == "NONE"
    assert body["alerts"] == []
    assert len(body["external_indicators"]) == 6
