"""Parse a CoastWatch ERDDAP CSV subset. EXPERIMENTAL / PHASE 7.5.

This module does not train a model, does not downscale, and does not create an alert.
"""

from __future__ import annotations

from dataclasses import dataclass

CELSIUS_LABELS = {"degree_C", "degree_Celsius"}
CONVERSION_VERSION = "phase75-celsius-labels-1"


class AcquisitionError(ValueError):
    """A source file could not be read. No substitute value is invented."""


@dataclass(frozen=True)
class CanonicalRecord:
    where_latitude: str
    where_longitude: str
    when: str
    what: str
    value: str
    original_unit: str
    canonical_unit: str | None
    conversion: str
    conversion_version: str
    source: str
    source_product: str
    source_version: str
    resolution: str
    method: str
    source_provided_quality: str
    baliza_quality: str
    quality_note: str
    uncertainty: str
    transformation_type: str
    spatial_precision: str
    temporal_precision: str
    spatial_relation: str


PRODUCTS: dict[str, dict[str, str]] = {
    "noaacrwsstDaily": {
        "what": "crw_coraltemp_sst",
        "variable": "analysed_sst",
        "version": "CoralTemp-v3.1",
        "method": "CRW CoralTemp gap-filled foundation SST",
    },
    "noaacrwsstanomalyDaily": {
        "what": "crw_sst_anomaly_v31",
        "variable": "sea_surface_temperature_anomaly",
        "version": "Satellite_Daily_Global_5km_SST_Anomaly",
        "method": "CRW v3.1 SST anomaly",
    },
    "noaacrwsstanomalybaselineDaily": {
        "what": "crw_sst_anomaly_1991_2020",
        "variable": "sea_surface_temperature_anomaly",
        "version": "1991-2020 climatological baseline",
        "method": "CRW SST anomaly on the 1991-2020 baseline",
    },
    "noaacrwhotspotDaily": {
        "what": "crw_hotspot",
        "variable": "hotspot",
        "version": "Satellite_Daily_Global_5km_Coral_Bleaching_HotSpot",
        "method": "CRW HotSpot grid as published on this ERDDAP dataset",
    },
    "noaacrwdhwDaily": {
        "what": "crw_dhw",
        "variable": "degree_heating_week",
        "version": "Satellite_Daily_Global_5km_Degree_Heating_Week",
        "method": "CRW Degree Heating Week grid",
    },
    "noaacrwbaa7dDaily": {
        "what": "crw_bleaching_alert_area_7d",
        "variable": "bleaching_alert_area",
        "version": "Satellite_Daily_Global_5km_7day_Maximum_Bleaching_Alert_Area_Composite",
        "method": "CRW 7-day maximum Bleaching Alert Area, external class code",
    },
}


def parse_crw_griddap_csv(text: str, dataset_id: str) -> list[CanonicalRecord]:
    product = PRODUCTS.get(dataset_id)
    if product is None:
        raise AcquisitionError(f"Unknown CRW dataset id: {dataset_id}")
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if len(lines) < 3:
        raise AcquisitionError("CRW CSV has no data row.")
    header = lines[0].split(",")
    units = lines[1].split(",")
    if header[:3] != ["time", "latitude", "longitude"] or len(header) != 4:
        raise AcquisitionError("CRW CSV header is not a single-variable griddap table.")
    if header[3] != product["variable"]:
        raise AcquisitionError("CRW CSV variable does not match the dataset id.")
    records: list[CanonicalRecord] = []
    for line in lines[2:]:
        fields = line.split(",")
        if len(fields) != 4 or any(field == "" for field in fields):
            raise AcquisitionError("CRW CSV data row is malformed.")
        when, latitude, longitude, value = fields
        original_unit = units[3]
        canonical_unit = "degC" if original_unit in CELSIUS_LABELS else None
        conversion = "identity" if canonical_unit == "degC" else "none"
        baliza_quality = "UNKNOWN"
        quality_note = "The ERDDAP row contains no quality flag."
        if dataset_id == "noaacrwhotspotDaily":
            try:
                numeric = float(value)
            except ValueError as exc:
                raise AcquisitionError("HotSpot value is not numeric.") from exc
            if numeric < 0:
                baliza_quality = "QUESTIONABLE"
                quality_note = (
                    "Retrieved HotSpot is negative. The CRW methodology page defines "
                    "HotSpot as max(SST - MMM, 0). This dataset comment does not state that clip. "
                    "The value is kept as retrieved."
                )
        records.append(
            CanonicalRecord(
                where_latitude=latitude,
                where_longitude=longitude,
                when=when,
                what=product["what"],
                value=value,
                original_unit=original_unit,
                canonical_unit=canonical_unit,
                conversion=conversion,
                conversion_version=CONVERSION_VERSION,
                source="NOAA Coral Reef Watch",
                source_product=dataset_id,
                source_version=product["version"],
                resolution="ERDDAP geospatial resolution attribute 0.049999999999999996 degrees",
                method=product["method"],
                source_provided_quality="UNKNOWN",
                baliza_quality=baliza_quality,
                quality_note=quality_note,
                uncertainty="Pixel footprint versus a spot is unresolved. No numeric error is assigned.",
                transformation_type="DERIVED",
                spatial_precision="GRID",
                temporal_precision="daily",
                spatial_relation="UNKNOWN",
            )
        )
    if not records:
        raise AcquisitionError("CRW CSV produced no records.")
    return records
