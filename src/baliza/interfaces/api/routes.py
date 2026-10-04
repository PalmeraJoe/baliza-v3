from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from baliza.application.queries import alert_chain, alert_situation, decision_context, package_situation
from baliza.application.use_cases import (
    Repositories,
    acknowledge_alert,
    build_dss_package,
    calculate_indicator,
    evaluate_and_maybe_alert,
    record_human_action,
    record_human_decision,
    record_human_outcome,
    record_observation,
)
from baliza.domain.enums import DataQualityFacet
from baliza.domain.errors import DomainError
from baliza.domain.ids import (
    ActorId,
    AlertId,
    DataSourceId,
    DecisionId,
    DssPackageId,
    EvidenceItemId,
    EvidencePackageId,
    IndicatorValueId,
    IndicatorVersionId,
    ObservationId,
    RuleVersionId,
)
from baliza.domain.quality import DataQuality

router = APIRouter()


class ObservationIn(BaseModel):
    variable: str
    unit: str
    observed_at: datetime
    value: float | None = None
    quality_facet: DataQualityFacet
    quality_score: float | None = None
    spatial_ref: str | None = None
    source_id: str | None = None
    subject: str | None = None


class CalculateIn(BaseModel):
    indicator_version_id: str
    observation_id: str


class EvaluateIn(BaseModel):
    observation_id: str
    indicator_value_id: str
    rule_version_id: str


class AcknowledgeIn(BaseModel):
    actor_id: str


class DssIn(BaseModel):
    alert_ids: list[str] = Field(default_factory=list)
    gaps: list[str] = Field(default_factory=list)
    protocol_version: str | None = None


class DecisionIn(BaseModel):
    actor_id: str
    package_id: str
    justification: str
    selected_option: str


class ActionIn(BaseModel):
    actor_id: str
    decision_id: str
    action_type: str
    description: str


class OutcomeIn(BaseModel):
    action_id: str
    decision_id: str
    notes: str


def _repos(request: Request) -> Repositories:
    bound = getattr(request.state, "repos", None)
    return bound if bound is not None else request.app.state.repos


def _actor(repos: Repositories, actor_id: str):
    actor = repos.actors.get(ActorId(actor_id))
    if actor is None:
        raise HTTPException(status_code=400, detail="Actor is required and was not found.")
    return actor


@router.post("/observations")
def post_observation(body: ObservationIn, request: Request) -> dict:
    repos = _repos(request)
    metadata = {"subject": body.subject} if body.subject else {}
    metadata["label"] = "DEMO / NON-SCIENTIFIC"
    try:
        obs = record_observation(
            repos,
            variable=body.variable,
            unit=body.unit,
            observed_at=body.observed_at,
            quality=DataQuality(facet=body.quality_facet, score=body.quality_score),
            value=body.value,
            source_id=DataSourceId(body.source_id) if body.source_id else None,
            spatial_ref=body.spatial_ref,
            metadata=metadata,
        )
    except (DomainError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"id": str(obs.id), "quality": obs.quality.facet.value, "implies_no_risk": obs.quality.implies_no_risk()}


@router.get("/observations/{observation_id}")
def get_observation(observation_id: str, request: Request) -> dict:
    obs = _repos(request).observations.get(ObservationId(observation_id))
    if obs is None:
        raise HTTPException(status_code=404, detail="Observation not found.")
    return {
        "id": str(obs.id),
        "variable": obs.variable,
        "unit": obs.unit,
        "value": obs.value,
        "observed_at": obs.observed_at.isoformat(),
        "processed_at": obs.processed_at.isoformat(),
        "quality": obs.quality.facet.value,
        "spatial_ref": obs.spatial_ref,
        "metadata": dict(obs.metadata),
    }


@router.post("/indicators/calculate")
def post_calculate(body: CalculateIn, request: Request) -> dict:
    repos = _repos(request)
    version = repos.indicators.get_version(IndicatorVersionId(body.indicator_version_id))
    observation = repos.observations.get(ObservationId(body.observation_id))
    if version is None or observation is None:
        raise HTTPException(status_code=404, detail="Indicator version or observation not found.")
    value = calculate_indicator(repos, version=version, observation=observation)
    return {
        "id": str(value.id),
        "indicator_version": value.indicator_version,
        "value": value.value,
        "quality": value.quality.facet.value,
        "source_observation_ids": [str(i) for i in value.source_observation_ids],
        "notes": list(value.notes),
    }


