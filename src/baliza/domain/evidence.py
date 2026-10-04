from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from baliza.domain.enums import EpistemicLabel, EvidenceKind
from baliza.domain.errors import InvariantViolation
from baliza.domain.hashing import require_aware
from baliza.domain.ids import EvidenceItemId, EvidencePackageId


@dataclass(frozen=True, slots=True)
class EvidenceItem:
    id: EvidenceItemId
    kind: EvidenceKind
    epistemic_label: EpistemicLabel
    referenced_type: str
    referenced_id: str
    created_at: datetime
    content_hash: str | None = None
    object_key: str | None = None
    narrative: str | None = None
    uncertainty_notes: str | None = None

    def __post_init__(self) -> None:
        require_aware(self.created_at, "created_at")
        if not self.referenced_id:
            raise InvariantViolation("EvidenceItem requires a referenced artifact (Invariant 13).")
        if self.kind == EvidenceKind.PRIMARY and self.epistemic_label not in {
            EpistemicLabel.FACT,
        }:
            raise InvariantViolation("Primary evidence must be labeled FACT.")


@dataclass(frozen=True, slots=True)
class EvidencePackage:
    id: EvidencePackageId
    subject: str
    item_ids: tuple[EvidenceItemId, ...]
    assembled_at: datetime
    assembler_version: str = "baliza.evidence.v1"
    gaps: tuple[str, ...] = field(default_factory=tuple)
    conflicts: tuple[str, ...] = field(default_factory=tuple)
    incomplete: bool = False

    def __post_init__(self) -> None:
        require_aware(self.assembled_at, "assembled_at")
        if not self.item_ids and not self.incomplete:
            raise InvariantViolation(
                "Empty EvidencePackage must be marked incomplete (never silent empty)."
            )


def item_from_ref(
    *,
    kind: EvidenceKind,
    label: EpistemicLabel,
    referenced_type: str,
    referenced_id: str,
    created_at: datetime,
    content_hash: str | None = None,
    narrative: str | None = None,
) -> EvidenceItem:
    return EvidenceItem(
        id=EvidenceItemId(),
        kind=kind,
        epistemic_label=label,
        referenced_type=referenced_type,
        referenced_id=referenced_id,
        created_at=created_at,
        content_hash=content_hash,
        narrative=narrative,
    )
