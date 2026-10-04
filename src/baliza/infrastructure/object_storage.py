from __future__ import annotations


class InMemoryObjectStorage:
    def __init__(self) -> None:
        self._store: dict[str, bytes] = {}

    def put(self, key: str, data: bytes, content_type: str = "application/octet-stream") -> str:
        self._store[key] = data
        return key

    def get(self, key: str) -> bytes:
        return self._store[key]
