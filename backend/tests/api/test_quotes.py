import pytest
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


def create_user_device(client, token):
    res = client.post(
        "/api/v1/devices",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "category": "smartphone",
            "brand": "Samsung",
            "model": "Galaxy S23",
            "condition": "Damaged Display"
        }
    )
    return res.json()["id"]


def setup_repair_in_inspection(client):
    """Helper to setup customer, tech, device, repair in DIAGNOSIS_PENDING state."""
    cust_token = gen_token(client, email="quote_cust@revivo.internal", role="customer", name="Alice Quote")
    tech_token = gen_token(client, email="quote_tech@revivo.internal", role="technician", name="Bob Fixer")
    
    tech_prof = client.patch(
        "/api/v1/technicians/profile",
        headers={"Authorization": f"Bearer {tech_token}"},
        json={"business_name": "Fixer Hub", "service_area": "Seattle, WA"}
    ).json()

    dev_id = create_user_device(client, cust_token)

    repair = client.post(
        "/api/v1/repairs",
        headers={"Authorization": f"Bearer {cust_token}"},
        json={"device_id": dev_id, "problem_description": "Flickering AMOLED and cracked glass."}
    ).json()

    repair_id = repair["id"]

    # Tech accepts
    client.post(f"/api/v1/repairs/{repair_id}/accept", headers={"Authorization": f"Bearer {tech_token}"})
    # Tech receives device
    client.patch(
        f"/api/v1/repairs/{repair_id}/status",
        headers={"Authorization": f"Bearer {tech_token}"},
        json={"status": "DEVICE_RECEIVED"}
    )
    # Move to DIAGNOSIS_PENDING
    client.patch(
        f"/api/v1/repairs/{repair_id}/status",
        headers={"Authorization": f"Bearer {tech_token}"},
        json={"status": "DIAGNOSIS_PENDING"}
    )

    return {
        "cust_token": cust_token,
        "tech_token": tech_token,
        "tech_id": tech_prof["id"],
        "repair_id": repair_id
    }


def test_technician_submit_quote(client):
    ctx = setup_repair_in_inspection(client)
    repair_id = ctx["repair_id"]
    tech_token = ctx["tech_token"]
    cust_token = ctx["cust_token"]

    quote_payload = {
        "diagnosis": "OLED panel failure and digitizer flex cable ribbon tear.",
        "labor_cost": 65.0,
        "parts_cost": 140.0,
        "other_fees": 15.0,
        "expected_completion_time": "2 business days",
        "warranty_duration": "90 days warranty on parts and labor",
        "notes": "Original OEM Samsung AMOLED replacement panel.",
        "before_repair_images": ["https://revivo-cdn.internal/repairs/1/before_front.jpg", "https://revivo-cdn.internal/repairs/1/before_inside.jpg"]
    }

    res = client.post(
        f"/api/v1/repairs/{repair_id}/quotes",
        headers={"Authorization": f"Bearer {tech_token}"},
        json=quote_payload
    )
    assert res.status_code == status.HTTP_201_CREATED
    data = res.json()
    assert data["version"] == 1
    assert data["status"] == "PENDING"
    assert data["labor_cost"] == 65.0
    assert data["parts_cost"] == 140.0
    assert data["other_fees"] == 15.0
    assert data["total_amount"] == 220.0
    assert data["diagnosis"] == quote_payload["diagnosis"]
    assert len(data["before_repair_images"]) == 2

    # IMPORTANT: Price Integrity - Repair quote_amount MUST NOT be set or finalized before customer approval
    rep_res = client.get(f"/api/v1/repairs/{repair_id}", headers={"Authorization": f"Bearer {cust_token}"})
    rep_data = rep_res.json()
    assert rep_data["status"] == "QUOTE_PENDING"
    assert rep_data["quote_amount"] is None


