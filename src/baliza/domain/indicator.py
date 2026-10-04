from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime

from baliza.domain.enums import PublicationStatus
from baliza.domain.errors import PublishedVersionImmutable
from baliza.domain.hashing import require_aware
from baliza.domain.ids import IndicatorId, IndicatorValueId, IndicatorVersionId, ObservationId
from baliza.domain.observation import Observation
from baliza.domain.quality import DataQuality, DataQualityFacet, Uncertainty, health_from_quality


@dataclass(frozen=True, slots=True)
class Indicator:
    id: IndicatorId
    name: str
    description: str = ""


@dataclass(frozen=True, slots=True)
class IndicatorVersion:
    id: IndicatorVersionId
    indicator_id: IndicatorId
    version: str
    unit: str
    formula_kind: str
    baseline: float | None = None
    status: PublicationStatus = PublicationStatus.DRAFT
    input_variable: str | None = None

    def publish(self) -> IndicatorVersion:
        if self.status == PublicationStatus.PUBLISHED:
            return self
        return replace(self, status=PublicationStatus.PUBLISHED)

    def with_baseline(self, baseline: float) -> IndicatorVersion:
        self._require_draft()
        return replace(self, baseline=baseline)

    def with_formula(self, formula_kind: str) -> IndicatorVersion:
        self._require_draft()
        return replace(self, formula_kind=formula_kind)

    def _require_draft(self) -> None:
        if self.status != PublicationStatus.DRAFT:
            raise PublishedVersionImmutable("Published IndicatorVersion cannot be mutated.")


@dataclass(frozen=True, slots=True)
class IndicatorValue:
    id: IndicatorValueId
    indicator_id: IndicatorId
    indicator_version_id: IndicatorVersionId
    indicator_version: str
    computed_at: datetime
    unit: str
    source_observation_ids: tuple[ObservationId, ...]
    quality: DataQuality
    value: float | None = None
    time_window_start: datetime | None = None
    time_window_end: datetime | None = None
    uncertainty: Uncertainty | None = None
    notes: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        require_aware(self.computed_at, "computed_at")

    @property
    def scope_health(self):
        return health_from_quality(self.quality)


def calculate_indicator_value(
    *,
    version: IndicatorVersion,
    observations: tuple[ObservationId, ...],
    observation_value: float | None,
    observation_quality: DataQuality,
    computed_at: datetime,
    unit: str,
) -> IndicatorValue:
    """Deterministic derivation. Missing inputs yield a value with quality flags, not 'no risk'."""
    notes: list[str] = []
    value: float | None = None
    quality = observation_quality

    if observation_value is None or not observation_quality.is_usable_for_critical_rules:
        notes.append("insufficient_or_unusable_input")
    elif version.formula_kind == "passthrough":
        value = observation_value
    elif version.formula_kind == "subtract_baseline":
        if version.baseline is None:
            notes.append("missing_baseline")
            quality = DataQuality(facet=observation_quality.facet, notes="missing_baseline")
        else:
            value = observation_value - version.baseline
    else:
        notes.append(f"unknown_formula:{version.formula_kind}")

    return IndicatorValue(
        id=IndicatorValueId(),
        indicator_id=version.indicator_id,
        indicator_version_id=version.id,
        indicator_version=version.version,
        computed_at=computed_at,
        unit=unit,
        source_observation_ids=observations,
        quality=quality,
        value=value,
        notes=tuple(notes),
    )


def _combined_quality(observations: tuple[Observation, ...]) -> DataQuality:
    if not observations:
        return DataQuality(facet=DataQualityFacet.MISSING, notes="no_observations")
    facets = {obs.quality.facet for obs in observations}
    if DataQualityFacet.INVALID in facets:
        return DataQuality(facet=DataQualityFacet.INVALID, notes="invalid_member")
    if DataQualityFacet.MISSING in facets or any(obs.value is None for obs in observations):
        return DataQuality(facet=DataQualityFacet.MISSING, notes="missing_member")
    if DataQualityFacet.INSUFFICIENT in facets:
        return DataQuality(facet=DataQualityFacet.INSUFFICIENT, notes="insufficient_member")
    if DataQualityFacet.UNKNOWN in facets:
        return DataQuality(facet=DataQualityFacet.UNKNOWN, notes="unknown_member")
    if DataQualityFacet.SUSPECT in facets or DataQualityFacet.LOW_QUALITY in facets:
        return DataQuality(facet=DataQualityFacet.SUSPECT, notes="suspect_member")
    return observations[0].quality


def calculate_from_observations(
    *,
    version: IndicatorVersion,
    observations: tuple[Observation, ...],
    computed_at: datetime,
) -> IndicatorValue:
    """Deterministic aggregates. Missing members stay missing; they are not zeros."""
    quality = _combined_quality(observations)
    notes: list[str] = []
    value: float | None = None
    numbers = [obs.value for obs in observations if obs.value is not None]
    kind = version.formula_kind
    if not quality.is_usable_for_critical_rules or len(numbers) != len(observations):
        notes.append("insufficient_or_unusable_input")
    elif kind == "mean":
        value = sum(numbers) / len(numbers)
    elif kind == "min":
        value = min(numbers)
    elif kind == "max":
        value = max(numbers)
    elif kind == "sum":
        value = sum(numbers)
    elif kind == "count":
        value = float(len(numbers))
    elif kind in {"passthrough", "subtract_baseline"} and len(observations) == 1:
        return calculate_indicator_value(
            version=version,
            observations=(observations[0].id,),
            observation_value=observations[0].value,
            observation_quality=observations[0].quality,
            computed_at=computed_at,
            unit=version.unit,
        )
    else:
        notes.append(f"unsupported_formula:{kind}")
        quality = DataQuality(facet=quality.facet, notes="unsupported_formula")
    return IndicatorValue(
        id=IndicatorValueId(),
        indicator_id=version.indicator_id,
        indicator_version_id=version.id,
        indicator_version=version.version,
        computed_at=computed_at,
        unit=version.unit,
        source_observation_ids=tuple(obs.id for obs in observations),
        quality=quality,
        value=value,
        notes=tuple(notes),
    )
