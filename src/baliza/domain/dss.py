from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime
from types import MappingProxyType
from typing import Any, Mapping

from baliza.domain.alert import Alert
from baliza.domain.errors import SnapshotImmutable
from baliza.domain.evidence import EvidenceItem, EvidencePackage
from baliza.domain.hashing import freeze_value, require_aware, sha256_canonical
from baliza.domain.ids import AlertId, DssContextSnapshotId, DssPackageId, EvidencePackageId, RuleEvaluationId
from baliza.domain.indicator import IndicatorValue
from baliza.domain.observation import Observation
from baliza.domain.rule import RuleEvaluation


@dataclass(frozen=True, slots=True)
class RecommendationView:
    """A labeled option for a human. Never a Decision or an Action."""

    recommendation_id: str
    source: str
    text: str
    epistemic_label: str = "RECOMMENDATION"
    rationale: str = ""
    evidence_refs: tuple[str, ...] = ()
    uncertainty_note: str | None = None
    preconditions: tuple[str, ...] = ()
    constraints: tuple[str, ...] = ()


@dataclass
class DssPackage:
    """Live assembled DSS context. Mutable while open. Not a Decision."""

    id: DssPackageId
    opened_at: datetime
    alert_ids: list[AlertId] = field(default_factory=list)
    evidence_package_ids: list[EvidencePackageId] = field(default_factory=list)
    evaluation_ids: list[RuleEvaluationId] = field(default_factory=list)
    protocol_version: str | None = None
    recommendations: list[RecommendationView] = field(default_factory=list)
    gaps: list[str] = field(default_factory=list)
    uncertainty_notes: list[str] = field(default_factory=list)
    agent_run_ids_shown: list[str] = field(default_factory=list)
    closed: bool = False

    def __post_init__(self) -> None:
        require_aware(self.opened_at, "opened_at")

    def add_alert(self, alert_id: AlertId) -> None:
        if alert_id not in self.alert_ids:
            self.alert_ids.append(alert_id)

    def add_evaluation(self, evaluation_id: RuleEvaluationId) -> None:
        if evaluation_id not in self.evaluation_ids:
            self.evaluation_ids.append(evaluation_id)

    def add_gap(self, gap: str) -> None:
        if gap not in self.gaps:
            self.gaps.append(gap)


@dataclass(frozen=True, slots=True)
class DssContextSnapshot:
    """Immutable freeze bound to a Decision (Invariant 17)."""

    id: DssContextSnapshotId
    dss_package_id: DssPackageId
    frozen_at: datetime
    content_hash: str
    payload: Mapping[str, Any]
    object_key: str | None = None

    def __post_init__(self) -> None:
        require_aware(self.frozen_at, "frozen_at")
        object.__setattr__(self, "payload", freeze_value(dict(self.payload)))

    def with_payload(self, payload: Mapping[str, Any]) -> DssContextSnapshot:
        raise SnapshotImmutable("DssContextSnapshot cannot be mutated after freeze.")


