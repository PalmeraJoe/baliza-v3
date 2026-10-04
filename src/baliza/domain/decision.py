from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from baliza.domain.dss import DssContextSnapshot
from baliza.domain.errors import InvariantViolation, MissingActor, MissingSnapshot
from baliza.domain.hashing import require_aware
from baliza.domain.ids import ActorId, DecisionId, DssContextSnapshotId, DssPackageId


@dataclass(frozen=True, slots=True)
class Decision:
    id: DecisionId
    actor_id: ActorId
    dss_context_snapshot_id: DssContextSnapshotId
    dss_package_id: DssPackageId
    decided_at: datetime
    justification: str
    selected_option: str
    snapshot_hash: str

    def __post_init__(self) -> None:
        require_aware(self.decided_at, "decided_at")
        if not self.justification.strip():
            raise InvariantViolation("Decision justification is mandatory (Invariant 15).")


def record_decision(
    *,
    actor_id: ActorId | None,
    snapshot: DssContextSnapshot | None,
    decided_at: datetime,
    justification: str,
    selected_option: str,
) -> Decision:
    if actor_id is None:
        raise MissingActor("Decision requires a responsible Actor (Invariant 1).")
    if snapshot is None:
        raise MissingSnapshot("Decision requires DssContextSnapshot (Invariant 17).")
    if not justification.strip():
        raise InvariantViolation("Decision justification is mandatory (Invariant 15).")
    return Decision(
        id=DecisionId(),
        actor_id=actor_id,
        dss_context_snapshot_id=snapshot.id,
        dss_package_id=snapshot.dss_package_id,
        decided_at=decided_at,
        justification=justification.strip(),
        selected_option=selected_option,
        snapshot_hash=snapshot.content_hash,
    )
