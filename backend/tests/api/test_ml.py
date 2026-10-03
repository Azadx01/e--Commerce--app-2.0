import pytest
from fastapi.testclient import TestClient
from app.main import app
from ai.datasets.schema import RepairCostRecord, validate_dataset, REQUIRED_COLUMNS
from ai.inference.predictor import get_repair_cost_predictor, PredictionInput
import pandas as pd

client = TestClient(app)

def test_dataset_schema_validation():
    # Valid record
    valid_data = {
        "device_model": "iPhone 14 Pro",
        "device_age": 12.0,
        "issue": "screen_cracked",
        "repair_cost": 279.0,
        "parts_cost": 190.0,
        "labor_cost": 75.0,
        "condition": "good",
        "resale_value": 650.0,
        "repair_duration": 1.5,
        "repair_outcome": "SUCCESS"
    }
    record = RepairCostRecord(**valid_data)
    assert record.device_model == "iPhone 14 Pro"
    assert record.repair_cost == 279.0

    df = pd.DataFrame([valid_data])
    report = validate_dataset(df)
    assert report["valid"] is True
    assert report["rows"] == 1
    assert set(REQUIRED_COLUMNS).issubset(set(df.columns))

def test_dataset_schema_missing_column():
    invalid_df = pd.DataFrame([{
        "device_model": "iPhone 14 Pro",
        "device_age": 12.0,
    }])
    with pytest.raises(ValueError) as exc_info:
        validate_dataset(invalid_df)
    assert "missing mandatory schema columns" in str(exc_info.value)

def test_ml_model_info_endpoint():
    response = client.get("/api/v1/ml/model-info")
    assert response.status_code == 200
    data = response.json()
    assert "is_model_available" in data
    assert data["is_model_available"] is True
    assert "model_version" in data
    assert "evaluation_metrics" in data
    assert "candidate_benchmarks" in data

def test_ml_predict_repair_cost_endpoint():
    payload = {
        "device_model": "Apple iPhone 14 Pro",
        "device_age": 10.0,
        "issue": "screen_cracked",
        "parts_cost": 180.0,
        "labor_cost": 70.0,
        "condition": "good",
        "resale_value": 700.0,
        "repair_duration": 1.5,
        "repair_outcome": "SUCCESS"
    }
    response = client.post("/api/v1/ml/predict-repair-cost", json=payload)
    assert response.status_code == 200
    res = response.json()
    assert "estimated_repair_cost" in res
    assert res["estimated_repair_cost"] > 0
    assert "lower_bound" in res
    assert "upper_bound" in res
    assert res["lower_bound"] <= res["estimated_repair_cost"] <= res["upper_bound"]
    assert "evaluation_mae" in res
    assert "evaluation_r2" in res
    assert res["is_trained_model"] is True

def test_ml_predictor_singleton():
    predictor = get_repair_cost_predictor()
    inp = PredictionInput(
        device_model="Samsung Galaxy S23",
        device_age=8.0,
        issue="battery_drain",
        parts_cost=65.0,
        labor_cost=45.0,
        condition="fair",
        resale_value=500.0,
        repair_duration=1.0,
        repair_outcome="SUCCESS"
    )
    prediction = predictor.predict(inp)
    assert prediction["estimated_repair_cost"] > 0
    assert prediction["model_version"] != ""
    assert prediction["is_trained_model"] is True
