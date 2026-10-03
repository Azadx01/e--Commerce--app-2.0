import pytest
from fastapi import status

def gen_token(client, email="decision_user@example.com"):
    client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "password123", "role": "customer", "name": "Decision Maker"}
    )
    res = client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": "password123"}
    )
    return res.json()["access_token"]


def test_post_decisions_endpoint(client):
    res = client.post(
        "/api/v1/decisions",
        json={
            "device_age": 14.0,
            "device_condition": "fair",
            "repair_estimate": 130.0,
            "current_estimated_resale_value": 260.0,
            "new_device_reference_price": 750.0,
            "warranty_status": "out_of_warranty",
            "user_priority": "budget"
        }
    )
    assert res.status_code == status.HTTP_200_OK
    data = res.json()

    # Verify calculated core metrics
    assert data["repair_ratio"] == 0.5  # 130 / 260
    assert data["repair_vs_new"] == round(130.0 / 750.0, 4)
    assert data["estimated_value_after_repair"] > 260.0

    # Verify all 3 options returned
    assert "repair_option" in data
    assert "sell_option" in data
    assert "replace_option" in data

    # Check structure of each option
    for key in ["repair_option", "sell_option", "replace_option"]:
        opt = data[key]
        assert "estimated_cost_or_value" in opt
        assert "range" in opt
        assert "min" in opt["range"] and "max" in opt["range"]
        assert "explanation" in opt and len(opt["explanation"]) > 0
        assert "confidence" in opt
        assert "uncertainty" in opt

    # Verify no forced winner
    assert "winner" not in data
    assert data["selection_mode"] == "user_driven_choice"


def test_post_decisions_with_field_aliases(client):
    # Testing alternative alias field names: age, current_resale_value, new_device_price, priority
    res = client.post(
        "/api/v1/decisions",
        json={
            "age": 20.0,
            "device_condition": "good",
            "repair_estimate": 100.0,
            "current_resale_value": 300.0,
            "new_device_price": 900.0,
            "warranty": "expired",
            "priority": "speed"
        }
    )
    assert res.status_code == status.HTTP_200_OK
    data = res.json()
    assert data["repair_ratio"] == round(100.0 / 300.0, 4)
    assert data["repair_vs_new"] == round(100.0 / 900.0, 4)


def test_post_decisions_linked_device(client):
    token = gen_token(client)
    
    # 1. Create device
    dev_res = client.post(
        "/api/v1/devices",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "category": "laptop",
            "brand": "Dell",
            "model": "XPS 15"
        }
    )
    device_id = dev_res.json()["id"]

    # 2. Evaluate decision linked to device
    res = client.post(
        "/api/v1/decisions",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "device_id": device_id,
            "device_age": 24.0,
            "device_condition": "fair",
            "repair_estimate": 250.0,
            "current_estimated_resale_value": 500.0,
            "new_device_reference_price": 1500.0,
            "warranty_status": "expired"
        }
    )
    assert res.status_code == status.HTTP_200_OK
    data = res.json()
    assert data["device_id"] == device_id
    assert "id" in data


def test_post_decisions_device_not_found(client):
    res = client.post(
        "/api/v1/decisions",
        json={
            "device_id": 999999,
            "device_age": 12.0,
            "device_condition": "good",
            "repair_estimate": 100.0,
            "current_estimated_resale_value": 200.0,
            "new_device_reference_price": 600.0,
            "warranty_status": "none"
        }
    )
    assert res.status_code == status.HTTP_404_NOT_FOUND
