import pytest
from fastapi import status

# Helper function to register and login user to get token
def gen_token(client, email="user@example.com"):
    client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "password", "role": "customer", "name": "Customer User"}
    )
    res = client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": "password"}
    )
    return res.json()["access_token"]


def test_create_device(client):
    token = gen_token(client)
    res = client.post(
        "/api/v1/devices",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "category": "smartphone",
            "brand": "Apple",
            "model": "iPhone 13",
            "serial_number": "IM-1234567890",
            "condition": "Screen cracked"
        }
    )
    assert res.status_code == status.HTTP_201_CREATED
    data = res.json()
    assert data["brand"] == "Apple"
    assert "serial_number_hash" not in data # Secure payload assertion


def test_create_device_unsupported_category(client):
    token = gen_token(client)
    res = client.post(
        "/api/v1/devices",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "category": "television", # Rejected by MVP constraint
            "brand": "Samsung",
            "model": "Smart TV"
        }
    )
    assert res.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_read_devices_isolation(client):
    token1 = gen_token(client, "user1@example.com")
    token2 = gen_token(client, "user2@example.com")
    
    # User 1 creates device
    client.post("/api/v1/devices", headers={"Authorization": f"Bearer {token1}"}, json={"category": "laptop", "brand": "Dell", "model": "XPS"})
    
    # User 2 creates 2 devices
    client.post("/api/v1/devices", headers={"Authorization": f"Bearer {token2}"}, json={"category": "smartphone", "brand": "Samsung", "model": "Galaxy S22"})
    client.post("/api/v1/devices", headers={"Authorization": f"Bearer {token2}"}, json={"category": "laptop", "brand": "Lenovo", "model": "Thinkpad"})
    
    # Checks
    res1 = client.get("/api/v1/devices", headers={"Authorization": f"Bearer {token1}"})
    assert len(res1.json()) == 1
    
    res2 = client.get("/api/v1/devices", headers={"Authorization": f"Bearer {token2}"})
    assert len(res2.json()) == 2


def test_read_others_device_fails(client):
    token1 = gen_token(client, "user1@example.com")
    token2 = gen_token(client, "user2@example.com")
    
    res_create = client.post("/api/v1/devices", headers={"Authorization": f"Bearer {token1}"}, json={"category": "laptop", "brand": "HP", "model": "Spectre"})
    device_id = res_create.json()["id"]
    
    # User 2 trying to read User 1's device
    res_read = client.get(f"/api/v1/devices/{device_id}", headers={"Authorization": f"Bearer {token2}"})
    assert res_read.status_code == status.HTTP_403_FORBIDDEN


def test_modify_delete_own_device(client):
    token = gen_token(client)
    res = client.post("/api/v1/devices", headers={"Authorization": f"Bearer {token}"}, json={"category": "smartphone", "brand": "Google", "model": "Pixel 7"})
    device_id = res.json()["id"]
    
    res_patch = client.patch(
        f"/api/v1/devices/{device_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"condition": "Battery degraded"}
    )
    assert res_patch.status_code == status.HTTP_200_OK
    assert res_patch.json()["condition"] == "Battery degraded"
    
    res_del = client.delete(f"/api/v1/devices/{device_id}", headers={"Authorization": f"Bearer {token}"})
    assert res_del.status_code == status.HTTP_200_OK
    
    # Check it's gone
    res_check = client.get(f"/api/v1/devices/{device_id}", headers={"Authorization": f"Bearer {token}"})
    assert res_check.status_code == status.HTTP_404_NOT_FOUND
