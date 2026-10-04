"""Spatial association rules. Grid fixtures are TEST / SYNTHETIC / NON-SCIENTIFIC.

The NOAA heritage coordinate is a real published point. Its grid CRS is unknown,
so the test must not turn that point into a local measurement.
"""

from baliza.experimental.phase76.association import (
    GridSpec,
    associate_point_to_grid,
    point_relation,
    rectangle_overlap,
    temporal_relation,
)

# TEST / SYNTHETIC / NON-SCIENTIFIC. Not the NOAA grid and not a resort.
SYNTHETIC = GridSpec(
    crs="TEST:SYNTHETIC",
    lat_centers=(-1.0, -1.1),
    lon_centers=(10.0, 10.1),
    half_lat=0.05,
    half_lon=0.05,
    label="TEST / SYNTHETIC / NON-SCIENTIFIC",
)


def test_point_inside_one_cell() -> None:
    result = associate_point_to_grid(-1.0, 10.0, SYNTHETIC, spot_crs="TEST:SYNTHETIC")
    assert result.association_type == "CONTAINS"
    assert len(result.hits) == 1
    assert result.local_estimate == "NOT_AUTHORIZED"
    assert result.epistemic_class == "EXTERNAL_INDICATOR"


def test_point_on_edge_of_two_cells() -> None:
    result = associate_point_to_grid(-1.05, 10.0, SYNTHETIC, spot_crs="TEST:SYNTHETIC")
    assert result.association_type == "INTERSECTS"
    assert len(result.hits) == 2
    assert result.local_estimate == "NOT_AUTHORIZED"


def test_point_on_corner_of_four_cells() -> None:
    result = associate_point_to_grid(-1.05, 10.05, SYNTHETIC, spot_crs="TEST:SYNTHETIC")
    assert len(result.hits) == 4
    assert result.local_estimate == "NOT_AUTHORIZED"


def test_point_outside_coverage_is_not_zero() -> None:
    result = associate_point_to_grid(40.0, 40.0, SYNTHETIC, spot_crs="TEST:SYNTHETIC")
    assert result.hits == []
    assert "SPATIAL GAP" in result.gaps
    assert result.local_estimate == "NOT_AUTHORIZED"


def test_partial_overlap_and_containing_polygon() -> None:
    spot = (0.0, 0.0, 1.0, 1.0)
    partial = rectangle_overlap(spot, (0.5, 0.5, 1.5, 1.5), spot_crs="TEST:SYNTHETIC", feature_crs="TEST:SYNTHETIC")
    contained = rectangle_overlap(spot, (-1.0, -1.0, 2.0, 2.0), spot_crs="TEST:SYNTHETIC", feature_crs="TEST:SYNTHETIC")
    assert partial.association_type == "INTERSECTS"
    assert contained.association_type == "CONTAINS"
    assert partial.epistemic_class == "CONTEXT_ONLY"
    assert partial.distance == 0.25


def test_nearby_point_is_not_the_spot() -> None:
    near = point_relation(
        same_identity=False,
        distance=150,
        distance_unit="m",
        inside_polygon=False,
        spot_crs="TEST:SYNTHETIC",
        source_crs="TEST:SYNTHETIC",
    )
    exact = point_relation(
        same_identity=True,
        distance=None,
        distance_unit=None,
        inside_polygon=False,
        spot_crs="TEST:SYNTHETIC",
        source_crs="TEST:SYNTHETIC",
    )
    assert near.association_type == "UNKNOWN"
    assert near.distance == 150
    assert exact.association_type == "DIRECT"


def test_different_crs_is_not_compared() -> None:
    result = associate_point_to_grid(-1.0, 10.0, SYNTHETIC, spot_crs="EPSG:3857")
    assert result.association_type == "UNKNOWN"
    assert result.hits == []
    assert result.crs_status == "INCOMPATIBLE"


def test_nodata_cell_is_a_gap() -> None:
    result = associate_point_to_grid(
        -1.0,
        10.0,
        SYNTHETIC,
        spot_crs="TEST:SYNTHETIC",
        values={(-1.0, 10.0): None},
    )
    assert result.hits[0].value is None
    assert "DATA GAP" in result.gaps


def test_temporal_monthly_product_is_not_the_survey_instant() -> None:
    assert temporal_relation("monthly_composite", "2026-07", "2026-07-14") == "AGGREGATED_PERIOD"
    assert temporal_relation("daily", "2026-07-14T12:00:00Z", "2026-07-14") == "SAME_DAY"
    assert temporal_relation("daily", "2026-07-15T12:00:00Z", "2026-07-14") == "UNKNOWN"


def test_published_noaa_point_is_not_resolved_without_a_crs() -> None:
    # NOAA orig24_names.txt publishes -23.5, 152.0. The 5 km grid CRS code is UNKNOWN.
    grid = GridSpec(
        crs="UNKNOWN",
        lat_centers=(-23.475, -23.525),
        lon_centers=(151.975, 152.025),
        half_lat=0.025,
        half_lon=0.025,
        label="published CRW center spacing; CRS not confirmed",
    )
    result = associate_point_to_grid(-23.5, 152.0, grid, spot_crs="UNKNOWN")
    assert result.association_type == "UNKNOWN"
    assert result.hits == []
    assert result.local_estimate == "NOT_AUTHORIZED"
    assert result.epistemic_class == "EXTERNAL_INDICATOR"
