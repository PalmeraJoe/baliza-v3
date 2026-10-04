import hashlib
import json
from pathlib import Path

from baliza.experimental.phase75.allen import (
    AllenAccessError,
    authenticate,
    classify_http,
    discover,
    parse_wfs_attributes,
    portal_login_refused,
    secret_variable_names,
)

RAW = Path(__file__).resolve().parents[1] / "data" / "phase75" / "allen" / "raw"
CHECKSUMS = {
    "benthic_bbox.json": "9c8e75badd8ef73073f3fe0130360fb5878e2674a65d3bee87dabbca7f6beda9",
    "geomorphic_bbox.json": "f06c0b7ad90c10942c0d1c3fab3148db075421f0eed1b82f2c0ade32ae2e5a58",
    "mapping_maps.json": "8b8649f8d74e8e51f107784a377eeb88fe0c41ed7792a6305d2a2cd2926278e6",
}


def test_raw_checksums() -> None:
    for name, expected in CHECKSUMS.items():
        digest = hashlib.sha256((RAW / name).read_bytes()).hexdigest()
        assert digest == expected


def test_benthic_response_keeps_every_intersecting_class() -> None:
    text = (RAW / "benthic_bbox.json").read_text(encoding="utf-8")
    records = parse_wfs_attributes(text, "benthic")
    assert len(records) == 47
    assert len({record.value for record in records}) > 1
    assert all(record.transformation_type == "MODEL_ESTIMATED" for record in records)
    assert all(record.spatial_relation == "INTERSECTS" for record in records)
    assert all(record.spatial_precision == "UNKNOWN" for record in records)


def test_truncated_response_is_rejected() -> None:
    payload = {"numberMatched": 2, "features": [{"properties": {"class_name": "Rock"}}]}
    try:
        parse_wfs_attributes(json.dumps(payload), "benthic")
    except AllenAccessError as exc:
        assert exc.code == "INVALID_FILE"
        return
    raise AssertionError("A partial feature list must not be normalized.")


def test_portal_login_is_not_attempted_and_secrets_are_not_returned() -> None:
    import os

    os.environ["ALLEN_CORAL_ATLAS_PASSWORD"] = "test-secret-not-real"
    try:
        status = authenticate()
        refusal = portal_login_refused()
        assert status["wfs_wms"] == "NOT_REQUIRED"
        assert status["secrets_read"] == "no"
        assert "test-secret-not-real" not in str(status)
        assert "test-secret-not-real" not in str(refusal)
        assert refusal.code == "AUTOMATION_NOT_PERMITTED"
        assert "test-secret-not-real" not in secret_variable_names()
    finally:
        del os.environ["ALLEN_CORAL_ATLAS_PASSWORD"]


def test_http_failures_stay_distinct() -> None:
    assert classify_http(401) == "AUTHENTICATION_FAILED"
    assert classify_http(403) == "AUTHORIZATION_FAILED"
    assert classify_http(404) == "PRODUCT_UNAVAILABLE"
    assert classify_http(429) == "RATE_LIMITED"
    assert classify_http(503) == "ENDPOINT_UNAVAILABLE"
