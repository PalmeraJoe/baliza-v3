from datetime import UTC, datetime

from baliza.application.use_cases import (
    acknowledge_alert,
    build_dss_package,
    calculate_indicator,
    evaluate_and_maybe_alert,
    record_human_decision,
    record_observation,
)
from baliza.domain.actor import Actor
from baliza.domain.dss import RecommendationView
from baliza.domain.enums import DataQualityFacet
from baliza.domain.ids import ActorId
from baliza.domain.quality import DataQuality

NOW = datetime(2026, 9, 30, 12, 0, tzinfo=UTC)


def test_live_package_mutation_does_not_change_snapshot(
    repos, published_indicator, published_rule
) -> None:
    indicator, iversion = published_indicator
    rule, rversion = published_rule
    repos.indicators.add_definition(indicator, iversion)
    repos.rules.add_rule(rule, rversion)
    actor = Actor(id=ActorId(), display_name="manager")
    repos.actors.add(actor)

    obs = record_observation(
        repos,
        variable="sst",
        unit="degC",
        observed_at=NOW,
        quality=DataQuality(facet=DataQualityFacet.VALID, score=0.95),
        value=30.0,
    )
    ivalue = calculate_indicator(repos, version=iversion, observation=obs)
    result = evaluate_and_maybe_alert(
        repos, observation=obs, indicator_value=ivalue, rule=rule, rule_version=rversion
    )
    assert result.alert is not None
    pkg = build_dss_package(
        repos,
        alert=result.alert,
        protocol_version="p-1.0.0",
        recommendations=[
            RecommendationView(
                recommendation_id="opt-monitor",
                source="protocol",
                text="Intensify monitoring",
            )
        ],
    )
    decision = record_human_decision(
        repos,
        actor=actor,
        package=pkg,
        justification="precautionary monitoring",
        selected_option="opt-monitor",
        extra_snapshot={
            "rule_version": rversion.version,
            "rule_evaluation_id": str(result.evaluation.id),
            "indicator_version": iversion.version,
            "evidence_item_ids": [str(i.id) for i in result.evidence_items],
        },
    )
    snap = repos.dss.get_snapshot(decision.dss_context_snapshot_id)
    assert snap is not None
    original_hash = snap.content_hash
    original_gaps = list(snap.payload["gaps"])
    pkg.add_gap("appeared-after-decision")
    repos.dss.save_package(pkg)
    snap_again = repos.dss.get_snapshot(decision.dss_context_snapshot_id)
    assert snap_again is not None
    assert snap_again.content_hash == original_hash
    assert snap_again.payload["gaps"] == tuple(original_gaps)
    assert "appeared-after-decision" not in snap_again.payload["gaps"]
    assert decision.actor_id == actor.id
    assert "rule_evaluation_id" in snap_again.payload


def test_acknowledge_does_not_create_decision(
    repos, published_indicator, published_rule
) -> None:
    indicator, iversion = published_indicator
    rule, rversion = published_rule
    repos.indicators.add_definition(indicator, iversion)
    repos.rules.add_rule(rule, rversion)
    actor = Actor(id=ActorId(), display_name="operator")
    obs = record_observation(
        repos,
        variable="sst",
        unit="degC",
        observed_at=NOW,
        quality=DataQuality(facet=DataQualityFacet.VALID, score=0.95),
        value=30.0,
    )
    ivalue = calculate_indicator(repos, version=iversion, observation=obs)
    result = evaluate_and_maybe_alert(
        repos, observation=obs, indicator_value=ivalue, rule=rule, rule_version=rversion
    )
    assert result.alert is not None
    updated = acknowledge_alert(repos, alert=result.alert, actor=actor)
    assert repos.decisions.get(updated.id) is None  # type: ignore[arg-type]
    assert len(repos.decisions._items) == 0  # noqa: SLF001
    events = repos.audit.list_for_entity("Alert", str(updated.id))
    assert any(e.action == "alert.acknowledged" for e in events)
