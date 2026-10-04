from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime

from baliza.domain.enums import AlertSeverity, AlertStatus
from baliza.domain.errors import InsufficientEvidence, InvalidTransition
from baliza.domain.hashing import require_aware
from baliza.domain.ids import AlertId, EvidencePackageId, RuleEvaluationId
from baliza.domain.quality import ScopeHealth


@dataclass(frozen=True, slots=True)
class AlertStatusChange:
    status: AlertStatus
    reviewed_at: datetime
    actor_id: str | None = None
    note: str | None = None


@dataclass(frozen=True, slots=True)
class Alert:
    id: AlertId
    severity: AlertSeverity
    status: AlertStatus
    alerted_at: datetime
    evidence_package_id: EvidencePackageId
    rule_evaluation_ids: tuple[RuleEvaluationId, ...]
    spatial_ref: str | None = None
    health: ScopeHealth = ScopeHealth.UNKNOWN
    reviewed_at: datetime | None = None
    history: tuple[AlertStatusChange, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        require_aware(self.alerted_at, "alerted_at")
        if self.severity == AlertSeverity.CRITICAL and self.evidence_package_id is None:
            raise InsufficientEvidence("Critical alerts require EvidencePackage (Invariant 3).")
        if not self.rule_evaluation_ids:
            raise InsufficientEvidence("Alerts on the critical path require RuleEvaluation.")

    def acknowledge(self, *, reviewed_at: datetime, actor_id: str) -> Alert:
        """Awareness only — does not create a Decision (Invariant 6)."""
        require_aware(reviewed_at, "reviewed_at")
        if self.status in {AlertStatus.CLOSED, AlertStatus.RETRACTED}:
            raise InvalidTransition("Cannot acknowledge a closed/retracted alert.")
        change = AlertStatusChange(
            status=AlertStatus.ACKNOWLEDGED,
            reviewed_at=reviewed_at,
            actor_id=actor_id,
            note="acknowledged",
        )
        return replace(
            self,
            status=AlertStatus.ACKNOWLEDGED,
            reviewed_at=reviewed_at,
            history=(*self.history, change),
        )

    def is_decision(self) -> bool:
        return False
