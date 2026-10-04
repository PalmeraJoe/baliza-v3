from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Mapping

from baliza.domain.hashing import freeze_value, require_aware
from baliza.domain.ids import DataSourceId, ObservationId
from baliza.domain.quality import DataQuality, Uncertainty


@dataclass(frozen=True, slots=True)
class Observation:
    """Recorded measurement/claim. FACT of recording, not world-truth."""

    id: ObservationId
    variable: str
    unit: str
    observed_at: datetime
    processed_at: datetime
    quality: DataQuality
    source_id: DataSourceId | None = None
    value: float | None = None
    spatial_ref: str | None = None
    method: str | None = None
    uncertainty: Uncertainty | None = None
    metadata: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        require_aware(self.observed_at, "observed_at")
        require_aware(self.processed_at, "processed_at")
        if not self.variable.strip():
            raise ValueError("Observation.variable is required.")
        object.__setattr__(self, "metadata", freeze_value(self.metadata))
