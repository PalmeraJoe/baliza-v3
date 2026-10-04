"""Phase 7.14 Visual MVP API bootstrap tests."""

from pathlib import Path

from fastapi.testclient import TestClient

from baliza.interfaces.api.app import create_app

ROOT = Path(__file__).resolve().parents[1]


def test_mvp_bootstrap_stops_before_decision_and_lists_spots() -> None:
    client = TestClient(create_app())
    spots = client.get("/scientific/spots")
    assert spots.status_code == 200
    assert spots.json()["spots"][0]["spot_id"] == "DEMO-CRW-ORIG24-HERITAGE-POINT"
    assert spots.json()["spots"][0]["latitude"] == -23.5

    boot = client.post("/scientific/mvp/bootstrap")
    assert boot.status_code == 200
    body = boot.json()
    assert body["session"]["threshold_status"] == "DEMO / NON-SCIENTIFIC"
    assert body["session"]["scientifically_validated"] is False
    assert body["session"]["thermal_ground_truth"] == "NOT_AVAILABLE"
    assert body["session"]["through"] == "dss"
    assert body["summary"]["decision_id"] is None

    session = client.get("/scientific/mvp/session")
    assert session.status_code == 200
    assert session.json()["session"]["alert_id"] == body["session"]["alert_id"]

    alerts = client.get("/alerts")
    assert alerts.status_code == 200
    assert len(alerts.json()["alerts"]) >= 1

    packages = client.get("/dss/packages")
    assert packages.status_code == 200
    assert len(packages.json()["packages"]) >= 1

    options = client.get(f"/dss/packages/{body['session']['dss_package_id']}/options")
    assert options.status_code == 200
    assert options.json()["options"]
    assert all(item["epistemic_label"] == "RECOMMENDATION" for item in options.json()["options"])
    assert all(item["is_decision"] is False for item in options.json()["options"])
