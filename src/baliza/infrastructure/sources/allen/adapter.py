"""Allen Coral Atlas adapter over verified WFS attribute extracts.

Maps stay CONTEXT_ONLY. Geometry was not stored, so polygon overlay is not claimed.
No credential is used. Raw files are never overwritten.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from baliza.infrastructure.sources.allen.catalog import (
    AVAILABLE_LAYERS,
    ATTRIBUTION,
    ENDPOINT,
    LICENSE,
    NORMALIZATION_VERSION,
    NOT_AVAILABLE_PRODUCTS,
    PARSER_VERSION,
    REQUEST_BBOX,
    SERVICE_DEFAULT_CRS,
    SOURCE,
    SOURCE_LABEL,
    WFS_VERSION,
)
from baliza.infrastructure.sources.crw.raw_store import sha256_file


class AllenAdapterError(ValueError):
    """An Allen artifact could not be used. No substitute class is invented."""


class AllenAdapter:
    def discover(self, *, live: bool = False) -> dict:
        return {
            "source": SOURCE,
            "endpoint": ENDPOINT,
            "service_type": "WFS",
            "wfs_version": WFS_VERSION,
            "discovery_mode": "VERIFIED_CATALOG" if not live else "LIVE_NOT_RUN",
            "authentication": "None required for the verified WFS attribute reads.",
            "portal_login": "Not used. Automation of the website package download is not permitted.",
            "available": [
                {"type_name": type_name, **meta, "status": "AVAILABLE"}
                for type_name, meta in AVAILABLE_LAYERS.items()
            ],
            "not_available": [
                {"product_id": product_id, **meta} for product_id, meta in NOT_AVAILABLE_PRODUCTS.items()
            ],
            "license": LICENSE,
            "attribution": ATTRIBUTION,
            "service_default_crs": SERVICE_DEFAULT_CRS,
            "request_bbox": REQUEST_BBOX,
        }

    def validate(self, path: Path) -> dict:
        if not path.is_file():
            raise AllenAdapterError(f"Allen raw file is missing: {path.name}")
        payload = json.loads(path.read_text(encoding="utf-8"))
        if payload.get("type") != "FeatureCollection":
            raise AllenAdapterError("Allen extract is not a FeatureCollection.")
        features = payload.get("features")
        if not isinstance(features, list):
            raise AllenAdapterError("Allen extract has no feature list.")
        matched = payload.get("numberMatched")
        returned = payload.get("numberReturned", len(features))
        if matched is not None and returned != matched:
            raise AllenAdapterError("Allen extract is truncated relative to numberMatched.")
        return {
            "ok": True,
            "numberMatched": matched,
            "numberReturned": returned,
            "feature_crs": payload.get("crs") if payload.get("crs") else "UNKNOWN",
            "timeStamp": payload.get("timeStamp", "UNKNOWN"),
        }

    def parse(self, path: Path, type_name: str) -> dict:
        meta = AVAILABLE_LAYERS[type_name]
        validation = self.validate(path)
        payload = json.loads(path.read_text(encoding="utf-8"))
        classes = []
        geometries_present = 0
        for feature in payload["features"]:
            properties = feature.get("properties") or {}
            if "class_name" not in properties:
                raise AllenAdapterError("Allen feature is missing class_name.")
            if feature.get("geometry") is not None:
                geometries_present += 1
            classes.append(
                {
                    "class_name": properties["class_name"],
                    "area_sqkm": properties.get("area_sqkm"),
                    "feature_id": feature.get("id", "UNKNOWN"),
                    "geometry": feature.get("geometry"),
                }
            )
        counts = Counter(item["class_name"] for item in classes)
        return {
            "type_name": type_name,
            "product": meta["product"],
            "layer": meta["layer"],
            "classes": classes,
            "class_counts": dict(sorted(counts.items())),
            "geometry_present_count": geometries_present,
            "validation": validation,
            "epoch": "UNKNOWN",
            "product_version": "UNKNOWN",
            "native_resolution": "UNKNOWN",
            "feature_crs": validation["feature_crs"],
            "service_default_crs": SERVICE_DEFAULT_CRS,
            "map_epoch_is_observation_time": False,
        }

    def normalize(self, parsed: dict) -> dict:
        meta = AVAILABLE_LAYERS[parsed["type_name"]]
        return {
            "source": SOURCE,
            "source_label": SOURCE_LABEL,
            "product": parsed["product"],
            "layer": parsed["layer"],
            "type_name": parsed["type_name"],
            "class_counts": parsed["class_counts"],
            "feature_count": len(parsed["classes"]),
            "unit": "class_name / area_sqkm where present",
            "original_unit": "class_name",
            "canonical_unit": None,
            "conversion": "none",
            "conversion_applied": False,
            "scientific_layer": meta["epistemic"],
            "epistemic_label": "FACT",
            "scientific_role": meta["scientific_role"],
            "transformation_type": meta["transformation_type"],
            "transformation_origin": meta["transformation_origin"],
            "measured": False,
            "field_observation": False,
            "estimated": "NONE",
            "epoch": parsed["epoch"],
            "product_version": parsed["product_version"],
            "native_resolution": parsed["native_resolution"],
            "feature_crs": parsed["feature_crs"],
            "service_default_crs": parsed["service_default_crs"],
            "spatial_precision": "UNKNOWN",
            "temporal_precision": "UNKNOWN",
            "temporal_semantics": "MAP_EPOCH",
            "map_epoch_is_observation_time": False,
            "observation_time": "UNKNOWN",
            "quality": {
                "source_quality": "UNKNOWN",
                "baliza_quality": "UNKNOWN",
                "association_quality": "UNKNOWN",
            },
            "uncertainty": {
                "measurement": "UNKNOWN",
                "spatial": "UNKNOWN",
                "temporal": "UNKNOWN",
                "association": "UNKNOWN",
                "model": "UNKNOWN",
            },
            "note": meta["note"],
            "parser_version": PARSER_VERSION,
            "normalization_version": NORMALIZATION_VERSION,
        }

    def emit_provenance(
        self,
        *,
        type_name: str,
        raw_filename: str,
        raw_checksum: str,
        retrieval_timestamp: str,
        bytes_size: int,
    ) -> dict:
        meta = AVAILABLE_LAYERS[type_name]
        return {
            "source": SOURCE,
            "source_label": SOURCE_LABEL,
            "product": meta["product"],
            "layer": meta["layer"],
            "version": "UNKNOWN",
            "epoch": "UNKNOWN",
            "retrieval_timestamp": retrieval_timestamp,
            "source_url": ENDPOINT,
            "download_parameters": {
                "service": "WFS",
                "version": WFS_VERSION,
                "request": "GetFeature",
                "typeNames": type_name,
                "propertyName": "class_name,area_sqkm",
                "outputFormat": "application/json",
                "bbox": REQUEST_BBOX["bbox_param"],
                "crs": REQUEST_BBOX["crs"],
            },
            "file_format": "JSON",
            "raw_file": raw_filename,
            "raw_checksum_sha256": raw_checksum,
            "size": bytes_size,
            "content_type": "application/json",
            "license": LICENSE,
            "attribution": ATTRIBUTION,
            "parser_version": PARSER_VERSION,
            "normalization_version": NORMALIZATION_VERSION,
            "transformation_chain": ["RAW", "PARSE", "NORMALIZE"],
            "crs": {
                "source_crs": "UNKNOWN",
                "feature_crs": "UNKNOWN",
                "service_default_crs": SERVICE_DEFAULT_CRS,
                "normalized_crs": "UNKNOWN",
                "transformation": "NONE",
                "transformation_method": "NONE",
            },
        }

    def load_stored_layer(self, raw_dir: Path, provenance_path: Path, type_name: str) -> dict:
        if type_name not in AVAILABLE_LAYERS:
            raise AllenAdapterError(f"Layer is not in the verified available catalog: {type_name}")
        provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
        filename = AVAILABLE_LAYERS[type_name]["file"]
        checksums = {item["name"]: item for item in provenance["files"]}
        if filename not in checksums:
            raise AllenAdapterError(f"No stored checksum for {filename}")
        path = raw_dir / filename
        computed = sha256_file(path)
        if computed != checksums[filename]["sha256"]:
            raise AllenAdapterError(f"Checksum mismatch for {filename}")
        parsed = self.parse(path, type_name)
        normalized = self.normalize(parsed)
        retrieval = provenance["response_timestamps"].get(filename, provenance["retrieval_http_date"])
        return {
            "parsed": parsed,
            "normalized": normalized,
            "provenance": self.emit_provenance(
                type_name=type_name,
                raw_filename=filename,
                raw_checksum=computed,
                retrieval_timestamp=retrieval,
                bytes_size=checksums[filename]["bytes"],
            ),
        }
