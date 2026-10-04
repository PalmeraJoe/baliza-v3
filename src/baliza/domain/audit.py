from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from baliza.domain.hashing import require_aware
from baliza.domain.ids import ActorId, AuditEventId


@dataclass(frozen=True, slots=True)
class AuditEvent:
    """Business audit record. Not an application log."""

    id: AuditEventId
    occurred_at: datetime
    action: str
    entity_type: str
    entity_id: str
    actor_id: ActorId | None = None
    system_component: str | None = None
    entity_version: str | None = None
    reason: str | None = None
    context: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        require_aware(self.occurred_at, "occurred_at")
        if self.actor_id is None and not self.system_component:
            raise ValueError("AuditEvent requires actor_id or system_component.")


def audit(
    *,
    occurred_at: datetime,
    action: str,
    entity_type: str,
    entity_id: str,
    actor_id: ActorId | None = None,
    system_component: str | None = None,
    entity_version: str | None = None,
    reason: str | None = None,
    context: dict[str, Any] | None = None,
) -> AuditEvent:
    return AuditEvent(
        id=AuditEventId(),
        occurred_at=occurred_at,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        actor_id=actor_id,
        system_component=system_component,
        entity_version=entity_version,
        reason=reason,
        context=context or {},
    )
