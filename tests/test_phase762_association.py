import json
from pathlib import Path

from baliza.experimental.phase76.association import GridSpec
from baliza.experimental.phase762.engine import (
    allen_real_case,
    freshness,
    heritage_spot,
    noaa_real_cell_associations,
    point_source_association,
    polygon_association,
    raster_associations,
    render_noaa_case,
    source_conflict,
    spot_geometry,
    temporal_association,
    transect_association,
)

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "phase75" / "raw"
PROVENANCE = ROOT / "data" / "phase75" / "provenance.json"
ALLEN = ROOT / "data" / "phase75" / "allen" / "raw" / "benthic_bbox.json"
ALLEN_PROVENANCE = ROOT / "data" / "phase75" / "allen" / "provenance.json"
TEST_CRS = "TEST-SAME-AXIS"


def _one_cell_grid() -> GridSpec:
    return GridSpec(
        crs=TEST_CRS,
        lat_centers=(-23.475,),
        lon_centers=(151.975,),
        half_lat=0.025,
        half_lon=0.025,
        label="TEST / SYNTHETIC CRS. Value is the stored NOAA cell.",
    )


def _four_cell_grid() -> GridSpec:
    return GridSpec(
        crs=TEST_CRS,
        lat_centers=(-23.475, -23.525),
        lon_centers=(151.975, 152.025),
        half_lat=0.025,
        half_lon=0.025,
        label="TEST / SYNTHETIC CRS. Not the NOAA production CRS.",
    )


def test_single_pixel_is_one_external_association() -> None:
    spot = spot_geometry(
        spot_id="TEST-CELL-CENTER",
        geometry_type="POINT",
        crs=TEST_CRS,
        spatial_precision="GRID",
        source="Test point placed on the retrieved cell center.",
        latitude=-23.475,
        longitude=151.975,
        reference_time="2026-09-26T12:00:00Z",
    )
    result = raster_associations(
        spot,
        _one_cell_grid(),
        source="NOAA Coral Reef Watch",
        product="crw_coraltemp_sst",
        product_version="CoralTemp-v3.1",
        variable="analysed_sst",
        unit="degree_C",
        values={(-23.475, 151.975): "22.72"},
        observation_time="2026-09-26T12:00:00Z",
        ingestion_time="2026-10-01",
        temporal_precision="daily",
        source_quality="UNKNOWN",
        baliza_quality="UNKNOWN",
        dataset_id="noaacrwsstDaily",
        raw_file="noaacrwsstDaily_2026-09-26.csv",
        raw_checksum="stored",
        transformation="DERIVED",
        cell_resolution="0.05 degree",
    )
    assert len(result["associations"]) == 1
    row = result["associations"][0]
    assert row["spatial"]["association_type"] == "CONTAINS"
    assert row["epistemic"]["scientific_layer"] == "EXTERNAL_INDICATOR"
    assert row["measured"] is False
    assert row["local_estimate"] == "NOT_AUTHORIZED"
    assert row["temporal"]["association_type"] == "EXACT_TIME"
    assert row["temporal"]["ingestion_time"] == "2026-10-01"
    assert row["temporal"]["observation_time"] == "2026-09-26T12:00:00Z"


def test_four_pixels_stay_separate_on_a_shared_test_crs() -> None:
    spot = spot_geometry(
        spot_id="TEST-CORNER",
        geometry_type="POINT",
        crs=TEST_CRS,
        spatial_precision=None,
        source="Test point on a cell corner. CRS token is not NOAA's CRS.",
        latitude=-23.5,
        longitude=152.0,
    )
    result = raster_associations(
        spot,
        _four_cell_grid(),
        source="NOAA Coral Reef Watch",
        product="crw_hotspot",
        product_version="Satellite_Daily_Global_5km_Coral_Bleaching_HotSpot",
        variable="hotspot",
        unit="degree_C",
        values={
            (-23.475, 151.975): "-4.39",
            (-23.475, 152.025): None,
            (-23.525, 151.975): None,
            (-23.525, 152.025): None,
        },
        observation_time="2026-09-26T12:00:00Z",
        ingestion_time="2026-10-01",
        temporal_precision="daily",
        source_quality="UNKNOWN",
        baliza_quality="QUESTIONABLE",
        dataset_id="noaacrwhotspotDaily",
        raw_file="noaacrwhotspotDaily_2026-09-26.csv",
        raw_checksum="stored",
        transformation="DERIVED",
        cell_resolution="0.05 degree",
    )
    assert len(result["associations"]) == 4
    assert result["averaged_value"] is None
    assert {row["spatial"]["association_type"] for row in result["associations"]} == {"INTERSECTS"}
    values = [row["value"] for row in result["associations"]]
    assert values.count("-4.39") == 1
    assert values.count("UNKNOWN") == 3
    assert all(row["spatial"]["distance_m"] == "UNKNOWN" for row in result["associations"])
    assert all(row["measured"] is False for row in result["associations"])


