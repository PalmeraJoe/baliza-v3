from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import Uuid
from sqlalchemy.orm import Session

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
from baliza.domain.quality import DataQuality, ScopeHealth
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
from baliza.domain.rule import Rule, RuleEvaluation, RuleVersion, Threshold
from baliza.domain.evidence import EvidenceItem, EvidencePackage
from baliza.domain.hashing import canonical_for_hash

from baliza.infrastructure.persistence.models import (
    ActionRow,
    AlertEvaluationRow,
    AlertRow,
    AuditEventRow,
    DecisionRow,
    DssPackageRow,
    DssSnapshotRow,
    EvidenceItemRow,
    EvidencePackageItemRow,
    EvidencePackageRow,
    IndicatorValueObservationRow,
    IndicatorValueRow,
    ObservationRow,
    OutcomeRow,
    RuleEvaluationInputRow,
    RuleEvaluationRow,
    RuleVersionRow,
)


def _as_utc(ts: datetime) -> datetime:
    if ts.tzinfo is None:
        return ts.replace(tzinfo=UTC)
    return ts


class SqlObservationRepository:
    def __init__(self, session: Session) -> None:
        self._s = session

    def add(self, observation: Observation) -> None:
        self._s.add(
            ObservationRow(
                id=observation.id.value,
                variable=observation.variable,
                unit=observation.unit,
                value=observation.value,
                observed_at=observation.observed_at,
                processed_at=observation.processed_at,
                quality_facet=observation.quality.facet.value,
                quality_score=observation.quality.score,
                spatial_ref=observation.spatial_ref,
                metadata_json=dict(observation.metadata),
            )
        )

    def get(self, observation_id: ObservationId) -> Observation | None:
        row = self._s.get(ObservationRow, observation_id.value)
        if row is None:
            return None
        return Observation(
            id=ObservationId(row.id),
            variable=row.variable,
            unit=row.unit,
            observed_at=_as_utc(row.observed_at),
            processed_at=_as_utc(row.processed_at),
            quality=DataQuality(
                facet=DataQualityFacet(row.quality_facet), score=row.quality_score
            ),
            value=row.value,
            spatial_ref=row.spatial_ref,
            metadata=row.metadata_json or {},
        )


class SqlIndicatorRepository:
    def __init__(self, session: Session) -> None:
        self._s = session

    def add_definition(self, indicator, version) -> None:
        from baliza.infrastructure.persistence.models import IndicatorVersionRow

        self._s.add(
            IndicatorVersionRow(
                id=version.id.value,
                indicator_id=indicator.id.value,
                name=indicator.name,
                version=version.version,
                unit=version.unit,
                formula_kind=version.formula_kind,
                baseline=version.baseline,
                status=version.status.value,
                input_variable=version.input_variable,
            )
        )
        self._s.flush()

    def get_version(self, version_id: IndicatorVersionId):
        from baliza.infrastructure.persistence.models import IndicatorVersionRow
        from baliza.domain.enums import PublicationStatus
        from baliza.domain.ids import IndicatorId
        from baliza.domain.indicator import IndicatorVersion

        row = self._s.get(IndicatorVersionRow, version_id.value)
        if row is None:
            return None
        return IndicatorVersion(
            id=IndicatorVersionId(row.id),
            indicator_id=IndicatorId(row.indicator_id),
            version=row.version,
            unit=row.unit,
            formula_kind=row.formula_kind,
            baseline=row.baseline,
            status=PublicationStatus(row.status),
            input_variable=row.input_variable,
        )

    def add_value(self, value: IndicatorValue) -> None:
        self._s.add(
            IndicatorValueRow(
                id=value.id.value,
                indicator_id=value.indicator_id.value,
                indicator_version_id=value.indicator_version_id.value,
                indicator_version=value.indicator_version,
                computed_at=value.computed_at,
                unit=value.unit,
                value=value.value,
                quality_facet=value.quality.facet.value,
                notes=list(value.notes),
            )
        )
        self._s.flush()
        for position, observation_id in enumerate(value.source_observation_ids):
            self._s.add(
                IndicatorValueObservationRow(
                    indicator_value_id=value.id.value,
                    observation_id=observation_id.value,
                    position=position,
                )
            )

    def get_value(self, value_id: IndicatorValueId) -> IndicatorValue | None:
        row = self._s.get(IndicatorValueRow, value_id.value)
        if row is None:
            return None
        links = (
            self._s.query(IndicatorValueObservationRow)
            .filter_by(indicator_value_id=row.id)
            .order_by(IndicatorValueObservationRow.position)
            .all()
        )
        return IndicatorValue(
            id=IndicatorValueId(row.id),
            indicator_id=IndicatorId(row.indicator_id),
            indicator_version_id=IndicatorVersionId(row.indicator_version_id),
            indicator_version=row.indicator_version,
            computed_at=_as_utc(row.computed_at),
            unit=row.unit,
            source_observation_ids=tuple(ObservationId(link.observation_id) for link in links),
            quality=DataQuality(facet=DataQualityFacet(row.quality_facet)),
            value=row.value,
            notes=tuple(row.notes),
        )


