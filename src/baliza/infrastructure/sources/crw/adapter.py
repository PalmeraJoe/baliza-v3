"""NOAA Coral Reef Watch adapter.

discover / retrieve / validate / parse / normalize / extract_metadata / emit_provenance

CRW grid values stay EXTERNAL_INDICATOR. They are never Spot MEASURED values.
No averaging, interpolation, nearest-cell pick, downscaling, or alert threshold.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass
from pathlib import Path

from baliza.infrastructure.sources.crw.catalog import (
    AVAILABLE_PRODUCTS,
    CONVERSION_VERSION,
    ENDPOINT,
    GRIDDAP,
    INFO,
    NORMALIZATION_VERSION,
    NOT_AVAILABLE_PRODUCTS,
    PARSER_VERSION,
    SOURCE,
    SOURCE_LABEL,
)
from baliza.infrastructure.sources.crw.raw_store import preserve_raw, sha256_bytes, sha256_file

CELSIUS_LABELS = {"degree_C", "degree_Celsius"}
USER_AGENT = "BALIZA-V3-CRW-adapter/phase78"


class CrwAdapterError(ValueError):
    """A CRW file or response could not be used. No substitute value is invented."""


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
    scientific_layer: str
    epistemic_label: str
    scientific_role: str
    baliza_alert: str
    parser_version: str
    normalization_version: str


class CrwAdapter:
    """Source-specific CRW adapter. Domain code does not import this module's internals."""

    def discover(self, *, live: bool = False) -> dict:
        catalog = {
            "source": SOURCE,
            "endpoint": ENDPOINT,
            "available": [
                {
                    "dataset_id": dataset_id,
                    **meta,
                    "status": "AVAILABLE",
                }
                for dataset_id, meta in AVAILABLE_PRODUCTS.items()
            ],
            "not_available": [
                {"product_id": product_id, **meta} for product_id, meta in NOT_AVAILABLE_PRODUCTS.items()
            ],
            "live_probe": None,
        }
        if not live:
            catalog["discovery_mode"] = "VERIFIED_CATALOG"
            return catalog
        url = ENDPOINT + "search/index.json?searchFor=noaa%20crw&page=1&itemsPerPage=20"
        request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                body = response.read()
                catalog["live_probe"] = {
                    "url": url,
                    "http_status": response.status,
                    "sha256": sha256_bytes(body),
                }
        except urllib.error.HTTPError as exc:
            catalog["live_probe"] = {"url": url, "http_status": exc.code, "error": "HTTPError"}
        except OSError as exc:
            catalog["live_probe"] = {"url": url, "http_status": None, "error": type(exc).__name__}
        catalog["discovery_mode"] = "LIVE_PROBE"
        return catalog

    def retrieve(
        self,
        dataset_id: str,
        *,
        time: str,
        latitude: float,
        longitude: float,
        raw_dir: Path | None = None,
        filename: str | None = None,
        live: bool = False,
        existing_text: str | None = None,
    ) -> dict:
        if dataset_id not in AVAILABLE_PRODUCTS:
            raise CrwAdapterError(f"Dataset is not in the verified available catalog: {dataset_id}")
        variable = AVAILABLE_PRODUCTS[dataset_id]["variable"]
        query = (
            f"{dataset_id}.csv?"
            f"{variable}%5B({time})%5D%5B({latitude}):({latitude})%5D%5B({longitude}):({longitude})%5D"
        )
        url = GRIDDAP + query
        if existing_text is not None:
            payload = existing_text.encode("utf-8")
            source_mode = "SUPPLIED_BODY"
        elif not live:
            if raw_dir is None or filename is None:
                raise CrwAdapterError("Offline retrieve needs raw_dir and filename, or existing_text.")
            path = raw_dir / filename
            if not path.is_file():
                raise CrwAdapterError(f"Raw CRW file is missing: {filename}")
            payload = path.read_bytes()
            source_mode = "RAW_STORE"
        else:
            request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "text/csv"})
            with urllib.request.urlopen(request, timeout=90) as response:
                payload = response.read()
            source_mode = "LIVE_DOWNLOAD"
            if raw_dir is not None and filename is not None:
                preserve_raw(raw_dir, filename, payload)
        return {
            "dataset_id": dataset_id,
            "source_url": url,
            "download_parameters": {
                "time": time,
                "latitude": latitude,
                "longitude": longitude,
                "variable": variable,
            },
            "file_format": "CSV",
            "payload": payload,
            "sha256": sha256_bytes(payload),
            "source_mode": source_mode,
        }

    def validate(self, payload: bytes, dataset_id: str) -> dict:
        text = payload.decode("utf-8")
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        if len(lines) < 3:
            raise CrwAdapterError("CRW CSV has no data row.")
        header = lines[0].split(",")
        product = AVAILABLE_PRODUCTS[dataset_id]
        if header[:3] != ["time", "latitude", "longitude"] or len(header) != 4:
            raise CrwAdapterError("CRW CSV header is not a single-variable griddap table.")
        if header[3] != product["variable"]:
            raise CrwAdapterError("CRW CSV variable does not match the dataset id.")
        return {"ok": True, "rows": len(lines) - 2, "variable": header[3]}

    def parse(self, payload: bytes, dataset_id: str) -> list[CanonicalRecord]:
        self.validate(payload, dataset_id)
        product = AVAILABLE_PRODUCTS[dataset_id]
        lines = [line.strip() for line in payload.decode("utf-8").splitlines() if line.strip()]
        units = lines[1].split(",")
        records: list[CanonicalRecord] = []
        for line in lines[2:]:
            fields = line.split(",")
            if len(fields) != 4 or any(field == "" for field in fields):
                raise CrwAdapterError("CRW CSV data row is malformed.")
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
                    raise CrwAdapterError("HotSpot value is not numeric.") from exc
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
                    source=SOURCE_LABEL,
                    source_product=dataset_id,
                    source_version=product["version"],
                    resolution="ERDDAP geospatial resolution attribute 0.049999999999999996 degrees",
                    method=product["method"],
                    source_provided_quality="UNKNOWN",
                    baliza_quality=baliza_quality,
                    quality_note=quality_note,
                    uncertainty="UNKNOWN",
                    transformation_type="DERIVED",
                    spatial_precision="GRID",
                    temporal_precision="DAY",
                    spatial_relation="UNKNOWN",
                    scientific_layer="EXTERNAL_INDICATOR",
                    epistemic_label="FACT",
                    scientific_role=product["scientific_role"],
                    baliza_alert=product.get("baliza_alert", "NO"),
                    parser_version=PARSER_VERSION,
                    normalization_version=NORMALIZATION_VERSION,
                )
            )
        if not records:
            raise CrwAdapterError("CRW CSV produced no records.")
        return records

    def normalize(self, record: CanonicalRecord) -> dict:
        return {
            "where": {"latitude": record.where_latitude, "longitude": record.where_longitude},
            "when": record.when,
            "what": record.what,
            "value": record.value,
            "unit": record.original_unit,
            "original_unit": record.original_unit,
            "canonical_unit": record.canonical_unit,
            "conversion": record.conversion,
            "conversion_version": record.conversion_version,
            "source": SOURCE,
            "source_label": record.source,
            "source_product": record.source_product,
            "source_version": record.source_version,
            "resolution": record.resolution,
            "method": record.method,
            "quality": {
                "source_quality": record.source_provided_quality,
                "baliza_quality": record.baliza_quality,
                "association_quality": "UNKNOWN",
                "quality_note": record.quality_note,
            },
            "uncertainty": record.uncertainty,
            "provenance": {
                "source": SOURCE,
                "product": record.source_product,
                "version": record.source_version,
                "parser_version": record.parser_version,
                "normalization_version": record.normalization_version,
            },
            "transformation_type": record.transformation_type,
            "spatial_precision": record.spatial_precision,
            "temporal_precision": record.temporal_precision,
            "scientific_layer": record.scientific_layer,
            "epistemic_label": record.epistemic_label,
            "scientific_role": record.scientific_role,
            "baliza_alert": record.baliza_alert,
            "measured": False,
            "estimated": "NONE",
        }

    def extract_metadata(self, dataset_id: str, info_path: Path | None = None) -> dict:
        meta = {
            "dataset_id": dataset_id,
            "product": AVAILABLE_PRODUCTS.get(dataset_id, {}),
            "info_url": INFO + f"{dataset_id}/index.json",
            "product_version_attr": AVAILABLE_PRODUCTS.get(dataset_id, {}).get("product_version_attr", "UNKNOWN"),
        }
        if info_path is None or not info_path.is_file():
            return meta
        payload = json.loads(info_path.read_text(encoding="utf-8"))
        attrs = {}
        for row in payload.get("rows") or []:
            if len(row) >= 5 and row[0] == "attribute" and row[1] == "NC_GLOBAL":
                attrs[row[2]] = row[4]
        meta["global_attributes"] = {
            key: attrs[key]
            for key in ("product_version", "id", "geospatial_lat_resolution", "date_created")
            if key in attrs
        }
        return meta

    def emit_provenance(
        self,
        *,
        dataset_id: str,
        raw_filename: str,
        raw_checksum: str,
        retrieval_timestamp: str,
        source_url: str,
        download_parameters: dict,
        source_mode: str,
    ) -> dict:
        return {
            "source": SOURCE,
            "source_label": SOURCE_LABEL,
            "product": dataset_id,
            "product_version": AVAILABLE_PRODUCTS[dataset_id]["version"],
            "retrieval_timestamp": retrieval_timestamp,
            "source_url": source_url,
            "download_parameters": download_parameters,
            "file_format": "CSV",
            "raw_file": raw_filename,
            "raw_checksum_sha256": raw_checksum,
            "source_mode": source_mode,
            "parser_version": PARSER_VERSION,
            "normalization_version": NORMALIZATION_VERSION,
            "transformation_chain": ["RAW", "PARSE", "NORMALIZE"],
            "crs": "UNKNOWN",
        }

    def load_stored_product(
        self,
        raw_dir: Path,
        provenance_path: Path,
        dataset_id: str,
        grid_day: str = "2026-09-26",
    ) -> dict:
        provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
        filename = f"{dataset_id}_{grid_day}.csv"
        checksums = {item["name"]: item["sha256"] for item in provenance["files"]}
        if filename not in checksums:
            raise CrwAdapterError(f"No stored checksum for {filename}")
        path = raw_dir / filename
        payload = path.read_bytes()
        computed = sha256_file(path)
        if computed != checksums[filename]:
            raise CrwAdapterError(f"Checksum mismatch for {filename}")
        records = self.parse(payload, dataset_id)
        normalized = [self.normalize(record) for record in records]
        retrieved = self.retrieve(
            dataset_id,
            time=provenance["request"]["time"],
            latitude=provenance["request"]["latitude"],
            longitude=provenance["request"]["longitude"],
            raw_dir=raw_dir,
            filename=filename,
            live=False,
        )
        return {
            "records": [asdict(record) for record in records],
            "normalized": normalized,
            "provenance": self.emit_provenance(
                dataset_id=dataset_id,
                raw_filename=filename,
                raw_checksum=computed,
                retrieval_timestamp=provenance["retrieval_calendar_date"],
                source_url=retrieved["source_url"],
                download_parameters=retrieved["download_parameters"],
                source_mode=retrieved["source_mode"],
            ),
            "metadata": self.extract_metadata(dataset_id, raw_dir / "metadata" / f"{dataset_id}.info.json"),
        }
