from __future__ import annotations

from baliza.domain.action import Action, Outcome
from baliza.domain.actor import Actor
from baliza.domain.alert import Alert
from baliza.domain.audit import AuditEvent
from baliza.domain.decision import Decision
from baliza.domain.dss import DssContextSnapshot, DssPackage
from baliza.domain.evidence import EvidenceItem, EvidencePackage
from baliza.domain.ids import (
    ActorId,
    AlertId,
    DecisionId,
    DssContextSnapshotId,
    DssPackageId,
    EvidenceItemId,
    EvidencePackageId,
    IndicatorValueId,
    IndicatorVersionId,
    ObservationId,
    RuleEvaluationId,
    RuleId,
    RuleVersionId,
)
from baliza.domain.indicator import Indicator, IndicatorValue, IndicatorVersion
from baliza.domain.observation import Observation
from baliza.domain.rule import Rule, RuleEvaluation, RuleVersion


class InMemoryObservationRepository:
    def __init__(self) -> None:
        self._items: dict[str, Observation] = {}

    def add(self, observation: Observation) -> None:
        self._items[str(observation.id)] = observation

    def get(self, observation_id: ObservationId) -> Observation | None:
        return self._items.get(str(observation_id))


class InMemoryIndicatorRepository:
    def __init__(self) -> None:
        self.definitions: dict[str, Indicator] = {}
        self.versions: dict[str, IndicatorVersion] = {}
        self.values: dict[str, IndicatorValue] = {}

    def add_definition(self, indicator: Indicator, version: IndicatorVersion) -> None:
        self.definitions[str(indicator.id)] = indicator
        self.versions[str(version.id)] = version

    def get_version(self, version_id: IndicatorVersionId) -> IndicatorVersion | None:
        return self.versions.get(str(version_id))

    def add_value(self, value: IndicatorValue) -> None:
        self.values[str(value.id)] = value

    def get_value(self, value_id: IndicatorValueId) -> IndicatorValue | None:
        return self.values.get(str(value_id))


class InMemoryRuleRepository:
    def __init__(self) -> None:
        self.rules: dict[str, Rule] = {}
        self.versions: dict[str, RuleVersion] = {}
        self.evaluations: dict[str, RuleEvaluation] = {}

    def add_rule(self, rule: Rule, version: RuleVersion) -> None:
        self.rules[str(rule.id)] = rule
        self.versions[str(version.id)] = version

    def get_rule(self, rule_id: RuleId) -> Rule | None:
        return self.rules.get(str(rule_id))

    def get_version(self, version_id: RuleVersionId) -> RuleVersion | None:
        return self.versions.get(str(version_id))

    def replace_version(self, version: RuleVersion) -> None:
        from baliza.domain.enums import PublicationStatus
        from baliza.domain.errors import PublishedVersionImmutable

        current = self.versions[str(version.id)]
        if current.status == PublicationStatus.PUBLISHED:
            raise PublishedVersionImmutable("Published RuleVersion cannot be mutated.")
        self.versions[str(version.id)] = version

    def add_evaluation(self, evaluation: RuleEvaluation) -> None:
        self.evaluations[str(evaluation.id)] = evaluation

    def get_evaluation(self, evaluation_id: RuleEvaluationId) -> RuleEvaluation | None:
        return self.evaluations.get(str(evaluation_id))


class InMemoryEvidenceRepository:
    def __init__(self) -> None:
        self.items: dict[str, EvidenceItem] = {}
        self.packages: dict[str, EvidencePackage] = {}
        self._package_items: dict[str, list[str]] = {}

    def add_item(self, item: EvidenceItem) -> None:
        self.items[str(item.id)] = item

    def add_package(self, package: EvidencePackage) -> None:
        self.packages[str(package.id)] = package
        self._package_items[str(package.id)] = [str(i) for i in package.item_ids]

    def get_item(self, item_id: EvidenceItemId) -> EvidenceItem | None:
        return self.items.get(str(item_id))

    def get_package(self, package_id: EvidencePackageId) -> EvidencePackage | None:
        return self.packages.get(str(package_id))

    def items_for_package(self, package_id: EvidencePackageId) -> list[EvidenceItem]:
        ids = self._package_items.get(str(package_id), [])
        return [self.items[i] for i in ids if i in self.items]


