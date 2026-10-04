from __future__ import annotations

from datetime import datetime
from typing import Protocol

from baliza.domain.action import Action, Outcome
from baliza.domain.actor import Actor
from baliza.domain.alert import Alert
from baliza.domain.audit import AuditEvent
from baliza.domain.decision import Decision
from baliza.domain.dss import DssContextSnapshot, DssPackage
from baliza.domain.evidence import EvidenceItem, EvidencePackage
from baliza.domain.ids import (
    ActionId,
    ActorId,
    AlertId,
    DecisionId,
    EvidenceItemId,
    OutcomeId,
    DssContextSnapshotId,
    DssPackageId,
    EvidencePackageId,
    IndicatorId,
    IndicatorValueId,
    ObservationId,
    RuleEvaluationId,
    RuleId,
    RuleVersionId,
)
from baliza.domain.indicator import Indicator, IndicatorValue, IndicatorVersion
from baliza.domain.observation import Observation
from baliza.domain.rule import Rule, RuleEvaluation, RuleVersion


class Clock(Protocol):
    def now(self) -> datetime: ...


class UnitOfWork(Protocol):
    """Transaction boundary. Domain stays unaware of the session."""

    def begin(self) -> None: ...

    def commit(self) -> None: ...

    def rollback(self) -> None: ...


class ObjectStorage(Protocol):
    def put(self, key: str, data: bytes, content_type: str = "application/octet-stream") -> str: ...

    def get(self, key: str) -> bytes: ...


class ObservationRepository(Protocol):
    def add(self, observation: Observation) -> None: ...

    def get(self, observation_id: ObservationId) -> Observation | None: ...


class IndicatorRepository(Protocol):
    def add_definition(self, indicator: Indicator, version: IndicatorVersion) -> None: ...

    def get_version(self, version_id: IndicatorVersionId) -> IndicatorVersion | None: ...

    def add_value(self, value: IndicatorValue) -> None: ...

    def get_value(self, value_id: IndicatorValueId) -> IndicatorValue | None: ...


class RuleRepository(Protocol):
    def add_rule(self, rule: Rule, version: RuleVersion) -> None: ...

    def get_rule(self, rule_id: RuleId) -> Rule | None: ...

    def get_version(self, version_id: RuleVersionId) -> RuleVersion | None: ...

    def replace_version(self, version: RuleVersion) -> None: ...

    def add_evaluation(self, evaluation: RuleEvaluation) -> None: ...

    def get_evaluation(self, evaluation_id: RuleEvaluationId) -> RuleEvaluation | None: ...


class EvidenceRepository(Protocol):
    def add_item(self, item: EvidenceItem) -> None: ...

    def add_package(self, package: EvidencePackage) -> None: ...

    def get_package(self, package_id: EvidencePackageId) -> EvidencePackage | None: ...

    def get_item(self, item_id: EvidenceItemId) -> EvidenceItem | None: ...

    def items_for_package(self, package_id: EvidencePackageId) -> list[EvidenceItem]: ...


class AlertRepository(Protocol):
    def add(self, alert: Alert) -> None: ...

    def get(self, alert_id: AlertId) -> Alert | None: ...

    def save(self, alert: Alert) -> None: ...

    def list_all(self) -> list[Alert]: ...


class DssRepository(Protocol):
    def add_package(self, package: DssPackage) -> None: ...

    def get_package(self, package_id: DssPackageId) -> DssPackage | None: ...

    def save_package(self, package: DssPackage) -> None: ...

    def add_snapshot(self, snapshot: DssContextSnapshot) -> None: ...

    def get_snapshot(self, snapshot_id: DssContextSnapshotId) -> DssContextSnapshot | None: ...

    def snapshots_for_package(self, package_id: DssPackageId) -> list[DssContextSnapshot]: ...


class DecisionRepository(Protocol):
    def add(self, decision: Decision) -> None: ...

    def get(self, decision_id: DecisionId) -> Decision | None: ...


class ActionRepository(Protocol):
    def add_action(self, action: Action) -> None: ...

    def get_action(self, action_id: ActionId) -> Action | None: ...

    def add_outcome(self, outcome: Outcome) -> None: ...

    def get_outcome(self, outcome_id: OutcomeId) -> Outcome | None: ...


class ActorRepository(Protocol):
    def add(self, actor: Actor) -> None: ...

    def get(self, actor_id: ActorId) -> Actor | None: ...


class AuditRepository(Protocol):
    def add(self, event: AuditEvent) -> None: ...

    def list_for_entity(self, entity_type: str, entity_id: str) -> list[AuditEvent]: ...
