import hashlib
import json
from pathlib import Path

from baliza.experimental.phase75.crw_csv import AcquisitionError, parse_crw_griddap_csv
from baliza.experimental.phase75.report import grid_cell_report

RAW = Path(__file__).resolve().parents[1] / "data" / "phase75" / "raw"


def test_sst_sample_stays_a_grid_value() -> None:
    text = (RAW / "noaacrwsstDaily_2026-09-26.csv").read_text(encoding="utf-8")
    record = parse_crw_griddap_csv(text, "noaacrwsstDaily")[0]
    assert record.value == "22.72"
    assert record.original_unit == "degree_C"
    assert record.canonical_unit == "degC"
    assert record.conversion == "identity"
    assert record.spatial_precision == "GRID"
    assert record.spatial_relation == "UNKNOWN"
    assert record.transformation_type == "DERIVED"
    assert record.source_provided_quality == "UNKNOWN"


def test_two_anomaly_products_stay_distinct() -> None:
    first = parse_crw_griddap_csv(
        (RAW / "noaacrwsstanomalyDaily_2026-09-26.csv").read_text(encoding="utf-8"),
        "noaacrwsstanomalyDaily",
    )[0]
    second = parse_crw_griddap_csv(
        (RAW / "noaacrwsstanomalybaselineDaily_2026-09-26.csv").read_text(encoding="utf-8"),
        "noaacrwsstanomalybaselineDaily",
    )[0]
    assert first.what != second.what
    assert first.value == "0.78"
    assert second.value == "0.4"
    assert second.original_unit == "degree_Celsius"


def test_negative_hotspot_is_kept_and_marked_questionable() -> None:
    record = parse_crw_griddap_csv(
        (RAW / "noaacrwhotspotDaily_2026-09-26.csv").read_text(encoding="utf-8"),
        "noaacrwhotspotDaily",
    )[0]
    assert record.value == "-4.39"
    assert record.baliza_quality == "QUESTIONABLE"
    assert float(record.value) < 0


def test_bleaching_alert_area_stays_an_external_code() -> None:
    record = parse_crw_griddap_csv(
        (RAW / "noaacrwbaa7dDaily_2026-09-26.csv").read_text(encoding="utf-8"),
        "noaacrwbaa7dDaily",
    )[0]
    assert record.value == "0"
    assert record.what == "crw_bleaching_alert_area_7d"
    assert record.canonical_unit is None
    report = grid_cell_report([record])
    assert report["estimated"] == "NONE"
    assert report["downscaling"] == "NOT AUTHORIZED"
    assert "alert" not in report


def test_raw_checksums_match_the_provenance_record() -> None:
    provenance = json.loads((RAW.parent / "provenance.json").read_text(encoding="utf-8"))
    for item in provenance["files"]:
        digest = hashlib.sha256((RAW / item["name"]).read_bytes()).hexdigest()
        assert digest == item["sha256"]


def test_malformed_csv_is_not_replaced() -> None:
    try:
        parse_crw_griddap_csv("time,latitude,longitude,analysed_sst\n", "noaacrwsstDaily")
    except AcquisitionError:
        return
    raise AssertionError("A short file must fail rather than invent a value.")