class InMemoryAlertRepository:
    def __init__(self) -> None:
        self._items: dict[str, Alert] = {}

    def add(self, alert: Alert) -> None:
        self._items[str(alert.id)] = alert

    def get(self, alert_id: AlertId) -> Alert | None:
        return self._items.get(str(alert_id))

    def save(self, alert: Alert) -> None:
        self._items[str(alert.id)] = alert

    def list_all(self) -> list[Alert]:
        return list(self._items.values())


class InMemoryDssRepository:
    def __init__(self) -> None:
        self.packages: dict[str, DssPackage] = {}
        self.snapshots: dict[str, DssContextSnapshot] = {}

    def add_package(self, package: DssPackage) -> None:
        self.packages[str(package.id)] = package

    def get_package(self, package_id: DssPackageId) -> DssPackage | None:
        return self.packages.get(str(package_id))

    def list_packages(self) -> list[DssPackage]:
        return list(self.packages.values())

    def save_package(self, package: DssPackage) -> None:
        self.packages[str(package.id)] = package

    def add_snapshot(self, snapshot: DssContextSnapshot) -> None:
        self.snapshots[str(snapshot.id)] = snapshot

    def get_snapshot(self, snapshot_id: DssContextSnapshotId) -> DssContextSnapshot | None:
        return self.snapshots.get(str(snapshot_id))

    def snapshots_for_package(self, package_id: DssPackageId) -> list[DssContextSnapshot]:
        return [item for item in self.snapshots.values() if item.dss_package_id == package_id]


class InMemoryDecisionRepository:
    def __init__(self) -> None:
        self._items: dict[str, Decision] = {}

    def add(self, decision: Decision) -> None:
        self._items[str(decision.id)] = decision

    def get(self, decision_id: DecisionId) -> Decision | None:
        return self._items.get(str(decision_id))

    def list_all(self) -> list[Decision]:
        return list(self._items.values())


class InMemoryActionRepository:
    def __init__(self) -> None:
        self.actions: dict[str, Action] = {}
        self.outcomes: dict[str, Outcome] = {}

    def add_action(self, action: Action) -> None:
        self.actions[str(action.id)] = action

    def get_action(self, action_id) -> Action | None:
        return self.actions.get(str(action_id))

    def add_outcome(self, outcome: Outcome) -> None:
        self.outcomes[str(outcome.id)] = outcome

    def get_outcome(self, outcome_id) -> Outcome | None:
        return self.outcomes.get(str(outcome_id))


class InMemoryActorRepository:
    def __init__(self) -> None:
        self._items: dict[str, Actor] = {}

    def add(self, actor: Actor) -> None:
        self._items[str(actor.id)] = actor

    def get(self, actor_id: ActorId) -> Actor | None:
        return self._items.get(str(actor_id))


class InMemoryAuditRepository:
    def __init__(self) -> None:
        self.events: list[AuditEvent] = []

    def add(self, event: AuditEvent) -> None:
        self.events.append(event)

    def list_for_entity(self, entity_type: str, entity_id: str) -> list[AuditEvent]:
        return [e for e in self.events if e.entity_type == entity_type and e.entity_id == entity_id]


class MemoryUnitOfWork:
    """Copy-on-begin rollback for the in-memory critical path."""

    def __init__(self, repos: object) -> None:
        self._repos = repos
        self._snap: dict | None = None

    def begin(self) -> None:
        repos = self._repos
        self._snap = {
            "evaluations": dict(repos.rules.evaluations),
            "items": dict(repos.evidence.items),
            "packages": dict(repos.evidence.packages),
            "package_items": {k: list(v) for k, v in repos.evidence._package_items.items()},
            "alerts": dict(repos.alerts._items),
            "events": list(repos.audit.events),
            "snapshots": dict(repos.dss.snapshots),
            "decisions": dict(repos.decisions._items),
        }

    def commit(self) -> None:
        self._snap = None

    def rollback(self) -> None:
        if self._snap is None:
            return
        repos = self._repos
        repos.rules.evaluations = self._snap["evaluations"]
        repos.evidence.items = self._snap["items"]
        repos.evidence.packages = self._snap["packages"]
        repos.evidence._package_items = self._snap["package_items"]
        repos.alerts._items = self._snap["alerts"]
        repos.audit.events = self._snap["events"]
        repos.dss.snapshots = self._snap["snapshots"]
        repos.decisions._items = self._snap["decisions"]
        self._snap = None


def bind_memory_unit_of_work(repos: object) -> object:
    repos.uow = MemoryUnitOfWork(repos)
    return repos
