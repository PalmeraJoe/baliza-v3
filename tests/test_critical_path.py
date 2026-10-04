from datetime import UTC, datetime

import pytest

from baliza.application.use_cases import (
    calculate_indicator,
    evaluate_and_maybe_alert,
    record_observation,
)
from baliza.domain.enums import DataQualityFacet, EvidenceKind, RuleOutcome
from baliza.domain.quality import DataQuality

NOW = datetime(2026, 9, 30, 12, 0, tzinfo=UTC)


def test_critical_path_triggered_without_ai(
    repos, published_indicator, published_rule
) -> None:
    indicator, iversion = published_indicator
    rule, rversion = published_rule
    repos.indicators.add_definition(indicator, iversion)
    repos.rules.add_rule(rule, rversion)
    obs = record_observation(
        repos,
        variable="sst",
        unit="degC",
        observed_at=NOW,
        quality=DataQuality(facet=DataQualityFacet.VALID, score=0.9),
        value=30.4,
    )
    ivalue = calculate_indicator(repos, version=iversion, observation=obs)
    assert ivalue.value == pytest.approx(3.4)
    assert ivalue.source_observation_ids == (obs.id,)
    result = evaluate_and_maybe_alert(
        repos, observation=obs, indicator_value=ivalue, rule=rule, rule_version=rversion
    )
    assert result.evaluation.outcome is RuleOutcome.TRIGGERED
    assert result.alert is not None
    assert result.evidence_package is not None
    kinds = {i.kind for i in result.evidence_items}
    assert EvidenceKind.PRIMARY in kinds
    assert EvidenceKind.DERIVED in kinds
    stored = repos.rules.get_evaluation(result.evaluation.id)
    assert stored is not None
    assert stored.rule_version == "1.0.0"


def test_missing_data_does_not_create_all_clear_alert(
    repos, published_indicator, published_rule
) -> None:
    indicator, iversion = published_indicator
    rule, rversion = published_rule
    repos.indicators.add_definition(indicator, iversion)
    repos.rules.add_rule(rule, rversion)
    obs = record_observation(
        repos,
        variable="sst",
        unit="degC",
        observed_at=NOW,
        quality=DataQuality(facet=DataQualityFacet.MISSING),
        value=None,
    )
    ivalue = calculate_indicator(repos, version=iversion, observation=obs)
    result = evaluate_and_maybe_alert(
        repos, observation=obs, indicator_value=ivalue, rule=rule, rule_version=rversion
    )
    assert result.alert is None
    assert result.evaluation.outcome is RuleOutcome.UNKNOWN
    assert any(item.kind is EvidenceKind.DATA_QUALITY for item in result.evidence_items)
    assert ivalue.quality.implies_no_risk() is False
    assert any(e.action == "rule.evaluated" for e in repos.audit.events)
