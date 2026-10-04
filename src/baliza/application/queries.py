from __future__ import annotations

from dataclasses import dataclass

from baliza.application.use_cases import Repositories
from baliza.domain.alert import Alert
from baliza.domain.decision import Decision
from baliza.domain.dss import DssContextSnapshot, DssPackage
from baliza.domain.evidence import EvidenceItem, EvidencePackage
from baliza.domain.ids import AlertId, DecisionId, DssPackageId
from baliza.domain.indicator import IndicatorValue
from baliza.domain.observation import Observation
from baliza.domain.rule import RuleEvaluation
from baliza.domain.situation import SituationReading, interpret_situation


@dataclass(frozen=True, slots=True)
class AlertChain:
    alert: Alert
    evidence_package: EvidencePackage | None
    items: tuple[EvidenceItem, ...]
    evaluations: tuple[RuleEvaluation, ...]
    indicator_values: tuple[IndicatorValue, ...]
    observations: tuple[Observation, ...]


@dataclass(frozen=True, slots=True)
class DecisionContext:
    decision: Decision
    snapshot: DssContextSnapshot | None
    package: DssPackage | None


def alert_chain(repos: Repositories, alert_id: AlertId) -> AlertChain | None:
    alert = repos.alerts.get(alert_id)
    if alert is None:
        return None
    package = repos.evidence.get_package(alert.evidence_package_id)
    items = tuple(repos.evidence.items_for_package(alert.evidence_package_id))
    evaluations = tuple(
        ev
        for ev in (repos.rules.get_evaluation(eid) for eid in alert.rule_evaluation_ids)
        if ev is not None
    )
    indicator_values = tuple(
        value
        for ev in evaluations
        for value in (repos.indicators.get_value(vid) for vid in ev.input_indicator_value_ids)
        if value is not None
    )
    observations = tuple(
        obs
        for value in indicator_values
        for obs in (repos.observations.get(oid) for oid in value.source_observation_ids)
        if obs is not None
    )
    return AlertChain(
        alert=alert,
        evidence_package=package,
        items=items,
        evaluations=evaluations,
        indicator_values=indicator_values,
        observations=observations,
    )


def dss_detail(repos: Repositories, package_id: DssPackageId) -> DssPackage | None:
    return repos.dss.get_package(package_id)


def _reading_for_package(repos: Repositories, package: DssPackage) -> SituationReading:
    alerts = tuple(item for alert_id in package.alert_ids if (item := repos.alerts.get(alert_id)) is not None)
    evidence_packages = []
    evidence_items = []
    for package_id in package.evidence_package_ids:
        evidence_package = repos.evidence.get_package(package_id)
        if evidence_package is None:
            continue
        evidence_packages.append(evidence_package)
        evidence_items.extend(repos.evidence.items_for_package(package_id))
    evaluations = tuple(
        item for evaluation_id in package.evaluation_ids if (item := repos.rules.get_evaluation(evaluation_id)) is not None
    )
    indicator_values = []
    observations = []
    for evaluation in evaluations:
        for value_id in evaluation.input_indicator_value_ids:
            value = repos.indicators.get_value(value_id)
            if value is None:
                continue
            indicator_values.append(value)
            for observation_id in value.source_observation_ids:
                observation = repos.observations.get(observation_id)
                if observation is not None:
                    observations.append(observation)
    return interpret_situation(
        alerts=alerts,
        evidence_packages=tuple(evidence_packages),
        evidence_items=tuple(evidence_items),
        evaluations=evaluations,
        indicator_values=tuple(indicator_values),
        observations=tuple(observations),
        recommendations=tuple(package.recommendations),
    )


def package_situation(repos: Repositories, package_id: DssPackageId) -> SituationReading | None:
    package = repos.dss.get_package(package_id)
    if package is None:
        return None
    return _reading_for_package(repos, package)


def alert_situation(repos: Repositories, alert_id: AlertId) -> SituationReading | None:
    chain = alert_chain(repos, alert_id)
    if chain is None:
        return None
    return interpret_situation(
        alerts=(chain.alert,),
        evidence_packages=(chain.evidence_package,) if chain.evidence_package else (),
        evidence_items=chain.items,
        evaluations=chain.evaluations,
        indicator_values=chain.indicator_values,
        observations=chain.observations,
    )


def decision_context(repos: Repositories, decision_id: DecisionId) -> DecisionContext | None:
    decision = repos.decisions.get(decision_id)
    if decision is None:
        return None
    return DecisionContext(
        decision=decision,
        snapshot=repos.dss.get_snapshot(decision.dss_context_snapshot_id),
        package=repos.dss.get_package(decision.dss_package_id),
    )
