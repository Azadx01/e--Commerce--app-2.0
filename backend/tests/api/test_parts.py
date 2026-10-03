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


def test_list_parts_and_verify_required_fields(client):
    """
    Verify parts catalog returns parts with all required fields:
    name, SKU, manufacturer, condition, price, warranty, stock, seller, compatibility.
    """
    res = client.get("/api/v1/parts")
    assert res.status_code == status.HTTP_200_OK
    data = res.json()
    assert "items" in data
    assert "total" in data
    assert data["total"] > 0

    # Verify conditions present in catalog
    conditions = {item["condition"] for item in data["items"]}
    assert "OEM" in conditions
    assert "COMPATIBLE_THIRD_PARTY" in conditions
    assert "USED_TESTED" in conditions

    # Verify every part has required attributes
    for item in data["items"]:
        assert item["name"]
        assert item["sku"]
        assert item["manufacturer"]
        assert item["condition"] in ["OEM", "COMPATIBLE_THIRD_PARTY", "USED_TESTED"]
        assert item["price"] > 0
        assert item["warranty"]
        assert item["stock"] >= 0
        assert item["seller"]
        assert isinstance(item["compatibility"], list)
        assert len(item["compatibility"]) > 0


def test_device_model_compatibility_enforcement(client):
    """
    IMPORTANT: Do not recommend a part unless compatibility rules allow it.
    Verify device-model compatibility filtering strictly isolates compatible components.
    """
    # 1. Filter for Samsung Galaxy S23
    res_s23 = client.get("/api/v1/parts?device_model=Galaxy S23")
    assert res_s23.status_code == status.HTTP_200_OK
    s23_parts = res_s23.json()["items"]
    assert len(s23_parts) >= 3

    for part in s23_parts:
        # Must be compatible with Samsung
        brands = [c["brand"] for c in part["compatibility"] if c.get("brand")]
        assert "Samsung" in brands
        # Incompatible models must not be in this result
        assert "Pixel" not in part["name"]
        assert "MacBook" not in part["name"]

    # 2. Filter for Google Pixel 7 Pro
    res_p7p = client.get("/api/v1/parts?device_model=Pixel 7 Pro")
    assert res_p7p.status_code == status.HTTP_200_OK
    p7p_parts = res_p7p.json()["items"]
    assert len(p7p_parts) >= 2

    for part in p7p_parts:
        brands = [c["brand"] for c in part["compatibility"] if c.get("brand")]
        assert "Google" in brands
        assert "iPhone" not in part["name"]
        assert "Dell" not in part["name"]

    # 3. Filter for an unsupported / incompatible device model
    res_incompatible = client.get("/api/v1/parts?device_model=Nokia 3310 Vintage")
    assert res_incompatible.status_code == status.HTTP_200_OK
    data_incompatible = res_incompatible.json()
    assert data_incompatible["total"] == 0
    assert len(data_incompatible["items"]) == 0


def test_category_and_brand_filtering(client):
    # Laptop category only
    res = client.get("/api/v1/parts?device_category=laptop")
    assert res.status_code == status.HTTP_200_OK
    parts = res.json()["items"]
    assert len(parts) >= 2
    for part in parts:
        cats = [c["category"] for c in part["compatibility"] if c.get("category")]
        assert "laptop" in cats

    # Apple brand only
    res_apple = client.get("/api/v1/parts?device_brand=Apple")
    assert res_apple.status_code == status.HTTP_200_OK
    apple_parts = res_apple.json()["items"]
    assert len(apple_parts) >= 2
    for part in apple_parts:
        brands = [c["brand"] for c in part["compatibility"] if c.get("brand")]
        assert "Apple" in brands


def test_condition_filter(client):
    # OEM only
    res_oem = client.get("/api/v1/parts?condition=OEM")
    assert res_oem.status_code == status.HTTP_200_OK
    for item in res_oem.json()["items"]:
        assert item["condition"] == "OEM"

    # Compatible Third-Party only
    res_tp = client.get("/api/v1/parts?condition=COMPATIBLE_THIRD_PARTY")
    assert res_tp.status_code == status.HTTP_200_OK
    for item in res_tp.json()["items"]:
        assert item["condition"] == "COMPATIBLE_THIRD_PARTY"

    # Used Tested only
    res_used = client.get("/api/v1/parts?condition=USED_TESTED")
    assert res_used.status_code == status.HTTP_200_OK
    for item in res_used.json()["items"]:
        assert item["condition"] == "USED_TESTED"


def test_part_search_and_price_filter(client):
    # Search query
    res = client.get("/api/v1/parts?query=OLED")
    assert res.status_code == status.HTTP_200_OK
    items = res.json()["items"]
    assert len(items) > 0
    for item in items:
        text = f"{item['name']} {item['sku']} {item['manufacturer']} {item['description']}".lower()
        assert "oled" in text

    # Price range filter ($40 to $100)
    res_price = client.get("/api/v1/parts?min_price=40&max_price=100")
    assert res_price.status_code == status.HTTP_200_OK
    for item in res_price.json()["items"]:
        assert 40.0 <= item["price"] <= 100.0


def test_get_single_part_by_id(client):
    # List to get an ID
    res = client.get("/api/v1/parts?limit=1")
    first_part = res.json()["items"][0]
    part_id = first_part["id"]

    # Get by ID
    res_single = client.get(f"/api/v1/parts/{part_id}")
    assert res_single.status_code == status.HTTP_200_OK
    data = res_single.json()
    assert data["id"] == part_id
    assert data["sku"] == first_part["sku"]
    assert data["name"] == first_part["name"]

    # Non-existent ID returns 404
    res_404 = client.get("/api/v1/parts/999999")
    assert res_404.status_code == status.HTTP_404_NOT_FOUND


def test_create_spare_part_admin_only(client):
    admin_token = gen_token(client, email="admin_parts@revivo.internal", role="admin", name="Admin")
    cust_token = gen_token(client, email="cust_parts@revivo.internal", role="customer", name="Customer")

    payload = {
        "sku": "SKU-CUSTOM-BAT-001",
        "name": "Custom Precision Lithium Battery",
        "part_type": "Battery",
        "manufacturer": "AmpTech Precision",
        "condition": "OEM",
        "price": 59.99,
        "warranty": "1 year warranty",
        "stock": 40,
        "seller": "ReVivo Certified Supply",
        "compatibility": [
            {
                "category": "smartphone",
                "brand": "Google",
                "models": ["Pixel 8 Pro", "Pixel 8"],
                "notes": "Fast charging 30W compatible"
            }
        ],
        "description": "Premium replacement cell with temperature sensors."
    }

    # Customer cannot create parts
    res_cust = client.post("/api/v1/parts", headers={"Authorization": f"Bearer {cust_token}"}, json=payload)
    assert res_cust.status_code == status.HTTP_403_FORBIDDEN

    # Admin creates part successfully
    res_admin = client.post("/api/v1/parts", headers={"Authorization": f"Bearer {admin_token}"}, json=payload)
    assert res_admin.status_code == status.HTTP_201_CREATED
    created = res_admin.json()
    assert created["sku"] == payload["sku"]
    assert created["condition"] == "OEM"
    assert created["stock"] == 40