@router.get("/indicator-values/{value_id}")
def get_indicator_value(value_id: str, request: Request) -> dict:
    value = _repos(request).indicators.get_value(IndicatorValueId(value_id))
    if value is None:
        raise HTTPException(status_code=404, detail="IndicatorValue not found.")
    return {
        "id": str(value.id),
        "indicator_version": value.indicator_version,
        "value": value.value,
        "quality": value.quality.facet.value,
        "computed_at": value.computed_at.isoformat(),
        "source_observation_ids": [str(i) for i in value.source_observation_ids],
    }


@router.post("/rules/evaluate")
def post_evaluate(body: EvaluateIn, request: Request) -> dict:
    repos = _repos(request)
    observation = repos.observations.get(ObservationId(body.observation_id))
    indicator_value = repos.indicators.get_value(IndicatorValueId(body.indicator_value_id))
    version = repos.rules.get_version(RuleVersionId(body.rule_version_id))
    rule = repos.rules.get_rule(version.rule_id) if version else None
    if observation is None or indicator_value is None or version is None or rule is None:
        raise HTTPException(status_code=404, detail="Evaluation inputs not found.")
    try:
        result = evaluate_and_maybe_alert(
            repos,
            observation=observation,
            indicator_value=indicator_value,
            rule=rule,
            rule_version=version,
        )
    except (DomainError, RuntimeError) as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return {
        "evaluation_id": str(result.evaluation.id),
        "outcome": result.evaluation.outcome.value,
        "reason": result.evaluation.reason,
        "evidence_package_id": str(result.evidence_package.id) if result.evidence_package else None,
        "alert_id": str(result.alert.id) if result.alert else None,
        "ai_used": False,
        "threshold_status": "DEMO / NON-SCIENTIFIC",
    }


@router.get("/rule-evaluations/{evaluation_id}")
def get_evaluation(evaluation_id: str, request: Request) -> dict:
    from baliza.domain.ids import RuleEvaluationId

    ev = _repos(request).rules.get_evaluation(RuleEvaluationId(evaluation_id))
    if ev is None:
        raise HTTPException(status_code=404, detail="RuleEvaluation not found.")
    return {
        "id": str(ev.id),
        "rule_version": ev.rule_version,
        "outcome": ev.outcome.value,
        "reason": ev.reason,
        "thresholds": dict(ev.thresholds_applied),
        "evaluated_at": ev.evaluated_at.isoformat(),
    }


@router.get("/evidence/{item_id}")
def get_evidence_item(item_id: str, request: Request) -> dict:
    item = _repos(request).evidence.get_item(EvidenceItemId(item_id))
    if item is None:
        raise HTTPException(status_code=404, detail="EvidenceItem not found.")
    return {
        "id": str(item.id),
        "kind": item.kind.value,
        "epistemic_label": item.epistemic_label.value,
        "referenced_type": item.referenced_type,
        "referenced_id": item.referenced_id,
    }


@router.get("/evidence-packages/{package_id}")
def get_evidence_package(package_id: str, request: Request) -> dict:
    package = _repos(request).evidence.get_package(EvidencePackageId(package_id))
    if package is None:
        raise HTTPException(status_code=404, detail="EvidencePackage not found.")
    items = _repos(request).evidence.items_for_package(package.id)
    return {
        "id": str(package.id),
        "subject": package.subject,
        "incomplete": package.incomplete,
        "gaps": list(package.gaps),
        "items": [
            {"id": str(i.id), "kind": i.kind.value, "referenced_type": i.referenced_type, "referenced_id": i.referenced_id}
            for i in items
        ],
    }


@router.get("/alerts")
def get_alerts(request: Request) -> dict:
    alerts = _repos(request).alerts.list_all()
    return {"alerts": [{"id": str(a.id), "status": a.status.value, "severity": a.severity.value} for a in alerts]}