def test_customer_approves_quote(client):
    ctx = setup_repair_in_inspection(client)
    repair_id = ctx["repair_id"]
    tech_token = ctx["tech_token"]
    cust_token = ctx["cust_token"]

    quote_res = client.post(
        f"/api/v1/repairs/{repair_id}/quotes",
        headers={"Authorization": f"Bearer {tech_token}"},
        json={
            "diagnosis": "Dead charging port and blown capacitor.",
            "labor_cost": 50.0,
            "parts_cost": 30.0,
            "other_fees": 10.0,
            "expected_completion_time": "1 day",
            "warranty_duration": "60 days",
            "notes": "Soldered new sub-board."
        }
    )
    quote_id = quote_res.json()["id"]

    # Customer approves
    app_res = client.post(
        f"/api/v1/repairs/{repair_id}/quotes/{quote_id}/approve",
        headers={"Authorization": f"Bearer {cust_token}"},
        json={"customer_notes": "Approved. Please proceed ASAP."}
    )
    assert app_res.status_code == status.HTTP_200_OK
    quote_data = app_res.json()
    assert quote_data["status"] == "APPROVED"
    assert quote_data["customer_notes"] == "Approved. Please proceed ASAP."
    assert quote_data["approved_at"] is not None

    # Repair should now be CUSTOMER_APPROVED and have quote_amount set
    rep_res = client.get(f"/api/v1/repairs/{repair_id}", headers={"Authorization": f"Bearer {cust_token}"})
    rep_data = rep_res.json()
    assert rep_data["status"] == "CUSTOMER_APPROVED"
    assert rep_data["quote_amount"] == 90.0


def test_customer_rejects_initial_quote(client):
    ctx = setup_repair_in_inspection(client)
    repair_id = ctx["repair_id"]
    tech_token = ctx["tech_token"]
    cust_token = ctx["cust_token"]

    quote_res = client.post(
        f"/api/v1/repairs/{repair_id}/quotes",
        headers={"Authorization": f"Bearer {tech_token}"},
        json={
            "diagnosis": "Extensive motherboard corrosion.",
            "labor_cost": 250.0,
            "parts_cost": 300.0,
            "other_fees": 50.0,
            "expected_completion_time": "7 days",
            "warranty_duration": "30 days"
        }
    )
    quote_id = quote_res.json()["id"]

    # Customer rejects quote
    rej_res = client.post(
        f"/api/v1/repairs/{repair_id}/quotes/{quote_id}/reject",
        headers={"Authorization": f"Bearer {cust_token}"},
        json={"customer_notes": "Too expensive, I will replace the device."}
    )
    assert rej_res.status_code == status.HTTP_200_OK
    assert rej_res.json()["status"] == "REJECTED"

    # Repair should now be CANCELLED
    rep_res = client.get(f"/api/v1/repairs/{repair_id}", headers={"Authorization": f"Bearer {cust_token}"})
    assert rep_res.json()["status"] == "CANCELLED"


def test_quote_clarification_loop(client):
    ctx = setup_repair_in_inspection(client)
    repair_id = ctx["repair_id"]
    tech_token = ctx["tech_token"]
    cust_token = ctx["cust_token"]

    quote_res = client.post(
        f"/api/v1/repairs/{repair_id}/quotes",
        headers={"Authorization": f"Bearer {tech_token}"},
        json={
            "diagnosis": "Battery replacement required.",
            "labor_cost": 40.0,
            "parts_cost": 50.0,
            "other_fees": 0.0,
            "expected_completion_time": "Same day",
            "warranty_duration": "180 days"
        }
    )
    quote_id = quote_res.json()["id"]

    # 1. Customer asks clarification
    clar_res = client.post(
        f"/api/v1/repairs/{repair_id}/quotes/{quote_id}/clarification",
        headers={"Authorization": f"Bearer {cust_token}"},
        json={"message": "Is this an original OEM battery with genuine serial pairing?"}
    )
    assert clar_res.status_code == status.HTTP_200_OK
    assert clar_res.json()["status"] == "CLARIFICATION_REQUESTED"
    assert clar_res.json()["clarification_message"] == "Is this an original OEM battery with genuine serial pairing?"

    # 2. Technician answers clarification
    resp_res = client.post(
        f"/api/v1/repairs/{repair_id}/quotes/{quote_id}/clarify-response",
        headers={"Authorization": f"Bearer {tech_token}"},
        json={"response": "Yes, OEM certified Samsung battery with serial calibration."}
    )
    assert resp_res.status_code == status.HTTP_200_OK
    assert resp_res.json()["status"] == "PENDING"
    assert resp_res.json()["clarification_response"] == "Yes, OEM certified Samsung battery with serial calibration."

    # 3. Customer approves after clarification
    app_res = client.post(
        f"/api/v1/repairs/{repair_id}/quotes/{quote_id}/approve",
        headers={"Authorization": f"Bearer {cust_token}"}
    )
    assert app_res.status_code == status.HTTP_200_OK
    assert app_res.json()["status"] == "APPROVED"


