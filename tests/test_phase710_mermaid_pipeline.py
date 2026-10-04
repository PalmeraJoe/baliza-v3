import json
from pathlib import Path

from fastapi.testclient import TestClient

from baliza.experimental.phase763.mermaid import associate_record, keep_bleaching_category
from baliza.infrastructure.sources.mermaid.adapter import MermaidAdapter
from baliza.infrastructure.sources.mermaid.catalog import DEMO_SPOT
from baliza.infrastructure.sources.mermaid.spot_intelligence import build_mermaid_spot_intelligence
from baliza.interfaces.api.app import app

ROOT = Path(__file__).resolve().parents[1]
INQUIRY = ROOT / "data" / "phase763" / "mermaid-inquiry.json"
AUSTRALIA = ROOT / "data" / "phase763" / "mermaid-australia-summary.json"
client = TestClient(app)


def test_discover_and_load_real_summary() -> None:
    discovery = MermaidAdapter().discover(live=False)
    assert discovery["source"] == "MERMAID"
    assert discovery["thermal_ground_truth"] == "NOT_AVAILABLE"
    available = {item["dataset_id"] for item in discovery["available"]}
    assert "summarysampleevents" in available
    blocked = {item["dataset_id"] for item in discovery["partial_or_blocked"]}
    assert "sites" in blocked
    assert "bleaching_observations" in blocked
    summary = MermaidAdapter().load_australia_summary(AUSTRALIA)
    assert summary["count"] == 45
    assert summary["raw_body_stored"] is False
    assert MermaidAdapter().validate_summary(summary)["page_complete"] is True
    assert "observers" not in json.dumps(summary["records"])


def test_normalize_preserves_depth_protocols_and_bleaching_rules() -> None:
    summary = MermaidAdapter().load_australia_summary(AUSTRALIA)
    row = next(item for item in summary["records"] if "colonies_bleached" in item["protocol_names"])
    normalized = MermaidAdapter().normalize_summary_record(
        row,
        retrieval_timestamp=summary["http_date"],
        response_sha256=summary["response_sha256"],
    )
    assert normalized["scientific_layer"] == "MEASURED"
    assert normalized["measured_ecological_observation"] is True
    assert normalized["measured_temperature"] is False
    assert normalized["thermal_ground_truth"] is False
    assert normalized["validates_crw"] is False
    assert "BLEACHING" in normalized["dataset_types"]
    assert normalized["depth_avg"] is not None
    assert normalized["depth_unit"] == "m"
    assert normalized["source_crs"] == "UNKNOWN"
    assert normalized["survey_date"] != summary["http_date"]
    bleaching = keep_bleaching_category("recently_dead")
    assert bleaching["bleaching_category"] == "recently_dead"
    assert bleaching["mortality_percentage"] == "NOT_EQUIVALENT"
    assert bleaching["converted"] is False


def test_near_is_not_measured_and_demo_has_no_match() -> None:
    near = associate_record(
        {"spot_id": "SPOT", "geometry": {"latitude": -23.5, "longitude": 152.0}, "crs": "TEST-SAME-AXIS", "reference_time": "UNKNOWN"},
        {"record_id": "synthetic-near", "latitude": -23.51, "longitude": 152.01, "survey_date": "2020-10-01"},
        label="TEST / SYNTHETIC / NON-SCIENTIFIC",
        distance_m=120.0,
        source_crs="TEST-SAME-AXIS",
    )
    assert near["spatial"]["association_type"] == "NEAR"
    assert near["local_to_spot"] is False
    assert near["scientific"]["layer"] != "MEASURED"
    package = build_mermaid_spot_intelligence(INQUIRY, AUSTRALIA, spot_id=DEMO_SPOT["spot_id"])
    assert package["spot"]["latitude"] == -23.5
    assert package["spot"]["longitude"] == 152.0
    assert package["demo_spot_coordinates_unchanged"] is True
    assert package["demo_spot_match"] == "NO_MATCH"
    assert package["usable_spot_observations"] == 0
    assert package["field_observations_for_spot"] == []
    assert package["mermaid_spatial_compatibility"] == "UNKNOWN"
    assert package["mermaid_temporal_compatibility"] == "UNKNOWN"
    assert package["mermaid_thermal_ground_truth"] == "NOT_AVAILABLE"
    assert package["ground_truth_availability"] == "UNVERIFIED"
    assert package["estimated"] == "NONE"
    assert package["alerts"] == []
    assert package["baliza_alert_separation"]["mermaid_is_baliza_alert"] is False
    assert package["australia_summary"]["protocol_presence_in_page"]["BLEACHING"] is True
    assert package["australia_summary"]["protocol_presence_in_page"]["BENTHIC"] is True
    assert package["bleaching_semantics"]["recently_dead_is_mortality_percent"] is False
    assert package["bleaching_semantics"]["bleaching_is_temperature"] is False
    text = json.dumps(package)
    assert "NO BLEACHING" not in text
    assert "HEALTHY" not in text
    assert "xgboost" not in text.lower()


def test_api_endpoints() -> None:
    discovery = client.get("/scientific/mermaid/discovery")
    assert discovery.status_code == 200
    assert discovery.json()["source"] == "MERMAID"
    demo = client.get(f"/scientific/spots/{DEMO_SPOT['spot_id']}/mermaid")
    assert demo.status_code == 200
    assert demo.json()["demo_spot_match"] == "NO_MATCH"
    assert demo.json()["usable_spot_observations"] == 0
    missing = client.get("/scientific/spots/NOT-A-SPOT/mermaid")
    assert missing.status_code == 404
