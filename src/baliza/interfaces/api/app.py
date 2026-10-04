from fastapi import FastAPI
from fastapi.responses import JSONResponse

from baliza.interfaces.api.routes import router

from baliza import __version__
from baliza.application.use_cases import (
    Repositories,
    build_dss_package,
    calculate_indicator,
    evaluate_and_maybe_alert,
    record_human_decision,
    record_observation,
)
from baliza.domain.actor import Actor
from baliza.domain.enums import ComparisonOp, DataQualityFacet, PublicationStatus
from baliza.domain.ids import ActorId, IndicatorId, IndicatorVersionId, RuleId, RuleVersionId
from baliza.domain.indicator import Indicator, IndicatorVersion
from baliza.domain.quality import DataQuality
from baliza.domain.rule import Rule, RuleVersion, Threshold
from baliza.infrastructure.clock import SystemClock
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

def memory_repos() -> Repositories:
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
        clock=SystemClock(),
    )
    return bind_memory_unit_of_work(built)


def create_app(
    repos: Repositories | None = None,
    *,
    database_url: str | None = None,
    create_schema: bool = False,
) -> FastAPI:
    from baliza.infrastructure.persistence.repositories import open_database, sql_repositories

    application = FastAPI(title="BALIZA V3", version=__version__)
    application.state.clock = SystemClock()
    application.state.session_factory = None
    application.state.mvp_session = None
    try:
        from fastapi.middleware.cors import CORSMiddleware

        application.add_middleware(
            CORSMiddleware,
            allow_origins=[
                "http://localhost:5173",
                "http://127.0.0.1:5173",
                "http://localhost:4173",
                "http://127.0.0.1:4173",
            ],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    except Exception:
        pass
    if database_url:
        factory, engine = open_database(database_url, create_schema=create_schema)
        application.state.session_factory = factory
        application.state.engine = engine
        application.state.repos = None

        @application.middleware("http")
        async def bind_sql_session(request, call_next):
            session = factory()
            request.state.repos = sql_repositories(session, application.state.clock)
            try:
                response = await call_next(request)
            except Exception:
                session.rollback()
                session.close()
                raise
            session.commit()
            session.close()
            return response
    else:
        application.state.repos = repos or memory_repos()
    application.include_router(router)

    @application.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "service": "baliza", "version": __version__}

    return application


app = create_app()


@app.post("/demo/critical-path")
def demo_critical_path(sst: float = 30.0) -> JSONResponse:
    """Synchronous LLM-free demo. Not a production API contract."""
    repos = memory_repos()
    actor = Actor(id=ActorId(), display_name="demo-manager")
    repos.actors.add(actor)
    indicator = Indicator(id=IndicatorId(), name="sst_anomaly")
    iversion = IndicatorVersion(
        id=IndicatorVersionId(),
        indicator_id=indicator.id,
        version="1.0.0",
        unit="degC",
        formula_kind="subtract_baseline",
        baseline=27.0,
        status=PublicationStatus.PUBLISHED,
        input_variable="sst",
    )
    repos.indicators.add_definition(indicator, iversion)
    rule = Rule(id=RuleId(), name="thermal_stress_candidate")
    rversion = RuleVersion(
        id=RuleVersionId(),
        rule_id=rule.id,
        version="1.0.0",
        thresholds=(Threshold(name="anomaly_high", value=2.0),),
        operator=ComparisonOp.GT,
        threshold_name="anomaly_high",
        severity_if_triggered="critical",
        status=PublicationStatus.PUBLISHED,
    )
    repos.rules.add_rule(rule, rversion)
    from datetime import UTC, datetime

    obs = record_observation(
        repos,
        variable="sst",
        unit="degC",
        observed_at=datetime.now(UTC),
        quality=DataQuality(facet=DataQualityFacet.VALID, score=0.9),
        value=sst,
    )
    ivalue = calculate_indicator(repos, version=iversion, observation=obs)
    result = evaluate_and_maybe_alert(
        repos,
        observation=obs,
        indicator_value=ivalue,
        rule=rule,
        rule_version=rversion,
    )
    body: dict = {
        "evaluation_outcome": result.evaluation.outcome.value,
        "evaluation_reason": result.evaluation.reason,
        "rule_version": result.evaluation.rule_version,
        "alert_id": str(result.alert.id) if result.alert else None,
        "ai_used": False,
        "threshold_status": "DEMO / NON-SCIENTIFIC",
        "production_ready": False,
    }
    if result.alert:
        dss = build_dss_package(repos, alert=result.alert, protocol_version="protocol:0.0.0")
        decision = record_human_decision(
            repos,
            actor=actor,
            package=dss,
            justification="demo decision for architecture smoke test",
            selected_option="no_action",
            extra_snapshot={
                "rule_version": rversion.version,
                "rule_evaluation_id": str(result.evaluation.id),
                "indicator_version": iversion.version,
            },
        )
        body["decision_id"] = str(decision.id)
        body["snapshot_id"] = str(decision.dss_context_snapshot_id)
        body["snapshot_hash"] = decision.snapshot_hash
    return JSONResponse(body)
