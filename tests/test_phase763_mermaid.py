import json
from pathlib import Path

from baliza.experimental.phase761.record import build_spot_record
from baliza.experimental.phase762.engine import heritage_spot
from baliza.experimental.phase763.mermaid import (
    ACCESS_GAP,
    MATCH_FOUND,
    NO_COMPATIBLE_RECORD,
    associate_record,
    classify_retrieval,
    deduplicate,
    keep_bleaching_category,
    real_spot_mermaid,
    redact,
    render_real,
)

ROOT = Path(__file__).resolve().parents[1]
INQUIRY = ROOT / "data" / "phase763" / "mermaid-inquiry.json"
AUSTRALIA = ROOT / "data" / "phase763" / "mermaid-australia-summary.json"
SYNTHETIC = "TEST / SYNTHETIC / NON-SCIENTIFIC"


def _spot():
    spot = heritage_spot()
    spot["reference_time"] = "2026-09-26T12:00:00Z"
    spot["crs"] = "TEST-SAME-AXIS"
    return spot


def test_exact_record_is_a_field_observation_not_a_validation() -> None:
    row = associate_record(
        _spot(),
        {
            "record_id": "synthetic-exact",
            "latitude": -23.5,
            "longitude": 152.0,
            "survey_date": "2026-09-26T12:00:00Z",
            "bleaching_category": "normal",
            "depth": 6,
            "depth_unit": "m",
        },
        label=SYNTHETIC,
        distance_m=0,
        source_crs="TEST-SAME-AXIS",
    )
    assert row["spatial"]["association_type"] == "EXACT"
    assert row["local_to_spot"] is True
    assert row["scientific"]["layer"] == "MEASURED"
    assert row["model_validated"] is False
    assert row["contemporary_evidence"] is True
    assert classify_retrieval(http_status=200, spatial_search_completed=True, compatible_count=1) == MATCH_FOUND


def test_near_record_is_not_a_local_measurement() -> None:
    row = associate_record(
        _spot(),
        {"record_id": "synthetic-near", "latitude": -23.51, "longitude": 152.01, "survey_date": "2026-09-26"},
        label=SYNTHETIC,
        distance_m=184.7,
        source_crs="TEST-SAME-AXIS",
    )
    assert row["spatial"]["association_type"] == "NEAR"
    assert row["spatial"]["distance_m"] == 184.7
    assert row["local_to_spot"] is False
    assert row["scientific"]["layer"] != "MEASURED"
    assert row["local_estimate"] == "NOT_AUTHORIZED"


def test_temporal_mismatch_is_not_contemporary_evidence() -> None:
    row = associate_record(
        _spot(),
        {"record_id": "synthetic-old", "latitude": -23.5, "longitude": 152.0, "survey_date": "2011-02-10"},
        label=SYNTHETIC,
        distance_m=0,
        source_crs="TEST-SAME-AXIS",
    )
    assert row["spatially_associated"] is True
    assert row["temporal"]["association_type"] == "UNKNOWN"
    assert row["temporally_associated"] == "UNKNOWN"
    assert row["temporal"]["policy"] == "NOT_DEFINED"
    assert row["contemporary_evidence"] is False


def test_empty_authorized_search_is_not_an_access_error() -> None:
    assert classify_retrieval(http_status=200, spatial_search_completed=True, compatible_count=0) == NO_COMPATIBLE_RECORD


def test_unauthorized_or_failed_read_is_an_access_gap() -> None:
    assert classify_retrieval(http_status=401, spatial_search_completed=False, compatible_count=0) == ACCESS_GAP
    assert classify_retrieval(http_status=502, spatial_search_completed=False, compatible_count=0) == ACCESS_GAP
    assert ACCESS_GAP != NO_COMPATIBLE_RECORD


def test_missing_coordinates_do_not_invent_a_relation() -> None:
    row = associate_record(_spot(), {"record_id": "no-xy", "survey_date": "2026-09-26"}, label=SYNTHETIC)
    assert row["spatial"]["association_type"] == "UNKNOWN"
    assert row["spatial"]["distance_m"] == "UNKNOWN"
    assert "COORDINATE GAP" in row["gaps"]


def test_missing_date_stays_temporally_unknown() -> None:
    row = associate_record(
        _spot(),
        {"record_id": "no-date", "latitude": -23.5, "longitude": 152.0},
        label=SYNTHETIC,
        distance_m=0,
        source_crs="TEST-SAME-AXIS",
    )
    assert row["temporal"]["association_type"] == "UNKNOWN"
    assert row["temporal"]["survey_date"] == "UNKNOWN"