@router.get("/alerts/{alert_id}")
def get_alert(alert_id: str, request: Request) -> dict:
    chain = alert_chain(_repos(request), AlertId(alert_id))
    if chain is None:
        raise HTTPException(status_code=404, detail="Alert not found.")
    return {
        "id": str(chain.alert.id),
        "status": chain.alert.status.value,
        "severity": chain.alert.severity.value,
        "is_decision": chain.alert.is_decision(),
        "evidence_package_id": str(chain.alert.evidence_package_id),
        "evaluations": [str(e.id) for e in chain.evaluations],
        "indicator_values": [str(v.id) for v in chain.indicator_values],
        "observations": [str(o.id) for o in chain.observations],
    }


@router.get("/alerts/{alert_id}/context")
def get_alert_context(alert_id: str, request: Request) -> dict:
    reading = alert_situation(_repos(request), AlertId(alert_id))
    if reading is None:
        raise HTTPException(status_code=404, detail="Alert not found.")
    body = reading.to_dict()
    body["threshold_status"] = "DEMO / NON-SCIENTIFIC"
    return body


@router.post("/alerts/{alert_id}/acknowledge")
def post_acknowledge(alert_id: str, body: AcknowledgeIn, request: Request) -> dict:
    repos = _repos(request)
    alert = repos.alerts.get(AlertId(alert_id))
    if alert is None:
        raise HTTPException(status_code=404, detail="Alert not found.")
    updated = acknowledge_alert(repos, alert=alert, actor=_actor(repos, body.actor_id))
    return {"id": str(updated.id), "status": updated.status.value, "decision_created": False}


@router.post("/dss/packages")
def post_dss(body: DssIn, request: Request) -> dict:
    repos = _repos(request)
    alerts = []
    for raw in body.alert_ids:
        alert = repos.alerts.get(AlertId(raw))
        if alert is None:
            raise HTTPException(status_code=404, detail=f"Alert {raw} not found.")
        alerts.append(alert)
    package = build_dss_package(
        repos,
        alerts=alerts,
        extra_gaps=body.gaps,
        protocol_version=body.protocol_version,
    )
    return {"id": str(package.id), "alert_ids": [str(a) for a in package.alert_ids], "ai_used": False}


@router.get("/dss/packages/{package_id}")
def get_dss(package_id: str, request: Request) -> dict:
    package = _repos(request).dss.get_package(DssPackageId(package_id))
    if package is None:
        raise HTTPException(status_code=404, detail="DssPackage not found.")
    return {
        "id": str(package.id),
        "alert_ids": [str(a) for a in package.alert_ids],
        "evidence_package_ids": [str(e) for e in package.evidence_package_ids],
        "evaluation_ids": [str(e) for e in package.evaluation_ids],
        "gaps": list(package.gaps),
        "protocol_version": package.protocol_version,
        "recommendations": [r.text for r in package.recommendations],
    }


@router.get("/dss/packages/{package_id}/brief")
def get_dss_brief(package_id: str, request: Request) -> dict:
    reading = package_situation(_repos(request), DssPackageId(package_id))
    if reading is None:
        raise HTTPException(status_code=404, detail="DssPackage not found.")
    body = reading.to_dict()
    body["threshold_status"] = "DEMO / NON-SCIENTIFIC"
    return body


@router.get("/dss/packages/{package_id}/evidence")
def get_dss_evidence(package_id: str, request: Request) -> dict:
    reading = package_situation(_repos(request), DssPackageId(package_id))
    if reading is None:
        raise HTTPException(status_code=404, detail="DssPackage not found.")
    return reading.synthesis_payload()


@router.get("/dss/packages/{package_id}/options")
def get_dss_options(package_id: str, request: Request) -> dict:
    package = _repos(request).dss.get_package(DssPackageId(package_id))
    if package is None:
        raise HTTPException(status_code=404, detail="DssPackage not found.")
    return {
        "options": [
            {
                "recommendation_id": item.recommendation_id,
                "text": item.text,
                "epistemic_label": item.epistemic_label,
                "source": item.source,
                "preconditions": list(item.preconditions),
                "constraints": list(item.constraints),
                "is_decision": False,
            }
            for item in package.recommendations
        ]
    }