class SqlRuleRepository:
    def __init__(self, session: Session) -> None:
        self._s = session

    def add_rule(self, rule, version) -> None:
        from baliza.infrastructure.persistence.models import RuleVersionRow

        self._s.add(
            RuleVersionRow(
                id=version.id.value,
                rule_id=rule.id.value,
                version=version.version,
                status=version.status.value,
                operator=version.operator.value,
                threshold_name=version.threshold_name,
                thresholds={t.name: t.value for t in version.thresholds},
                severity_if_triggered=version.severity_if_triggered,
                evaluator_engine_id=version.evaluator_engine_id,
            )
        )
        self._s.flush()

    def get_rule(self, rule_id: RuleId):
        row = self._s.query(RuleVersionRow).filter_by(rule_id=rule_id.value).first()
        if row is None:
            return None
        return Rule(id=RuleId(row.rule_id), name="")

    def get_version(self, version_id: RuleVersionId):
        row = self._s.get(RuleVersionRow, version_id.value)
        if row is None:
            return None
        return RuleVersion(
            id=RuleVersionId(row.id),
            rule_id=RuleId(row.rule_id),
            version=row.version,
            thresholds=tuple(Threshold(name=k, value=float(v)) for k, v in row.thresholds.items()),
            operator=ComparisonOp(row.operator),
            threshold_name=row.threshold_name,
            severity_if_triggered=row.severity_if_triggered,
            status=PublicationStatus(row.status),
            evaluator_engine_id=row.evaluator_engine_id,
        )

    def replace_version(self, version: RuleVersion) -> None:
        row = self._s.get(RuleVersionRow, version.id.value)
        if row is None:
            raise KeyError(str(version.id))
        row.status = version.status.value
        row.thresholds = {t.name: t.value for t in version.thresholds}
        row.operator = version.operator.value
        row.threshold_name = version.threshold_name
        row.severity_if_triggered = version.severity_if_triggered

    def add_evaluation(self, evaluation: RuleEvaluation) -> None:
        self._s.add(
            RuleEvaluationRow(
                id=evaluation.id.value,
                rule_id=evaluation.rule_id.value,
                rule_version_id=evaluation.rule_version_id.value,
                rule_version=evaluation.rule_version,
                evaluated_at=evaluation.evaluated_at,
                outcome=evaluation.outcome.value,
                reason=evaluation.reason,
                thresholds_applied=canonical_for_hash(evaluation.thresholds_applied),
                input_snapshot=canonical_for_hash(evaluation.input_snapshot),
                evaluator_engine_id=evaluation.evaluator_engine_id,
            )
        )
        self._s.flush()
        for position, value_id in enumerate(evaluation.input_indicator_value_ids):
            self._s.add(
                RuleEvaluationInputRow(
                    rule_evaluation_id=evaluation.id.value,
                    indicator_value_id=value_id.value,
                    position=position,
                )
            )

    def get_evaluation(self, evaluation_id: RuleEvaluationId) -> RuleEvaluation | None:
        row = self._s.get(RuleEvaluationRow, evaluation_id.value)
        if row is None:
            return None
        return RuleEvaluation(
            id=RuleEvaluationId(row.id),
            rule_id=RuleId(row.rule_id),
            rule_version_id=RuleVersionId(row.rule_version_id),
            rule_version=row.rule_version,
            evaluated_at=_as_utc(row.evaluated_at),
            outcome=RuleOutcome(row.outcome),
            input_indicator_value_ids=tuple(
                IndicatorValueId(link.indicator_value_id)
                for link in self._s.query(RuleEvaluationInputRow)
                .filter_by(rule_evaluation_id=row.id)
                .order_by(RuleEvaluationInputRow.position)
                .all()
            ),
            thresholds_applied=dict(row.thresholds_applied),
            evaluator_engine_id=row.evaluator_engine_id,
            reason=row.reason,
            input_snapshot=dict(row.input_snapshot),
        )


