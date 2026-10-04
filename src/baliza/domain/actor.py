from __future__ import annotations

from dataclasses import dataclass

from baliza.domain.ids import ActorId


@dataclass(frozen=True, slots=True)
class Actor:
    """Domain identity. Not an IdP user record (ADR-008)."""

    id: ActorId
    display_name: str
    active: bool = True
