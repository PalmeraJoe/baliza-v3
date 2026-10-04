from __future__ import annotations

from dataclasses import dataclass

from baliza.domain.alert import Alert
from baliza.domain.dss import RecommendationView
from baliza.domain.enums import DataGapKind, DataQualityFacet, EvidenceKind, RuleOutcome, UncertaintyType
from baliza.domain.evidence import EvidenceItem, EvidencePackage
from baliza.domain.indicator import IndicatorValue
from baliza.domain.observation import Observation
from baliza.domain.quality import health_from_quality
from baliza.domain.rule import RuleEvaluation


@dataclass(frozen=True, slots=True)
class DataGap:
    """Missing or unreliable context. Not an alert, a risk, or a decision."""

    kind: DataGapKind
    reason: str
    source_type: str
    source_id: str


@dataclass(frozen=True, slots=True)
class UncertaintyStatement:
    uncertainty_type: UncertaintyType
    reason: str
    source_type: str
    source_id: str
    affected_indicator_id: str | None = None
    affected_rule_id: str | None = None


@dataclass(frozen=True, slots=True)
class SignalReading:
    rule_evaluation_id: str
    rule_id: str
    rule_version_id: str
    rule_version: str
    outcome: str
    reason: str
    thresholds: dict[str, float]
    indicator_value_id: str | None
    indicator_version: str | None
    indicator_unit: str | None
    observed_value: float | None
    quality: str | None
    quality_statement: str
    alert_id: str | None
    alert_status: str | None
    alert_severity: str | None
    scope_health: str | None
    observed_at: str | None
    evaluated_at: str
    alerted_at: str | None
    spatial_ref: str | None


@dataclass(frozen=True, slots=True)
class SituationReading:
    """Projection for a human. It does not select an option or record a Decision."""

    readings: tuple[SignalReading, ...]
    gaps: tuple[DataGap, ...]
    uncertainty: tuple[UncertaintyStatement, ...]
    supports: tuple[dict, ...]
    limits: tuple[dict, ...]
    context_items: tuple[dict, ...]
    contradictory: tuple[str, ...]
    recommendations: tuple[RecommendationView, ...]

    def gaps_payload(self) -> list[dict]:
        return [
            {
                "kind": gap.kind.value,
                "reason": gap.reason,
                "source_type": gap.source_type,
                "source_id": gap.source_id,
            }
            for gap in self.gaps
        ]

    def uncertainty_payload(self) -> list[dict]:
        return [
            {
                "uncertainty_type": item.uncertainty_type.value,
                "reason": item.reason,
                "source_type": item.source_type,
                "source_id": item.source_id,
                "affected_indicator_id": item.affected_indicator_id,
                "affected_rule_id": item.affected_rule_id,
            }
            for item in self.uncertainty
        ]

    def readings_payload(self) -> list[dict]:
        return [
            {
                "rule_evaluation_id": row.rule_evaluation_id,
                "rule_id": row.rule_id,
                "rule_version_id": row.rule_version_id,
                "rule_version": row.rule_version,
                "outcome": row.outcome,
                "reason": row.reason,
                "thresholds": dict(row.thresholds),
                "indicator_value_id": row.indicator_value_id,
                "indicator_version": row.indicator_version,
                "indicator_unit": row.indicator_unit,
                "observed_value": row.observed_value,
                "quality": row.quality,
                "quality_statement": row.quality_statement,
                "alert_id": row.alert_id,
                "alert_status": row.alert_status,
                "alert_severity": row.alert_severity,
                "scope_health": row.scope_health,
                "observed_at": row.observed_at,
                "evaluated_at": row.evaluated_at,
                "alerted_at": row.alerted_at,
                "spatial_ref": row.spatial_ref,
            }
            for row in self.readings
        ]

    def synthesis_payload(self) -> dict:
        return {
            "supports": list(self.supports),
            "limits": list(self.limits),
            "contextual": list(self.context_items),
            "contradictory": list(self.contradictory),
            "missing": self.gaps_payload(),
        }

    def to_dict(self) -> dict:
        return {
            "signals": self.readings_payload(),
            "evidence": self.synthesis_payload(),
            "data_gaps": self.gaps_payload(),
            "uncertainty": self.uncertainty_payload(),
            "options": [
                {
                    "recommendation_id": item.recommendation_id,
                    "source": item.source,
                    "text": item.text,
                    "epistemic_label": item.epistemic_label,
                    "rationale": item.rationale,
                    "evidence_refs": list(item.evidence_refs),
                    "uncertainty_note": item.uncertainty_note,
                    "preconditions": list(item.preconditions),
                    "constraints": list(item.constraints),
                    "is_decision": False,
                }
                for item in self.recommendations
            ],
            "decision": None,
            "ai_used": False,
        }


