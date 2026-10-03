import pytest
from fastapi import status, Depends, APIRouter
from app.main import app
from app.api.deps import get_current_admin

def test_register_user_success(client):
    res = client.post(
        "/api/v1/auth/register",
        json={"email": "test@example.com", "password": "strongpassword", "role": "customer", "name": "Test User"}
    )
    assert res.status_code == status.HTTP_201_CREATED, res.text
    data = res.json()
    assert data["email"] == "test@example.com"
    assert data["role"] == "customer"

def test_register_duplicate_account(client):
    client.post(
        "/api/v1/auth/register",
        json={"email": "test@example.com", "password": "strongpassword", "role": "customer"}
    )
    res = client.post(
        "/api/v1/auth/register",
        json={"email": "test@example.com", "password": "strongpassword", "role": "customer"}
    )
    assert res.status_code == status.HTTP_400_BAD_REQUEST

def test_login_success(client):
    client.post(
        "/api/v1/auth/register",
        json={"email": "test@example.com", "password": "strongpassword", "role": "customer"}
    )
    res = client.post(
        "/api/v1/auth/login",
        data={"username": "test@example.com", "password": "strongpassword"}
    )
    assert res.status_code == status.HTTP_200_OK
    data = res.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_password(client):
    client.post(
        "/api/v1/auth/register",
        json={"email": "test@example.com", "password": "strongpassword", "role": "customer"}
    )
    res = client.post(
        "/api/v1/auth/login",
        data={"username": "test@example.com", "password": "wrongpassword"}
    )
    assert res.status_code == status.HTTP_401_UNAUTHORIZED

def test_unauthorized_endpoint_access(client):
    res = client.get("/api/v1/auth/me")
    assert res.status_code == status.HTTP_401_UNAUTHORIZED

def test_logout_revocation(client):
    client.post(
        "/api/v1/auth/register",
        json={"email": "test@example.com", "password": "strongpassword", "role": "customer"}
    )
    res = client.post(
        "/api/v1/auth/login",
        data={"username": "test@example.com", "password": "strongpassword"}
    )
    token = res.json()["access_token"]
    
    # logout
    res_logout = client.post("/api/v1/auth/logout", headers={"Authorization": f"Bearer {token}"})
    assert res_logout.status_code == status.HTTP_200_OK
    
    # Try fetching me
    res_me = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert res_me.status_code == status.HTTP_401_UNAUTHORIZED

def test_create_and_test_role_restriction(client):
    router = APIRouter()
    @router.get("/admin-only")
    def admin_only(current_user: dict = Depends(get_current_admin)):
        return {"success": True}
    
    app.include_router(router, prefix="/api/v1/test")
    
    client.post(
        "/api/v1/auth/register",
        json={"email": "customer@example.com", "password": "pw", "role": "customer"}
    )
    login_res = client.post(
        "/api/v1/auth/login",
        data={"username": "customer@example.com", "password": "pw"}
    )
    token = login_res.json()["access_token"]
    
    res = client.get("/api/v1/test/admin-only", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == status.HTTP_403_FORBIDDEN
