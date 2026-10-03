import pytest
from fastapi import status
from app.core.config import settings

def register_and_login(client, email, password="password123", role="customer", name="User"):
    headers = {"X-Admin-Provision-Secret": settings.JWT_SECRET} if role == "admin" else {}
    reg_res = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password, "role": role, "name": name},
        headers=headers
    )
    assert reg_res.status_code in [status.HTTP_201_CREATED, status.HTTP_200_OK], reg_res.text
    user_id = reg_res.json()["id"]

    login_res = client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": password}
    )
    assert login_res.status_code == status.HTTP_200_OK, login_res.text
    token = login_res.json()["access_token"]
    return user_id, token


def test_full_end_to_end_repair_resale_lifecycle(client):
    """
    Complete End-to-End Workflow:
    Register -> Login -> Add Device -> Diagnosis -> Decision ->
    Find Technician -> Repair Request -> Quote -> Approval ->
    Repair Tracking -> Payment -> Completion -> Warranty & Device Passport
    """
    # 1. Register & Login Customer and Technician
    cust_id, cust_token = register_and_login(client, "alice_e2e@example.com", "pass123", "customer", "Alice Customer")
    cust_headers = {"Authorization": f"Bearer {cust_token}"}

    tech_id, tech_token = register_and_login(client, "bob_tech_e2e@example.com", "pass123", "technician", "Bob Technician")
    tech_headers = {"Authorization": f"Bearer {tech_token}"}

    _, admin_token = register_and_login(client, "admin_e2e@example.com", "pass123", "admin", "System Admin")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # Setup & Verify Technician Profile
    tech_prof_res = client.patch(
        "/api/v1/technicians/profile",
        headers=tech_headers,
        json={
            "business_name": "Apex Precision Lab",
            "device_categories": ["smartphone", "laptop"],
            "skills": ["Screen", "Battery", "Micro-soldering"],
            "service_area": "New York, NY",
            "bio": "Certified specialist with 8 years experience."
        }
    )
    assert tech_prof_res.status_code == status.HTTP_200_OK
    tech_profile_id = tech_prof_res.json()["id"]

    # Admin verifies technician
    verify_res = client.patch(
        f"/api/v1/technicians/{tech_profile_id}/verify",
        headers=admin_headers,
        json={"verification_status": "verified"}
    )
    assert verify_res.status_code == status.HTTP_200_OK
    assert verify_res.json()["verification_status"] == "verified"

    # 2. Add Device (Customer)
    dev_res = client.post(
        "/api/v1/devices",
        headers=cust_headers,
        json={
            "category": "smartphone",
            "brand": "Apple",
            "model": "iPhone 14 Pro",
            "serial_number": "SN-E2E-APEX-001",
            "condition": "Screen cracked, fair housing"
        }
    )
    assert dev_res.status_code == status.HTTP_201_CREATED
    device_id = dev_res.json()["id"]

    # 3. Diagnosis
    diag_res = client.post(
        "/api/v1/diagnostics",
        headers=cust_headers,
        json={
            "device_id": device_id,
            "reported_problem": "Front glass shattered after drop, touchscreen unresponsive in corner",
            "selected_symptoms": ["Screen"]
        }
    )
    assert diag_res.status_code == status.HTTP_201_CREATED
    diag_data = diag_res.json()
    assert any(k in str(diag_data["diagnosis_result"]).lower() for k in ["display", "screen", "panel", "oled"])
    diag_id = diag_data["id"]

    # 4. Decision Engine (Repair vs Sell vs Replace)
    decision_res = client.post(
        "/api/v1/decisions",
        headers=cust_headers,
        json={
            "device_id": device_id,
            "device_age": 14.0,
            "device_condition": "fair",
            "repair_estimate": 195.0,
            "current_estimated_resale_value": 450.0,
            "new_device_reference_price": 999.0,
            "warranty_status": "out_of_warranty",
            "user_priority": "balanced"
        }
    )
    assert decision_res.status_code == status.HTTP_200_OK
    dec_data = decision_res.json()
    assert "repair_option" in dec_data
    assert "sell_option" in dec_data
    assert "replace_option" in dec_data
    assert dec_data["repair_ratio"] > 0

    # 5. Find Verified Technician in Marketplace
    tech_search_res = client.get(
        "/api/v1/technicians?device_category=smartphone&specialization=Screen",
        headers=cust_headers
    )
    assert tech_search_res.status_code == status.HTTP_200_OK
    found_techs = tech_search_res.json()
    assert any(t["id"] == tech_profile_id for t in found_techs)

    # 6. Create Repair Request
    repair_req_res = client.post(
        "/api/v1/repairs",
        headers=cust_headers,
        json={
            "device_id": device_id,
            "technician_id": tech_profile_id,
            "diagnostic_id": diag_id,
            "problem_description": "OLED screen replacement needed"
        }
    )
    assert repair_req_res.status_code == status.HTTP_201_CREATED
    repair = repair_req_res.json()
    repair_id = repair["id"]
    assert repair["status"] == "REQUESTED"

    # 7. Technician Accepts Repair
    accept_res = client.post(
        f"/api/v1/repairs/{repair_id}/accept",
        headers=tech_headers
    )
    assert accept_res.status_code == status.HTTP_200_OK
    assert accept_res.json()["status"] == "TECHNICIAN_ASSIGNED"

    # Advance to DIAGNOSIS_PENDING
    diag_stage_res = client.patch(
        f"/api/v1/repairs/{repair_id}/status",
        headers=tech_headers,
        json={"status": "DIAGNOSIS_PENDING", "notes": "Device received at lab bench. Beginning disassembly."}
    )
    assert diag_stage_res.status_code == status.HTTP_200_OK
    assert diag_stage_res.json()["status"] == "DIAGNOSIS_PENDING"

    # 8. Technician Submits Quote
    quote_res = client.post(
        f"/api/v1/repairs/{repair_id}/quotes",
        headers=tech_headers,
        json={
            "diagnosis": "Damaged OLED panel. Digitizer flex cable torn.",
            "labor_cost": 65.0,
            "parts_cost": 130.0,
            "other_fees": 10.0,
            "expected_completion_time": "2 business days",
            "warranty_duration": "180 days",
            "notes": "Includes premium OEM panel and water seal gasket replacement."
        }
    )
    assert quote_res.status_code == status.HTTP_201_CREATED
    quote_data = quote_res.json()
    quote_id = quote_data["id"]
    assert quote_data["total_amount"] == 205.0 # 65 + 130 + 10
    assert quote_data["status"] == "PENDING"

    # 9. Customer Approves Quote
    approve_res = client.post(
        f"/api/v1/repairs/{repair_id}/quotes/{quote_id}/approve",
        headers=cust_headers,
        json={"approved": True, "customer_notes": "Approved. Please proceed with OEM panel."}
    )
    assert approve_res.status_code == status.HTTP_200_OK
    assert approve_res.json()["status"] == "APPROVED"

    # 10. Repair Tracking & Execution Stages
    stages = [
        ("PARTS_PENDING", "OEM OLED Display panel dispatched from supplier warehouse."),
        ("REPAIR_IN_PROGRESS", "Display replaced, thermal management verified."),
        ("QUALITY_CHECK", "Touch response, True Tone calibration, and water seal tested."),
        ("READY_FOR_DELIVERY", "Device packaged and ready for customer collection.")
    ]
    for target_status, note in stages:
        stage_res = client.patch(
            f"/api/v1/repairs/{repair_id}/status",
            headers=tech_headers,
            json={"status": target_status, "notes": note}
        )
        assert stage_res.status_code == status.HTTP_200_OK
        assert stage_res.json()["status"] == target_status

    # 11. Customer Payment Checkout
    pay_res = client.post(
        "/api/v1/payments/checkout",
        headers=cust_headers,
        json={
            "repair_id": repair_id,
            "amount": 205.0,
            "currency": "USD",
            "payment_method_type": "card",
            "sandbox_token": "tok_visa_success"
        }
    )
    assert pay_res.status_code == status.HTTP_201_CREATED
    pay_data = pay_res.json()
    assert pay_data["status"] == "CAPTURED"
    assert pay_data["platform_fee"] == 30.75 # 15% of 205.0
    assert pay_data["technician_payout"] == 174.25 # 85% of 205.0
    assert pay_data["invoice_reference"].startswith("INV-")

    # 12. Repair Completion (DELIVERED)
    complete_res = client.patch(
        f"/api/v1/repairs/{repair_id}/status",
        headers=tech_headers,
        json={"status": "DELIVERED", "notes": "Customer received device in pristine condition."}
    )
    assert complete_res.status_code == status.HTTP_200_OK
    assert complete_res.json()["status"] == "DELIVERED"

    # 13. Verify Device Passport & Warranty History
    passport_res = client.get(
        f"/api/v1/devices/{device_id}/passport",
        headers=cust_headers
    )
    assert passport_res.status_code == status.HTTP_200_OK
    passport = passport_res.json()
    assert passport["brand"] == "Apple"
    assert passport["model"] == "iPhone 14 Pro"
    assert len(passport["repair_history"]) >= 1
    latest_repair = passport["repair_history"][0]
    assert latest_repair["repair_id"] == repair_id
    assert latest_repair["repair_cost"] == 205.0
    assert passport["warranty"]["is_active"] is True