def test_price_increase_requires_change_request_and_customer_approval(client):
    """
    Technician cannot unilaterally increase the final price without creating
    a new quote/change request and obtaining customer approval.
    """
    ctx = setup_repair_in_inspection(client)
    repair_id = ctx["repair_id"]
    tech_token = ctx["tech_token"]
    cust_token = ctx["cust_token"]

    # 1. Tech submits initial quote ($100 total)
    q1_res = client.post(
        f"/api/v1/repairs/{repair_id}/quotes",
        headers={"Authorization": f"Bearer {tech_token}"},
        json={
            "diagnosis": "Cracked back glass",
            "labor_cost": 40.0,
            "parts_cost": 60.0,
            "other_fees": 0.0,
            "expected_completion_time": "1 day",
            "warranty_duration": "30 days"
        }
    )
    q1_id = q1_res.json()["id"]

    # Customer approves Q1
    client.post(f"/api/v1/repairs/{repair_id}/quotes/{q1_id}/approve", headers={"Authorization": f"Bearer {cust_token}"})

    # Tech advances to REPAIR_IN_PROGRESS
    client.patch(
        f"/api/v1/repairs/{repair_id}/status",
        headers={"Authorization": f"Bearer {tech_token}"},
        json={"status": "REPAIR_IN_PROGRESS"}
    )

    # Verify active approved price is $100
    rep_initial = client.get(f"/api/v1/repairs/{repair_id}", headers={"Authorization": f"Bearer {cust_token}"}).json()
    assert rep_initial["quote_amount"] == 100.0

    # 2. Tech discovers hidden internal camera sensor damage mid-repair and submits a change request ($170 total)
    cr_res = client.post(
        f"/api/v1/repairs/{repair_id}/quotes",
        headers={"Authorization": f"Bearer {tech_token}"},
        json={
            "is_change_request": True,
            "diagnosis": "Cracked back glass + torn telephoto OIS sensor found during disassembly",
            "labor_cost": 50.0,
            "parts_cost": 110.0,
            "other_fees": 10.0,
            "expected_completion_time": "2 days",
            "warranty_duration": "60 days",
            "notes": "Supplemental parts required for telephoto lens."
        }
    )
    assert cr_res.status_code == status.HTTP_201_CREATED
    cr_data = cr_res.json()
    assert cr_data["version"] == 2
    assert cr_data["is_change_request"] is True
    assert cr_data["total_amount"] == 170.0
    assert cr_data["status"] == "PENDING"

    # IMPORTANT: Price MUST NOT increase to $170 automatically! It must remain $100 until customer approval!
    rep_check = client.get(f"/api/v1/repairs/{repair_id}", headers={"Authorization": f"Bearer {cust_token}"}).json()
    assert rep_check["quote_amount"] == 100.0

    # 3. Customer approves the change request
    cr_app = client.post(
        f"/api/v1/repairs/{repair_id}/quotes/{cr_data['id']}/approve",
        headers={"Authorization": f"Bearer {cust_token}"},
        json={"customer_notes": "Understood, approve the additional telephoto sensor fix."}
    )
    assert cr_app.status_code == status.HTTP_200_OK

    # Price is now updated to $170
    rep_final = client.get(f"/api/v1/repairs/{repair_id}", headers={"Authorization": f"Bearer {cust_token}"}).json()
    assert rep_final["quote_amount"] == 170.0


def test_quote_history_endpoint(client):
    ctx = setup_repair_in_inspection(client)
    repair_id = ctx["repair_id"]
    tech_token = ctx["tech_token"]
    cust_token = ctx["cust_token"]

    # Create Quote v1
    q1 = client.post(
        f"/api/v1/repairs/{repair_id}/quotes",
        headers={"Authorization": f"Bearer {tech_token}"},
        json={
            "diagnosis": "Quote 1",
            "labor_cost": 50.0,
            "parts_cost": 50.0,
            "other_fees": 0.0,
            "expected_completion_time": "1 day",
            "warranty_duration": "30 days"
        }
    ).json()

    # Create Quote v2 (superseding v1 pending)
    q2 = client.post(
        f"/api/v1/repairs/{repair_id}/quotes",
        headers={"Authorization": f"Bearer {tech_token}"},
        json={
            "diagnosis": "Quote 2 revised",
            "labor_cost": 60.0,
            "parts_cost": 50.0,
            "other_fees": 0.0,
            "expected_completion_time": "1 day",
            "warranty_duration": "30 days"
        }
    ).json()

    # Customer fetches quote history
    history_res = client.get(
        f"/api/v1/repairs/{repair_id}/quotes",
        headers={"Authorization": f"Bearer {cust_token}"}
    )
    assert history_res.status_code == status.HTTP_200_OK
    quotes = history_res.json()
    assert len(quotes) == 2
    assert quotes[0]["version"] == 1
    assert quotes[0]["status"] == "SUPERSEDED"
    assert quotes[1]["version"] == 2
    assert quotes[1]["status"] == "PENDING"
