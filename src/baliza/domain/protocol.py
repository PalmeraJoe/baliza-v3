from __future__ import annotations

from dataclasses import dataclass, replace

from baliza.domain.dss import RecommendationView
from baliza.domain.enums import PublicationStatus
from baliza.domain.errors import PublishedVersionImmutable
from baliza.domain.ids import ProtocolId, ProtocolVersionId


@dataclass(frozen=True, slots=True)
class Protocol:
    """Catalog of options. A protocol never executes an Action."""

    id: ProtocolId
    name: str
    description: str = ""


@dataclass(frozen=True, slots=True)
class ProtocolOption:
    """A possible operational response. The system does not execute it."""

    code: str
    description: str
    preconditions: tuple[str, ...] = ()
    constraints: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class ProtocolVersion:
    id: ProtocolVersionId
    protocol_id: ProtocolId
    version: str
    options: tuple[str, ...]
    status: PublicationStatus = PublicationStatus.DRAFT
    option_details: tuple[ProtocolOption, ...] = ()

    def publish(self) -> ProtocolVersion:
        if self.status == PublicationStatus.PUBLISHED:
            return self
        return replace(self, status=PublicationStatus.PUBLISHED)

    def with_options(self, options: tuple[str, ...]) -> ProtocolVersion:
        if self.status == PublicationStatus.PUBLISHED:
            raise PublishedVersionImmutable("Published ProtocolVersion cannot be mutated.")
        return replace(self, options=options)

    def with_option_details(self, option_details: tuple[ProtocolOption, ...]) -> ProtocolVersion:
        if self.status == PublicationStatus.PUBLISHED:
            raise PublishedVersionImmutable("Published ProtocolVersion cannot be mutated.")
        return replace(self, option_details=option_details)


def recommendations_from_protocol(version: ProtocolVersion) -> tuple[RecommendationView, ...]:
    """Options presented for human review. Not an execution plan and not a Decision."""
    if version.option_details:
        return tuple(
            RecommendationView(
                recommendation_id=f"{version.version}:{option.code}",
                source="protocol",
                text=option.description,
                epistemic_label="RECOMMENDATION",
                rationale="",
                evidence_refs=(),
                uncertainty_note=None,
                preconditions=option.preconditions,
                constraints=option.constraints,
            )
            for option in version.option_details
        )
    return tuple(
        RecommendationView(
            recommendation_id=f"{version.version}:{index}",
            source="protocol",
            text=text,
            epistemic_label="RECOMMENDATION",
        )
        for index, text in enumerate(version.options)
    )