class SqlEvidenceRepository:
    def __init__(self, session: Session) -> None:
        self._s = session

    def add_item(self, item: EvidenceItem) -> None:
        self._s.add(
            EvidenceItemRow(
                id=item.id.value,
                kind=item.kind.value,
                epistemic_label=item.epistemic_label.value,
                referenced_type=item.referenced_type,
                referenced_id=item.referenced_id,
                created_at=item.created_at,
                content_hash=item.content_hash,
                narrative=item.narrative,
            )
        )

    def get_item(self, item_id: EvidenceItemId):
        row = self._s.get(EvidenceItemRow, item_id.value)
        if row is None:
            return None
        return EvidenceItem(
            id=EvidenceItemId(row.id),
            kind=EvidenceKind(row.kind),
            epistemic_label=EpistemicLabel(row.epistemic_label),
            referenced_type=row.referenced_type,
            referenced_id=row.referenced_id,
            created_at=_as_utc(row.created_at),
            content_hash=row.content_hash,
            narrative=row.narrative,
        )

    def add_package(self, package: EvidencePackage) -> None:
        self._s.add(
            EvidencePackageRow(
                id=package.id.value,
                subject=package.subject,
                assembled_at=package.assembled_at,
                gaps=list(package.gaps),
                incomplete=package.incomplete,
            )
        )
        self._s.flush()
        for position, item_id in enumerate(package.item_ids):
            self._s.add(
                EvidencePackageItemRow(
                    package_id=package.id.value,
                    item_id=item_id.value,
                    position=position,
                )
            )

    def get_package(self, package_id: EvidencePackageId) -> EvidencePackage | None:
        row = self._s.get(EvidencePackageRow, package_id.value)
        if row is None:
            return None
        links = (
            self._s.query(EvidencePackageItemRow)
            .filter_by(package_id=row.id)
            .order_by(EvidencePackageItemRow.position)
            .all()
        )
        return EvidencePackage(
            id=EvidencePackageId(row.id),
            subject=row.subject,
            item_ids=tuple(EvidenceItemId(link.item_id) for link in links),
            assembled_at=_as_utc(row.assembled_at),
            gaps=tuple(row.gaps),
            incomplete=row.incomplete,
        )

    def items_for_package(self, package_id: EvidencePackageId) -> list[EvidenceItem]:
        pkg = self.get_package(package_id)
        if pkg is None:
            return []
        items = []
        for iid in pkg.item_ids:
            row = self._s.get(EvidenceItemRow, iid.value)
            if row:
                items.append(
                    EvidenceItem(
                        id=EvidenceItemId(row.id),
                        kind=EvidenceKind(row.kind),
                        epistemic_label=EpistemicLabel(row.epistemic_label),
                        referenced_type=row.referenced_type,
                        referenced_id=row.referenced_id,
                        created_at=_as_utc(row.created_at),
                        content_hash=row.content_hash,
                        narrative=row.narrative,
                    )
                )
        return items


