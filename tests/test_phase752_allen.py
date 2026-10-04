import json
from pathlib import Path

from baliza.experimental.phase75.closure import (
    BENTHIC_URL,
    EPISTEMIC,
    GEOMORPHIC_URL,
    content_fingerprint,
    feature_file_crs,
    license_record,
    normalize_class,
    service_default_crs,
    sha256_bytes,
)

ROOT = Path(__file__).resolve().parents[1] / "data" / "phase75" / "allen"
RAW = ROOT / "raw"
CHECKSUMS = {
    "benthic_bbox.json": "9c8e75badd8ef73073f3fe0130360fb5878e2674a65d3bee87dabbca7f6beda9",
    "geomorphic_bbox.json": "f06c0b7ad90c10942c0d1c3fab3148db075421f0eed1b82f2c0ade32ae2e5a58",
    "mapping_maps.json": "8b8649f8d74e8e51f107784a377eeb88fe0c41ed7792a6305d2a2cd2926278e6",
    "wfs-capabilities-2.0.0.xml": "976ca6a84dadf72dfa1e9082732cae65424ffaf0e5a9e74e59dc9028f66755b7",
    "benthic-describe-feature-type.xml": "19dfd61dbc1d5529b9abc8d677d8959d65c1c9c203c81da2eb83d374bb3c242d",
    "geomorphic-describe-feature-type.xml": "e4daecfc4a8b87d4a0518952dadbaccb46f89b32ef78066263d48479691324f2",
}


def test_stored_raw_checksums_still_match() -> None:
    for name, expected in CHECKSUMS.items():
        assert sha256_bytes((RAW / name).read_bytes()) == expected


def test_repeat_would_match_class_content_not_bytes() -> None:
    note = json.loads((ROOT / "reproducibility.json").read_text(encoding="utf-8"))
    assert note["benthic"]["same_class_and_area"] is True
    assert note["benthic"]["same_bytes"] is False
    benthic = (RAW / "benthic_bbox.json").read_text(encoding="utf-8")
    assert len(content_fingerprint(benthic)) == 47
    assert feature_file_crs(benthic) == "UNKNOWN"


def test_service_crs_is_read_from_capabilities_not_invented() -> None:
    crs = service_default_crs((RAW / "wfs-capabilities-2.0.0.xml").read_text(encoding="utf-8"))
    assert crs["coral-atlas:benthic_data_verbose"] == "urn:ogc:def:crs:EPSG::4326"
    assert crs["coral-atlas:geomorphic_data_verbose"] == "urn:ogc:def:crs:EPSG::4326"


def test_class_is_not_converted_to_a_number() -> None:
    normalized = normalize_class("Coral/Algae")
    assert normalized["conversion_method"] == "NONE"
    assert normalized["canonical_value"] == "Coral/Algae"
    assert normalized["canonical_unit"] == "class"


def test_epistemic_classes_and_license_gaps() -> None:
    assert EPISTEMIC["benthic"] == "CONTEXT_ONLY"
    assert EPISTEMIC["bathymetry"] == "NOT_AVAILABLE"
    record = license_record()
    assert "CC BY 4.0" in record["maps_bathymetry_statistics"]
    assert record["inside_feature_file"] == "UNKNOWN"
    assert "typeNames=coral-atlas:benthic_data_verbose" in BENTHIC_URL
    assert "typeNames=coral-atlas:geomorphic_data_verbose" in GEOMORPHIC_URL


def test_schema_names_the_geometry_field() -> None:
    schema = (RAW / "benthic-describe-feature-type.xml").read_text(encoding="utf-8")
    assert "MultiSurface" in schema
    assert "class_name" in schema
    assert "native_resolution" not in schema
