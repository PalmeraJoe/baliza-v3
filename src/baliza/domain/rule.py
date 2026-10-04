from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime
from typing import Any, Mapping

from baliza.domain.enums import ComparisonOp, PublicationStatus, RuleOutcome
from baliza.domain.errors import PublishedVersionImmutable
from baliza.domain.hashing import freeze_value, require_aware
from baliza.domain.ids import IndicatorValueId, RuleEvaluationId, RuleId, RuleVersionId
from baliza.domain.indicator import IndicatorValue
from baliza.domain.quality import DataQualityFacet

EVALUATOR_ENGINE_ID = "baliza.rules.threshold_v1"


@dataclass(frozen=True, slots=True)
class Rule:
    id: RuleId
    name: str
    description: str = ""


@dataclass(frozen=True, slots=True)
class Threshold:
    name: str
    value: float


@dataclass(frozen=True, slots=True)
class RuleVersion:
    """Published bodies are immutable (Invariant 7)."""

    id: RuleVersionId
    rule_id: RuleId
    version: str
    thresholds: tuple[Threshold, ...]
    operator: ComparisonOp
    threshold_name: str
    severity_if_triggered: str
    status: PublicationStatus = PublicationStatus.DRAFT
    min_quality_usable: bool = True
    evaluator_engine_id: str = EVALUATOR_ENGINE_ID

    def threshold_map(self) -> dict[str, float]:
        return {t.name: t.value for t in self.thresholds}

    def publish(self) -> RuleVersion:
        if self.status == PublicationStatus.PUBLISHED:
            return self
        return replace(self, status=PublicationStatus.PUBLISHED)

    def with_threshold(self, name: str, value: float) -> RuleVersion:
        if self.status == PublicationStatus.PUBLISHED:
            raise PublishedVersionImmutable("Published RuleVersion cannot be mutated.")
        others = tuple(t for t in self.thresholds if t.name != name)
        return replace(self, thresholds=(*others, Threshold(name=name, value=value)))


@dataclass(frozen=True, slots=True)
class RuleEvaluation:
    id: RuleEvaluationId
    rule_id: RuleId
    rule_version_id: RuleVersionId
    rule_version: str
    evaluated_at: datetime
    outcome: RuleOutcome
    input_indicator_value_ids: tuple[IndicatorValueId, ...]
    thresholds_applied: Mapping[str, float]
    evaluator_engine_id: str
    reason: str
    input_snapshot: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        require_aware(self.evaluated_at, "evaluated_at")
        if not self.rule_version:
            raise ValueError("RuleEvaluation must store rule_version (Invariant 4).")
        object.__setattr__(self, "input_snapshot", freeze_value(self.input_snapshot))
        object.__setattr__(self, "thresholds_applied", freeze_value(self.thresholds_applied))


def _compare(op: ComparisonOp, left: float, right: float, upper: float | None = None) -> bool:
    if op is ComparisonOp.GT:
        return left > right
    if op is ComparisonOp.GTE:
        return left >= right
    if op is ComparisonOp.LT:
        return left < right
    if op is ComparisonOp.LTE:
        return left <= right
    if op is ComparisonOp.BETWEEN:
        if upper is None:
            raise ValueError("BETWEEN requires an upper threshold.")
        return right <= left <= upper
    return left == right


def evaluate_rule(
    *,
    rule: Rule,
    version: RuleVersion,
    indicator_value: IndicatorValue | None,
    evaluated_at: datetime,
) -> RuleEvaluation:
    """Deterministic; never calls LLM. Missing data → INSUFFICIENT_DATA, not 'no risk'."""
    thresholds = version.threshold_map()
    bound = thresholds.get(version.threshold_name)
    inputs = (indicator_value.id,) if indicator_value else ()
    snapshot: dict[str, Any] = {
        "indicator_value": indicator_value.value if indicator_value else None,
        "quality": indicator_value.quality.facet.value if indicator_value else None,
        "formula_notes": list(indicator_value.notes) if indicator_value else [],
    }

    def result(outcome: RuleOutcome, reason: str) -> RuleEvaluation:
        return RuleEvaluation(
            id=RuleEvaluationId(),
            rule_id=rule.id,
            rule_version_id=version.id,
            rule_version=version.version,
            evaluated_at=evaluated_at,
            outcome=outcome,
            input_indicator_value_ids=inputs,
            thresholds_applied=dict(thresholds),
            evaluator_engine_id=version.evaluator_engine_id,
            reason=reason,
            input_snapshot=snapshot,
        )

    if indicator_value is None or indicator_value.value is None:
        facet = indicator_value.quality.facet if indicator_value is not None else DataQualityFacet.MISSING
        if facet == DataQualityFacet.INSUFFICIENT:
            return result(RuleOutcome.INSUFFICIENT_DATA, "insufficient_sample")
        return result(RuleOutcome.UNKNOWN, "required_input_absent")
    if version.min_quality_usable and not indicator_value.quality.is_usable_for_critical_rules:
        facet = indicator_value.quality.facet
        if facet == DataQualityFacet.INVALID:
            return result(RuleOutcome.INVALID_INPUT, "invalid_input_quality")
        if facet == DataQualityFacet.UNKNOWN:
            return result(RuleOutcome.UNKNOWN, "quality_not_determinable")
        if facet in {DataQualityFacet.MISSING, DataQualityFacet.SOURCE_UNAVAILABLE}:
            return result(RuleOutcome.UNKNOWN, "required_input_absent")
        if facet == DataQualityFacet.INSUFFICIENT:
            return result(RuleOutcome.INSUFFICIENT_DATA, "insufficient_sample")
        return result(RuleOutcome.INSUFFICIENT_DATA, f"below_minimum_quality:{facet.value}")
    if bound is None:
        return result(RuleOutcome.INVALID_INPUT, f"missing_threshold:{version.threshold_name}")
    upper = thresholds.get(f"{version.threshold_name}_upper")
    if version.operator is ComparisonOp.BETWEEN and upper is None:
        return result(RuleOutcome.INVALID_INPUT, f"missing_threshold:{version.threshold_name}_upper")

    triggered = _compare(version.operator, indicator_value.value, bound, upper)
    if triggered:
        return result(
            RuleOutcome.TRIGGERED,
            f"{indicator_value.value} {version.operator.value} {bound}",
        )
    return result(
        RuleOutcome.NOT_TRIGGERED,
        f"{indicator_value.value} not {version.operator.value} {bound}",
    )
