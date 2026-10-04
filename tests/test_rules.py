from datetime import UTC, datetime

from baliza.domain.enums import ComparisonOp, DataQualityFacet, RuleOutcome
from baliza.domain.ids import IndicatorId, IndicatorValueId, IndicatorVersionId, ObservationId
from baliza.domain.indicator import IndicatorValue
from baliza.domain.quality import DataQuality
from baliza.domain.rule import evaluate_rule

NOW = datetime(2026, 9, 30, 12, 0, tzinfo=UTC)


def _value(v: float | None, facet: DataQualityFacet) -> IndicatorValue:
    return IndicatorValue(
        id=IndicatorValueId(),
        indicator_id=IndicatorId(),
        indicator_version_id=IndicatorVersionId(),
        indicator_version="1.0.0",
        computed_at=NOW,
        unit="degC",
        source_observation_ids=(ObservationId(),),
        quality=DataQuality(facet=facet, score=0.9 if facet is DataQualityFacet.VALID else None),
        value=v,
    )


def test_triggered(published_rule) -> None:
    rule, version = published_rule
    ev = evaluate_rule(
        rule=rule, version=version, indicator_value=_value(3.1, DataQualityFacet.VALID), evaluated_at=NOW
    )
    assert ev.outcome is RuleOutcome.TRIGGERED
    assert ev.rule_version == "1.0.0"
    assert ev.thresholds_applied["anomaly_high"] == 2.0


def test_not_triggered(published_rule) -> None:
    rule, version = published_rule
    ev = evaluate_rule(
        rule=rule, version=version, indicator_value=_value(1.0, DataQualityFacet.VALID), evaluated_at=NOW
    )
    assert ev.outcome is RuleOutcome.NOT_TRIGGERED


def test_threshold_boundary_not_gt(published_rule) -> None:
    rule, version = published_rule
    ev = evaluate_rule(
        rule=rule, version=version, indicator_value=_value(2.0, DataQualityFacet.VALID), evaluated_at=NOW
    )
    assert ev.outcome is RuleOutcome.NOT_TRIGGERED


def test_missing_input(published_rule) -> None:
    rule, version = published_rule
    ev = evaluate_rule(rule=rule, version=version, indicator_value=None, evaluated_at=NOW)
    assert ev.outcome is RuleOutcome.UNKNOWN
    assert ev.outcome is not RuleOutcome.NOT_TRIGGERED
    assert ev.reason == "required_input_absent"


def test_invalid_input(published_rule) -> None:
    rule, version = published_rule
    ev = evaluate_rule(
        rule=rule,
        version=version,
        indicator_value=_value(9.0, DataQualityFacet.INVALID),
        evaluated_at=NOW,
    )
    assert ev.outcome is RuleOutcome.INVALID_INPUT


def test_version_change_creates_distinct_evaluation(published_rule) -> None:
    rule, v1 = published_rule
    from baliza.domain.enums import PublicationStatus
    from baliza.domain.rule import RuleVersion, Threshold

    v2 = RuleVersion(
        id=v1.id.__class__(),
        rule_id=rule.id,
        version="2.0.0",
        thresholds=(Threshold(name="anomaly_high", value=5.0),),
        operator=ComparisonOp.GT,
        threshold_name="anomaly_high",
        severity_if_triggered="critical",
        status=PublicationStatus.PUBLISHED,
    )
    iv = _value(3.1, DataQualityFacet.VALID)
    e1 = evaluate_rule(rule=rule, version=v1, indicator_value=iv, evaluated_at=NOW)
    e2 = evaluate_rule(rule=rule, version=v2, indicator_value=iv, evaluated_at=NOW)
    assert e1.rule_version == "1.0.0"
    assert e2.rule_version == "2.0.0"
    assert e1.outcome is RuleOutcome.TRIGGERED
    assert e2.outcome is RuleOutcome.NOT_TRIGGERED
