from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from baliza.application.ports import (
    ActorRepository,
    AlertRepository,
    AuditRepository,
    Clock,
    ActionRepository,
    DecisionRepository,
    DssRepository,
    EvidenceRepository,
    IndicatorRepository,
    ObservationRepository,
    RuleRepository,
    UnitOfWork,
)
from baliza.domain.action import Action, Outcome, record_action, record_outcome
from baliza.domain.actor import Actor
from baliza.domain.alert import Alert
from baliza.domain.audit import audit
from baliza.domain.critical_path import CriticalPathResult, run_critical_path
from baliza.domain.decision import Decision, record_decision
from baliza.domain.dss import DssPackage, RecommendationView, freeze_dss_package, presented_context_payload
from baliza.domain.enums import DataQualityFacet, PublicationStatus
from baliza.domain.ids import (
    ActorId,
    AlertId,
    DataSourceId,
    DssPackageId,
    IndicatorId,
    ObservationId,
    RuleId,
)
from baliza.domain.indicator import (
    Indicator,
    IndicatorValue,
    IndicatorVersion,
    calculate_indicator_value,
)
from baliza.domain.observation import Observation
from baliza.domain.protocol import ProtocolVersion, recommendations_from_protocol
from baliza.domain.quality import DataQuality
from baliza.domain.rule import Rule, RuleVersion


@dataclass(slots=True)
class Repositories:
    actors: ActorRepository
    observations: ObservationRepository
    indicators: IndicatorRepository
    rules: RuleRepository
    evidence: EvidenceRepository
    alerts: AlertRepository
    dss: DssRepository
    decisions: DecisionRepository
    actions: ActionRepository
    audit: AuditRepository
    clock: Clock
    uow: UnitOfWork | None = None


def record_observation(
    repos: Repositories,
    *,
    variable: str,
    unit: str,
    observed_at: datetime,
    quality: DataQuality,
    value: float | None,
    source_id: DataSourceId | None = None,
    spatial_ref: str | None = None,
    metadata: dict[str, str] | None = None,
) -> Observation:
    now = repos.clock.now()
    obs = Observation(
        id=ObservationId(),
        variable=variable,
        unit=unit,
        observed_at=observed_at,
        processed_at=now,
        quality=quality,
        source_id=source_id,
        value=value,
        spatial_ref=spatial_ref,
        metadata=metadata or {},
    )
    repos.observations.add(obs)
    repos.audit.add(
        audit(
            occurred_at=now,
            action="observation.recorded",
            entity_type="Observation",
            entity_id=str(obs.id),
            system_component="ingestion",
        )
    )
    return obs


def calculate_indicator(
    repos: Repositories,
    *,
    version: IndicatorVersion,
    observation: Observation,
) -> IndicatorValue:
    value = calculate_indicator_value(
        version=version,
        observations=(observation.id,),
        observation_value=observation.value,
        observation_quality=observation.quality,
        computed_at=repos.clock.now(),
        unit=version.unit,
    )
    repos.indicators.add_value(value)
    repos.audit.add(
        audit(
            occurred_at=value.computed_at,
            action="indicator.calculated",
            entity_type="IndicatorValue",
            entity_id=str(value.id),
            system_component="indicators",
            entity_version=version.version,
        )
    )
    return value


