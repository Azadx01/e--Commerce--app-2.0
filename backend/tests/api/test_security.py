import pytest
from fastapi import status
from app.main import app

def test_customer_cannot_register_as_admin(client):
    """
    Verify role escalation prevention: public registration cannot create admin accounts.
    """
    res = client.post(
        "/api/v1/auth/register",
        json={
            "email": "hacker_admin@example.com",
            "password": "Password123!",
            "name": "Attacker",
            "role": "admin"
        }
    )
    assert res.status_code == status.HTTP_403_FORBIDDEN
    assert "administrative role" in res.json()["detail"]

def test_customer_a_cannot_access_customer_b_device(client):
    """
    Verify Customer A cannot view, update, delete, or fetch passport of Customer B's device.
    """
    # 1. Register and login Customer B
    client.post("/api/v1/auth/register", json={"email": "custB@example.com", "password": "pass", "role": "customer"})
    token_b = client.post("/api/v1/auth/login", data={"username": "custB@example.com", "password": "pass"}).json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    dev_res = client.post(
        "/api/v1/devices",
        json={"category": "smartphone", "brand": "Apple", "model": "iPhone 15 Pro", "serial_number": "SN_B_123"},
        headers=headers_b
    )
    assert dev_res.status_code == status.HTTP_201_CREATED
    dev_b_id = dev_res.json()["id"]

    # 2. Register and login Customer A
    client.post("/api/v1/auth/register", json={"email": "custA@example.com", "password": "pass", "role": "customer"})
    token_a = client.post("/api/v1/auth/login", data={"username": "custA@example.com", "password": "pass"}).json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Attempt to read Customer B's device
    res_read = client.get(f"/api/v1/devices/{dev_b_id}", headers=headers_a)
    assert res_read.status_code == status.HTTP_403_FORBIDDEN

    # Attempt to read Customer B's device passport
    res_pass = client.get(f"/api/v1/devices/{dev_b_id}/passport", headers=headers_a)
    assert res_pass.status_code == status.HTTP_403_FORBIDDEN

    # Attempt to update Customer B's device
    res_update = client.patch(f"/api/v1/devices/{dev_b_id}", json={"brand": "Tampered"}, headers=headers_a)
    assert res_update.status_code == status.HTTP_403_FORBIDDEN

    # Attempt to delete Customer B's device
    res_delete = client.delete(f"/api/v1/devices/{dev_b_id}", headers=headers_a)
    assert res_delete.status_code == status.HTTP_403_FORBIDDEN

def test_technician_cannot_access_unrelated_customer_data(client):
    """
    Verify Technician cannot access unrelated customer device passports, quotes, or payments.
    """
    # 1. Create Customer and device
    client.post("/api/v1/auth/register", json={"email": "victim_cust@example.com", "password": "pass", "role": "customer"})
    token_c = client.post("/api/v1/auth/login", data={"username": "victim_cust@example.com", "password": "pass"}).json()["access_token"]
    headers_c = {"Authorization": f"Bearer {token_c}"}

    dev_res = client.post(
        "/api/v1/devices",
        json={"category": "laptop", "brand": "Dell", "model": "XPS 15", "serial_number": "SN_XPS_999"},
        headers=headers_c
    )
    dev_id = dev_res.json()["id"]

    # 2. Create unrelated technician
    client.post("/api/v1/auth/register", json={"email": "unrelated_tech@example.com", "password": "pass", "role": "technician"})
    token_t = client.post("/api/v1/auth/login", data={"username": "unrelated_tech@example.com", "password": "pass"}).json()["access_token"]
    headers_t = {"Authorization": f"Bearer {token_t}"}

    # Unrelated technician tries to view customer device passport
    res_pass = client.get(f"/api/v1/devices/{dev_id}/passport", headers=headers_t)
    assert res_pass.status_code == status.HTTP_403_FORBIDDEN
    assert "assigned customer devices" in res_pass.json()["detail"]

def test_customer_cannot_access_admin_apis(client):
    """
    Verify standard customer cannot access administrative endpoints.
    """
    client.post("/api/v1/auth/register", json={"email": "standard_user@example.com", "password": "pass", "role": "customer"})
    token = client.post("/api/v1/auth/login", data={"username": "standard_user@example.com", "password": "pass"}).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. ML Retrain endpoint (Admin only)
    res_ml = client.post("/api/v1/ml/train", headers=headers)
    assert res_ml.status_code == status.HTTP_403_FORBIDDEN

    # 2. Technician Admin Verification endpoint (Admin only)
    res_tech_verify = client.patch(
        "/api/v1/technicians/1/verify",
        json={"verification_status": "verified"},
        headers=headers
    )
    assert res_tech_verify.status_code == status.HTTP_403_FORBIDDEN

    # 3. Create Spare Part (Supplier / Admin only)
    res_part = client.post(
        "/api/v1/parts",
        json={
            "sku": "SEC-PART-01",
            "name": "Unauthorized Part",
            "part_type": "Screen",
            "manufacturer": "OEM",
            "condition": "OEM",
            "price": 100.0,
            "warranty": "90 days",
            "stock": 10,
            "seller": "Apex",
            "compatibility": [{"category": "smartphone", "brand": "Apple"}]
        },
        headers=headers
    )
    assert res_part.status_code == status.HTTP_403_FORBIDDEN

def test_security_headers_present_on_responses(client):
    """
    Verify security headers (X-Content-Type-Options, X-Frame-Options, X-XSS-Protection) are sent.
    """
    res = client.get("/api/v1/health")
    assert res.status_code == status.HTTP_200_OK
    assert res.headers.get("X-Content-Type-Options") == "nosniff"
    assert res.headers.get("X-Frame-Options") == "DENY"
    assert res.headers.get("X-XSS-Protection") == "1; mode=block"
    assert "Referrer-Policy" in res.headers