def test_depth_is_kept_when_present_and_unknown_when_absent() -> None:
    present = associate_record(
        _spot(),
        {"record_id": "d", "latitude": -23.5, "longitude": 152.0, "depth": 8, "depth_unit": "m"},
        label=SYNTHETIC,
        distance_m=0,
        source_crs="TEST-SAME-AXIS",
    )
    absent = associate_record(
        _spot(),
        {"record_id": "d0", "latitude": -23.5, "longitude": 152.0},
        label=SYNTHETIC,
        distance_m=0,
        source_crs="TEST-SAME-AXIS",
    )
    assert present["depth"] == 8
    assert present["depth_unit"] == "m"
    assert absent["depth"] == "UNKNOWN"
    assert absent["depth_unit"] == "UNKNOWN"


def test_bleaching_category_is_not_turned_into_mortality() -> None:
    kept = keep_bleaching_category("recently_dead")
    assert kept["bleaching_category"] == "recently_dead"
    assert kept["mortality_percentage"] == "NOT_EQUIVALENT"
    assert kept["converted"] is False
    row = associate_record(
        _spot(),
        {"record_id": "b", "latitude": -23.5, "longitude": 152.0, "bleaching_category": "0-20%"},
        label=SYNTHETIC,
        distance_m=0,
        source_crs="TEST-SAME-AXIS",
    )
    assert row["bleaching"]["bleaching_category"] == "0-20%"
    assert "mortality_percentage" not in row["variables"]


def test_duplicates_are_counted_once() -> None:
    rows = deduplicate(
        [
            {"sample_event_id": "same", "latitude": 1},
            {"sample_event_id": "same", "latitude": 1},
            {"sample_event_id": "other", "latitude": 2},
        ]
    )
    assert len(rows["records"]) == 2
    assert rows["duplicate_count"] == 1


def test_privacy_fields_are_removed() -> None:
    cleaned = redact({"latitude": -23.5, "observers": ["a person"], "project_admins": [{"id": "hidden"}]})
    assert "observers" not in cleaned
    assert "project_admins" not in cleaned
    assert cleaned["latitude"] == -23.5


def test_real_australia_page_does_not_associate_the_spot() -> None:
    result = real_spot_mermaid(INQUIRY, AUSTRALIA, heritage_spot())
    text = json.dumps(result)
    assert result["mermaid_status"] == ACCESS_GAP
    assert result["mermaid_data_gap"] == ACCESS_GAP
    assert result["identical_coordinates_in_australia_summary"] == 0
    assert result["australia_page_complete"] is True
    assert result["australia_summary_count"] == 45
    assert result["mermaid_candidates"] == []
    assert result["mermaid_spatial_associations"] == []
    assert result["sites_http_status"] == 401
    assert result["name_query_heron_island_count"] == 0
    assert result["model_validated"] is False
    assert result["local_estimate"] == "NOT_AUTHORIZED"
    assert result["alerts"] == []
    assert result["mermaid_provenance"]["status"] == "PARTIAL"
    assert result["mermaid_provenance"]["raw_body_stored"] is False
    assert "threshold" not in text.lower()
    rendered = render_real(result)
    assert "not a statement that MERMAID has no data" in rendered
    assert "ACCESS GAP" in rendered
    stored = json.loads(AUSTRALIA.read_text(encoding="utf-8"))
    assert "observers" not in json.dumps(stored)
    assert "project_admins" not in json.dumps(stored)


def test_real_status_does_not_become_a_spot_measurement() -> None:
    record = build_spot_record(ROOT / "data" / "phase75" / "raw", ROOT / "data" / "phase75" / "provenance.json")
    mermaid = real_spot_mermaid(INQUIRY, AUSTRALIA, heritage_spot())
    record["mermaid_status"] = mermaid["mermaid_status"]
    record["mermaid_records_found"] = mermaid["mermaid_records_found"]
    record["mermaid_candidates"] = mermaid["mermaid_candidates"]
    record["mermaid_spatial_associations"] = mermaid["mermaid_spatial_associations"]
    record["mermaid_temporal_associations"] = mermaid["mermaid_temporal_associations"]
    record["mermaid_ground_truth_status"] = mermaid["mermaid_ground_truth_status"]
    record["mermaid_data_gap"] = mermaid["mermaid_data_gap"]
    record["mermaid_provenance"] = mermaid["mermaid_provenance"]
    assert record["measured"] == []
    assert record["estimated"] == []
    assert record["alerts"] == []
    assert record["mermaid_status"] == ACCESS_GAP