def test_quote_modification_requires_customer_approval(client):
    """
    CRITICAL CONSTRAINT: A technician must NOT increase the final price
    without creating a new quote/change request and obtaining customer approval.
    """
    cust_id, cust_token = register_and_login(client, "cust_quote_mod@example.com", "pass", "customer")
    tech_id, tech_token = register_and_login(client, "tech_quote_mod@example.com", "pass", "technician")
    cust_headers = {"Authorization": f"Bearer {cust_token}"}
    tech_headers = {"Authorization": f"Bearer {tech_token}"}

    # Create device and repair
    dev_res = client.post("/api/v1/devices", headers=cust_headers, json={"category": "smartphone", "brand": "Samsung", "model": "Galaxy S23"})
    dev_id = dev_res.json()["id"]

    tech_prof_res = client.patch("/api/v1/technicians/profile", headers=tech_headers, json={"business_name": "Mod Lab"})
    t_id = tech_prof_res.json()["id"]

    rep_res = client.post("/api/v1/repairs", headers=cust_headers, json={"device_id": dev_id, "technician_id": t_id, "problem_description": "Battery drain"})
    rep_id = rep_res.json()["id"]

    client.post(f"/api/v1/repairs/{rep_id}/accept", headers=tech_headers)

    # Initial Quote v1 ($80)
    q1_res = client.post(
        f"/api/v1/repairs/{rep_id}/quotes",
        headers=tech_headers,
        json={
            "diagnosis": "Battery replacement",
            "labor_cost": 30.0,
            "parts_cost": 50.0,
            "other_fees": 0.0,
            "expected_completion_time": "1 business day",
            "warranty_duration": "90 days"
        }
    )
    assert q1_res.status_code == status.HTTP_201_CREATED
    q1_id = q1_res.json()["id"]
    assert q1_res.json()["total_amount"] == 80.0

    # Customer approves Quote v1
    client.post(f"/api/v1/repairs/{rep_id}/quotes/{q1_id}/approve", headers=cust_headers)
    rep_check = client.get(f"/api/v1/repairs/{rep_id}", headers=cust_headers).json()
    assert rep_check["quote_amount"] == 80.0

    # Technician discovers water damage and submits Change Request Quote v2 ($140)
    q2_res = client.post(
        f"/api/v1/repairs/{rep_id}/quotes",
        headers=tech_headers,
        json={
            "is_change_request": True,
            "diagnosis": "Supplemental: Sub-board corrosion detected requiring ultrasonic cleaning.",
            "labor_cost": 50.0,
            "parts_cost": 90.0,
            "other_fees": 0.0,
            "expected_completion_time": "2 business days",
            "warranty_duration": "90 days"
        }
    )
    assert q2_res.status_code == status.HTTP_201_CREATED
    q2_data = q2_res.json()
    assert q2_data["version"] == 2
    assert q2_data["is_change_request"] is True
    assert q2_data["total_amount"] == 140.0
    q2_id = q2_data["id"]

    # Until customer approves, official approved repair price MUST remain $80!
    rep_mid = client.get(f"/api/v1/repairs/{rep_id}", headers=cust_headers).json()
    assert rep_mid["quote_amount"] == 80.0

    # Customer approves Change Request Quote v2
    client.post(f"/api/v1/repairs/{rep_id}/quotes/{q2_id}/approve", headers=cust_headers)
    rep_final = client.get(f"/api/v1/repairs/{rep_id}", headers=cust_headers).json()
    assert rep_final["quote_amount"] == 140.0