def presented_context_payload(
    *,
    alerts: tuple[Alert, ...],
    evidence_packages: tuple[EvidencePackage, ...],
    evidence_items: tuple[EvidenceItem, ...],
    evaluations: tuple[RuleEvaluation, ...],
    indicator_units: Mapping[str, str] | None = None,
    input_qualities: Mapping[str, str] | None = None,
    indicator_versions: Mapping[str, str] | None = None,
    protocol_options: tuple[str, ...] = (),
    indicator_values: tuple[IndicatorValue, ...] = (),
    observations: tuple[Observation, ...] = (),
    recommendations: tuple[RecommendationView, ...] = (),
) -> dict[str, Any]:
    """Copies of the context shown to the decider. Not live row references."""
    from baliza.domain.situation import interpret_situation

    reading = interpret_situation(
        alerts=alerts,
        evidence_packages=evidence_packages,
        evidence_items=evidence_items,
        evaluations=evaluations,
        indicator_values=indicator_values,
        observations=observations,
        recommendations=recommendations,
    )
    units = dict(indicator_units or {})
    qualities = dict(input_qualities or {})
    versions = dict(indicator_versions or {})
    return {
        "alerts_at_freeze": [
            {
                "alert_id": str(alert.id),
                "alert_status_at_freeze": alert.status.value,
                "severity": alert.severity.value,
                "alerted_at": alert.alerted_at.isoformat(),
                "reviewed_at": alert.reviewed_at.isoformat() if alert.reviewed_at else None,
                "health": alert.health.value,
                "evidence_package_id": str(alert.evidence_package_id),
                "rule_evaluation_ids": [str(item) for item in alert.rule_evaluation_ids],
            }
            for alert in alerts
        ],
        "evidence_descriptors_at_freeze": [
            {
                "evidence_item_id": str(item.id),
                "kind": item.kind.value,
                "epistemic_label": item.epistemic_label.value,
                "referenced_type": item.referenced_type,
                "referenced_id": item.referenced_id,
                "narrative": item.narrative,
                "created_at": item.created_at.isoformat(),
                "content_hash": item.content_hash,
            }
            for item in evidence_items
        ],
        "evidence_packages_at_freeze": [
            {
                "evidence_package_id": str(package.id),
                "subject": package.subject,
                "item_ids": [str(item) for item in package.item_ids],
                "gaps": list(package.gaps),
                "incomplete": package.incomplete,
            }
            for package in evidence_packages
        ],
        "thresholds_at_freeze": [
            {
                "rule_evaluation_id": str(evaluation.id),
                "rule_id": str(evaluation.rule_id),
                "rule_version_id": str(evaluation.rule_version_id),
                "rule_version": evaluation.rule_version,
                "thresholds": dict(evaluation.thresholds_applied),
                "indicator_unit": units.get(str(evaluation.id)),
                "indicator_version": versions.get(str(evaluation.id)),
                "input_quality": qualities.get(str(evaluation.id)),
                "outcome": evaluation.outcome.value,
                "reason": evaluation.reason,
            }
            for evaluation in evaluations
        ],
        "protocol_options_at_freeze": list(protocol_options),
        "data_gaps_at_freeze": reading.gaps_payload(),
        "uncertainty_at_freeze": reading.uncertainty_payload(),
        "signal_readings_at_freeze": reading.readings_payload(),
        "evidence_synthesis_at_freeze": reading.synthesis_payload(),
    }


def freeze_dss_package(
    package: DssPackage,
    *,
    frozen_at: datetime,
    extra: Mapping[str, Any] | None = None,
    presented: Mapping[str, Any] | None = None,
) -> DssContextSnapshot:
    payload: dict[str, Any] = {
        "dss_package_id": str(package.id),
        "opened_at": package.opened_at.isoformat(),
        "frozen_at": frozen_at.isoformat(),
        "alert_ids": [str(a) for a in package.alert_ids],
        "evidence_package_ids": [str(e) for e in package.evidence_package_ids],
        "evaluation_ids": [str(e) for e in package.evaluation_ids],
        "protocol_version": package.protocol_version,
        "recommendations": [
            {
                "recommendation_id": r.recommendation_id,
                "source": r.source,
                "text": r.text,
                "epistemic_label": r.epistemic_label,
                "rationale": r.rationale,
                "evidence_refs": list(r.evidence_refs),
                "uncertainty_note": r.uncertainty_note,
                "preconditions": list(r.preconditions),
                "constraints": list(r.constraints),
            }
            for r in package.recommendations
        ],
        "gaps": list(package.gaps),
        "uncertainty_notes": list(package.uncertainty_notes),
        "agent_run_ids_shown": list(package.agent_run_ids_shown),
    }
    if extra:
        payload.update(dict(extra))
    historical = dict(presented or {})
    for key in (
        "alerts_at_freeze",
        "evidence_descriptors_at_freeze",
        "evidence_packages_at_freeze",
        "thresholds_at_freeze",
        "protocol_options_at_freeze",
        "data_gaps_at_freeze",
        "uncertainty_at_freeze",
        "signal_readings_at_freeze",
        "evidence_synthesis_at_freeze",
    ):
        payload[key] = historical.get(key, [])
    digest = sha256_canonical(payload)
    return DssContextSnapshot(
        id=DssContextSnapshotId(),
        dss_package_id=package.id,
        frozen_at=frozen_at,
        content_hash=digest,
        payload=payload,
    )
