from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from types import MappingProxyType
from typing import Any, Mapping


def utc_now() -> datetime:
    return datetime.now(UTC)


def require_aware(ts: datetime, field: str) -> datetime:
    if ts.tzinfo is None:
        raise ValueError(f"{field} must be timezone-aware (UTC preferred).")
    return ts


def freeze_value(value: Any) -> Any:
    """Recursively copy into read-only structures. Integrity, not authentication."""
    if isinstance(value, MappingProxyType):
        return MappingProxyType({k: freeze_value(v) for k, v in value.items()})
    if isinstance(value, Mapping):
        return MappingProxyType({str(k): freeze_value(v) for k, v in value.items()})
    if isinstance(value, (list, tuple)):
        return tuple(freeze_value(v) for v in value)
    if isinstance(value, (set, frozenset)):
        return frozenset(freeze_value(v) for v in value)
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    raise TypeError(f"Cannot freeze value of type {type(value).__name__}")


def canonical_for_hash(value: Any) -> Any:
    """JSON-ready form: mappings sorted, sequences as lists, sets sorted."""
    if isinstance(value, Mapping):
        return {str(k): canonical_for_hash(v) for k, v in sorted(value.items(), key=lambda kv: str(kv[0]))}
    if isinstance(value, (list, tuple)):
        return [canonical_for_hash(v) for v in value]
    if isinstance(value, (set, frozenset)):
        return sorted((canonical_for_hash(v) for v in value), key=lambda v: json.dumps(v, sort_keys=True))
    return value


def sha256_canonical(payload: Any) -> str:
    raw = json.dumps(
        canonical_for_hash(payload),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()
