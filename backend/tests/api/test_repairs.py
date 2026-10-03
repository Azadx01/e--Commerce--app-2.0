import pytest
from fastapi import status
from app.core.config import settings

def gen_token(client, email="user@revivo.internal", role="customer", name="User"):
    headers = {"X-Admin-Provision-Secret": settings.JWT_SECRET} if role == "admin" else {}
    client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "password123", "role": role, "name": name},
        headers=headers
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
            "brand": "Google",
            "model": "Pixel 7 Pro",
            "condition": "Cracked Screen"
        }
    )
    return res.json()["id"]


def test_create_repair_request(client):
    cust_token = gen_token(client, email="cust_repair1@revivo.internal", role="customer", name="Alice Customer")
    device_id = create_user_device(client, cust_token)

    res = client.post(
        "/api/v1/repairs",
        headers={"Authorization": f"Bearer {cust_token}"},
        json={
            "device_id": device_id,
            "problem_description": "Dropped phone, OLED display has green lines and touch is dead.",
            "customer_notes": "Please handle with care, contains work data."
        }
    )
    assert res.status_code == status.HTTP_201_CREATED
    data = res.json()
    assert data["status"] == "REQUESTED"
    assert data["device_id"] == device_id
    assert len(data["status_history"]) == 1
    assert data["status_history"][0]["to_status"] == "REQUESTED"


def test_customer_cannot_create_repair_for_other_user_device(client):
    cust1_token = gen_token(client, email="cust1_dev@revivo.internal", role="customer")
    cust2_token = gen_token(client, email="cust2_dev@revivo.internal", role="customer")
    dev_id = create_user_device(client, cust1_token)

    res = client.post(
        "/api/v1/repairs",
        headers={"Authorization": f"Bearer {cust2_token}"},
        json={"device_id": dev_id, "problem_description": "Trying to access other's device"}
    )
    assert res.status_code == status.HTTP_403_FORBIDDEN