class SqlAlertRepository:
    def __init__(self, session: Session) -> None:
        self._s = session

    def add(self, alert: Alert) -> None:
        self._s.add(self._to_row(alert))
        self._s.flush()
        for position, evaluation_id in enumerate(alert.rule_evaluation_ids):
            self._s.add(
                AlertEvaluationRow(
                    alert_id=alert.id.value,
                    rule_evaluation_id=evaluation_id.value,
                    position=position,
                )
            )

    def get(self, alert_id: AlertId) -> Alert | None:
        row = self._s.get(AlertRow, alert_id.value)
        return self._from_row(row) if row else None

    def save(self, alert: Alert) -> None:
        existing = self._s.get(AlertRow, alert.id.value)
        if existing is None:
            self.add(alert)
            return
        existing.status = alert.status.value
        existing.reviewed_at = alert.reviewed_at
        existing.history = [
            {
                "status": h.status.value,
                "reviewed_at": h.reviewed_at.isoformat(),
                "actor_id": h.actor_id,
                "note": h.note,
            }
            for h in alert.history
        ]

    def list_all(self) -> list[Alert]:
        return [self._from_row(row) for row in self._s.query(AlertRow).all()]

    def _to_row(self, alert: Alert) -> AlertRow:
        return AlertRow(
            id=alert.id.value,
            severity=alert.severity.value,
            status=alert.status.value,
            alerted_at=alert.alerted_at,
            evidence_package_id=alert.evidence_package_id.value,
            history=[
                {
                    "status": h.status.value,
                    "reviewed_at": h.reviewed_at.isoformat(),
                    "actor_id": h.actor_id,
                    "note": h.note,
                }
                for h in alert.history
            ],
            health=alert.health.value,
            reviewed_at=alert.reviewed_at,
        )

    def _from_row(self, row: AlertRow) -> Alert:
        history = tuple(
            AlertStatusChange(
                status=AlertStatus(h["status"]),
                reviewed_at=datetime.fromisoformat(h["reviewed_at"]),
                actor_id=h.get("actor_id"),
                note=h.get("note"),
            )
            for h in (row.history or [])
        )
        return Alert(
            id=AlertId(row.id),
            severity=AlertSeverity(row.severity),
            status=AlertStatus(row.status),
            alerted_at=_as_utc(row.alerted_at),
            evidence_package_id=EvidencePackageId(row.evidence_package_id),
            rule_evaluation_ids=tuple(
                RuleEvaluationId(link.rule_evaluation_id)
                for link in self._s.query(AlertEvaluationRow)
                .filter_by(alert_id=row.id)
                .order_by(AlertEvaluationRow.position)
                .all()
            ),
            health=ScopeHealth(row.health),
            history=history,
        )


