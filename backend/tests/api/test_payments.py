import pytest
from fastapi import status
from app.core.config import settings

def gen_token(client, email="pay_user@example.com", role="customer"):
    headers = {"X-Admin-Provision-Secret": settings.JWT_SECRET} if role == "admin" else {}
    client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "password", "role": role, "name": "Payment Test User"},
        headers=headers
    )
    res = client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": "password"}
    )
    return res.json()["access_token"]


def create_test_device_and_repair(client, token):
    headers = {"Authorization": f"Bearer {token}"}
    dev_res = client.post(
        "/api/v1/devices",
        headers=headers,
        json={
            "category": "smartphone",
            "brand": "Apple",
            "model": "iPhone 14 Pro",
            "serial_number": "SN-PAY-9921",
            "condition": "Cracked OLED"
        }
    )
    dev_id = dev_res.json()["id"]

    rep_res = client.post(
        "/api/v1/repairs",
        headers=headers,
        json={
            "device_id": dev_id,
            "problem_description": "OLED screen replacement needed"
        }
    )
    rep_id = rep_res.json()["id"]
    return dev_id, rep_id


def test_payment_lifecycle_states(client):
    """
    Tests full transition through states: CREATED -> AUTHORIZED -> CAPTURED -> REFUNDED.
    Ensures 15% platform commission and NO sensitive card numbers stored.
    """
    token = gen_token(client, email="lifecycle_pay@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    dev_id, rep_id = create_test_device_and_repair(client, token)

    # 1. CREATE INTENT
    intent_res = client.post(
        "/api/v1/payments/create-intent",
        headers=headers,
        json={
            "repair_id": rep_id,
            "amount": 200.0,
            "currency": "USD",
            "payment_method_type": "card"
        }
    )
    assert intent_res.status_code == status.HTTP_201_CREATED, intent_res.text
    payment_data = intent_res.json()
    payment_id = payment_data["id"]

    assert payment_data["status"] == "CREATED"
    assert payment_data["amount"] == 200.0
    assert payment_data["platform_fee"] == 30.0  # 15% of 200
    assert payment_data["technician_payout"] == 170.0 # 85% of 200
    assert payment_data["invoice_reference"].startswith("INV-")
    assert payment_data["provider"] == "sandbox"
    # Verify NO card data stored
    assert "card_number" not in payment_data
    assert "cvv" not in payment_data

    # 2. AUTHORIZE PAYMENT (with Sandbox Token)
    auth_res = client.post(
        f"/api/v1/payments/{payment_id}/authorize",
        headers=headers,
        json={"sandbox_token": "tok_visa"}
    )
    assert auth_res.status_code == status.HTTP_200_OK
    auth_data = auth_res.json()
    assert auth_data["status"] == "AUTHORIZED"
    assert auth_data["card_brand"] == "Visa"
    assert auth_data["card_last4"] == "4242"
    assert auth_data["authorized_at"] is not None

    # 3. CAPTURE PAYMENT
    cap_res = client.post(
        f"/api/v1/payments/{payment_id}/capture",
        headers=headers,
        json={}
    )
    assert cap_res.status_code == status.HTTP_200_OK
    cap_data = cap_res.json()
    assert cap_data["status"] == "CAPTURED"
    assert cap_data["captured_at"] is not None

    # 4. CUSTOMER INVOICE VIEW
    invoice_res = client.get(f"/api/v1/payments/{payment_id}/invoice", headers=headers)
    assert invoice_res.status_code == status.HTTP_200_OK
    inv = invoice_res.json()
    assert inv["invoice_reference"] == payment_data["invoice_reference"]
    assert inv["status"] == "CAPTURED"
    assert inv["total_amount"] == 200.0
    assert inv["order_reference"] == f"REP-{rep_id:04d}"
    assert inv["is_sandbox"] is True
    assert len(inv["line_items"]) > 0

    # 5. REFUND PAYMENT (Admin role)
    admin_token = gen_token(client, email="admin_payer@example.com", role="admin")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    refund_res = client.post(
        f"/api/v1/payments/{payment_id}/refund",
        headers=admin_headers,
        json={"refund_amount": 200.0, "reason": "Warranty return approved"}
    )
    assert refund_res.status_code == status.HTTP_200_OK
    ref_data = refund_res.json()
    assert ref_data["status"] == "REFUNDED"
    assert ref_data["refunded_amount"] == 200.0
    assert ref_data["refunded_at"] is not None


def test_payment_failure_state(client):
    """
    Tests simulated failure leading to FAILED state.
    """
    token = gen_token(client, email="fail_pay@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    # Create intent
    intent_res = client.post(
        "/api/v1/payments/create-intent",
        headers=headers,
        json={
            "order_reference": "PO-TEST-01",
            "amount": 150.0,
            "currency": "USD"
        }
    )
    payment_id = intent_res.json()["id"]

    # Authorize with decline token
    auth_res = client.post(
        f"/api/v1/payments/{payment_id}/authorize",
        headers=headers,
        json={"sandbox_token": "tok_sandbox_decline"}
    )
    assert auth_res.status_code == status.HTTP_200_OK
    data = auth_res.json()
    assert data["status"] == "FAILED"
    assert "declined" in data["failure_reason"].lower()


def test_instant_checkout(client):
    """
    Tests one-step direct checkout endpoint for mobile.
    """
    token = gen_token(client, email="instant_pay@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    res = client.post(
        "/api/v1/payments/checkout",
        headers=headers,
        json={
            "order_reference": "PO-9941",
            "amount": 89.0,
            "currency": "USD",
            "sandbox_token": "tok_mastercard"
        }
    )
    assert res.status_code == status.HTTP_201_CREATED
    data = res.json()
    assert data["status"] == "CAPTURED"
    assert data["card_brand"] == "Mastercard"
    assert data["card_last4"] == "5555"
    assert data["amount"] == 89.0
