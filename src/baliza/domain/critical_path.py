from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from baliza.domain.alert import Alert
from baliza.domain.enums import (
    AlertSeverity,
    AlertStatus,
    EpistemicLabel,
    EvidenceKind,
    RuleOutcome,
)
from baliza.domain.errors import InsufficientEvidence
from baliza.domain.evidence import EvidenceItem, EvidencePackage, item_from_ref
from baliza.domain.ids import AlertId, EvidencePackageId
from baliza.domain.indicator import IndicatorValue
from baliza.domain.observation import Observation
from baliza.domain.quality import ScopeHealth, health_from_quality
from baliza.domain.rule import Rule, RuleEvaluation, RuleVersion, evaluate_rule


@dataclass(frozen=True, slots=True)
class CriticalPathResult:
    observation: Observation
    indicator_value: IndicatorValue
    evaluation: RuleEvaluation
    evidence_items: tuple[EvidenceItem, ...]
    evidence_package: EvidencePackage | None
    alert: Alert | None


def run_critical_path(
    *,
    observation: Observation,
    indicator_value: IndicatorValue,
    rule: Rule,
    rule_version: RuleVersion,
    evaluated_at: datetime,
    alerted_at: datetime,
    spatial_ref: str | None = None,
) -> CriticalPathResult:
    """Synchronous, LLM-free critical path."""
    evaluation = evaluate_rule(
        rule=rule,
        version=rule_version,
        indicator_value=indicator_value,
        evaluated_at=evaluated_at,
    )
    obs_item = item_from_ref(
        kind=EvidenceKind.PRIMARY,
        label=EpistemicLabel.FACT,
        referenced_type="Observation",
        referenced_id=str(observation.id),
        created_at=evaluated_at,
        narrative=f"variable={observation.variable}",
    )
    ind_item = item_from_ref(
        kind=EvidenceKind.DERIVED,
        label=EpistemicLabel.FACT,
        referenced_type="IndicatorValue",
        referenced_id=str(indicator_value.id),
        created_at=evaluated_at,
    )
    limitation = evaluation.outcome in {
        RuleOutcome.UNKNOWN,
        RuleOutcome.INSUFFICIENT_DATA,
        RuleOutcome.INVALID_INPUT,
    }
    eval_item = item_from_ref(
        kind=EvidenceKind.DATA_QUALITY if limitation else EvidenceKind.DERIVED,
        label=EpistemicLabel.FACT,
        referenced_type="RuleEvaluation",
        referenced_id=str(evaluation.id),
        created_at=evaluated_at,
        narrative=evaluation.reason,
    )
    items = (obs_item, ind_item, eval_item)
    gaps: list[str] = []
    if limitation:
        gaps.append(evaluation.reason)

    package: EvidencePackage | None = None
    alert: Alert | None = None
    if evaluation.outcome == RuleOutcome.TRIGGERED:
        package = EvidencePackage(
            id=EvidencePackageId(),
            subject=f"rule:{rule.id}",
            item_ids=tuple(i.id for i in items),
            assembled_at=evaluated_at,
            gaps=tuple(gaps),
            incomplete=False,
        )
        severity = AlertSeverity(rule_version.severity_if_triggered)
        if severity == AlertSeverity.CRITICAL and package is None:
            raise InsufficientEvidence("Critical alert without evidence.")
        alert = Alert(
            id=AlertId(),
            severity=severity,
            status=AlertStatus.OPEN,
            alerted_at=alerted_at,
            evidence_package_id=package.id,
            rule_evaluation_ids=(evaluation.id,),
            spatial_ref=spatial_ref,
            health=health_from_quality(indicator_value.quality),
        )
    else:
        package = EvidencePackage(
            id=EvidencePackageId(),
            subject=f"rule:{rule.id}:not_triggered",
            item_ids=tuple(i.id for i in items),
            assembled_at=evaluated_at,
            gaps=tuple(gaps) or ("not_triggered",),
            incomplete=evaluation.outcome != RuleOutcome.NOT_TRIGGERED,
        )
        # No alert on not_triggered / insufficient data — health is not 'no risk'
        _ = ScopeHealth.INSUFFICIENT_DATA

    return CriticalPathResult(
        observation=observation,
        indicator_value=indicator_value,
        evaluation=evaluation,
        evidence_items=items,
        evidence_package=package,
        alert=alert,
    )