class SqlDssRepository:
    def __init__(self, session: Session) -> None:
        self._s = session

    def add_package(self, package: DssPackage) -> None:
        self._s.add(
            DssPackageRow(
                id=package.id.value,
                opened_at=package.opened_at,
                payload={
                    "alert_ids": [str(a) for a in package.alert_ids],
                    "evaluation_ids": [str(e) for e in package.evaluation_ids],
                    "evidence_package_ids": [str(e) for e in package.evidence_package_ids],
                    "protocol_version": package.protocol_version,
                    "gaps": list(package.gaps),
                    "uncertainty_notes": list(package.uncertainty_notes),
                    "recommendations": [
                        {
                            "recommendation_id": r.recommendation_id,
                            "source": r.source,
                            "text": r.text,
                            "epistemic_label": r.epistemic_label,
                            "rationale": r.rationale,
                            "evidence_refs": list(r.evidence_refs),
                            "uncertainty_note": r.uncertainty_note,
                            "preconditions": list(r.preconditions),
                            "constraints": list(r.constraints),
                        }
                        for r in package.recommendations
                    ],
                    "agent_run_ids_shown": list(package.agent_run_ids_shown),
                },
            )
        )
        self._s.flush()

    def get_package(self, package_id: DssPackageId) -> DssPackage | None:
        row = self._s.get(DssPackageRow, package_id.value)
        if row is None:
            return None
        p = row.payload or {}
        pkg = DssPackage(id=DssPackageId(row.id), opened_at=_as_utc(row.opened_at))
        pkg.alert_ids = [AlertId(x) for x in p.get("alert_ids", [])]
        pkg.evaluation_ids = [RuleEvaluationId(x) for x in p.get("evaluation_ids", [])]
        pkg.evidence_package_ids = [EvidencePackageId(x) for x in p.get("evidence_package_ids", [])]
        pkg.protocol_version = p.get("protocol_version")
        pkg.gaps = list(p.get("gaps", []))
        pkg.uncertainty_notes = list(p.get("uncertainty_notes", []))
        pkg.recommendations = [
            RecommendationView(
                recommendation_id=r["recommendation_id"],
                source=r["source"],
                text=r["text"],
                epistemic_label=r.get("epistemic_label", "RECOMMENDATION"),
                rationale=r.get("rationale", ""),
                evidence_refs=tuple(r.get("evidence_refs", ())),
                uncertainty_note=r.get("uncertainty_note"),
                preconditions=tuple(r.get("preconditions", ())),
                constraints=tuple(r.get("constraints", ())),
            )
            for r in p.get("recommendations", [])
        ]
        pkg.agent_run_ids_shown = list(p.get("agent_run_ids_shown", []))
        return pkg

    def save_package(self, package: DssPackage) -> None:
        existing = self._s.get(DssPackageRow, package.id.value)
        if existing is None:
            self.add_package(package)
            return
        existing.payload = {
            "alert_ids": [str(a) for a in package.alert_ids],
            "evaluation_ids": [str(e) for e in package.evaluation_ids],
            "evidence_package_ids": [str(e) for e in package.evidence_package_ids],
            "protocol_version": package.protocol_version,
            "gaps": list(package.gaps),
            "uncertainty_notes": list(package.uncertainty_notes),
            "recommendations": [
                {
                    "recommendation_id": r.recommendation_id,
                    "source": r.source,
                    "text": r.text,
                    "epistemic_label": r.epistemic_label,
                    "rationale": r.rationale,
                    "evidence_refs": list(r.evidence_refs),
                    "uncertainty_note": r.uncertainty_note,
                    "preconditions": list(r.preconditions),
                    "constraints": list(r.constraints),
                }
                for r in package.recommendations
            ],
            "agent_run_ids_shown": list(package.agent_run_ids_shown),
        }

    def add_snapshot(self, snapshot: DssContextSnapshot) -> None:
        self._s.add(
            DssSnapshotRow(
                id=snapshot.id.value,
                dss_package_id=snapshot.dss_package_id.value,
                frozen_at=snapshot.frozen_at,
                content_hash=snapshot.content_hash,
                payload=canonical_for_hash(snapshot.payload),
                object_key=snapshot.object_key,
            )
        )
        self._s.flush()

    def get_snapshot(self, snapshot_id: DssContextSnapshotId) -> DssContextSnapshot | None:
        row = self._s.get(DssSnapshotRow, snapshot_id.value)
        if row is None:
            return None
        return DssContextSnapshot(
            id=DssContextSnapshotId(row.id),
            dss_package_id=DssPackageId(row.dss_package_id),
            frozen_at=_as_utc(row.frozen_at),
            content_hash=row.content_hash,
            payload=row.payload,
            object_key=row.object_key,
        )

    def snapshots_for_package(self, package_id: DssPackageId) -> list[DssContextSnapshot]:
        rows = self._s.query(DssSnapshotRow).filter_by(dss_package_id=package_id.value).all()
        return [item for row in rows if (item := self.get_snapshot(DssContextSnapshotId(row.id))) is not None]


class SqlDecisionRepository:
    def __init__(self, session: Session) -> None:
        self._s = session

    def add(self, decision: Decision) -> None:
        self._s.add(
            DecisionRow(
                id=decision.id.value,
                actor_id=decision.actor_id.value,
                dss_context_snapshot_id=decision.dss_context_snapshot_id.value,
                dss_package_id=decision.dss_package_id.value,
                decided_at=decision.decided_at,
                justification=decision.justification,
                selected_option=decision.selected_option,
                snapshot_hash=decision.snapshot_hash,
            )
        )
        self._s.flush()

    def get(self, decision_id: DecisionId) -> Decision | None:
        row = self._s.get(DecisionRow, decision_id.value)
        if row is None:
            return None
        return Decision(
            id=DecisionId(row.id),
            actor_id=ActorId(row.actor_id),
            dss_context_snapshot_id=DssContextSnapshotId(row.dss_context_snapshot_id),
            dss_package_id=DssPackageId(row.dss_package_id),
            decided_at=_as_utc(row.decided_at),
            justification=row.justification,
            selected_option=row.selected_option,
            snapshot_hash=row.snapshot_hash,
        )


