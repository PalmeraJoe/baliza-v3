from datetime import UTC, datetime

import pytest

from baliza.application.use_cases import Repositories
from baliza.domain.enums import ComparisonOp, DataQualityFacet, PublicationStatus
from baliza.domain.ids import IndicatorId, IndicatorVersionId, RuleId, RuleVersionId
from baliza.domain.indicator import Indicator, IndicatorVersion
from baliza.domain.rule import Rule, RuleVersion, Threshold
from baliza.infrastructure.clock import FixedClock
from baliza.infrastructure.memory import (
    InMemoryActorRepository,
    InMemoryAlertRepository,
    InMemoryAuditRepository,
    InMemoryDecisionRepository,
    InMemoryDssRepository,
    InMemoryEvidenceRepository,
    InMemoryIndicatorRepository,
    InMemoryActionRepository,
    InMemoryObservationRepository,
    InMemoryRuleRepository,
    bind_memory_unit_of_work,
)

NOW = datetime(2026, 9, 30, 12, 0, tzinfo=UTC)


@pytest.fixture
def now() -> datetime:
    return NOW


@pytest.fixture
def repos(now: datetime) -> Repositories:
    built = Repositories(
        actors=InMemoryActorRepository(),
        observations=InMemoryObservationRepository(),
        indicators=InMemoryIndicatorRepository(),
        rules=InMemoryRuleRepository(),
        evidence=InMemoryEvidenceRepository(),
        alerts=InMemoryAlertRepository(),
        dss=InMemoryDssRepository(),
        decisions=InMemoryDecisionRepository(),
        actions=InMemoryActionRepository(),
        audit=InMemoryAuditRepository(),
        clock=FixedClock(now),
    )
    return bind_memory_unit_of_work(built)


@pytest.fixture
def published_indicator() -> tuple[Indicator, IndicatorVersion]:
    indicator = Indicator(id=IndicatorId(), name="sst_anomaly")
    version = IndicatorVersion(
        id=IndicatorVersionId(),
        indicator_id=indicator.id,
        version="1.0.0",
        unit="degC",
        formula_kind="subtract_baseline",
        baseline=27.0,
        status=PublicationStatus.PUBLISHED,
        input_variable="sst",
    )
    return indicator, version


@pytest.fixture
def published_rule() -> tuple[Rule, RuleVersion]:
    rule = Rule(id=RuleId(), name="thermal_stress_candidate")
    version = RuleVersion(
        id=RuleVersionId(),
        rule_id=rule.id,
        version="1.0.0",
        thresholds=(Threshold(name="anomaly_high", value=2.0),),
        operator=ComparisonOp.GT,
        threshold_name="anomaly_high",
        severity_if_triggered="critical",
        status=PublicationStatus.PUBLISHED,
    )
    return rule, version
