from __future__ import annotations


class DomainError(Exception):
    """Base domain error."""


class InvariantViolation(DomainError):
    """A documented domain invariant was violated."""


class PublishedVersionImmutable(InvariantViolation):
    pass


class InsufficientEvidence(InvariantViolation):
    pass


class MissingActor(InvariantViolation):
    pass


class MissingSnapshot(InvariantViolation):
    pass


class SnapshotImmutable(InvariantViolation):
    pass


class InvalidTransition(InvariantViolation):
    pass


class ActionWithoutDecision(InvariantViolation):
    pass
