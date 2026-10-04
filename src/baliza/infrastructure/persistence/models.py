from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Index, Integer, String, Text, UniqueConstraint, Uuid, create_engine, event, inspect
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

from baliza.domain.alert import Alert, AlertStatusChange
from baliza.domain.audit import AuditEvent
from baliza.domain.decision import Decision
from baliza.domain.dss import DssContextSnapshot, DssPackage, RecommendationView
from baliza.domain.enums import (
    AlertSeverity,
    AlertStatus,
    ComparisonOp,
    DataQualityFacet,
    EpistemicLabel,
    EvidenceKind,
    PublicationStatus,
    RuleOutcome,
)
from baliza.domain.evidence import EvidenceItem, EvidencePackage
from baliza.domain.ids import (
    ActorId,
    AlertId,
    AuditEventId,
    DecisionId,
    DssContextSnapshotId,
    DssPackageId,
    EvidenceItemId,
    EvidencePackageId,
    IndicatorId,
    IndicatorValueId,
    IndicatorVersionId,
    ObservationId,
    RuleEvaluationId,
    RuleId,
    RuleVersionId,
)
from baliza.domain.indicator import IndicatorValue
from baliza.domain.observation import Observation
from baliza.domain.quality import DataQuality
from baliza.domain.rule import RuleEvaluation, Threshold


class Base(DeclarativeBase):
    pass


class ObservationRow(Base):
    __tablename__ = "observations"
    __table_args__ = (Index("ix_observations_observed_at", "observed_at"),)

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    variable: Mapped[str] = mapped_column(String(128))
    unit: Mapped[str] = mapped_column(String(32))
    value: Mapped[float | None] = mapped_column(Float, nullable=True)
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    processed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    quality_facet: Mapped[str] = mapped_column(String(32))
    quality_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    spatial_ref: Mapped[str | None] = mapped_column(String(256), nullable=True)
    metadata_json: Mapped[dict[str, Any]] = mapped_column("metadata", JSON, default=dict)


class IndicatorVersionRow(Base):
    __tablename__ = "indicator_versions"
    __table_args__ = (UniqueConstraint("indicator_id", "version", name="uq_indicator_version_identity"),)

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    indicator_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True))
    name: Mapped[str] = mapped_column(String(128))
    version: Mapped[str] = mapped_column(String(32))
    unit: Mapped[str] = mapped_column(String(32))
    formula_kind: Mapped[str] = mapped_column(String(64))
    baseline: Mapped[float | None] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(String(16))
    input_variable: Mapped[str | None] = mapped_column(String(128), nullable=True)


class IndicatorValueRow(Base):
    __tablename__ = "indicator_values"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    indicator_id: Mapped[UUID] = mapped_column()
    indicator_version_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("indicator_versions.id"), nullable=False
    )
    indicator_version: Mapped[str] = mapped_column(String(32))
    computed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    unit: Mapped[str] = mapped_column(String(32))
    value: Mapped[float | None] = mapped_column(Float, nullable=True)
    quality_facet: Mapped[str] = mapped_column(String(32))
    notes: Mapped[list[Any]] = mapped_column(JSON)


class RuleVersionRow(Base):
    __tablename__ = "rule_versions"
    __table_args__ = (UniqueConstraint("rule_id", "version", name="uq_rule_version_identity"),)

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    rule_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True))
    version: Mapped[str] = mapped_column(String(32))
    status: Mapped[str] = mapped_column(String(16))
    operator: Mapped[str] = mapped_column(String(8))
    threshold_name: Mapped[str] = mapped_column(String(64))
    thresholds: Mapped[dict[str, Any]] = mapped_column(JSON)
    severity_if_triggered: Mapped[str] = mapped_column(String(16))
    evaluator_engine_id: Mapped[str] = mapped_column(String(64))