@router.get("/dss/packages/{package_id}/snapshots")
def get_dss_snapshots(package_id: str, request: Request) -> dict:
    package = _repos(request).dss.get_package(DssPackageId(package_id))
    if package is None:
        raise HTTPException(status_code=404, detail="DssPackage not found.")
    snaps = _repos(request).dss.snapshots_for_package(package.id)
    return {
        "snapshots": [
            {
                "id": str(item.id),
                "content_hash": item.content_hash,
                "frozen_at": item.frozen_at.isoformat(),
                "alert_ids": list(item.payload.get("alert_ids", ())),
            }
            for item in snaps
        ]
    }


@router.post("/dss/packages/{package_id}/freeze")
def post_freeze(package_id: str, body: DecisionIn, request: Request) -> dict:
    """Freeze is performed together with the human Decision. This route records that Decision."""
    if body.package_id != package_id:
        raise HTTPException(status_code=400, detail="package_id mismatch.")
    return _record_decision(body, request)


@router.post("/decisions")
def post_decision(body: DecisionIn, request: Request) -> dict:
    return _record_decision(body, request)


def _record_decision(body: DecisionIn, request: Request) -> dict:
    repos = _repos(request)
    package = repos.dss.get_package(DssPackageId(body.package_id))
    if package is None:
        raise HTTPException(status_code=404, detail="DssPackage not found.")
    try:
        decision = record_human_decision(
            repos,
            actor=_actor(repos, body.actor_id),
            package=package,
            justification=body.justification,
            selected_option=body.selected_option,
        )
    except DomainError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {
        "id": str(decision.id),
        "snapshot_id": str(decision.dss_context_snapshot_id),
        "snapshot_hash": decision.snapshot_hash,
    }


@router.get("/decisions/{decision_id}")
def get_decision(decision_id: str, request: Request) -> dict:
    ctx = decision_context(_repos(request), DecisionId(decision_id))
    if ctx is None:
        raise HTTPException(status_code=404, detail="Decision not found.")
    return {
        "id": str(ctx.decision.id),
        "actor_id": str(ctx.decision.actor_id),
        "snapshot_id": str(ctx.decision.dss_context_snapshot_id),
        "snapshot_hash": ctx.decision.snapshot_hash,
        "justification": ctx.decision.justification,
        "selected_option": ctx.decision.selected_option,
        "decided_at": ctx.decision.decided_at.isoformat(),
        "package_id": str(ctx.decision.dss_package_id),
        "snapshot_alerts": list(ctx.snapshot.payload["alert_ids"]) if ctx.snapshot else [],
    }


@router.post("/actions")
def post_action(body: ActionIn, request: Request) -> dict:
    repos = _repos(request)
    decision = repos.decisions.get(DecisionId(body.decision_id))
    if decision is None:
        raise HTTPException(status_code=400, detail="Action requires an existing Decision.")
    action = record_human_action(
        repos,
        decision=decision,
        description=body.description,
        actor=_actor(repos, body.actor_id),
        action_type=body.action_type,
    )
    return {"id": str(action.id), "decision_id": str(action.decision_id), "action_type": action.action_type}


@router.get("/actions/{action_id}")
def get_action(action_id: str, request: Request) -> dict:
    from baliza.domain.ids import ActionId

    action = _repos(request).actions.get_action(ActionId(action_id))
    if action is None:
        raise HTTPException(status_code=404, detail="Action not found.")
    return {
        "id": str(action.id),
        "decision_id": str(action.decision_id),
        "action_type": action.action_type,
        "acted_at": action.acted_at.isoformat(),
    }


@router.post("/outcomes")
def post_outcome(body: OutcomeIn, request: Request) -> dict:
    repos = _repos(request)
    from baliza.domain.ids import ActionId

    action = repos.actions.get_action(ActionId(body.action_id))
    decision = repos.decisions.get(DecisionId(body.decision_id))
    if action is None or decision is None:
        raise HTTPException(status_code=400, detail="Outcome requires Action and Decision.")
    outcome = record_human_outcome(repos, action=action, decision=decision, notes=body.notes)
    return {"id": str(outcome.id), "action_id": str(outcome.action_id), "decision_id": str(outcome.decision_id)}