def test_full_repair_workflow_and_audit_history(client):
    # 1. Setup Customer & Device
    cust_token = gen_token(client, email="workflow_cust@revivo.internal", role="customer", name="Carol")
    device_id = create_user_device(client, cust_token)

    # 2. Setup Technician
    tech_token = gen_token(client, email="workflow_tech@revivo.internal", role="technician", name="Bob Tech")
    tech_prof_res = client.patch(
        "/api/v1/technicians/profile",
        headers={"Authorization": f"Bearer {tech_token}"},
        json={"business_name": "Bob's Micro Repairs", "service_area": "Austin, TX"}
    )
    tech_id = tech_prof_res.json()["id"]

    # 3. Customer creates repair request -> REQUESTED
    req_res = client.post(
        "/api/v1/repairs",
        headers={"Authorization": f"Bearer {cust_token}"},
        json={
            "device_id": device_id,
            "problem_description": "Battery drains instantly and screen flickers."
        }
    )
    assert req_res.status_code == status.HTTP_201_CREATED
    repair_id = req_res.json()["id"]

    # 4. Technician accepts request -> TECHNICIAN_ASSIGNED
    accept_res = client.post(
        f"/api/v1/repairs/{repair_id}/accept",
        headers={"Authorization": f"Bearer {tech_token}"}
    )
    assert accept_res.status_code == status.HTTP_200_OK
    assert accept_res.json()["status"] == "TECHNICIAN_ASSIGNED"
    assert accept_res.json()["technician_id"] == tech_id

    # 5. Technician marks device received -> DEVICE_RECEIVED
    recv_res = client.patch(
        f"/api/v1/repairs/{repair_id}/status",
        headers={"Authorization": f"Bearer {tech_token}"},
        json={"status": "DEVICE_RECEIVED", "notes": "Received device at repair center"}
    )
    assert recv_res.status_code == status.HTTP_200_OK
    assert recv_res.json()["status"] == "DEVICE_RECEIVED"

    # 6. Technician begins diagnosis -> DIAGNOSIS_PENDING
    diag_res = client.patch(
        f"/api/v1/repairs/{repair_id}/status",
        headers={"Authorization": f"Bearer {tech_token}"},
        json={
            "status": "DIAGNOSIS_PENDING",
            "inspection_notes": "Tested battery health: 65% capacity. Display connector pin loose."
        }
    )
    assert diag_res.status_code == status.HTTP_200_OK
    assert diag_res.json()["status"] == "DIAGNOSIS_PENDING"

    # 7. Technician creates quote -> QUOTE_PENDING
    quote_res = client.post(
        f"/api/v1/repairs/{repair_id}/quote",
        headers={"Authorization": f"Bearer {tech_token}"},
        json={
            "quote_amount": 129.50,
            "quote_details": "OEM Battery ($45) + Display flex repair ($35) + Labor ($49.50)"
        }
    )
    assert quote_res.status_code == status.HTTP_200_OK
    assert quote_res.json()["status"] == "QUOTE_PENDING"
    assert quote_res.json()["quote_amount"] == 129.50

    # 8. Customer approves quote -> CUSTOMER_APPROVED
    approve_res = client.post(
        f"/api/v1/repairs/{repair_id}/quote/respond",
        headers={"Authorization": f"Bearer {cust_token}"},
        json={"approved": True, "notes": "Approved, please proceed with OEM parts"}
    )
    assert approve_res.status_code == status.HTTP_200_OK
    assert approve_res.json()["status"] == "CUSTOMER_APPROVED"

    # 9. Technician waits for parts -> PARTS_PENDING
    parts_res = client.patch(
        f"/api/v1/repairs/{repair_id}/status",
        headers={"Authorization": f"Bearer {tech_token}"},
        json={"status": "PARTS_PENDING", "notes": "OEM battery ordered, delivery expected in 2 days"}
    )
    assert parts_res.status_code == status.HTTP_200_OK
    assert parts_res.json()["status"] == "PARTS_PENDING"

    # 10. Technician starts repair -> REPAIR_IN_PROGRESS
    prog_res = client.patch(
        f"/api/v1/repairs/{repair_id}/status",
        headers={"Authorization": f"Bearer {tech_token}"},
        json={"status": "REPAIR_IN_PROGRESS", "notes": "Parts arrived. Battery and flex repair underway."}
    )
    assert prog_res.status_code == status.HTTP_200_OK
    assert prog_res.json()["status"] == "REPAIR_IN_PROGRESS"

    # 11. Technician completes repair, moves to QA -> QUALITY_CHECK
    qa_res = client.patch(
        f"/api/v1/repairs/{repair_id}/status",
        headers={"Authorization": f"Bearer {tech_token}"},
        json={"status": "QUALITY_CHECK", "notes": "Running battery drain test & screen touch calibration"}
    )
    assert qa_res.status_code == status.HTTP_200_OK
    assert qa_res.json()["status"] == "QUALITY_CHECK"

    # 12. QA passes -> READY_FOR_DELIVERY
    ready_res = client.patch(
        f"/api/v1/repairs/{repair_id}/status",
        headers={"Authorization": f"Bearer {tech_token}"},
        json={"status": "READY_FOR_DELIVERY", "notes": "All hardware diagnostics passed. Packaged."}
    )
    assert ready_res.status_code == status.HTTP_200_OK
    assert ready_res.json()["status"] == "READY_FOR_DELIVERY"

    # 13. Delivery dispatched -> DELIVERED
    deliv_res = client.patch(
        f"/api/v1/repairs/{repair_id}/status",
        headers={"Authorization": f"Bearer {tech_token}"},
        json={"status": "DELIVERED", "notes": "Handed over to customer with tracking"}
    )
    assert deliv_res.status_code == status.HTTP_200_OK
    assert deliv_res.json()["status"] == "DELIVERED"

    # 14. Customer confirms and closes -> CLOSED
    close_res = client.patch(
        f"/api/v1/repairs/{repair_id}/status",
        headers={"Authorization": f"Bearer {cust_token}"},
        json={"status": "CLOSED", "notes": "Device received in excellent condition. Everything works!"}
    )
    assert close_res.status_code == status.HTTP_200_OK
    assert close_res.json()["status"] == "CLOSED"

    # 15. Verify full audit trail
    history_res = client.get(
        f"/api/v1/repairs/{repair_id}/history",
        headers={"Authorization": f"Bearer {cust_token}"}
    )
    assert history_res.status_code == status.HTTP_200_OK
    history_list = history_res.json()
    assert len(history_list) == 12  # Initial REQUESTED + 11 transitions

    expected_statuses = [
        "REQUESTED",
        "TECHNICIAN_ASSIGNED",
        "DEVICE_RECEIVED",
        "DIAGNOSIS_PENDING",
        "QUOTE_PENDING",
        "CUSTOMER_APPROVED",
        "PARTS_PENDING",
        "REPAIR_IN_PROGRESS",
        "QUALITY_CHECK",
        "READY_FOR_DELIVERY",
        "DELIVERED",
        "CLOSED",
    ]
    actual_statuses = [h["to_status"] for h in history_list]
    assert actual_statuses == expected_statuses


