"""Raw CRW file preservation. Never overwrites an existing raw file."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


class RawOverwriteError(ValueError):
    """A raw CRW file already exists and may not be replaced."""


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def preserve_raw(raw_dir: Path, filename: str, payload: bytes, *, allow_existing_match: bool = True) -> dict:
    """Write a raw body only if the path is free, or if an identical file is already there."""
    raw_dir.mkdir(parents=True, exist_ok=True)
    path = raw_dir / filename
    digest = sha256_bytes(payload)
    if path.exists():
        existing = sha256_file(path)
        if existing == digest and allow_existing_match:
            return {
                "path": str(path).replace("\\", "/"),
                "filename": filename,
                "sha256": digest,
                "bytes": path.stat().st_size,
                "written": False,
                "status": "ALREADY_PRESENT",
            }
        raise RawOverwriteError(f"Raw file already exists and must not be overwritten: {filename}")
    path.write_bytes(payload)
    return {
        "path": str(path).replace("\\", "/"),
        "filename": filename,
        "sha256": digest,
        "bytes": len(payload),
        "written": True,
        "status": "STORED",
    }


def load_provenance(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def verify_stored_checksums(raw_dir: Path, provenance_path: Path) -> list[dict]:
    provenance = load_provenance(provenance_path)
    rows = []
    for item in provenance["files"]:
        path = raw_dir / item["name"]
        computed = sha256_file(path)
        rows.append(
            {
                "name": item["name"],
                "stored": item["sha256"],
                "computed": computed,
                "match": computed == item["sha256"],
            }
        )
    return rows
