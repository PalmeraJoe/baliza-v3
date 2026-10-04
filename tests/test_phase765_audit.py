import json
from pathlib import Path

from baliza.experimental.phase765.audit import build_audit, compare_checksum, render_audit

ROOT = Path(__file__).resolve().parents[1]


def _audit() -> dict:
    return build_audit(ROOT)


def _row(audit: dict, dataset_id: str) -> dict:
    return next(row for row in audit["datasets"] if row["dataset_id"] == dataset_id)


def test_real_inventory_matches_stored_checksums_and_keeps_gaps() -> None:
    audit = _audit()
    sst = _row(audit, "noaacrwsstDaily")
    assert sst["raw_exists"] is True
    assert sst["raw_readable"] is True
    assert sst["checksum"]["comparison"] == "MATCH"
    assert sst["checksum"]["provenance_integrity_issue"] is False
    assert sst["product_version"] == "3.1"
    assert sst["crs"] == "UNKNOWN"
    assert sst["conversion_applied"] is False
    assert sst["freshness_status"] == "UNKNOWN"
    assert sst["uncertainty"] == "UNKNOWN"
    assert sst["evidence_completeness"] == "PARTIAL"
    assert sst["chain_integrity"] == "PARTIAL"
    assert sst["source_transformation"] == "Provider product. Not produced by BALIZA."
    assert audit["noaa_pixel_count"] == 4
    assert audit["noaa_valued_cells"] == 1
    assert audit["noaa_averaged_value"] is None
    hotspot = _row(audit, "noaacrwhotspotDaily")
    assert hotspot["quality"] == "QUESTIONABLE"
    assert hotspot["checksum"]["comparison"] == "MATCH"
    missing = _row(audit, "emodnet-bathymetry")
    assert missing["raw_exists"] is False
    assert missing["raw_status"] == "NOT_AVAILABLE"
    assert missing["documented_is_not_retrieved"] is True
    assert missing["chain_integrity"] == "BROKEN"
    assert missing["usable_in_later_indicator"] is False
    allen = _row(audit, "allen-benthic_bbox.json")
    assert allen["checksum"]["comparison"] == "MATCH"
    assert allen["product_version"] == "UNKNOWN"
    assert "field observation" in allen["association"]
    xml = _row(audit, "allen-wfs-capabilities-2.0.0.xml")
    assert xml["raw_exists"] is True
    assert xml["checksum"]["comparison"] == "NOT_AVAILABLE"
    mermaid = _row(audit, "mermaid-summarysampleevents")
    assert mermaid["official_access"] == "PARTIAL"
    assert mermaid["summary_sample_event_count"] == 16557
    assert mermaid["usable_spot_observations"] == 0
    assert mermaid["spot_result"] == "NO_MATCH_WITH_DEMO_SPOT"
    assert mermaid["spatial_compatibility"] == "UNKNOWN"
    resort = _row(audit, "resort")
    assert resort["status"] == "NOT_AVAILABLE"
    assert resort["base_model_training"] is False
    assert audit["alerts"] == []
    assert audit["downscaling"] == "NOT_AUTHORIZED"
    assert audit["provenance_integrity_issues"] == []
    text = render_audit(audit)
    assert "not a statement that MERMAID has no data" in text
    assert "No average" in text
    kinds = {gap["gap_type"] for gap in audit["gaps"]}
    assert "LICENSE_ACCESS_GAP" in kinds
    assert "SOURCE_GAP" in kinds
    stored = json.loads((ROOT / "data" / "phase75" / "provenance.json").read_text(encoding="utf-8"))
    assert stored["files"][0]["sha256"] == _row(audit, "noaacrwsstDaily")["checksum"]["stored_checksum"]


def test_checksum_mismatch_is_not_replaced(tmp_path: Path) -> None:
    target = tmp_path / "row.csv"
    target.write_text("time,latitude\n", encoding="utf-8")
    compared = compare_checksum(target, "0" * 64)
    assert compared["comparison"] == "MISMATCH"
    assert compared["provenance_integrity_issue"] is True
    assert compared["stored_checksum"] == "0" * 64
    assert compared["baliza_computed_checksum"] != compared["stored_checksum"]
    absent = compare_checksum(tmp_path / "missing.csv", None)
    assert absent["comparison"] == "NOT_AVAILABLE"