def test_real_noaa_crs_blocks_the_four_centers() -> None:
    result = noaa_real_cell_associations(RAW, PROVENANCE)
    hotspot = next(item for item in result["products"] if item["associations"][0]["product"] == "crw_hotspot")
    assert len(hotspot["associations"]) == 4
    assert hotspot["averaged_value"] is None
    assert {row["spatial"]["association_type"] for row in hotspot["associations"]} == {"UNKNOWN"}
    assert {row["spatial"]["source_crs"] for row in hotspot["associations"]} == {"UNKNOWN"}
    retrieved = [row for row in hotspot["associations"] if row["value"] == "-4.39"]
    missing = [row for row in hotspot["associations"] if row["value"] == "UNKNOWN"]
    assert len(retrieved) == 1
    assert len(missing) == 3
    assert retrieved[0]["provenance"]["status"] == "CLOSED"
    assert retrieved[0]["provenance"]["raw_checksum"]
    assert all(row["provenance"]["status"] == "PARTIAL" for row in missing)
    assert all(row["uncertainty"]["measurement"] == "UNKNOWN" for row in hotspot["associations"])
    assert all(row["uncertainty"]["spatial"] != 0 for row in hotspot["associations"])
    text = render_noaa_case(result)
    assert "No temperature was averaged" in text
    assert "UNKNOWN" in text


def test_real_allen_extract_is_not_a_field_class() -> None:
    case = allen_real_case(ALLEN, ALLEN_PROVENANCE, heritage_spot())
    assert case["associations"] == []
    assert case["class_attached_to_spot"] is False
    assert case["field_observation"] is False
    assert case["geometry_present"] is False
    assert case["overlap_fraction"] == "UNKNOWN"
    assert case["feature_crs"] == "UNKNOWN"
    assert case["epoch"] == "UNKNOWN"
    assert case["scientific_layer"] == "CONTEXT_ONLY"
    assert case["provenance"]["raw_checksum"].startswith("9c8e75ba")
    assert "SPATIAL GAP" in case["gaps"]
    assert "Coral/Algae" not in case["note"]


def test_synthetic_polygon_overlap_stays_context() -> None:
    spot = spot_geometry(
        spot_id="TEST-BOX",
        geometry_type="POLYGON",
        crs=TEST_CRS,
        spatial_precision="TEST",
        source="Synthetic box.",
    )
    row = polygon_association(
        (0, 0, 2, 2),
        (1, 1, 3, 3),
        spot=spot,
        feature_crs=TEST_CRS,
        layer="TEST-LAYER",
        class_name="TEST-CLASS",
        epoch=None,
        polygon_id="box-1",
        resolution=None,
        label="TEST / SYNTHETIC / NON-SCIENTIFIC",
    )
    assert row["spatial"]["association_type"] == "INTERSECTS"
    assert row["spatial"]["overlap_fraction"] == 0.25
    assert row["epistemic"]["scientific_layer"] == "CONTEXT_ONLY"
    assert row["field_observation"] is False
    assert row["epoch"] == "UNKNOWN"
    assert row["spatial"]["distance_m"] == "UNKNOWN"


def test_mermaid_absence_creates_no_measurement() -> None:
    case = transect_association(heritage_spot(), None)
    assert case["associations"] == []
    assert case["status"] == "NOT_AVAILABLE"
    assert case["measured"] is False
    listed = transect_association(
        heritage_spot(),
        {
            "transect_id": "NOT-A-STORED-ROW",
            "geometry": "TRANSECT",
            "depth": "UNKNOWN",
            "survey_date": None,
            "method": "UNKNOWN",
            "site": "UNKNOWN",
            "variable": "benthic_cover",
        },
    )
    row = listed["associations"][0]
    assert row["representative_value"] is None
    assert row["spatial"]["association_type"] == "UNKNOWN"
    assert row["spatial"]["point_relation"] != "NEAR"
    assert row["measured"] is False
    assert row["geometry"] == "TRANSECT"