def quality_statement(facet: DataQualityFacet | None, outcome: RuleOutcome) -> str:
    if outcome is RuleOutcome.UNKNOWN or facet in {None, DataQualityFacet.UNKNOWN, DataQualityFacet.MISSING}:
        return "State cannot be determined reliably"
    if outcome is RuleOutcome.INSUFFICIENT_DATA or facet in {
        DataQualityFacet.SUSPECT,
        DataQualityFacet.INSUFFICIENT,
        DataQualityFacet.LOW_QUALITY,
        DataQualityFacet.DELAYED,
        DataQualityFacet.INVALID,
        DataQualityFacet.SOURCE_UNAVAILABLE,
    }:
        return "Evidence is limited"
    return "Evidence supports the signal"


def _item_payload(item: EvidenceItem) -> dict:
    return {
        "evidence_item_id": str(item.id),
        "kind": item.kind.value,
        "epistemic_label": item.epistemic_label.value,
        "referenced_type": item.referenced_type,
        "referenced_id": item.referenced_id,
        "narrative": item.narrative,
        "created_at": item.created_at.isoformat(),
    }


def interpret_situation(
    *,
    alerts: tuple[Alert, ...] = (),
    evidence_packages: tuple[EvidencePackage, ...] = (),
    evidence_items: tuple[EvidenceItem, ...] = (),
    evaluations: tuple[RuleEvaluation, ...] = (),
    indicator_values: tuple[IndicatorValue, ...] = (),
    observations: tuple[Observation, ...] = (),
    recommendations: tuple[RecommendationView, ...] = (),
) -> SituationReading:
    values = {str(value.id): value for value in indicator_values}
    observed = {str(obs.id): obs for obs in observations}
    alerts_by_evaluation: dict[str, Alert] = {}
    for alert in alerts:
        for evaluation_id in alert.rule_evaluation_ids:
            alerts_by_evaluation.setdefault(str(evaluation_id), alert)

    gaps: list[DataGap] = []
    seen_gaps: set[tuple[str, str, str, str]] = set()
    uncertainty: list[UncertaintyStatement] = []
    readings: list[SignalReading] = []

    def add_gap(kind: DataGapKind, reason: str, source_type: str, source_id: str) -> None:
        key = (kind.value, reason, source_type, source_id)
        if key in seen_gaps:
            return
        seen_gaps.add(key)
        gaps.append(DataGap(kind=kind, reason=reason, source_type=source_type, source_id=source_id))

    for evaluation in evaluations:
        value = next((values[str(vid)] for vid in evaluation.input_indicator_value_ids if str(vid) in values), None)
        observation = None
        if value is not None:
            observation = next(
                (observed[str(oid)] for oid in value.source_observation_ids if str(oid) in observed),
                None,
            )
        facet = value.quality.facet if value is not None else None
        alert = alerts_by_evaluation.get(str(evaluation.id))
        if evaluation.outcome is RuleOutcome.UNKNOWN:
            kind = (
                DataGapKind.UNKNOWN_QUALITY
                if evaluation.reason == "quality_not_determinable"
                else DataGapKind.MISSING_OBSERVATION
            )
            add_gap(kind, evaluation.reason, "RuleEvaluation", str(evaluation.id))
            uncertainty.append(
                UncertaintyStatement(
                    uncertainty_type=UncertaintyType.UNKNOWN,
                    reason=evaluation.reason,
                    source_type="RuleEvaluation",
                    source_id=str(evaluation.id),
                    affected_indicator_id=str(value.id) if value else None,
                    affected_rule_id=str(evaluation.rule_id),
                )
            )
        elif evaluation.outcome is RuleOutcome.INSUFFICIENT_DATA:
            kind = (
                DataGapKind.INSUFFICIENT_COVERAGE
                if evaluation.reason == "insufficient_sample"
                else DataGapKind.BELOW_MINIMUM_QUALITY
            )
            add_gap(kind, evaluation.reason, "RuleEvaluation", str(evaluation.id))
            uncertainty_type = (
                UncertaintyType.SUSPECT if facet is DataQualityFacet.SUSPECT else UncertaintyType.INSUFFICIENT
            )
            uncertainty.append(
                UncertaintyStatement(
                    uncertainty_type=uncertainty_type,
                    reason=evaluation.reason,
                    source_type="RuleEvaluation",
                    source_id=str(evaluation.id),
                    affected_indicator_id=str(value.id) if value else None,
                    affected_rule_id=str(evaluation.rule_id),
                )
            )
        elif facet is DataQualityFacet.VALID and evaluation.outcome in {
            RuleOutcome.TRIGGERED,
            RuleOutcome.NOT_TRIGGERED,
        }:
            uncertainty.append(
                UncertaintyStatement(
                    uncertainty_type=UncertaintyType.KNOWN,
                    reason=evaluation.reason,
                    source_type="RuleEvaluation",
                    source_id=str(evaluation.id),
                    affected_indicator_id=str(value.id) if value else None,
                    affected_rule_id=str(evaluation.rule_id),
                )
            )
        spatial = None
        if alert is not None and alert.spatial_ref:
            spatial = alert.spatial_ref
        elif observation is not None:
            spatial = observation.spatial_ref
        health = alert.health.value if alert is not None else (
            health_from_quality(value.quality).value if value is not None else None
        )
        readings.append(
            SignalReading(
                rule_evaluation_id=str(evaluation.id),
                rule_id=str(evaluation.rule_id),
                rule_version_id=str(evaluation.rule_version_id),
                rule_version=evaluation.rule_version,
                outcome=evaluation.outcome.value,
                reason=evaluation.reason,
                thresholds=dict(evaluation.thresholds_applied),
                indicator_value_id=str(value.id) if value else None,
                indicator_version=value.indicator_version if value else None,
                indicator_unit=value.unit if value else None,
                observed_value=value.value if value else None,
                quality=facet.value if facet else None,
                quality_statement=quality_statement(facet, evaluation.outcome),
                alert_id=str(alert.id) if alert else None,
                alert_status=alert.status.value if alert else None,
                alert_severity=alert.severity.value if alert else None,
                scope_health=health,
                observed_at=observation.observed_at.isoformat() if observation else None,
                evaluated_at=evaluation.evaluated_at.isoformat(),
                alerted_at=alert.alerted_at.isoformat() if alert else None,
                spatial_ref=spatial,
            )
        )

    for package in evidence_packages:
        for conflict in package.conflicts:
            uncertainty.append(
                UncertaintyStatement(
                    uncertainty_type=UncertaintyType.CONFLICTING,
                    reason=conflict,
                    source_type="EvidencePackage",
                    source_id=str(package.id),
                )
            )
        for gap in package.gaps:
            if gap == "not_triggered":
                continue
            if any(item.reason == gap for item in gaps):
                continue
            add_gap(DataGapKind.STATED_GAP, gap, "EvidencePackage", str(package.id))

    supports = tuple(
        _item_payload(item) for item in evidence_items if item.kind in {EvidenceKind.PRIMARY, EvidenceKind.DERIVED}
    )
    limits = tuple(_item_payload(item) for item in evidence_items if item.kind is EvidenceKind.DATA_QUALITY)
    contextual = tuple(_item_payload(item) for item in evidence_items if item.kind is EvidenceKind.CONTEXTUAL)
    contradictory = tuple(conflict for package in evidence_packages for conflict in package.conflicts)
    return SituationReading(
        readings=tuple(readings),
        gaps=tuple(gaps),
        uncertainty=tuple(uncertainty),
        supports=supports,
        limits=limits,
        context_items=contextual,
        contradictory=contradictory,
        recommendations=recommendations,
    )