class RuleEvaluationRow(Base):
    __tablename__ = "rule_evaluations"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    rule_id: Mapped[UUID] = mapped_column()
    rule_version_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("rule_versions.id"))
    rule_version: Mapped[str] = mapped_column(String(32))
    evaluated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    outcome: Mapped[str] = mapped_column(String(32))
    reason: Mapped[str] = mapped_column(Text)
    thresholds_applied: Mapped[dict[str, Any]] = mapped_column(JSON)
    input_snapshot: Mapped[dict[str, Any]] = mapped_column(JSON)
    evaluator_engine_id: Mapped[str] = mapped_column(String(64))


class EvidenceItemRow(Base):
    __tablename__ = "evidence_items"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    kind: Mapped[str] = mapped_column(String(32))
    epistemic_label: Mapped[str] = mapped_column(String(32))
    referenced_type: Mapped[str] = mapped_column(String(64))
    referenced_id: Mapped[str] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    content_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    narrative: Mapped[str | None] = mapped_column(Text, nullable=True)


class EvidencePackageRow(Base):
    __tablename__ = "evidence_packages"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    subject: Mapped[str] = mapped_column(String(256))
    assembled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    gaps: Mapped[list[Any]] = mapped_column(JSON)
    incomplete: Mapped[bool]


class AlertRow(Base):
    __tablename__ = "alerts"
    __table_args__ = (Index("ix_alerts_status", "status"),)

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    severity: Mapped[str] = mapped_column(String(16))
    status: Mapped[str] = mapped_column(String(32))
    alerted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    evidence_package_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("evidence_packages.id"), nullable=False
    )
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    history: Mapped[list[Any]] = mapped_column(JSON)
    health: Mapped[str] = mapped_column(String(32))


class DssPackageRow(Base):
    __tablename__ = "dss_packages"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    opened_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    payload: Mapped[dict[str, Any]] = mapped_column(JSON)


class DssSnapshotRow(Base):
    __tablename__ = "dss_context_snapshots"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    dss_package_id: Mapped[UUID] = mapped_column(ForeignKey("dss_packages.id"))
    frozen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    content_hash: Mapped[str] = mapped_column(String(64))
    payload: Mapped[dict[str, Any]] = mapped_column(JSON)
    object_key: Mapped[str | None] = mapped_column(String(256), nullable=True)


class DecisionRow(Base):
    __tablename__ = "decisions"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    actor_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    dss_context_snapshot_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("dss_context_snapshots.id"), nullable=False
    )
    dss_package_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("dss_packages.id"))
    decided_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    justification: Mapped[str] = mapped_column(Text, nullable=False)
    selected_option: Mapped[str] = mapped_column(String(256), nullable=False)
    snapshot_hash: Mapped[str] = mapped_column(String(64), nullable=False)


class IndicatorValueObservationRow(Base):
    __tablename__ = "indicator_value_observations"

    indicator_value_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("indicator_values.id"), primary_key=True
    )
    observation_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("observations.id"), primary_key=True
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False)


class RuleEvaluationInputRow(Base):
    __tablename__ = "rule_evaluation_inputs"

    rule_evaluation_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("rule_evaluations.id"), primary_key=True
    )
    indicator_value_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("indicator_values.id"), primary_key=True
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False)


class AlertEvaluationRow(Base):
    __tablename__ = "alert_evaluations"

    alert_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("alerts.id"), primary_key=True)
    rule_evaluation_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("rule_evaluations.id"), primary_key=True
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False)


class EvidencePackageItemRow(Base):
    __tablename__ = "evidence_package_items"

    package_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("evidence_packages.id"), primary_key=True
    )
    item_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("evidence_items.id"), primary_key=True
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False)


class ActionRow(Base):
    __tablename__ = "actions"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    decision_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("decisions.id"), nullable=False)
    acted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    action_type: Mapped[str] = mapped_column(String(64), nullable=False, default="recorded_step")
    metadata_json: Mapped[dict[str, Any]] = mapped_column("metadata", JSON, default=dict)
    recorded_by: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False)