def test_temporal_mismatch_does_not_become_near() -> None:
    spot = spot_geometry(
        spot_id="TEST-CELL-CENTER",
        geometry_type="POINT",
        crs=TEST_CRS,
        spatial_precision="GRID",
        source="Test.",
        latitude=-23.475,
        longitude=151.975,
        reference_time="2026-09-20T12:00:00Z",
    )
    result = raster_associations(
        spot,
        _one_cell_grid(),
        source="NOAA Coral Reef Watch",
        product="crw_coraltemp_sst",
        product_version="CoralTemp-v3.1",
        variable="analysed_sst",
        unit="degree_C",
        values={(-23.475, 151.975): "22.72"},
        observation_time="2026-09-26T12:00:00Z",
        ingestion_time="2026-10-01",
        temporal_precision="daily",
        source_quality="UNKNOWN",
        baliza_quality="UNKNOWN",
        dataset_id="noaacrwsstDaily",
        raw_file="a.csv",
        raw_checksum="abc",
        transformation="DERIVED",
        cell_resolution="0.05 degree",
    )
    row = result["associations"][0]
    assert row["spatially_associated"] is True
    assert row["temporal"]["association_type"] == "UNKNOWN"
    assert row["temporally_associated"] == "UNKNOWN"
    assert row["temporal"]["time_difference"] == "6 days, 0:00:00"
    assert row["temporal"]["policy"] == "NOT_DEFINED"
    assert row["temporal"]["association_type"] != "TEMPORALLY_NEAR"


def test_two_anomaly_products_conflict_without_a_winner() -> None:
    result = noaa_real_cell_associations(RAW, PROVENANCE)
    chosen = []
    for product in result["products"]:
        retrieved = next(row for row in product["associations"] if row["value"] != "UNKNOWN")
        if retrieved["product"].startswith("crw_sst_anomaly"):
            chosen.append(retrieved)
    conflict = source_conflict(chosen, dimension="SST anomaly on the retrieved cell")
    assert conflict["source_conflict"] is True
    assert conflict["resolved"] is False
    assert conflict["selected_source"] is None
    assert {row["value"] for row in chosen} == {"0.78", "0.4"}


def test_missing_time_and_missing_coverage_stay_unknown() -> None:
    assert temporal_association(source_kind="daily")["association_type"] == "UNKNOWN"
    spot = spot_geometry(
        spot_id="OUTSIDE",
        geometry_type="POINT",
        crs=TEST_CRS,
        spatial_precision="TEST",
        source="Test.",
        latitude=0,
        longitude=0,
    )
    result = raster_associations(
        spot,
        _one_cell_grid(),
        source="NOAA Coral Reef Watch",
        product="crw_coraltemp_sst",
        product_version=None,
        variable=None,
        unit=None,
        values={},
        observation_time=None,
        ingestion_time=None,
        temporal_precision=None,
        source_quality=None,
        baliza_quality=None,
        dataset_id=None,
        raw_file=None,
        raw_checksum=None,
        transformation=None,
        cell_resolution=None,
    )
    assert result["associations"] == []
    assert "DATA GAP" in result["gaps"]
    assert "SPATIAL GAP" in result["gaps"]


def test_nearby_point_keeps_distance_and_is_not_measured() -> None:
    spot = spot_geometry(
        spot_id="SPOT",
        geometry_type="POINT",
        crs=TEST_CRS,
        spatial_precision=None,
        source="Test.",
        latitude=-23.5,
        longitude=152.0,
    )
    row = point_source_association(
        spot,
        source="MERMAID",
        product="site",
        latitude=-23.51,
        longitude=152.01,
        source_crs=TEST_CRS,
        distance=0.014,
        distance_unit="degree",
        same_identity=False,
        inside_polygon=False,
        scientific_layer="EXTERNAL_INDICATOR",
    )
    assert row["spatial"]["point_relation"] == "UNKNOWN"
    assert row["spatial"]["point_relation"] != "NEAR"
    assert row["spatial"]["distance_m"] == "UNKNOWN"
    assert row["spatial"]["distance_degrees"] == 0.014
    assert row["measured"] is False


def test_freshness_does_not_replace_observation_with_ingestion() -> None:
    record = freshness(
        observation_time="2026-09-26T12:00:00Z",
        reference_time=None,
        ingestion_time="2026-10-01",
    )
    assert record["observation_time"] == "2026-09-26T12:00:00Z"
    assert record["ingestion_time"] == "2026-10-01"
    assert record["age"] == "UNKNOWN"
    assert record["freshness_status"] == "UNKNOWN"
    aged = freshness(
        observation_time="2026-09-26T12:00:00Z",
        reference_time="2026-09-27T12:00:00Z",
        ingestion_time="2026-10-01",
    )
    assert aged["age"] == "1 day, 0:00:00"
    assert aged["freshness_status"] == "UNKNOWN"


def test_real_bundle_has_no_estimate_and_checksums_match() -> None:
    result = noaa_real_cell_associations(RAW, PROVENANCE)
    text = json.dumps(result)
    assert "NOT_AUTHORIZED" in text
    assert "TEMPORALLY_NEAR" not in text
    provenance = json.loads(PROVENANCE.read_text(encoding="utf-8"))
    checksums = {item["name"]: item["sha256"] for item in provenance["files"]}
    for product in result["products"]:
        for row in product["associations"]:
            if row["provenance"]["status"] == "CLOSED":
                assert checksums[row["provenance"]["raw_file"]] == row["provenance"]["raw_checksum"]
