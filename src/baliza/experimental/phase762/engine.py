"""EXPERIMENTAL / PHASE 7.6.2. Spatial and temporal association.

An association does not create a local measurement, a mean, or an alert.
Degrees are not treated as metres. A missing CRS is not invented.
TEMPORALLY_NEAR is a reserved code. This version does not emit it:
no nearness policy is authorized.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from baliza.experimental.phase75.crw_csv import PRODUCTS, parse_crw_griddap_csv
from baliza.experimental.phase76.association import (
    GridSpec,
    associate_point_to_grid,
    point_relation,
    rectangle_overlap,
    temporal_relation,
)

ENGINE_VERSION = "phase762-1"
NOT_AUTHORIZED = "NOT_AUTHORIZED"
UNKNOWN = "UNKNOWN"
TEMPORAL_NEAR_POLICY = "NOT_DEFINED"

SPATIAL_TYPES = frozenset(
    {"DIRECT", "CONTAINS", "INTERSECTS", "NEAREST", "AGGREGATED", "ASSOCIATED", "UNKNOWN"}
)
POINT_RELATIONS = frozenset({"EXACT", "WITHIN", "NEAR", "UNKNOWN"})
TEMPORAL_TYPES = frozenset(
    {"EXACT_TIME", "SAME_DAY", "TEMPORALLY_NEAR", "AGGREGATED_PERIOD", "UNKNOWN"}
)

HERITAGE_LAT = -23.5
HERITAGE_LON = 152.0
CANDIDATE_CENTERS = (
    (-23.475, 151.975),
    (-23.475, 152.025),
    (-23.525, 151.975),
    (-23.525, 152.025),
)
RETRIEVED_CENTER = (-23.475, 151.975)
ALLEN_BBOX = (-23.48, 151.97, -23.47, 151.98)
DATASETS = (
    "noaacrwsstDaily",
    "noaacrwsstanomalyDaily",
    "noaacrwsstanomalybaselineDaily",
    "noaacrwhotspotDaily",
    "noaacrwdhwDaily",
    "noaacrwbaa7dDaily",
)


def _unknown(value: str | None) -> str:
    if value is None or value == "":
        return UNKNOWN
    return value


def spot_geometry(
    *,
    spot_id: str,
    geometry_type: str,
    crs: str | None,
    spatial_precision: str | None,
    source: str,
    latitude: float | None = None,
    longitude: float | None = None,
    reference_time: str | None = None,
) -> dict:
    """A spot the caller already has. This function does not invent a coordinate."""
    allowed = {"POINT", "POLYGON", "ZONE", "STATION", "TRANSECT", "UNKNOWN"}
    if geometry_type not in allowed:
        raise ValueError(f"Unsupported geometry type: {geometry_type}")
    geometry: dict = {"type": geometry_type}
    if geometry_type == "POINT":
        if latitude is None or longitude is None:
            raise ValueError("A point spot needs the coordinates that were supplied.")
        geometry["latitude"] = latitude
        geometry["longitude"] = longitude
    return {
        "spot_id": spot_id,
        "geometry": geometry,
        "geometry_type": geometry_type,
        "crs": _unknown(crs),
        "spatial_precision": _unknown(spatial_precision),
        "source": source,
        "reference_time": _unknown(reference_time),
    }


def _crs_known_and_same(source_crs: str, spot_crs: str) -> bool:
    if source_crs in ("", UNKNOWN) or spot_crs in ("", UNKNOWN):
        return False
    return source_crs == spot_crs


def _base_contract(
    *,
    spot: dict,
    source: str,
    product: str,
    product_version: str | None,
    variable: str | None,
    value: str | None,
    unit: str | None,
    scientific_layer: str,
    epistemic_label: str,
    association_label: str,
) -> dict:
    return {
        "engine_version": ENGINE_VERSION,
        "spot_id": spot["spot_id"],
        "source": source,
        "product": product,
        "product_version": _unknown(product_version),
        "variable": _unknown(variable),
        "value": UNKNOWN if value is None else value,
        "unit": _unknown(unit),
        "local_estimate": NOT_AUTHORIZED,
        "measured": False,
        "field_observation": False,
        "spatial": {
            "association_type": UNKNOWN,
            "point_relation": UNKNOWN,
            "spatial_precision": UNKNOWN,
            "source_crs": UNKNOWN,
            "spot_crs": spot["crs"],
            "calculation_crs": UNKNOWN,
            "crs_transformation": {
                "source_crs": UNKNOWN,
                "target_crs": UNKNOWN,
                "transformation_method": "NONE",
                "transformation_version": "NONE",
            },
            "distance_m": UNKNOWN,
            "distance_degrees": UNKNOWN,
            "distance_method": UNKNOWN,
            "overlap_fraction": UNKNOWN,
            "overlap_area": UNKNOWN,
            "comparison_performed": False,
        },
        "temporal": {
            "association_type": UNKNOWN,
            "observation_time": UNKNOWN,
            "measurement_time": UNKNOWN,
            "survey_date": UNKNOWN,
            "processing_time": UNKNOWN,
            "publication_time": UNKNOWN,
            "ingestion_time": UNKNOWN,
            "source_time_start": UNKNOWN,
            "source_time_end": UNKNOWN,
            "spot_reference_time": spot["reference_time"],
            "time_difference": UNKNOWN,
            "temporal_precision": UNKNOWN,
            "policy": TEMPORAL_NEAR_POLICY,
        },
        "quality": {
            "source_quality": UNKNOWN,
            "baliza_quality": UNKNOWN,
            "association_quality": UNKNOWN,
        },
        "uncertainty": {
            "measurement": UNKNOWN,
            "spatial": UNKNOWN,
            "temporal": UNKNOWN,
            "association": UNKNOWN,
            "model": UNKNOWN,
        },
        "epistemic": {
            "scientific_layer": scientific_layer,
            "label": epistemic_label,
            "association_label": association_label,
        },
        "provenance": {
            "status": "PARTIAL",
            "dataset_id": UNKNOWN,
            "product_version": _unknown(product_version),
            "raw_file": UNKNOWN,
            "raw_checksum": UNKNOWN,
            "transformation": UNKNOWN,
        },
    }


def attach_temporal(record: dict, temporal: dict) -> dict:
    record["temporal"] = temporal
    record["spatially_associated"] = record["spatial"]["comparison_performed"] and record["spatial"][
        "association_type"
    ] in {"DIRECT", "CONTAINS", "INTERSECTS", "ASSOCIATED"}
    record["temporally_associated"] = temporal["association_type"] in {
        "EXACT_TIME",
        "SAME_DAY",
        "AGGREGATED_PERIOD",
    }
    if temporal["association_type"] == UNKNOWN:
        record["temporally_associated"] = UNKNOWN
    return record


def temporal_association(
    *,
    source_kind: str,
    observation_time: str | None = None,
    measurement_time: str | None = None,
    survey_date: str | None = None,
    processing_time: str | None = None,
    publication_time: str | None = None,
    ingestion_time: str | None = None,
    source_time_start: str | None = None,
    source_time_end: str | None = None,
    spot_reference_time: str | None = None,
    temporal_precision: str | None = None,
) -> dict:
    """Classify time without a nearness window. Ingestion is not observation."""
    scientific = observation_time or measurement_time or survey_date
    relation = UNKNOWN
    difference = UNKNOWN
    if scientific and spot_reference_time:
        difference = _time_difference(scientific, spot_reference_time)
        if source_kind == "monthly_composite":
            relation = "AGGREGATED_PERIOD"
        elif scientific == spot_reference_time:
            relation = "EXACT_TIME"
        else:
            relation = temporal_relation(source_kind, scientific, spot_reference_time)
    if relation == "TEMPORALLY_NEAR":
        raise RuntimeError("This engine version must not emit TEMPORALLY_NEAR.")
    return {
        "association_type": relation,
        "observation_time": _unknown(observation_time),
        "measurement_time": _unknown(measurement_time),
        "survey_date": _unknown(survey_date),
        "processing_time": _unknown(processing_time),
        "publication_time": _unknown(publication_time),
        "ingestion_time": _unknown(ingestion_time),
        "source_time_start": _unknown(source_time_start),
        "source_time_end": _unknown(source_time_end),
        "spot_reference_time": _unknown(spot_reference_time),
        "time_difference": difference,
        "temporal_precision": _unknown(temporal_precision),
        "policy": TEMPORAL_NEAR_POLICY,
        "ingestion_used_as_observation": False,
    }


def _time_difference(source_time: str, spot_time: str) -> str:
    try:
        left = datetime.fromisoformat(source_time.replace("Z", "+00:00"))
        right = datetime.fromisoformat(spot_time.replace("Z", "+00:00"))
    except ValueError:
        return UNKNOWN
    return str(abs(left - right))


def raster_associations(
    spot: dict,
    grid: GridSpec,
    *,
    source: str,
    product: str,
    product_version: str | None,
    variable: str | None,
    unit: str | None,
    values: dict[tuple[float, float], str | None],
    observation_time: str | None,
    ingestion_time: str | None,
    temporal_precision: str | None,
    source_quality: str | None,
    baliza_quality: str | None,
    dataset_id: str | None,
    raw_file: str | None,
    raw_checksum: str | None,
    transformation: str | None,
    cell_resolution: str | None,
) -> dict:
    """One association per closed-footprint cell. No mean and no nearest pick.

    When the CRS blocks comparison, each supplied center is still listed, with
    association UNKNOWN. A value is copied only for a center that was retrieved.
    """
    latitude = spot["geometry"]["latitude"]
    longitude = spot["geometry"]["longitude"]
    compared = associate_point_to_grid(
        latitude,
        longitude,
        grid,
        spot_crs=spot["crs"],
        values=values,
    )
    temporal = temporal_association(
        source_kind="daily" if temporal_precision == "daily" else "unknown",
        observation_time=observation_time,
        ingestion_time=ingestion_time,
        spot_reference_time=None if spot["reference_time"] == UNKNOWN else spot["reference_time"],
        temporal_precision=temporal_precision,
    )
    if not _crs_known_and_same(grid.crs, spot["crs"]):
        centers = [(lat, lon) for lat in grid.lat_centers for lon in grid.lon_centers]
        rows = [
            _raster_row(
                spot=spot,
                center=center,
                association_type=UNKNOWN,
                comparison_performed=False,
                value=values.get(center),
                source=source,
                product=product,
                product_version=product_version,
                variable=variable,
                unit=unit,
                source_crs=grid.crs,
                cell_resolution=cell_resolution,
                source_quality=source_quality,
                baliza_quality=baliza_quality,
                dataset_id=dataset_id,
                raw_file=raw_file if center in values and values.get(center) is not None else None,
                raw_checksum=raw_checksum if center in values and values.get(center) is not None else None,
                transformation=transformation,
                temporal=temporal,
                note=compared.note,
            )
            for center in centers
        ]
        gaps = ["CRS GAP"]
        if any(values.get(center) is None for center in centers):
            gaps.append("DATA GAP")
        return {"associations": rows, "gaps": gaps, "averaged_value": None}

    if not compared.hits:
        return {
            "associations": [],
            "gaps": list(compared.gaps) or ["DATA GAP", "SPATIAL GAP"],
            "averaged_value": None,
            "note": compared.note,
        }

    rows = []
    for hit in compared.hits:
        rows.append(
            _raster_row(
                spot=spot,
                center=(hit.lat_center, hit.lon_center),
                association_type=compared.association_type,
                comparison_performed=True,
                value=hit.value,
                source=source,
                product=product,
                product_version=product_version,
                variable=variable,
                unit=unit,
                source_crs=grid.crs,
                cell_resolution=cell_resolution,
                source_quality=source_quality,
                baliza_quality=baliza_quality,
                dataset_id=dataset_id,
                raw_file=raw_file if hit.value is not None else None,
                raw_checksum=raw_checksum if hit.value is not None else None,
                transformation=transformation,
                temporal=temporal,
                note=compared.note,
            )
        )
    return {
        "associations": rows,
        "gaps": list(compared.gaps),
        "averaged_value": None,
    }


def _raster_row(
    *,
    spot: dict,
    center: tuple[float, float],
    association_type: str,
    comparison_performed: bool,
    value: str | None,
    source: str,
    product: str,
    product_version: str | None,
    variable: str | None,
    unit: str | None,
    source_crs: str,
    cell_resolution: str | None,
    source_quality: str | None,
    baliza_quality: str | None,
    dataset_id: str | None,
    raw_file: str | None,
    raw_checksum: str | None,
    transformation: str | None,
    temporal: dict,
    note: str,
) -> dict:
    if association_type not in SPATIAL_TYPES:
        raise ValueError(association_type)
    record = _base_contract(
        spot=spot,
        source=source,
        product=product,
        product_version=product_version,
        variable=variable,
        value=value,
        unit=unit,
        scientific_layer="EXTERNAL_INDICATOR",
        epistemic_label="FACT" if value is not None else "INFERENCE",
        association_label="INFERENCE" if comparison_performed else UNKNOWN,
    )
    record["cell_id"] = f"{center[0]},{center[1]}"
    record["cell_geometry"] = {
        "type": "GRID_CELL_CENTER",
        "latitude": center[0],
        "longitude": center[1],
    }
    record["cell_resolution"] = _unknown(cell_resolution)
    record["spatial"]["association_type"] = association_type
    record["spatial"]["spatial_precision"] = "GRID"
    record["spatial"]["source_crs"] = _unknown(source_crs)
    record["spatial"]["comparison_performed"] = comparison_performed
    record["spatial"]["distance_m"] = UNKNOWN
    record["spatial"]["distance_method"] = (
        "Not converted from degrees. No projected calculation CRS was supplied."
    )
    record["quality"]["source_quality"] = _unknown(source_quality)
    record["quality"]["baliza_quality"] = _unknown(baliza_quality)
    record["quality"]["association_quality"] = UNKNOWN
    checksum = _unknown(raw_checksum)
    record["provenance"] = {
        "status": "CLOSED" if value is not None and checksum != UNKNOWN and raw_file else "PARTIAL",
        "dataset_id": _unknown(dataset_id),
        "product_version": _unknown(product_version),
        "raw_file": _unknown(raw_file),
        "raw_checksum": checksum,
        "transformation": _unknown(transformation),
    }
    record["note"] = note
    return attach_temporal(record, temporal)


def point_source_association(
    spot: dict,
    *,
    source: str,
    product: str,
    latitude: float,
    longitude: float,
    source_crs: str | None,
    distance: float | None,
    distance_unit: str | None,
    same_identity: bool,
    inside_polygon: bool,
    scientific_layer: str,
) -> dict:
    """A source point. NEAR is not assigned. Metres are kept only if the unit is m."""
    relation = point_relation(
        same_identity=same_identity,
        distance=distance,
        distance_unit=distance_unit,
        inside_polygon=inside_polygon,
        spot_crs=spot["crs"],
        source_crs=_unknown(source_crs),
    )
    point_code = UNKNOWN
    spatial_type = relation.association_type if relation.association_type in SPATIAL_TYPES else UNKNOWN
    if relation.association_type == "DIRECT":
        point_code = "EXACT"
    elif relation.association_type == "CONTAINS":
        point_code = "WITHIN"
    record = _base_contract(
        spot=spot,
        source=source,
        product=product,
        product_version=None,
        variable=None,
        value=None,
        unit=None,
        scientific_layer=scientific_layer,
        epistemic_label="FACT",
        association_label="INFERENCE" if relation.crs_status == "SAME" else UNKNOWN,
    )
    record["spatial"]["association_type"] = spatial_type
    record["spatial"]["point_relation"] = point_code
    record["spatial"]["source_crs"] = _unknown(source_crs)
    record["spatial"]["comparison_performed"] = relation.crs_status == "SAME"
    record["spatial"]["distance_method"] = relation.distance_method or UNKNOWN
    if distance_unit == "m" and distance is not None and relation.crs_status == "SAME":
        record["spatial"]["distance_m"] = distance
    else:
        record["spatial"]["distance_m"] = UNKNOWN
        if distance_unit == "degree" and distance is not None and relation.crs_status == "SAME":
            record["spatial"]["distance_degrees"] = distance
    record["source_point"] = {"latitude": latitude, "longitude": longitude}
    record["note"] = relation.note
    record["measured"] = False
    return record


def polygon_association(
    spot_box: tuple[float, float, float, float],
    feature_box: tuple[float, float, float, float],
    *,
    spot: dict,
    feature_crs: str,
    layer: str,
    class_name: str | None,
    epoch: str | None,
    polygon_id: str | None,
    resolution: str | None,
    label: str,
) -> dict:
    """Axis-aligned boxes only. A map class stays context, not a field sighting."""
    compared = rectangle_overlap(
        spot_box,
        feature_box,
        spot_crs=spot["crs"],
        feature_crs=feature_crs,
    )
    record = _base_contract(
        spot=spot,
        source="caller-supplied box",
        product=layer,
        product_version=None,
        variable="class_name",
        value=class_name,
        unit=None,
        scientific_layer="CONTEXT_ONLY",
        epistemic_label="FACT" if class_name else UNKNOWN,
        association_label="INFERENCE" if compared.crs_status == "SAME" else UNKNOWN,
    )
    record["label"] = label
    record["layer"] = layer
    record["class_name"] = UNKNOWN if class_name is None else class_name
    record["epoch"] = _unknown(epoch)
    record["resolution"] = _unknown(resolution)
    record["polygon_id"] = _unknown(polygon_id)
    record["field_observation"] = False
    record["spatial"]["association_type"] = (
        compared.association_type if compared.association_type in SPATIAL_TYPES else UNKNOWN
    )
    record["spatial"]["source_crs"] = _unknown(feature_crs)
    record["spatial"]["comparison_performed"] = compared.crs_status == "SAME" and bool(
        compared.association_type in {"CONTAINS", "INTERSECTS"}
    )
    record["spatial"]["overlap_fraction"] = (
        compared.distance if compared.distance_unit == "fraction of spot box" else UNKNOWN
    )
    record["spatial"]["distance_m"] = UNKNOWN
    record["spatial"]["distance_method"] = compared.distance_method or UNKNOWN
    record["note"] = compared.note
    if compared.gaps:
        record["gaps"] = list(compared.gaps)
    return record


def transect_association(
    spot: dict,
    transect: dict | None,
) -> dict:
    """Keep the transect as a transect. Do not collapse it to one representative value."""
    if transect is None:
        return {
            "associations": [],
            "gaps": ["LICENSE / ACCESS GAP", "GROUND TRUTH GAP"],
            "status": "NOT_AVAILABLE",
            "measured": False,
            "note": "No MERMAID survey row is stored. Nothing was placed on the spot.",
        }
    record = _base_contract(
        spot=spot,
        source="MERMAID",
        product="transect",
        product_version=None,
        variable=transect.get("variable"),
        value=None,
        unit=None,
        scientific_layer="MEASURED" if transect.get("same_place") else "EXTERNAL_INDICATOR",
        epistemic_label="FACT",
        association_label=UNKNOWN,
    )
    record["transect_id"] = _unknown(transect.get("transect_id"))
    record["geometry"] = transect.get("geometry", UNKNOWN)
    record["depth"] = _unknown(transect.get("depth"))
    record["survey_date"] = _unknown(transect.get("survey_date"))
    record["method"] = _unknown(transect.get("method"))
    record["observer"] = _unknown(transect.get("observer"))
    record["site"] = _unknown(transect.get("site"))
    record["country"] = _unknown(transect.get("country"))
    record["latitude"] = transect.get("latitude", UNKNOWN)
    record["longitude"] = transect.get("longitude", UNKNOWN)
    record["representative_value"] = None
    record["spatial"]["association_type"] = UNKNOWN
    record["spatial"]["point_relation"] = UNKNOWN
    record["measured"] = False
    record["note"] = "A transect is not reduced to a point value. No nearness rule is authorized."
    temporal = temporal_association(
        source_kind="survey",
        survey_date=transect.get("survey_date"),
        spot_reference_time=None if spot["reference_time"] == UNKNOWN else spot["reference_time"],
    )
    return {"associations": [attach_temporal(record, temporal)], "gaps": [], "status": "LISTED", "measured": False}


def source_conflict(records: list[dict], *, dimension: str) -> dict:
    values = [(item["product"], item["value"], item["unit"]) for item in records]
    distinct = {item[1] for item in values}
    return {
        "dimension": dimension,
        "source_conflict": len(distinct) > 1,
        "resolved": False,
        "selected_source": None,
        "records": records,
    }


def freshness(
    *,
    observation_time: str | None,
    reference_time: str | None,
    ingestion_time: str | None,
) -> dict:
    age = UNKNOWN
    if observation_time and reference_time:
        age = _time_difference(observation_time, reference_time)
    return {
        "observation_time": _unknown(observation_time),
        "reference_time": _unknown(reference_time),
        "ingestion_time": _unknown(ingestion_time),
        "age": age,
        "freshness_status": UNKNOWN,
        "note": "No freshness class is approved. Ingestion time is not the observation time.",
    }


def heritage_spot() -> dict:
    return spot_geometry(
        spot_id="DEMO-CRW-ORIG24-HERITAGE-POINT",
        geometry_type="POINT",
        crs=None,
        spatial_precision=None,
        source="NOAA orig24_names.txt heritage coordinate. Not a resort survey.",
        latitude=HERITAGE_LAT,
        longitude=HERITAGE_LON,
        reference_time=None,
    )


def noaa_real_cell_associations(raw_dir: Path, provenance_path: Path) -> dict:
    """The stored CRW cell, plus three documented centers that were not retrieved.

    The grid CRS is unknown, so comparison_performed is false.
    """
    provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
    checksums = {item["name"]: item["sha256"] for item in provenance["files"]}
    spot = heritage_spot()
    grid = GridSpec(
        crs=UNKNOWN,
        lat_centers=tuple(sorted({lat for lat, _ in CANDIDATE_CENTERS})),
        lon_centers=tuple(sorted({lon for _, lon in CANDIDATE_CENTERS})),
        half_lat=0.025,
        half_lon=0.025,
        label="Documented 0.05 degree centers. CRS UNKNOWN. Not a confirmed intersection.",
    )
    by_product = []
    for dataset_id in DATASETS:
        filename = f"{dataset_id}_2026-09-26.csv"
        parsed = parse_crw_griddap_csv((raw_dir / filename).read_text(encoding="utf-8"), dataset_id)[0]
        center = (float(parsed.where_latitude), float(parsed.where_longitude))
        if center != RETRIEVED_CENTER:
            raise ValueError("Stored NOAA row is not the retrieved center.")
        values = {center: parsed.value}
        for candidate in CANDIDATE_CENTERS:
            values.setdefault(candidate, None)
        result = raster_associations(
            spot,
            grid,
            source=parsed.source,
            product=parsed.what,
            product_version=PRODUCTS[dataset_id]["version"],
            variable=PRODUCTS[dataset_id]["variable"],
            unit=parsed.original_unit,
            values=values,
            observation_time=parsed.when,
            ingestion_time=provenance["retrieval_calendar_date"],
            temporal_precision=parsed.temporal_precision,
            source_quality=parsed.source_provided_quality,
            baliza_quality=parsed.baliza_quality,
            dataset_id=dataset_id,
            raw_file=filename,
            raw_checksum=checksums[filename],
            transformation=parsed.transformation_type,
            cell_resolution=parsed.resolution,
        )
        by_product.append(result)
    return {"spot": spot, "products": by_product, "averaged_value": None}


def allen_real_case(benthic_path: Path, provenance_path: Path, spot: dict) -> dict:
    """The stored extract has no polygon. Classes are not attached to the spot."""
    payload = json.loads(benthic_path.read_text(encoding="utf-8"))
    provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
    checksum = next(item["sha256"] for item in provenance["files"] if item["name"] == benthic_path.name)
    geometries = [feature.get("geometry") for feature in payload["features"]]
    min_lat, min_lon, max_lat, max_lon = ALLEN_BBOX
    point = (spot["geometry"]["latitude"], spot["geometry"]["longitude"])
    inside = min_lat <= point[0] <= max_lat and min_lon <= point[1] <= max_lon
    return {
        "associations": [],
        "field_observation": False,
        "scientific_layer": "CONTEXT_ONLY",
        "class_attached_to_spot": False,
        "geometry_present": any(item is not None for item in geometries),
        "feature_crs": payload.get("crs") if payload.get("crs") else UNKNOWN,
        "epoch": UNKNOWN,
        "overlap_fraction": UNKNOWN,
        "association_type": UNKNOWN,
        "request_bbox_contains_spot": inside,
        "gaps": ["SPATIAL GAP", "PROVENANCE GAP"] if not inside else ["SPATIAL GAP"],
        "provenance": {
            "status": "PARTIAL",
            "raw_file": benthic_path.name,
            "raw_checksum": checksum,
            "reason": "Feature geometry is null, so the chain stops before an overlay.",
        },
        "note": (
            "Allen Coral Atlas classes in this file are map attributes for another bbox. "
            "They are not a field observation of this spot."
        ),
    }


def render_noaa_case(result: dict) -> str:
    hotspot = next(
        product for product in result["products"] if product["associations"][0]["product"] == "crw_hotspot"
    )
    lines = [
        "BALIZA SPATIAL AND TEMPORAL ASSOCIATION",
        f"Spot: {result['spot']['spot_id']}",
        "Geometry: POINT",
        "CRS: UNKNOWN",
        "",
        "The published point is listed against four documented NOAA cell centers.",
        "The grid CRS is unknown, so none of the four is a confirmed intersection.",
        "One cell was retrieved. Three values stay UNKNOWN.",
        "No temperature was averaged. No local measurement was created.",
        "",
    ]
    for row in hotspot["associations"]:
        lines.append(
            f"Cell {row['cell_id']}: HotSpot {row['value']} {row['unit']}; "
            f"association {row['spatial']['association_type']}; "
            f"distance_m {row['spatial']['distance_m']}"
        )
    lines.extend(
        [
            "",
            "Temporal association: UNKNOWN",
            "The spot has no reference time. The grid time is not replaced by the ingestion date.",
            "TEMPORALLY_NEAR policy: NOT_DEFINED",
        ]
    )
    return "\n".join(lines)