def evaluate_and_maybe_alert(
    repos: Repositories,
    *,
    observation: Observation,
    indicator_value: IndicatorValue,
    rule: Rule,
    rule_version: RuleVersion,
) -> CriticalPathResult:
    now = repos.clock.now()
    result = run_critical_path(
        observation=observation,
        indicator_value=indicator_value,
        rule=rule,
        rule_version=rule_version,
        evaluated_at=now,
        alerted_at=now,
        spatial_ref=observation.spatial_ref,
    )
    if repos.uow is None:
        raise RuntimeError("Critical path requires a UnitOfWork.")
    repos.uow.begin()
    try:
        repos.rules.add_evaluation(result.evaluation)
        for item in result.evidence_items:
            repos.evidence.add_item(item)
        if result.evidence_package is None:
            raise RuntimeError("critical path produced no evidence package")
        repos.evidence.add_package(result.evidence_package)
        repos.audit.add(
            audit(
                occurred_at=now,
                action="rule.evaluated",
                entity_type="RuleEvaluation",
                entity_id=str(result.evaluation.id),
                system_component="rules",
                entity_version=rule_version.version,
                context={"outcome": result.evaluation.outcome.value, "ai_used": False},
            )
        )
        repos.audit.add(
            audit(
                occurred_at=now,
                action="evidence.package_created",
                entity_type="EvidencePackage",
                entity_id=str(result.evidence_package.id),
                system_component="evidence",
                context={"outcome": result.evaluation.outcome.value},
            )
        )
        if result.alert:
            if result.alert.evidence_package_id is None:
                raise RuntimeError("alert without evidence package")
            repos.alerts.add(result.alert)
            repos.audit.add(
                audit(
                    occurred_at=now,
                    action="alert.created",
                    entity_type="Alert",
                    entity_id=str(result.alert.id),
                    system_component="alerts",
                    entity_version=rule_version.version,
                    context={"rule_id": str(rule.id), "outcome": result.evaluation.outcome.value},
                )
            )
        repos.uow.commit()
    except Exception:
        repos.uow.rollback()
        raise
    return result


def build_dss_package(
    repos: Repositories,
    *,
    alert: Alert | None = None,
    alerts: list[Alert] | None = None,
    extra_gaps: list[str] | None = None,
    protocol_version: str | None = None,
    protocol: ProtocolVersion | None = None,
    recommendations: list[RecommendationView] | None = None,
    uncertainty_notes: list[str] | None = None,
) -> DssPackage:
    package = DssPackage(id=DssPackageId(), opened_at=repos.clock.now())
    chosen = list(alerts or [])
    if alert is not None and alert not in chosen:
        chosen.append(alert)
    for item in chosen:
        package.add_alert(item.id)
        if item.evidence_package_id not in package.evidence_package_ids:
            package.evidence_package_ids.append(item.evidence_package_id)
        for evaluation_id in item.rule_evaluation_ids:
            package.add_evaluation(evaluation_id)
    if extra_gaps:
        for gap in extra_gaps:
            package.add_gap(gap)
    if uncertainty_notes:
        package.uncertainty_notes.extend(uncertainty_notes)
    if protocol is not None:
        package.protocol_version = f"{protocol.protocol_id}:{protocol.version}"
        package.recommendations.extend(recommendations_from_protocol(protocol))
    elif protocol_version:
        package.protocol_version = protocol_version
    if recommendations:
        package.recommendations.extend(recommendations)
    repos.dss.add_package(package)
    if package.recommendations:
        repos.audit.add(
            audit(
                occurred_at=package.opened_at,
                action="recommendation.presented",
                entity_type="DssPackage",
                entity_id=str(package.id),
                system_component="dss",
                context={
                    "count": len(package.recommendations),
                    "epistemic_label": "RECOMMENDATION",
                    "creates_decision": False,
                },
            )
        )
    repos.audit.add(
        audit(
            occurred_at=package.opened_at,
            action="dss.package_opened",
            entity_type="DssPackage",
            entity_id=str(package.id),
            system_component="dss",
            context={"alert_count": len(package.alert_ids), "ai_used": False},
        )
    )
    return package


def _presented_at_decision(repos: Repositories, package: DssPackage) -> dict:
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
    units: dict[str, str] = {}
    qualities: dict[str, str] = {}
    versions: dict[str, str] = {}
    indicator_values = []
    observations = []
    for evaluation in evaluations:
        for value_id in evaluation.input_indicator_value_ids:
            value = repos.indicators.get_value(value_id)
            if value is None:
                continue
            indicator_values.append(value)
            units.setdefault(str(evaluation.id), value.unit)
            qualities.setdefault(str(evaluation.id), value.quality.facet.value)
            versions.setdefault(str(evaluation.id), value.indicator_version)
            for observation_id in value.source_observation_ids:
                observation = repos.observations.get(observation_id)
                if observation is not None:
                    observations.append(observation)
    options = tuple(item.text for item in package.recommendations if item.source == "protocol")
    return presented_context_payload(
        alerts=alerts,
        evidence_packages=tuple(evidence_packages),
        evidence_items=tuple(evidence_items),
        evaluations=evaluations,
        indicator_units=units,
        input_qualities=qualities,
        indicator_versions=versions,
        protocol_options=options,
        indicator_values=tuple(indicator_values),
        observations=tuple(observations),
        recommendations=tuple(package.recommendations),
    )