class SqlAuditRepository:
    def __init__(self, session: Session) -> None:
        self._s = session

    def add(self, event: AuditEvent) -> None:
        self._s.add(
            AuditEventRow(
                id=event.id.value,
                occurred_at=event.occurred_at,
                action=event.action,
                entity_type=event.entity_type,
                entity_id=event.entity_id,
                actor_id=event.actor_id.value if event.actor_id else None,
                system_component=event.system_component,
                entity_version=event.entity_version,
                reason=event.reason,
                context=event.context,
            )
        )

    def list_for_entity(self, entity_type: str, entity_id: str) -> list[AuditEvent]:
        rows = (
            self._s.query(AuditEventRow)
            .filter_by(entity_type=entity_type, entity_id=entity_id)
            .all()
        )
        return [
            AuditEvent(
                id=AuditEventId(r.id),
                occurred_at=r.occurred_at,
                action=r.action,
                entity_type=r.entity_type,
                entity_id=r.entity_id,
                actor_id=ActorId(r.actor_id) if r.actor_id else None,
                system_component=r.system_component,
                entity_version=r.entity_version,
                reason=r.reason,
                context=r.context or {},
            )
            for r in rows
        ]


class SqlActionRepository:
    def __init__(self, session: Session) -> None:
        self._s = session

    def add_action(self, action) -> None:
        self._s.add(
            ActionRow(
                id=action.id.value,
                decision_id=action.decision_id.value,
                acted_at=action.acted_at,
                description=action.description,
                action_type=action.action_type,
                metadata_json=dict(action.metadata),
                recorded_by=action.recorded_by.value if action.recorded_by else None,
                status=action.status,
            )
        )
        self._s.flush()

    def get_action(self, action_id):
        row = self._s.get(ActionRow, action_id.value)
        if row is None:
            return None
        from baliza.domain.action import Action
        from baliza.domain.ids import ActionId

        return Action(
            id=ActionId(row.id),
            decision_id=DecisionId(row.decision_id),
            acted_at=_as_utc(row.acted_at),
            description=row.description,
            action_type=row.action_type,
            recorded_by=ActorId(row.recorded_by) if row.recorded_by else None,
            status=row.status,
            metadata=row.metadata_json or {},
        )

    def add_outcome(self, outcome) -> None:
        self._s.add(
            OutcomeRow(
                id=outcome.id.value,
                action_id=outcome.action_id.value,
                decision_id=outcome.decision_id.value,
                observed_outcome_at=outcome.observed_outcome_at,
                notes=outcome.notes,
            )
        )

    def get_outcome(self, outcome_id):
        row = self._s.get(OutcomeRow, outcome_id.value)
        if row is None:
            return None
        from baliza.domain.action import Outcome
        from baliza.domain.ids import ActionId, OutcomeId

        return Outcome(
            id=OutcomeId(row.id),
            action_id=ActionId(row.action_id),
            decision_id=DecisionId(row.decision_id),
            observed_outcome_at=_as_utc(row.observed_outcome_at),
            notes=row.notes,
        )


class SqlUnitOfWork:
    def __init__(self, session: Session) -> None:
        self._s = session

    def begin(self) -> None:
        return None

    def commit(self) -> None:
        self._s.commit()

    def rollback(self) -> None:
        self._s.rollback()


def open_database(url: str, *, create_schema: bool = False):
    """SQL adapter entry. Credentials come from the caller, not from this module."""
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.pool import StaticPool

    from baliza.infrastructure.persistence.models import Base, make_engine

    kwargs: dict = {}
    if url.startswith("sqlite"):
        kwargs = {"connect_args": {"check_same_thread": False}, "poolclass": StaticPool}
    engine = make_engine(url, **kwargs)
    if create_schema:
        Base.metadata.create_all(engine)
    return sessionmaker(bind=engine), engine


def sql_repositories(session: Session, clock) -> "object":
    from baliza.application.use_cases import Repositories
    from baliza.infrastructure.memory import InMemoryActorRepository

    return Repositories(
        actors=InMemoryActorRepository(),
        observations=SqlObservationRepository(session),
        indicators=SqlIndicatorRepository(session),
        rules=SqlRuleRepository(session),
        evidence=SqlEvidenceRepository(session),
        alerts=SqlAlertRepository(session),
        dss=SqlDssRepository(session),
        decisions=SqlDecisionRepository(session),
        actions=SqlActionRepository(session),
        audit=SqlAuditRepository(session),
        clock=clock,
        uow=SqlUnitOfWork(session),
    )
