from fastapi.testclient import TestClient

from baliza.interfaces.api.app import app

client = TestClient(app)


def test_health() -> None:
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_demo_critical_path_sync_no_ai() -> None:
    r = client.post("/demo/critical-path", params={"sst": 31.0})
    assert r.status_code == 200
    body = r.json()
    assert body["ai_used"] is False
    assert body["evaluation_outcome"] == "triggered"
    assert body["alert_id"]
    assert body["decision_id"]
    assert body["snapshot_hash"]