class OutcomeRow(Base):
    __tablename__ = "outcomes"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    action_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("actions.id"), nullable=False)
    decision_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("decisions.id"), nullable=False)
    observed_outcome_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    notes: Mapped[str] = mapped_column(Text, nullable=False)


class AuditEventRow(Base):
    __tablename__ = "audit_events"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    action: Mapped[str] = mapped_column(String(64))
    entity_type: Mapped[str] = mapped_column(String(64))
    entity_id: Mapped[str] = mapped_column(String(64))
    actor_id: Mapped[UUID | None] = mapped_column(nullable=True)
    system_component: Mapped[str | None] = mapped_column(String(64), nullable=True)
    entity_version: Mapped[str | None] = mapped_column(String(64), nullable=True)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    context: Mapped[dict[str, Any]] = mapped_column(JSON)


class ImmutablePersistenceError(Exception):
    """Raised when an insert-only historical row is updated or deleted."""


def _previous_status(target: object) -> str:
    history = inspect(target).attrs.status.history
    if history.deleted:
        return str(history.deleted[0])
    return str(target.status)


@event.listens_for(DssSnapshotRow, "before_update")
@event.listens_for(DssSnapshotRow, "before_delete")
def _snapshot_insert_only(*_args: object) -> None:
    raise ImmutablePersistenceError("dss_context_snapshots are insert-only")


@event.listens_for(RuleVersionRow, "before_update")
def _published_rule_no_update(_mapper: object, _connection: object, target: RuleVersionRow) -> None:
    if _previous_status(target) == "published":
        raise ImmutablePersistenceError("published RuleVersion cannot be updated")


@event.listens_for(IndicatorVersionRow, "before_update")
def _published_indicator_no_update(_mapper: object, _connection: object, target: IndicatorVersionRow) -> None:
    if _previous_status(target) == "published":
        raise ImmutablePersistenceError("published IndicatorVersion cannot be updated")


@event.listens_for(IndicatorVersionRow, "before_delete")
def _published_indicator_no_delete(_mapper: object, _connection: object, target: IndicatorVersionRow) -> None:
    if target.status == "published":
        raise ImmutablePersistenceError("published IndicatorVersion cannot be deleted")


@event.listens_for(RuleVersionRow, "before_delete")
def _published_rule_no_delete(_mapper: object, _connection: object, target: RuleVersionRow) -> None:
    if target.status == "published":
        raise ImmutablePersistenceError("published RuleVersion cannot be deleted")


@event.listens_for(RuleEvaluationRow, "before_update")
@event.listens_for(RuleEvaluationRow, "before_delete")
def _evaluation_insert_only(*_args: object) -> None:
    raise ImmutablePersistenceError("rule_evaluations are insert-only")


@event.listens_for(AuditEventRow, "before_update")
@event.listens_for(AuditEventRow, "before_delete")
def _audit_insert_only(*_args: object) -> None:
    raise ImmutablePersistenceError("audit_events are insert-only")


def make_engine(url: str, **kwargs: Any):
    engine = create_engine(url, **kwargs)

    @event.listens_for(engine, "connect")
    def _sqlite_foreign_keys(dbapi_connection: object, _record: object) -> None:
        if engine.dialect.name == "sqlite":
            cursor = dbapi_connection.cursor()  # type: ignore[attr-defined]
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    return engine


def make_session_factory(url: str):
    engine = make_engine(url)
    return sessionmaker(engine), engine


def observation_from_row(row: ObservationRow) -> Observation:
    return Observation(
        id=ObservationId(row.id),
        variable=row.variable,
        unit=row.unit,
        observed_at=row.observed_at,
        processed_at=row.processed_at,
        quality=DataQuality(
            facet=DataQualityFacet(row.quality_facet),
            score=row.quality_score,
        ),
        value=row.value,
        spatial_ref=row.spatial_ref,
    )
