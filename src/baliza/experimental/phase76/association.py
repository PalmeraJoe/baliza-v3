"""EXPERIMENTAL / PHASE 7.6. Spatial association only.

Associating a grid or a polygon with a spot does not create a local estimate.
Not on the operational critical path.
"""

from __future__ import annotations

from dataclasses import dataclass, field

NOT_AUTHORIZED = "NOT_AUTHORIZED"


@dataclass(frozen=True)
class GridSpec:
    """Axis-aligned cells. TEST grids must say so in `label`."""

    crs: str
    lat_centers: tuple[float, ...]
    lon_centers: tuple[float, ...]
    half_lat: float
    half_lon: float
    label: str


@dataclass(frozen=True)
class CellHit:
    lat_center: float
    lon_center: float
    value: str | None


@dataclass
class Association:
    association_type: str
    epistemic_class: str
    local_estimate: str
    crs_status: str
    hits: list[CellHit] = field(default_factory=list)
    distance: float | None = None
    distance_unit: str | None = None
    distance_method: str | None = None
    gaps: list[str] = field(default_factory=list)
    note: str = ""


def _crs_blocks(source_crs: str, spot_crs: str) -> bool:
    if not source_crs or not spot_crs:
        return True
    if source_crs == "UNKNOWN" or spot_crs == "UNKNOWN":
        return True
    return source_crs != spot_crs


def associate_point_to_grid(
    latitude: float,
    longitude: float,
    grid: GridSpec,
    *,
    spot_crs: str,
    values: dict[tuple[float, float], str | None] | None = None,
) -> Association:
    """List every cell whose closed footprint contains the point.

    Boundary points stay in every adjacent cell. A 1e-9 degree tolerance closes
    the interval against binary rounding. It is not a spatial buffer. No mean,
    nearest-cell pick, or interpolation is applied. A missing CRS blocks the comparison.
    """
    if _crs_blocks(grid.crs, spot_crs):
        return Association(
            association_type="UNKNOWN",
            epistemic_class="EXTERNAL_INDICATOR",
            local_estimate=NOT_AUTHORIZED,
            crs_status="UNKNOWN" if "UNKNOWN" in {grid.crs, spot_crs} else "INCOMPATIBLE",
            note="Coordinates are not compared across missing or different CRS values.",
        )
    hits: list[CellHit] = []
    nodata = False
    for lat in grid.lat_centers:
        for lon in grid.lon_centers:
            if abs(latitude - lat) <= grid.half_lat + 1e-9 and abs(longitude - lon) <= grid.half_lon + 1e-9:
                value = None if values is None else values.get((lat, lon))
                if values is not None and (lat, lon) not in values:
                    value = None
                    nodata = True
                elif value is None and values is not None:
                    nodata = True
                hits.append(CellHit(lat, lon, value))
    if not hits:
        return Association(
            association_type="UNKNOWN",
            epistemic_class="EXTERNAL_INDICATOR",
            local_estimate=NOT_AUTHORIZED,
            crs_status="SAME",
            gaps=["SPATIAL GAP", "DATA GAP"],
            note="The point is outside every listed cell. Absence is not zero.",
        )
    gaps = ["DATA GAP"] if nodata else []
    kind = "CONTAINS" if len(hits) == 1 else "INTERSECTS"
    return Association(
        association_type=kind,
        epistemic_class="EXTERNAL_INDICATOR",
        local_estimate=NOT_AUTHORIZED,
        crs_status="SAME",
        hits=hits,
        gaps=gaps,
        note="Cell values stay external. No local measurement is inferred.",
    )


def rectangle_overlap(
    spot: tuple[float, float, float, float],
    feature: tuple[float, float, float, float],
    *,
    spot_crs: str,
    feature_crs: str,
) -> Association:
    """Axis-aligned overlap. Boxes are (min_lon, min_lat, max_lon, max_lat).

    TEST / SYNTHETIC / NON-SCIENTIFIC when used on invented polygons.
    """
    if _crs_blocks(feature_crs, spot_crs):
        return Association(
            association_type="UNKNOWN",
            epistemic_class="CONTEXT_ONLY",
            local_estimate=NOT_AUTHORIZED,
            crs_status="INCOMPATIBLE",
            note="No overlay while CRS values differ.",
        )
    min_lon = max(spot[0], feature[0])
    min_lat = max(spot[1], feature[1])
    max_lon = min(spot[2], feature[2])
    max_lat = min(spot[3], feature[3])
    if max_lon <= min_lon or max_lat <= min_lat:
        return Association(
            association_type="UNKNOWN",
            epistemic_class="CONTEXT_ONLY",
            local_estimate=NOT_AUTHORIZED,
            crs_status="SAME",
            gaps=["SPATIAL GAP"],
            note="No overlap. Absence is not a class and not zero.",
        )
    spot_area = (spot[2] - spot[0]) * (spot[3] - spot[1])
    overlap = (max_lon - min_lon) * (max_lat - min_lat)
    contained = feature[0] <= spot[0] and feature[1] <= spot[1] and feature[2] >= spot[2] and feature[3] >= spot[3]
    return Association(
        association_type="CONTAINS" if contained else "INTERSECTS",
        epistemic_class="CONTEXT_ONLY",
        local_estimate=NOT_AUTHORIZED,
        crs_status="SAME",
        distance=overlap / spot_area if spot_area else None,
        distance_unit="fraction of spot box",
        distance_method="axis-aligned overlap; not a geodesic",
        note="A map class that overlaps a spot is context, not a field identification.",
    )


def point_relation(
    *,
    same_identity: bool,
    distance: float | None,
    distance_unit: str | None,
    inside_polygon: bool,
    spot_crs: str,
    source_crs: str,
) -> Association:
    """EXACT only for the same place. A positive distance is not membership."""
    if _crs_blocks(source_crs, spot_crs):
        return Association(
            association_type="UNKNOWN",
            epistemic_class="DIRECT_OBSERVATION",
            local_estimate=NOT_AUTHORIZED,
            crs_status="INCOMPATIBLE",
            note="Distance is not computed across CRS values.",
        )
    if same_identity or distance == 0:
        return Association(
            association_type="DIRECT",
            epistemic_class="DIRECT_OBSERVATION",
            local_estimate=NOT_AUTHORIZED,
            crs_status="SAME",
            distance=0,
            distance_unit=distance_unit,
            distance_method="identity or zero distance",
            note="DIRECT names the same place. It does not by itself make a resort file ground truth.",
        )
    if inside_polygon:
        return Association(
            association_type="CONTAINS",
            epistemic_class="DIRECT_OBSERVATION",
            local_estimate=NOT_AUTHORIZED,
            crs_status="SAME",
            distance=distance,
            distance_unit=distance_unit,
            distance_method="point in spot polygon",
            note="Inside the polygon is not the same as a sensor at an unstated point.",
        )
    return Association(
        association_type="UNKNOWN",
        epistemic_class="DIRECT_OBSERVATION",
        local_estimate=NOT_AUTHORIZED,
        crs_status="SAME",
        distance=distance,
        distance_unit=distance_unit,
        distance_method="recorded distance; no nearness threshold is approved",
        note="A nearby site is not this spot's measurement.",
    )


def temporal_relation(source_kind: str, source_time: str, spot_time: str) -> str:
    """No nearness window. Monthly products stay aggregated."""
    if source_kind == "monthly_composite":
        return "AGGREGATED_PERIOD"
    if source_kind == "daily" and len(source_time) >= 10 and source_time[:10] == spot_time[:10]:
        return "SAME_DAY"
    if source_time == spot_time:
        return "EXACT_TIME"
    return "UNKNOWN"