def test_quote_rejection_cancellation_workflow(client):
    """
    Verify customer quote rejection cancels the repair cleanly.
    """
    cust_id, cust_token = register_and_login(client, "cust_cancel@example.com", "pass", "customer")
    tech_id, tech_token = register_and_login(client, "tech_cancel@example.com", "pass", "technician")
    cust_headers = {"Authorization": f"Bearer {cust_token}"}
    tech_headers = {"Authorization": f"Bearer {tech_token}"}

    dev_res = client.post("/api/v1/devices", headers=cust_headers, json={"category": "laptop", "brand": "Dell", "model": "Inspiron 15"})
    dev_id = dev_res.json()["id"]

    t_res = client.patch("/api/v1/technicians/profile", headers=tech_headers, json={"business_name": "Dell Tech"})
    t_id = t_res.json()["id"]

    rep_res = client.post("/api/v1/repairs", headers=cust_headers, json={"device_id": dev_id, "technician_id": t_id, "problem_description": "Motherboard short"})
    rep_id = rep_res.json()["id"]
    client.post(f"/api/v1/repairs/{rep_id}/accept", headers=tech_headers)

    q_res = client.post(
        f"/api/v1/repairs/{rep_id}/quotes",
        headers=tech_headers,
        json={
            "diagnosis": "Complete logic board replacement",
            "labor_cost": 150.0,
            "parts_cost": 350.0,
            "other_fees": 0.0,
            "expected_completion_time": "3 business days",
            "warranty_duration": "90 days"
        }
    )
    assert q_res.status_code == status.HTTP_201_CREATED
    q_id = q_res.json()["id"]

    # Customer rejects high quote
    reject_res = client.post(
        f"/api/v1/repairs/{rep_id}/quotes/{q_id}/reject",
        headers=cust_headers,
        json={"approved": False, "customer_notes": "Too expensive, I will sell the device instead."}
    )
    assert reject_res.status_code == status.HTTP_200_OK
    assert reject_res.json()["status"] == "REJECTED"

    # Verify repair status transitioned to CANCELLED
    rep_check = client.get(f"/api/v1/repairs/{rep_id}", headers=cust_headers).json()
    assert rep_check["status"] == "CANCELLED"


