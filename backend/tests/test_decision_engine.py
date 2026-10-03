import pytest
from app.services.decision_engine import calculate_decision_metrics

def test_decision_engine_calculations_basic():
    # 2-year old device (24 months), $150 repair, $200 resale value, $800 new device
    metrics = calculate_decision_metrics(
        device_age=24.0,
        device_condition="good",
        repair_estimate=150.0,
        current_estimated_resale_value=200.0,
        new_device_reference_price=800.0,
        warranty_status="expired",
        user_priority="budget"
    )

    # 1. Verify repair_ratio = 150 / 200 = 0.75
    assert metrics["repair_ratio"] == 0.75

    # 2. Verify repair_vs_new = 150 / 800 = 0.1875
    assert metrics["repair_vs_new"] == 0.1875

    # 3. Verify estimated_value_after_repair > current_estimated_resale_value and < new_device_reference_price
    assert metrics["estimated_value_after_repair"] > 200.0
    assert metrics["estimated_value_after_repair"] < 800.0


def test_decision_engine_all_three_options_present():
    metrics = calculate_decision_metrics(
        device_age=18.0,
        device_condition="fair",
        repair_estimate=120.0,
        current_estimated_resale_value=250.0,
        new_device_reference_price=900.0,
        warranty_status="out_of_warranty",
        user_priority="balanced"
    )

    # Must return all three options
    assert "repair_option" in metrics
    assert "sell_option" in metrics
    assert "replace_option" in metrics

    repair = metrics["repair_option"]
    sell = metrics["sell_option"]
    replace = metrics["replace_option"]

    # Each option must include: estimated cost/value, range, explanation, uncertainty/confidence
    for opt in [repair, sell, replace]:
        assert "estimated_cost_or_value" in opt
        assert "range" in opt
        assert "min" in opt["range"] and "max" in opt["range"]
        assert opt["range"]["min"] <= opt["range"]["max"]
        assert "explanation" in opt and len(opt["explanation"]) > 0
        assert "confidence" in opt
        assert 0.0 < opt["confidence"] <= 1.0
        assert "uncertainty" in opt
        assert opt["uncertainty"] in ["Low", "Moderate", "High"]


def test_decision_engine_does_not_force_a_winner():
    metrics = calculate_decision_metrics(
        device_age=12.0,
        device_condition="good",
        repair_estimate=100.0,
        current_estimated_resale_value=300.0,
        new_device_reference_price=1000.0,
        warranty_status="expired",
        user_priority="balanced"
    )

    # Must NOT designate any option as a forced winner
    assert "winner" not in metrics
    assert "recommended_option" not in metrics
    assert "forced_winner" not in metrics
    assert metrics["selection_mode"] == "user_driven_choice"


def test_decision_engine_zero_resale_value_edge_case():
    metrics = calculate_decision_metrics(
        device_age=36.0,
        device_condition="broken",
        repair_estimate=100.0,
        current_estimated_resale_value=0.0,
        new_device_reference_price=700.0,
        warranty_status="expired"
    )

    assert metrics["repair_ratio"] == 1.0
    assert metrics["repair_vs_new"] == round(100.0 / 700.0, 4)
    assert metrics["estimated_value_after_repair"] > 0.0


def test_decision_engine_warranty_and_priority_influence():
    # Test under warranty with sustainability priority
    metrics = calculate_decision_metrics(
        device_age=10.0,
        device_condition="excellent",
        repair_estimate=80.0,
        current_estimated_resale_value=400.0,
        new_device_reference_price=800.0,
        warranty_status="in_warranty",
        user_priority="sustainability"
    )

    repair_exp = metrics["repair_option"]["explanation"].lower()
    assert "warranty" in repair_exp
    assert "sustainability" in repair_exp or "e-waste" in repair_exp
