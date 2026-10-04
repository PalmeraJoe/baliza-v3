from baliza.experimental.phase77.eligibility import eligibility_decision


def test_no_target_is_eligible_and_nothing_is_estimated() -> None:
    decision = eligibility_decision()
    assert decision["decision"] == "NO"
    assert decision["statement"] == "TARGET NOT YET ELIGIBLE FOR MODELING"
    assert decision["eligible_target_ids"] == []
    assert decision["estimated"] == "NONE"
    assert decision["ml_implementation"] == "NOT_AUTHORIZED"
    assert decision["downscaling"] == "NOT_AUTHORIZED"
    assert decision["alerts"] == []
    assert decision["thresholds"] == []
    assert decision["applicability"]["current_domain"] == "UNKNOWN_DOMAIN"
    assert decision["spatial_units"]["spatial_blocking_unit"] == "OPEN"
    assert decision["temporal_units"]["near_window"] == "NOT_DEFINED"
    assert decision["resort"]["base_model_training"] is False
    assert decision["resort"]["site_specific_validation"] == "NOT_AVAILABLE"
    ids = [item["target_id"] for item in decision["candidates"]]
    assert ids == [
        "A-local-absolute-temperature",
        "B-local-thermal-anomaly",
        "C-local-regional-residual",
        "D-ecological-response",
    ]
    assert all(item["current_eligibility"] == "NOT_ELIGIBLE" for item in decision["candidates"])
    by_source = {item["source"]: item["status"] for item in decision["ground_truth"]}
    assert by_source["In-situ temperature sensor"] == "NOT_AVAILABLE"
    assert by_source["NOAA Coral Reef Watch"] == "NOT_APPLICABLE"
    assert by_source["MERMAID"] == "PARTIAL"
    assert "MERMAID_IS_NOT_THERMAL_GROUND_TRUTH" in decision["do_not_estimate"]
    assert "GRID_IS_NOT_A_LOCAL_MEASUREMENT" in decision["do_not_estimate"]
    text = str(decision)
    assert "xgboost" not in text.lower()
    assert "quality_score" not in text.lower()