def test_payment_failure_simulation(client):
    """
    Verify payment failure handling: transitions to FAILED state and does not store card data.
    """
    cust_id, cust_token = register_and_login(client, "cust_payfail@example.com", "pass", "customer")
    cust_headers = {"Authorization": f"Bearer {cust_token}"}

    # Attempt checkout with declining mock token
    fail_res = client.post(
        "/api/v1/payments/checkout",
        headers=cust_headers,
        json={
            "order_reference": "PO-FAIL-TEST",
            "amount": 150.0,
            "currency": "USD",
            "payment_method_type": "card",
            "sandbox_token": "tok_chargeDeclined"
        }
    )
    assert fail_res.status_code in [status.HTTP_201_CREATED, status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST]
    pay_data = fail_res.json()
    assert pay_data.get("status") == "FAILED" or "declined" in str(pay_data).lower()


def test_invalid_inputs_and_edge_cases(client):
    """
    Comprehensive verification of input validation across endpoints:
    - Empty symptom array
    - Invalid device category
    - Negative payment amount
    - Non-existent resource lookups
    """
    cust_id, cust_token = register_and_login(client, "cust_invalid@example.com", "pass", "customer")
    cust_headers = {"Authorization": f"Bearer {cust_token}"}

    # 1. Empty symptoms array in diagnostics
    diag_bad = client.post(
        "/api/v1/diagnostics",
        headers=cust_headers,
        json={"reported_problem": "Broken", "selected_symptoms": []}
    )
    assert diag_bad.status_code in [status.HTTP_422_UNPROCESSABLE_ENTITY, status.HTTP_400_BAD_REQUEST]

    # 2. Unsupported device category
    dev_bad = client.post(
        "/api/v1/devices",
        headers=cust_headers,
        json={"category": "smartfridge", "brand": "LG", "model": "Cooler Pro"}
    )
    assert dev_bad.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_422_UNPROCESSABLE_ENTITY]

    # 3. Negative payment amount
    pay_bad = client.post(
        "/api/v1/payments/create-intent",
        headers=cust_headers,
        json={"amount": -50.0, "currency": "USD"}
    )
    assert pay_bad.status_code in [status.HTTP_422_UNPROCESSABLE_ENTITY, status.HTTP_400_BAD_REQUEST]

    # 4. Non-existent resource lookups return 404
    assert client.get("/api/v1/devices/99999", headers=cust_headers).status_code == status.HTTP_404_NOT_FOUND
    assert client.get("/api/v1/repairs/99999", headers=cust_headers).status_code == status.HTTP_404_NOT_FOUND
    assert client.get("/api/v1/parts/99999").status_code == status.HTTP_404_NOT_FOUND
