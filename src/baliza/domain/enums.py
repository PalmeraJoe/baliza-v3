from __future__ import annotations

from enum import StrEnum


class EpistemicLabel(StrEnum):
    FACT = "FACT"
    INFERENCE = "INFERENCE"
    RECOMMENDATION = "RECOMMENDATION"
    DECISION = "DECISION"


class EvidenceKind(StrEnum):
    PRIMARY = "primary"
    DERIVED = "derived"
    SCIENTIFIC = "scientific"
    CONTEXTUAL = "contextual"
    ANALYTICAL = "analytical"
    DATA_QUALITY = "data_quality"


class DataQualityFacet(StrEnum):
    VALID = "valid"
    INVALID = "invalid"
    MISSING = "missing"
    DELAYED = "delayed"
    LOW_QUALITY = "low_quality"
    SOURCE_UNAVAILABLE = "source_unavailable"
    SUSPECT = "suspect"
    INSUFFICIENT = "insufficient"
    UNKNOWN = "unknown"


class ScopeHealth(StrEnum):
    """Operational health of a monitored scope. Never means 'no ecological risk'."""

    OK = "OK"
    DEGRADED = "DEGRADED"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"
    UNKNOWN = "UNKNOWN"


class PublicationStatus(StrEnum):
    DRAFT = "draft"
    PUBLISHED = "published"
    DEPRECATED = "deprecated"


class RuleOutcome(StrEnum):
    TRIGGERED = "triggered"
    NOT_TRIGGERED = "not_triggered"
    INSUFFICIENT_DATA = "insufficient_data"
    UNKNOWN = "unknown"
    INVALID_INPUT = "invalid_input"


class AlertStatus(StrEnum):
    OPEN = "OPEN"
    UNDER_REVIEW = "UNDER_REVIEW"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"
    RETRACTED = "RETRACTED"


class AlertSeverity(StrEnum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class DataGapKind(StrEnum):
    """Why context is incomplete. Not an alert, a risk, or a decision."""

    MISSING_OBSERVATION = "missing_observation"
    INSUFFICIENT_COVERAGE = "insufficient_coverage"
    UNKNOWN_QUALITY = "unknown_quality"
    BELOW_MINIMUM_QUALITY = "below_minimum_quality"
    STATED_GAP = "stated_gap"


class UncertaintyType(StrEnum):
    """Qualitative uncertainty. Not a confidence score."""

    KNOWN = "known"
    UNKNOWN = "unknown"
    INSUFFICIENT = "insufficient"
    CONFLICTING = "conflicting"
    SUSPECT = "suspect"


class ComparisonOp(StrEnum):
    GT = "gt"
    GTE = "gte"
    LT = "lt"
    LTE = "lte"
    EQ = "eq"
    BETWEEN = "between"
