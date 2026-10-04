"""EXPERIMENTAL / PHASE 7.5.1. Allen WFS attributes only. Not on the critical path."""

from __future__ import annotations

import json
from dataclasses import dataclass

PARSER_VERSION = "phase75.1-allen-wfs-attributes-1"
SECRET_ENV_NAMES = (
    "ALLEN_CORAL_ATLAS_USERNAME",
    "ALLEN_CORAL_ATLAS_PASSWORD",
    "ALLEN_CORAL_ATLAS_TOKEN",
)

WFS_URL = "https://allencoralatlas.org/geoserver/ows"
WMS_CAPABILITIES = (
    "https://allencoralatlas.org/geoserver/ows?service=wms&version=1.3.0&request=GetCapabilities"
)
WFS_CAPABILITIES = (
    "https://allencoralatlas.org/geoserver/ows?service=wfs&version=2.0.0&request=GetCapabilities"
)
MAPS_URL = "https://allencoralatlas.org/mapping/maps"
TERMS_URL = "https://allencoralatlas.org/tou/"
ATTRIBUTION = (
    "Allen Coral Atlas maps, bathymetry and map statistics are © 2018-2023 "
    "Allen Coral Atlas Partnership and Arizona State University and licensed CC BY 4.0"
)

FAILURES = {
    "AUTHENTICATION_FAILED",
    "AUTHORIZATION_FAILED",
    "ENDPOINT_UNAVAILABLE",
    "PRODUCT_UNAVAILABLE",
    "AOI_UNAVAILABLE",
    "RATE_LIMITED",
    "AUTOMATION_NOT_PERMITTED",
    "DOWNLOAD_FAILED",
    "INVALID_FILE",
    "INVALID_METADATA",
    "LICENSE_RESTRICTION",
    "UNKNOWN_FAILURE",
}


class AllenAccessError(ValueError):
    def __init__(self, code: str, detail: str) -> None:
        if code not in FAILURES:
            code = "UNKNOWN_FAILURE"
        self.code = code
        super().__init__(f"{code}: {detail}")


@dataclass(frozen=True)
class AllenClassRecord:
    what: str
    value: str
    area_sqkm: float | None
    source: str
    source_product: str
    source_version: str
    unit: str
    transformation_type: str
    spatial_precision: str
    temporal_precision: str
    spatial_relation: str
    source_provided_quality: str
    method: str


def classify_http(status: int) -> str:
    if status == 401:
        return "AUTHENTICATION_FAILED"
    if status == 403:
        return "AUTHORIZATION_FAILED"
    if status == 404:
        return "PRODUCT_UNAVAILABLE"
    if status == 429:
        return "RATE_LIMITED"
    if status >= 500:
        return "ENDPOINT_UNAVAILABLE"
    return "DOWNLOAD_FAILED"


def discover() -> dict[str, str]:
    return {
        "wms_capabilities": WMS_CAPABILITIES,
        "wfs_capabilities": WFS_CAPABILITIES,
        "maps_metadata": MAPS_URL,
        "wfs_layers": "coral-atlas:benthic_data_verbose, coral-atlas:geomorphic_data_verbose",
        "portal_package_download": "AUTOMATION_NOT_PERMITTED",
        "bathymetry": "PRODUCT_UNAVAILABLE_ON_WFS",
        "turbidity": "PRODUCT_UNAVAILABLE_ON_WFS",
        "reef_mask": "PRODUCT_UNAVAILABLE_ON_WFS",
        "terms": TERMS_URL,
    }


def authenticate() -> dict[str, str]:
    """WFS and WMS answered without credentials. Portal login is not used."""
    return {
        "wfs_wms": "NOT_REQUIRED",
        "portal_login": "AUTOMATION_NOT_PERMITTED",
        "secrets_read": "no",
    }


def secret_variable_names() -> tuple[str, ...]:
    """Names only. Values are never read by this adapter."""
    return SECRET_ENV_NAMES


def portal_login_refused() -> AllenAccessError:
    return AllenAccessError(
        "AUTOMATION_NOT_PERMITTED",
        "The Atlas package download is a logged-in website flow. "
        "The terms prohibit automated retrieval of the site. Credentials are not sent.",
    )


def parse_wfs_attributes(text: str, product: str) -> list[AllenClassRecord]:
    if product not in {"benthic", "geomorphic"}:
        raise AllenAccessError("PRODUCT_UNAVAILABLE", "Only benthic and geomorphic WFS layers were retrieved.")
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise AllenAccessError("INVALID_FILE", "WFS body is not JSON.") from exc
    features = payload.get("features")
    if not isinstance(features, list) or not features:
        raise AllenAccessError("AOI_UNAVAILABLE", "WFS returned no features.")
    matched = payload.get("numberMatched")
    if matched is not None and matched != len(features):
        raise AllenAccessError(
            "INVALID_FILE",
            "The response is a truncated feature list and cannot be treated as the AOI.",
        )
    what = "allen_benthic_class" if product == "benthic" else "allen_geomorphic_class"
    records: list[AllenClassRecord] = []
    for feature in features:
        properties = feature.get("properties") or {}
        class_name = properties.get("class_name")
        if not class_name:
            raise AllenAccessError("INVALID_METADATA", "A feature has no class_name.")
        area = properties.get("area_sqkm")
        records.append(
            AllenClassRecord(
                what=what,
                value=str(class_name),
                area_sqkm=float(area) if isinstance(area, (int, float)) else None,
                source="Allen Coral Atlas",
                source_product=f"coral-atlas:{product}_data_verbose",
                source_version="WFS layer name; map version is not in the feature",
                unit="class",
                transformation_type="MODEL_ESTIMATED",
                spatial_precision="UNKNOWN",
                temporal_precision="map_epoch",
                spatial_relation="INTERSECTS",
                source_provided_quality="UNKNOWN",
                method=(
                    "Provider habitat map from remote sensing. Not a field observation "
                    "and not a BALIZA estimate. Geometry was not stored."
                ),
            )
        )
    return records
