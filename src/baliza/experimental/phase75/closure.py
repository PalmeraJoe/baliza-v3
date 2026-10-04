"""EXPERIMENTAL / PHASE 7.5.2. Provenance and checks over stored Allen files.

Does not download, associate a spot, or estimate a local value.
"""

from __future__ import annotations

import hashlib
import json
from xml.etree import ElementTree as ET

from baliza.experimental.phase75.allen import TERMS_URL

NORMALIZATION_VERSION = "phase75.2-none-1"
PARSER_VERSION = "phase75.2-allen-record-1"

BENTHIC_URL = (
    "https://allencoralatlas.org/geoserver/ows?service=WFS&version=2.0.0"
    "&request=GetFeature&typeNames=coral-atlas:benthic_data_verbose"
    "&propertyName=class_name,area_sqkm&outputFormat=application/json"
    "&bbox=-23.48,151.97,-23.47,151.98,urn:ogc:def:crs:EPSG::4326"
)
GEOMORPHIC_URL = (
    "https://allencoralatlas.org/geoserver/ows?service=WFS&version=2.0.0"
    "&request=GetFeature&typeNames=coral-atlas:geomorphic_data_verbose"
    "&propertyName=class_name,area_sqkm&outputFormat=application/json"
    "&bbox=-23.48,151.97,-23.47,151.98,urn:ogc:def:crs:EPSG::4326"
)

EPISTEMIC = {
    "benthic": "CONTEXT_ONLY",
    "geomorphic": "CONTEXT_ONLY",
    "bathymetry": "NOT_AVAILABLE",
    "turbidity": "NOT_AVAILABLE",
    "reef_mask": "NOT_AVAILABLE",
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def content_fingerprint(text: str) -> list[tuple[str, float | None]]:
    """Class and area only. Feature ids and the service timestamp are excluded."""
    payload = json.loads(text)
    rows: list[tuple[str, float | None]] = []
    for feature in payload["features"]:
        properties = feature["properties"]
        area = properties.get("area_sqkm")
        rows.append((str(properties["class_name"]), float(area) if isinstance(area, (int, float)) else None))
    return sorted(rows, key=lambda item: (item[0], item[1] is None, item[1] or 0.0))


def feature_file_crs(text: str) -> str:
    payload = json.loads(text)
    crs = payload.get("crs")
    return "UNKNOWN" if crs in (None, "") else str(crs)


def service_default_crs(capabilities_xml: str) -> dict[str, str]:
    root = ET.fromstring(capabilities_xml)
    found: dict[str, str] = {}
    for element in root.iter():
        if not element.tag.endswith("FeatureType"):
            continue
        name = ""
        crs = ""
        for child in element:
            if child.tag.endswith("Name") and child.text:
                name = child.text
            if child.tag.endswith("DefaultCRS") and child.text:
                crs = child.text
        if name and crs:
            found[name] = crs
    if not found:
        raise ValueError("WFS capabilities contain no feature-type CRS.")
    return found


def normalize_class(class_name: str) -> dict[str, str]:
    if not str(class_name).strip():
        raise ValueError("Missing class.")
    return {
        "original_value": class_name,
        "original_unit": "class",
        "canonical_value": class_name,
        "canonical_unit": "class",
        "conversion_method": "NONE",
        "conversion_version": NORMALIZATION_VERSION,
    }


def license_record() -> dict[str, str]:
    return {
        "maps_bathymetry_statistics": (
            "FAQ: © 2018-2023 Allen Coral Atlas Partnership and Arizona State University, CC BY 4.0"
        ),
        "research_citation": (
            "Allen Coral Atlas (2022). Imagery, maps and monitoring of the world's tropical coral reefs. "
            "https://doi.org/10.5281/zenodo.3833242"
        ),
        "satellite_mosaic": "Planet CC BY-NC-SA 4.0. Not retrieved.",
        "global_dataset": "FAQ: reproduction of the entire global habitat-map dataset needs prior written consent.",
        "website_automation": f"Terms of Use prohibit automated retrieval of the site. {TERMS_URL}",
        "wfs_status": (
            "FAQ publishes WFS for the habitat maps subject to the terms. "
            "Whether that sentence authorises every later automation is not decided here."
        ),
        "inside_feature_file": "UNKNOWN",
    }
