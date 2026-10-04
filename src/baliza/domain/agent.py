from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from baliza.domain.enums import EpistemicLabel
from baliza.domain.hashing import require_aware
from baliza.domain.ids import AgentId, AgentRunId, AgentVersionId


@dataclass(frozen=True, slots=True)
class AgentRun:
    """Assistive execution only. Never a Decision (Invariant 5)."""

    id: AgentRunId
    agent_id: AgentId
    agent_version_id: AgentVersionId
    agent_version: str
    started_at: datetime
    completed_at: datetime | None
    epistemic_label: EpistemicLabel
    summary: str

    def __post_init__(self) -> None:
        require_aware(self.started_at, "started_at")

    def is_decision(self) -> bool:
        return False
