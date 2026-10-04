from __future__ import annotations

from uuid import UUID, uuid4


class EntityId:
    """Typed UUID identity. Subclasses are distinct types for static checking."""

    __slots__ = ("value",)

    def __init__(self, value: UUID | str | None = None) -> None:
        if value is None:
            self.value = uuid4()
        elif isinstance(value, UUID):
            self.value = value
        else:
            self.value = UUID(str(value))

    def __eq__(self, other: object) -> bool:
        return isinstance(other, type(self)) and self.value == other.value

    def __hash__(self) -> int:
        return hash((type(self), self.value))

    def __str__(self) -> str:
        return str(self.value)

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.value!s})"


class ActorId(EntityId):
    pass


class ObservationId(EntityId):
    pass


class IndicatorId(EntityId):
    pass


class IndicatorVersionId(EntityId):
    pass


class IndicatorValueId(EntityId):
    pass


class RuleId(EntityId):
    pass


class RuleVersionId(EntityId):
    pass


class RuleEvaluationId(EntityId):
    pass


class EvidenceItemId(EntityId):
    pass


class EvidencePackageId(EntityId):
    pass


class AlertId(EntityId):
    pass


class DssPackageId(EntityId):
    pass


class DssContextSnapshotId(EntityId):
    pass


class DecisionId(EntityId):
    pass


class ActionId(EntityId):
    pass


class OutcomeId(EntityId):
    pass


class AgentId(EntityId):
    pass


class AgentVersionId(EntityId):
    pass


class AgentRunId(EntityId):
    pass


class AuditEventId(EntityId):
    pass


class ProtocolId(EntityId):
    pass


class ProtocolVersionId(EntityId):
    pass


class DatasetId(EntityId):
    pass


class DataSourceId(EntityId):
    pass
