from datetime import UTC, datetime

import pytest

from baliza.domain.enums import EpistemicLabel, EvidenceKind
from baliza.domain.errors import InvariantViolation
from baliza.domain.evidence import EvidencePackage, item_from_ref
from baliza.domain.ids import EvidenceItemId, EvidencePackageId

NOW = datetime(2026, 9, 30, 12, 0, tzinfo=UTC)


def test_primary_vs_derived_and_labels() -> None:
    primary = item_from_ref(
        kind=EvidenceKind.PRIMARY,
        label=EpistemicLabel.FACT,
        referenced_type="Observation",
        referenced_id="obs-1",
        created_at=NOW,
    )
    derived = item_from_ref(
        kind=EvidenceKind.DERIVED,
        label=EpistemicLabel.FACT,
        referenced_type="IndicatorValue",
        referenced_id="ind-1",
        created_at=NOW,
    )
    assert primary.kind is EvidenceKind.PRIMARY
    assert derived.kind is EvidenceKind.DERIVED
    assert primary.epistemic_label is EpistemicLabel.FACT


def test_primary_cannot_be_inference() -> None:
    with pytest.raises(InvariantViolation):
        item_from_ref(
            kind=EvidenceKind.PRIMARY,
            label=EpistemicLabel.INFERENCE,
            referenced_type="Observation",
            referenced_id="obs-1",
            created_at=NOW,
        )


def test_empty_package_must_be_incomplete() -> None:
    with pytest.raises(InvariantViolation):
        EvidencePackage(
            id=EvidencePackageId(),
            subject="x",
            item_ids=(),
            assembled_at=NOW,
            incomplete=False,
        )


def test_package_traceability() -> None:
    item = item_from_ref(
        kind=EvidenceKind.PRIMARY,
        label=EpistemicLabel.FACT,
        referenced_type="Observation",
        referenced_id="obs-1",
        created_at=NOW,
        content_hash="abc",
    )
    pkg = EvidencePackage(
        id=EvidencePackageId(),
        subject="alert",
        item_ids=(item.id,),
        assembled_at=NOW,
    )
    assert item.id in pkg.item_ids
    assert item.referenced_id == "obs-1"
    assert item.content_hash == "abc"
