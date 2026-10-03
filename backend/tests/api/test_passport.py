import pytest
from datetime import datetime, timezone, timedelta
from fastapi import status

def gen_token(client, email="user@revivo.internal", role="customer", name="User"):
    client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "password123", "role": role, "name": name}
    )
    res = client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": "password123"}
    )
    return res.json()["access_token"]


def test_device_passport_new_device(client):
    cust_token = gen_token(client, email="pass_cust1@revivo.internal", role="customer", name="Alice Passport")
    
    # Create device
    dev_res = client.post(
        "/api/v1/devices",
        headers={"Authorization": f"Bearer {cust_token}"},
        json={
            "category": "laptop",
            "brand": "Dell",
            "model": "Inspiron 15",
            "condition": "Brand New",
            "serial_number": "DELL-SECURE-SERIAL-998811"
        }
    )
    dev_id = dev_res.json()["id"]

    # Fetch passport
    pass_res = client.get(f"/api/v1/devices/{dev_id}/passport", headers={"Authorization": f"Bearer {cust_token}"})
    assert pass_res.status_code == status.HTTP_200_OK
    passport = pass_res.json()

    assert passport["device_id"] == dev_id
    assert passport["brand"] == "Dell"
    assert passport["model"] == "Inspiron 15"
    assert passport["passport_id"].startswith("REVIVO-DPP-")
    
    # Privacy verification: Raw serial number must NOT appear in output
    assert "DELL-SECURE-SERIAL-998811" not in str(passport)
    assert passport["masked_identifier"]

    # Warranty verification
    assert passport["warranty"]["is_active"] is True
    assert passport["warranty"]["status"] == "ACTIVE"
    assert passport["warranty"]["days_remaining"] > 0

    # Lifecycle events must contain at least PURCHASE event
    assert len(passport["lifecycle_timeline"]) >= 1
    assert passport["lifecycle_timeline"][0]["event_type"] in ["PURCHASE", "VALUATION"]

    # Resale valuation
    assert passport["resale_valuation"]["estimated_market_value"] > 0
    assert passport["resale_valuation"]["revivo_buyback_estimate"] > 0


def test_device_passport_with_full_repair_history_and_replaced_parts(client):
    """
    Test passport with repair history, replaced parts, technician info, and updated service warranty.
    Matches user example:
    Device: Dell Inspiron 15
    Repair History: Battery replaced, ₹4,500, 12 September 2026
    Warranty: Valid until 12 March 2027
    """
    cust_token = gen_token(client, email="pass_cust2@revivo.internal", role="customer", name="Bob Passport")
    tech_token = gen_token(client, email="pass_tech2@revivo.internal", role="technician", name="Dave Tech")
    
    client.patch(
        "/api/v1/technicians/profile",
        headers={"Authorization": f"Bearer {tech_token}"},
        json={"business_name": "Apex Precision Micro-Repairs", "service_area": "Seattle, WA"}
    )

    # 1. Register Device
    dev_res = client.post(
        "/api/v1/devices",
        headers={"Authorization": f"Bearer {cust_token}"},
        json={"category": "smartphone", "brand": "Samsung", "model": "Galaxy S23", "condition": "Screen Damaged"}
    )
    dev_id = dev_res.json()["id"]

    # 2. Diagnostic Scan
    client.post(
        "/api/v1/diagnostics",
        headers={"Authorization": f"Bearer {cust_token}"},
        json={
            "device_id": dev_id,
            "reported_problem": "Flickering OLED and weak battery",
            "selected_symptoms": ["Screen", "Battery"]
        }
    )

    # 3. Create Repair & Quote
    rep_res = client.post(
        "/api/v1/repairs",
        headers={"Authorization": f"Bearer {cust_token}"},
        json={"device_id": dev_id, "problem_description": "OLED panel replacement and battery service"}
    )
    repair_id = rep_res.json()["id"]

    client.post(f"/api/v1/repairs/{repair_id}/accept", headers={"Authorization": f"Bearer {tech_token}"})
    client.patch(f"/api/v1/repairs/{repair_id}/status", headers={"Authorization": f"Bearer {tech_token}"}, json={"status": "DEVICE_RECEIVED"})
    client.patch(f"/api/v1/repairs/{repair_id}/status", headers={"Authorization": f"Bearer {tech_token}"}, json={"status": "DIAGNOSIS_PENDING"})

    quote_res = client.post(
        f"/api/v1/repairs/{repair_id}/quotes",
        headers={"Authorization": f"Bearer {tech_token}"},
        json={
            "diagnosis": "Damaged OEM Display and swollen battery",
            "labor_cost": 50.0,
            "parts_cost": 150.0,
            "other_fees": 10.0,
            "expected_completion_time": "1 business day",
            "warranty_duration": "180 days warranty on parts and labor",
            "notes": "Replaced with factory original AMOLED and 3900mAh battery."
        }
    )
    quote_id = quote_res.json()["id"]

    # Customer approves quote
    client.post(f"/api/v1/repairs/{repair_id}/quotes/{quote_id}/approve", headers={"Authorization": f"Bearer {cust_token}"})

    # Tech completes repair
    client.patch(f"/api/v1/repairs/{repair_id}/status", headers={"Authorization": f"Bearer {tech_token}"}, json={"status": "REPAIR_IN_PROGRESS"})
    client.patch(f"/api/v1/repairs/{repair_id}/status", headers={"Authorization": f"Bearer {tech_token}"}, json={"status": "READY_FOR_DELIVERY"})
    client.patch(f"/api/v1/repairs/{repair_id}/status", headers={"Authorization": f"Bearer {tech_token}"}, json={"status": "DELIVERED"})

    # 4. Fetch Passport
    pass_res = client.get(f"/api/v1/devices/{dev_id}/passport", headers={"Authorization": f"Bearer {cust_token}"})
    assert pass_res.status_code == status.HTTP_200_OK
    passport = pass_res.json()

    # Verify repair history
    assert len(passport["repair_history"]) == 1
    repair_record = passport["repair_history"][0]
    assert repair_record["repair_id"] == repair_id
    assert repair_record["repair_cost"] == 210.0
    assert "Apex Precision Micro-Repairs" in repair_record["technician_business"]
    assert any("Display" in p or "Battery" in p for p in repair_record["parts_replaced"])

    # Verify warranty extended by repair service
    assert passport["warranty"]["is_active"] is True
    assert passport["warranty"]["days_remaining"] > 100
    assert "180 days" in passport["warranty"]["coverage_details"]

    # Verify lifecycle timeline has all events (Purchase, Diagnostic, Repair)
    event_types = [e["event_type"] for e in passport["lifecycle_timeline"]]
    assert "PURCHASE" in event_types
    assert "DIAGNOSTIC" in event_types
    assert "REPAIR" in event_types


def test_passport_authorization(client):
    cust1_token = gen_token(client, email="cust1_pass@revivo.internal", role="customer")
    cust2_token = gen_token(client, email="cust2_pass@revivo.internal", role="customer")

    dev_res = client.post(
        "/api/v1/devices",
        headers={"Authorization": f"Bearer {cust1_token}"},
        json={"category": "smartphone", "brand": "Google", "model": "Pixel 7", "condition": "Good"}
    )
    dev_id = dev_res.json()["id"]

    # Other customer cannot view passport
    res_forbidden = client.get(f"/api/v1/devices/{dev_id}/passport", headers={"Authorization": f"Bearer {cust2_token}"})
    assert res_forbidden.status_code == status.HTTP_403_FORBIDDEN