def test_invalid_status_transition_rejected(client):
    cust_token = gen_token(client, email="cust_invalid_t@revivo.internal", role="customer")
    device_id = create_user_device(client, cust_token)
    admin_token = gen_token(client, email="admin_t@revivo.internal", role="admin")

    # Create repair (status: REQUESTED)
    req_res = client.post(
        "/api/v1/repairs",
        headers={"Authorization": f"Bearer {cust_token}"},
        json={"device_id": device_id, "problem_description": "Test invalid jump"}
    )
    repair_id = req_res.json()["id"]

    # Invalid jump: REQUESTED -> REPAIR_IN_PROGRESS (must be rejected with 400)
    bad_res = client.patch(
        f"/api/v1/repairs/{repair_id}/status",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"status": "REPAIR_IN_PROGRESS"}
    )
    assert bad_res.status_code == status.HTTP_400_BAD_REQUEST
    assert "Invalid status transition" in bad_res.json()["detail"]


def test_quote_rejection_cancels_repair(client):
    cust_token = gen_token(client, email="cust_reject@revivo.internal", role="customer")
    tech_token = gen_token(client, email="tech_reject@revivo.internal", role="technician")
    device_id = create_user_device(client, cust_token)

    # Setup tech
    client.patch("/api/v1/technicians/profile", headers={"Authorization": f"Bearer {tech_token}"}, json={"service_area": "Dallas, TX"})

    # Create & Accept
    r_id = client.post("/api/v1/repairs", headers={"Authorization": f"Bearer {cust_token}"}, json={"device_id": device_id, "problem_description": "Water damage"}).json()["id"]
    client.post(f"/api/v1/repairs/{r_id}/accept", headers={"Authorization": f"Bearer {tech_token}"})
    client.patch(f"/api/v1/repairs/{r_id}/status", headers={"Authorization": f"Bearer {tech_token}"}, json={"status": "DEVICE_RECEIVED"})
    client.patch(f"/api/v1/repairs/{r_id}/status", headers={"Authorization": f"Bearer {tech_token}"}, json={"status": "DIAGNOSIS_PENDING"})
    client.post(f"/api/v1/repairs/{r_id}/quote", headers={"Authorization": f"Bearer {tech_token}"}, json={"quote_amount": 500.0, "quote_details": "Full board replacement"})

    # Customer rejects quote
    rej_res = client.post(
        f"/api/v1/repairs/{r_id}/quote/respond",
        headers={"Authorization": f"Bearer {cust_token}"},
        json={"approved": False, "notes": "Too expensive, prefer to buy a new device"}
    )
    assert rej_res.status_code == status.HTTP_200_OK
    assert rej_res.json()["status"] == "CANCELLED"


def test_dispute_transition(client):
    cust_token = gen_token(client, email="cust_dispute@revivo.internal", role="customer")
    tech_token = gen_token(client, email="tech_dispute@revivo.internal", role="technician")
    device_id = create_user_device(client, cust_token)

    client.patch("/api/v1/technicians/profile", headers={"Authorization": f"Bearer {tech_token}"}, json={"service_area": "Seattle, WA"})
    r_id = client.post("/api/v1/repairs", headers={"Authorization": f"Bearer {cust_token}"}, json={"device_id": device_id, "problem_description": "Battery dead"}).json()["id"]
    client.post(f"/api/v1/repairs/{r_id}/accept", headers={"Authorization": f"Bearer {tech_token}"})

    # Raise dispute
    disp_res = client.patch(
        f"/api/v1/repairs/{r_id}/status",
        headers={"Authorization": f"Bearer {cust_token}"},
        json={"status": "DISPUTED", "notes": "Technician has not picked up device for 5 days"}
    )
    assert disp_res.status_code == status.HTTP_200_OK
    assert disp_res.json()["status"] == "DISPUTED"
