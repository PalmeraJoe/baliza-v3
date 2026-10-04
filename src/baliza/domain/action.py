from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Mapping

from baliza.domain.errors import ActionWithoutDecision
from baliza.domain.hashing import freeze_value, require_aware
from baliza.domain.ids import ActionId, ActorId, DecisionId, OutcomeId


@dataclass(frozen=True, slots=True)
class Action:
    id: ActionId
    decision_id: DecisionId
    acted_at: datetime
    description: str
    action_type: str = "recorded_step"
    recorded_by: ActorId | None = None
    status: str = "recorded"
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        require_aware(self.acted_at, "acted_at")
        if self.decision_id is None:
            raise ActionWithoutDecision("Action requires a Decision (Invariant 2).")
        if not self.action_type.strip():
            raise ActionWithoutDecision("Action requires an action_type.")
        object.__setattr__(self, "metadata", freeze_value(self.metadata))


def record_action(
    *,
    decision_id: DecisionId | None,
    acted_at: datetime,
    description: str,
    recorded_by: ActorId | None = None,
    action_type: str = "recorded_step",
    metadata: Mapping[str, Any] | None = None,
) -> Action:
    if decision_id is None:
        raise ActionWithoutDecision("Action requires a Decision (Invariant 2).")
    return Action(
        id=ActionId(),
        decision_id=decision_id,
        acted_at=acted_at,
        description=description,
        action_type=action_type,
        recorded_by=recorded_by,
        metadata=metadata or {},
    )


@dataclass(frozen=True, slots=True)
class Outcome:
    id: OutcomeId
    action_id: ActionId
    decision_id: DecisionId
    observed_outcome_at: datetime
    notes: str
    observation_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        require_aware(self.observed_outcome_at, "observed_outcome_at")


def record_outcome(
    *,
    action_id: ActionId,
    decision_id: DecisionId,
    observed_outcome_at: datetime,
    notes: str,
) -> Outcome:
    return Outcome(
        id=OutcomeId(),
        action_id=action_id,
        decision_id=decision_id,
        observed_outcome_at=observed_outcome_at,
        notes=notes,
    )