@router.get("/outcomes/{outcome_id}")
def get_outcome(outcome_id: str, request: Request) -> dict:
    from baliza.domain.ids import OutcomeId

    outcome = _repos(request).actions.get_outcome(OutcomeId(outcome_id))
    if outcome is None:
        raise HTTPException(status_code=404, detail="Outcome not found.")
    return {
        "id": str(outcome.id),
        "action_id": str(outcome.action_id),
        "decision_id": str(outcome.decision_id),
        "notes": outcome.notes,
        "observed_outcome_at": outcome.observed_outcome_at.isoformat(),
    }


@router.get("/scientific/crw/discovery")
def crw_discovery() -> dict:
    """Verified CRW catalog. Does not download and does not create an alert."""
    from baliza.infrastructure.sources.crw.adapter import CrwAdapter

    return CrwAdapter().discover(live=False)


@router.get("/scientific/spots/{spot_id}/crw")
def crw_spot_intelligence(spot_id: str) -> dict:
    """CRW Spot Intelligence from stored official files. ESTIMATED stays NONE."""
    from pathlib import Path

    from baliza.infrastructure.sources.crw.catalog import DEMO_SPOT
    from baliza.infrastructure.sources.crw.spot_intelligence import build_crw_spot_intelligence

    if spot_id != DEMO_SPOT["spot_id"]:
        raise HTTPException(status_code=404, detail="Only the demonstration CRW spot is available in this phase.")
    root = Path(__file__).resolve().parents[4]
    return build_crw_spot_intelligence(
        root / "data" / "phase75" / "raw",
        root / "data" / "phase75" / "provenance.json",
    )


@router.get("/scientific/allen/discovery")
def allen_discovery() -> dict:
    """Verified Allen WFS catalog. Does not download and does not create an alert."""
    from baliza.infrastructure.sources.allen.adapter import AllenAdapter

    return AllenAdapter().discover(live=False)


@router.get("/scientific/spots/{spot_id}/allen")
def allen_spot_intelligence(spot_id: str) -> dict:
    """Allen Spot Intelligence from stored WFS extracts. ESTIMATED stays NONE."""
    from pathlib import Path

    from baliza.infrastructure.sources.allen.catalog import ALLEN_RESEARCH_TEST_SPOT, DEMO_SPOT
    from baliza.infrastructure.sources.allen.spot_intelligence import build_allen_spot_intelligence

    if spot_id not in {DEMO_SPOT["spot_id"], ALLEN_RESEARCH_TEST_SPOT["spot_id"]}:
        raise HTTPException(status_code=404, detail="Allen Spot Intelligence is only available for the DEMO or research-test Spot.")
    root = Path(__file__).resolve().parents[4]
    return build_allen_spot_intelligence(
        root / "data" / "phase75" / "allen" / "raw",
        root / "data" / "phase75" / "allen" / "provenance.json",
        spot_id=spot_id,
    )


@router.get("/scientific/mermaid/discovery")
def mermaid_discovery() -> dict:
    """Verified MERMAID catalog. Does not download and does not create an alert."""
    from baliza.infrastructure.sources.mermaid.adapter import MermaidAdapter

    return MermaidAdapter().discover(live=False)


@router.get("/scientific/spots/{spot_id}/mermaid")
def mermaid_spot_intelligence(spot_id: str) -> dict:
    """MERMAID Spot Intelligence from stored official summaries. ESTIMATED stays NONE."""
    from pathlib import Path

    from baliza.infrastructure.sources.mermaid.catalog import DEMO_SPOT
    from baliza.infrastructure.sources.mermaid.spot_intelligence import build_mermaid_spot_intelligence

    if spot_id != DEMO_SPOT["spot_id"]:
        raise HTTPException(status_code=404, detail="Only the demonstration Spot is available for MERMAID in this phase.")
    root = Path(__file__).resolve().parents[4]
    return build_mermaid_spot_intelligence(
        root / "data" / "phase763" / "mermaid-inquiry.json",
        root / "data" / "phase763" / "mermaid-australia-summary.json",
        spot_id=spot_id,
    )