def record_human_decision(
    repos: Repositories,
    *,
    actor: Actor,
    package: DssPackage,
    justification: str,
    selected_option: str,
    extra_snapshot: dict | None = None,
) -> Decision:
    now = repos.clock.now()
    snapshot = freeze_dss_package(
        package,
        frozen_at=now,
        extra=extra_snapshot,
        presented=_presented_at_decision(repos, package),
    )
    decision = record_decision(
        actor_id=actor.id,
        snapshot=snapshot,
        decided_at=now,
        justification=justification,
        selected_option=selected_option,
    )
    if repos.uow:
        repos.uow.begin()
    try:
        repos.dss.add_snapshot(snapshot)
        repos.decisions.add(decision)
    except Exception:
        if repos.uow:
            repos.uow.rollback()
        raise
    repos.audit.add(
        audit(
            occurred_at=now,
            action="dss_context_snapshot.frozen",
            entity_type="DssContextSnapshot",
            entity_id=str(snapshot.id),
            actor_id=actor.id,
            entity_version=snapshot.content_hash,
        )
    )
    repos.audit.add(
        audit(
            occurred_at=now,
            action="decision.recorded",
            entity_type="Decision",
            entity_id=str(decision.id),
            actor_id=actor.id,
            entity_version=snapshot.content_hash,
            reason=justification,
        )
    )
    if repos.uow:
        repos.uow.commit()
    return decision


def acknowledge_alert(
    repos: Repositories,
    *,
    alert: Alert,
    actor: Actor,
) -> Alert:
    updated = alert.acknowledge(reviewed_at=repos.clock.now(), actor_id=str(actor.id))
    repos.alerts.save(updated)
    repos.audit.add(
        audit(
            occurred_at=repos.clock.now(),
            action="alert.acknowledged",
            entity_type="Alert",
            entity_id=str(updated.id),
            actor_id=actor.id,
            reason="awareness_only",
        )
    )
    return updated


def activate_rule_version(repos: Repositories, version: RuleVersion) -> RuleVersion:
    if version.status == PublicationStatus.PUBLISHED:
        return version
    published = version.publish()
    repos.rules.replace_version(published)
    now = repos.clock.now()
    repos.audit.add(
        audit(
            occurred_at=now,
            action="rule_version.activated",
            entity_type="RuleVersion",
            entity_id=str(published.id),
            entity_version=published.version,
            system_component="baliza.application",
        )
    )
    return published


def record_human_action(
    repos: Repositories,
    *,
    decision: Decision,
    description: str,
    actor: Actor,
    action_type: str = "recorded_step",
    metadata: dict | None = None,
) -> Action:
    action = record_action(
        decision_id=decision.id,
        acted_at=repos.clock.now(),
        description=description,
        recorded_by=actor.id,
        action_type=action_type,
        metadata=metadata,
    )
    repos.actions.add_action(action)
    repos.audit.add(
        audit(
            occurred_at=action.acted_at,
            action="action.recorded",
            entity_type="Action",
            entity_id=str(action.id),
            actor_id=actor.id,
            reason=description,
        )
    )
    return action


def record_human_outcome(
    repos: Repositories,
    *,
    action: Action,
    decision: Decision,
    notes: str,
) -> Outcome:
    outcome = record_outcome(
        action_id=action.id,
        decision_id=decision.id,
        observed_outcome_at=repos.clock.now(),
        notes=notes,
    )
    repos.actions.add_outcome(outcome)
    repos.audit.add(
        audit(
            occurred_at=outcome.observed_outcome_at,
            action="outcome.recorded",
            entity_type="Outcome",
            entity_id=str(outcome.id),
            system_component="baliza.application",
            reason=notes,
        )
    )
    return outcome
