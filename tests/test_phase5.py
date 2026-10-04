from datetime import UTC, datetime

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from baliza.domain.enums import ComparisonOp, DataQualityFacet, PublicationStatus, RuleOutcome, EvidenceKind
from baliza.domain.errors import PublishedVersionImmutable
from baliza.domain.ids import IndicatorId, IndicatorValueId, IndicatorVersionId, ObservationId, RuleId, RuleVersionId
from baliza.domain.indicator import Indicator, IndicatorValue, IndicatorVersion
from baliza.domain.quality import DataQuality
from baliza.domain.rule import Rule, RuleVersion, Threshold, evaluate_rule
from baliza.infrastructure.persistence.models import (
    Base,
    EvidencePackageItemRow,
    ImmutablePersistenceError,
    IndicatorValueObservationRow,
    IndicatorVersionRow,
    make_engine,
)
from baliza.infrastructure.persistence.repositories import SqlEvidenceRepository, SqlIndicatorRepository, SqlObservationRepository
from baliza.domain.evidence import EvidenceItem, EvidencePackage
from baliza.domain.enums import EpistemicLabel
from baliza.domain.ids import EvidenceItemId, EvidencePackageId
from baliza.domain.observation import Observation

NOW = datetime(2026, 9, 30, 12, 0, tzinfo=UTC)


def _value(facet: DataQualityFacet, number: float | None) -> IndicatorValue:
    return IndicatorValue(
        id=IndicatorValueId(),
        indicator_id=IndicatorId(),
        indicator_version_id=IndicatorVersionId(),
        indicator_version="1.0.0",
        computed_at=NOW,
        unit="demo",
        source_observation_ids=(ObservationId(),),
        quality=DataQuality(facet=facet),
        value=number,
    )


def test_unknown_is_not_insufficient_or_clear(published_rule) -> None:
    rule, version = published_rule
    unknown = evaluate_rule(rule=rule, version=version, indicator_value=_value(DataQualityFacet.UNKNOWN, 9.0), evaluated_at=NOW)
    insufficient = evaluate_rule(
        rule=rule, version=version, indicator_value=_value(DataQualityFacet.INSUFFICIENT, 9.0), evaluated_at=NOW
    )
    assert unknown.outcome is RuleOutcome.UNKNOWN
    assert unknown.outcome is not RuleOutcome.NOT_TRIGGERED
    assert unknown.outcome is not RuleOutcome.INSUFFICIENT_DATA
    assert insufficient.outcome is RuleOutcome.INSUFFICIENT_DATA
    assert insufficient.outcome is not RuleOutcome.NOT_TRIGGERED
    assert unknown.reason == "quality_not_determinable"
    assert insufficient.reason == "insufficient_sample"


def test_published_indicator_version_is_immutable() -> None:
    version = IndicatorVersion(
        id=IndicatorVersionId(),
        indicator_id=IndicatorId(),
        version="1.0.0",
        unit="demo",
        formula_kind="mean",
        status=PublicationStatus.DRAFT,
    )
    edited = version.with_formula("max")
    assert edited.formula_kind == "max"
    published = edited.publish()
    with pytest.raises(PublishedVersionImmutable):
        published.with_formula("sum")
    engine = make_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    indicator = Indicator(id=version.indicator_id, name="demo")
    with Session(engine) as session:
        SqlIndicatorRepository(session).add_definition(indicator, published)
        session.commit()
        row = session.get(IndicatorVersionRow, published.id.value)
        row.formula_kind = "sum"
        with pytest.raises(ImmutablePersistenceError):
            session.flush()
        session.rollback()
        session.delete(session.get(IndicatorVersionRow, published.id.value))
        with pytest.raises(ImmutablePersistenceError):
            session.flush()
        session.rollback()
        newer = IndicatorVersion(
            id=IndicatorVersionId(),
            indicator_id=indicator.id,
            version="2.0.0",
            unit="demo",
            formula_kind="sum",
            status=PublicationStatus.PUBLISHED,
        )
        SqlIndicatorRepository(session).add_definition(indicator, newer)
        session.commit()
        assert session.get(IndicatorVersionRow, published.id.value).formula_kind == "max"


def test_links_come_from_junction_not_notes() -> None:
    engine = make_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    observation = Observation(
        id=ObservationId(),
        variable="demo_metric",
        unit="demo",
        observed_at=NOW,
        processed_at=NOW,
        quality=DataQuality(facet=DataQualityFacet.VALID),
        value=1.0,
    )
    indicator = Indicator(id=IndicatorId(), name="demo")
    version = IndicatorVersion(
        id=IndicatorVersionId(),
        indicator_id=indicator.id,
        version="1.0.0",
        unit="demo",
        formula_kind="passthrough",
        status=PublicationStatus.PUBLISHED,
    )
    value = IndicatorValue(
        id=IndicatorValueId(),
        indicator_id=indicator.id,
        indicator_version_id=version.id,
        indicator_version="1.0.0",
        computed_at=NOW,
        unit="demo",
        source_observation_ids=(observation.id,),
        quality=DataQuality(facet=DataQualityFacet.VALID),
        value=1.0,
        notes=("metadata-only",),
    )
    item = EvidenceItem(
        id=EvidenceItemId(),
        kind=EvidenceKind.DATA_QUALITY,
        epistemic_label=EpistemicLabel.FACT,
        referenced_type="Observation",
        referenced_id=str(observation.id),
        created_at=NOW,
        narrative="quality_not_determinable",
    )
    package = EvidencePackage(
        id=EvidencePackageId(),
        subject="demo",
        item_ids=(item.id,),
        assembled_at=NOW,
        incomplete=False,
    )
    with Session(engine) as session:
        SqlObservationRepository(session).add(observation)
        repo = SqlIndicatorRepository(session)
        repo.add_definition(indicator, version)
        repo.add_value(value)
        SqlEvidenceRepository(session).add_item(item)
        SqlEvidenceRepository(session).add_package(package)
        session.commit()
    with Session(engine) as session:
        loaded = SqlIndicatorRepository(session).get_value(value.id)
        assert loaded.source_observation_ids == (observation.id,)
        assert loaded.indicator_version_id == version.id
        from baliza.infrastructure.persistence.models import IndicatorValueRow

        stored = session.get(IndicatorValueRow, value.id.value)
        stored.notes = ["changed-metadata"]
        session.flush()
        assert SqlIndicatorRepository(session).get_value(value.id).source_observation_ids == (observation.id,)
        assert SqlIndicatorRepository(session).get_value(value.id).notes == ("changed-metadata",)
        items = SqlEvidenceRepository(session).items_for_package(package.id)
        assert items[0].narrative == "quality_not_determinable"
        assert session.query(EvidencePackageItemRow).count() == 1