@router.get("/scientific/spots/{spot_id}/intelligence")
def integrated_spot_intelligence(spot_id: str) -> dict:
    """Canonical integrated Spot Intelligence (CRW + Allen + MERMAID). ESTIMATED stays NONE."""
    from pathlib import Path

    from baliza.infrastructure.sources.crw.catalog import DEMO_SPOT
    from baliza.infrastructure.sources.integrated.spot_intelligence import (
        build_integrated_spot_intelligence,
    )

    if spot_id != DEMO_SPOT["spot_id"]:
        raise HTTPException(
            status_code=404,
            detail="Integrated Spot Intelligence is only available for the demonstration Spot in this phase.",
        )
    root = Path(__file__).resolve().parents[4]
    return build_integrated_spot_intelligence(root, spot_id=spot_id)


@router.get("/scientific/spots")
def list_scientific_spots() -> dict:
    """Known Spots for the Visual MVP. Coordinates are not invented."""
    from baliza.infrastructure.sources.crw.catalog import DEMO_SPOT

    return {
        "spots": [
            {
                **DEMO_SPOT,
                "spatial_precision_note": "CRS UNKNOWN. Point is the heritage coordinate, not a reef polygon.",
                "thermal_ground_truth": "NOT_AVAILABLE",
                "local_estimation": "NOT_AUTHORIZED",
            }
        ]
    }


@router.post("/scientific/mvp/bootstrap")
def mvp_bootstrap(request: Request) -> dict:
    """Seed in-memory DEMO session through DSS (no Decision). For Visual MVP only."""
    from pathlib import Path

    from baliza.application.phase712_scientific_dss import (
        DEMO_ONLY,
        SCIENTIFICALLY_VALIDATED,
        THRESHOLD_STATUS,
        run_e2e_scientific_dss,
    )

    repos = _repos(request)
    root = Path(__file__).resolve().parents[4]
    result = run_e2e_scientific_dss(repos, root, through="dss")
    session = {
        "phase": "7.14",
        "spot_id": result.machine_summary["spot_id"],
        "alert_id": result.machine_summary["alert_id"],
        "dss_package_id": result.machine_summary["dss_package_id"],
        "actor_id": result.machine_summary["actor_id"],
        "evaluation_id": str(result.evaluation.id),
        "rule_name": result.machine_summary["rule"]["name"],
        "rule_version": result.machine_summary["rule"]["version"],
        "threshold_status": THRESHOLD_STATUS,
        "demo_only": DEMO_ONLY,
        "scientifically_validated": SCIENTIFICALLY_VALIDATED,
        "through": "dss",
        "thermal_ground_truth": "NOT_AVAILABLE",
        "ml_implementation": "NOT_AUTHORIZED",
        "autonomous_action": False,
        "note": "Decision / Action / Outcome must be recorded by a human via existing APIs.",
    }
    request.app.state.mvp_session = session
    return {
        "session": session,
        "summary": result.machine_summary,
        "brief": result.brief,
        "spot_intelligence_available_at": f"/scientific/spots/{session['spot_id']}/intelligence",
    }


@router.get("/scientific/mvp/session")
def mvp_session(request: Request) -> dict:
    session = getattr(request.app.state, "mvp_session", None)
    if not session:
        raise HTTPException(status_code=404, detail="MVP session not bootstrapped. POST /scientific/mvp/bootstrap first.")
    return {"session": session}


@router.get("/decisions")
def list_decisions(request: Request) -> dict:
    repos = _repos(request)
    items = getattr(repos.decisions, "list_all", lambda: [])()
    return {
        "decisions": [
            {
                "id": str(item.id),
                "actor_id": str(item.actor_id),
                "package_id": str(item.dss_package_id),
                "snapshot_id": str(item.dss_context_snapshot_id),
                "selected_option": item.selected_option,
                "justification": item.justification,
                "decided_at": item.decided_at.isoformat(),
                "snapshot_hash": item.snapshot_hash,
                "is_human_decision": True,
            }
            for item in items
        ]
    }


@router.get("/dss/packages")
def list_dss_packages(request: Request) -> dict:
    repos = _repos(request)
    items = getattr(repos.dss, "list_packages", lambda: [])()
    return {
        "packages": [
            {
                "id": str(item.id),
                "alert_ids": [str(a) for a in item.alert_ids],
                "gaps": list(item.gaps),
                "recommendation_count": len(item.recommendations),
                "opened_at": item.opened_at.isoformat(),
            }
            for item in items
        ]
    }
