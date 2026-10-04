from __future__ import annotations

from dataclasses import dataclass

from baliza.domain.enums import DataQualityFacet, ScopeHealth
from baliza.domain.errors import InvariantViolation


@dataclass(frozen=True, slots=True)
class DataQuality:
    """Fitness-for-use. Missing/invalid data must never be encoded as 'no risk'."""

    facet: DataQualityFacet
    score: float | None = None
    notes: str | None = None
    method_version: str = "baliza.quality.v1"

    def __post_init__(self) -> None:
        if self.score is not None and not (0.0 <= self.score <= 1.0):
            raise InvariantViolation("DataQuality.score must be in [0, 1] when set.")

    @property
    def is_usable_for_critical_rules(self) -> bool:
        return self.facet == DataQualityFacet.VALID and (self.score is None or self.score >= 0.5)

    def implies_no_risk(self) -> bool:
        """Invariant 9: quality/missingness never implies absence of risk."""
        return False


@dataclass(frozen=True, slots=True)
class Uncertainty:
    missingness: bool = False
    conflict: bool = False
    confidence: float | None = None
    notes: str | None = None

    def __post_init__(self) -> None:
        if self.confidence is not None and not (0.0 <= self.confidence <= 1.0):
            raise InvariantViolation("Uncertainty.confidence must be in [0, 1] when set.")


def health_from_quality(quality: DataQuality) -> ScopeHealth:
    if quality.facet == DataQualityFacet.VALID:
        return ScopeHealth.OK
    if quality.facet in {DataQualityFacet.DELAYED, DataQualityFacet.LOW_QUALITY, DataQualityFacet.SUSPECT}:
        return ScopeHealth.DEGRADED
    if quality.facet in {
        DataQualityFacet.MISSING,
        DataQualityFacet.SOURCE_UNAVAILABLE,
        DataQualityFacet.INVALID,
        DataQualityFacet.INSUFFICIENT,
    }:
        return ScopeHealth.INSUFFICIENT_DATA
    return ScopeHealth.UNKNOWN
