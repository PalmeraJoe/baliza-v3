"""NOAA Coral Reef Watch product catalog verified against CoastWatch ERDDAP.

Products not listed as AVAILABLE were not present on the verified search list
or were not retrieved as files. They are not invented here.
"""

from __future__ import annotations

SOURCE = "NOAA_CORAL_REEF_WATCH"
SOURCE_LABEL = "NOAA Coral Reef Watch"
ENDPOINT = "https://coastwatch.noaa.gov/erddap/"
GRIDDAP = "https://coastwatch.noaa.gov/erddap/griddap/"
INFO = "https://coastwatch.noaa.gov/erddap/info/"
PARSER_VERSION = "phase78-crw-1"
NORMALIZATION_VERSION = "phase78-normalize-1"
CONVERSION_VERSION = "phase78-celsius-labels-1"

AVAILABLE_PRODUCTS: dict[str, dict[str, str]] = {
    "noaacrwsstDaily": {
        "what": "crw_coraltemp_sst",
        "variable": "analysed_sst",
        "version": "CoralTemp-v3.1",
        "product_version_attr": "3.1",
        "method": "CRW CoralTemp gap-filled foundation SST",
        "scientific_role": "temperature_indicator",
        "native_unit_example": "degree_C",
    },
    "noaacrwsstanomalyDaily": {
        "what": "crw_sst_anomaly_v31",
        "variable": "sea_surface_temperature_anomaly",
        "version": "Satellite_Daily_Global_5km_SST_Anomaly",
        "product_version_attr": "3.1",
        "method": "CRW v3.1 SST anomaly",
        "scientific_role": "anomaly_indicator",
        "native_unit_example": "degree_C",
    },
    "noaacrwsstanomalybaselineDaily": {
        "what": "crw_sst_anomaly_1991_2020",
        "variable": "sea_surface_temperature_anomaly",
        "version": "1991-2020 climatological baseline",
        "product_version_attr": "3.1",
        "method": "CRW SST anomaly on the 1991-2020 baseline",
        "scientific_role": "anomaly_indicator",
        "native_unit_example": "degree_Celsius",
    },
    "noaacrwhotspotDaily": {
        "what": "crw_hotspot",
        "variable": "hotspot",
        "version": "Satellite_Daily_Global_5km_Coral_Bleaching_HotSpot",
        "product_version_attr": "3.1",
        "method": "CRW HotSpot grid as published on this ERDDAP dataset",
        "scientific_role": "thermal_stress_indicator",
        "native_unit_example": "degree_C",
    },
    "noaacrwdhwDaily": {
        "what": "crw_dhw",
        "variable": "degree_heating_week",
        "version": "Satellite_Daily_Global_5km_Degree_Heating_Week",
        "product_version_attr": "3.1",
        "method": "CRW Degree Heating Week grid",
        "scientific_role": "accumulated_thermal_stress_indicator",
        "native_unit_example": "degree_Celsius_weeks",
    },
    "noaacrwbaa7dDaily": {
        "what": "crw_bleaching_alert_area_7d",
        "variable": "bleaching_alert_area",
        "version": "Satellite_Daily_Global_5km_7day_Maximum_Bleaching_Alert_Area_Composite",
        "product_version_attr": "3.1",
        "method": "CRW 7-day maximum Bleaching Alert Area, external class code",
        "scientific_role": "external_noaa_alert_area_indicator",
        "native_unit_example": "stress_level",
        "baliza_alert": "NO",
    },
}

NOT_AVAILABLE_PRODUCTS: dict[str, dict[str, str]] = {
    "crw_7day_sst_trend": {
        "status": "NOT_AVAILABLE",
        "reason": "Not in the verified CoastWatch ERDDAP CRW list. Product page exists; no file retrieved.",
        "scientific_role": "temporal_change_indicator",
    },
    "crw_bleaching_alert_area_daily": {
        "status": "NOT_AVAILABLE",
        "reason": "Single-day BAA not retrieved. Only the 7-day composite dataset was stored.",
        "scientific_role": "external_noaa_alert_area_indicator",
    },
    "crw_mmm_climatology": {
        "status": "NOT_AVAILABLE",
        "reason": "MMM climatology grid was not obtained as a file in the verified ERDDAP list.",
        "scientific_role": "reference_baseline_indicator",
    },
}

DEMO_SPOT = {
    "spot_id": "DEMO-CRW-ORIG24-HERITAGE-POINT",
    "label": "DEMONSTRATION / RESEARCH TEST SPOT",
    "geometry_type": "POINT",
    "latitude": -23.5,
    "longitude": 152.0,
    "crs": "UNKNOWN",
    "spatial_precision": "UNKNOWN",
    "source": "NOAA orig24_names.txt heritage coordinate. Not a resort survey.",
}

CANDIDATE_CENTERS = (
    (-23.475, 151.975),
    (-23.475, 152.025),
    (-23.525, 151.975),
    (-23.525, 152.025),
)
RETRIEVED_CENTER = (-23.475, 151.975)
GRID_TIME = "2026-09-26T12:00:00Z"
