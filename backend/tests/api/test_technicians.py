import pytest
from fastapi import status
from app.core.config import settings

def gen_token(client, email="customer@revivo.internal", role="customer", name="Test User"):
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


def test_technician_update_profile_and_cannot_self_verify(client):
    tech_token = gen_token(client, email="tech1@revivo.internal", role="technician", name="Alex Tech")
    
    # Update profile
    res = client.patch(
        "/api/v1/technicians/profile",
        headers={"Authorization": f"Bearer {tech_token}"},
        json={
            "business_name": "Apex Device Repairs",
            "bio": "Expert in Apple and Samsung board repairs.",
            "phone": "+1-555-0199",
            "years_of_experience": 6,
            "skills": ["Screen Replacement", "Battery Replacement", "Micro-soldering"],
            "device_categories": ["smartphone", "laptop"],
            "service_area": "Austin, TX",
            "service_radius_km": 30.0,
            "availability": "available",
            "hourly_rate": 65.0,
            "verification_status": "verified"  # Malicious attempt to self-verify
        }
    )
    assert res.status_code == status.HTTP_200_OK
    data = res.json()
    assert data["business_name"] == "Apex Device Repairs"
    assert data["skills"] == ["Screen Replacement", "Battery Replacement", "Micro-soldering"]
    assert data["device_categories"] == ["smartphone", "laptop"]
    assert data["service_area"] == "Austin, TX"
    assert data["verification_status"] == "pending"  # Self-verification must be ignored/prevented


def test_customer_cannot_update_technician_profile(client):
    cust_token = gen_token(client, email="customer1@revivo.internal", role="customer", name="Customer One")
    res = client.patch(
        "/api/v1/technicians/profile",
        headers={"Authorization": f"Bearer {cust_token}"},
        json={"business_name": "Should Fail"}
    )
    assert res.status_code == status.HTTP_403_FORBIDDEN


def test_admin_verification_flow(client):
    tech_token = gen_token(client, email="tech2@revivo.internal", role="technician", name="Sam Specialist")
    admin_token = gen_token(client, email="admin@revivo.internal", role="admin", name="Admin User")
    
    # Tech creates profile
    prof_res = client.patch(
        "/api/v1/technicians/profile",
        headers={"Authorization": f"Bearer {tech_token}"},
        json={"business_name": "Sam Repairs", "service_area": "San Francisco, CA"}
    )
    tech_id = prof_res.json()["id"]

    # Customer tries to verify tech -> 403
    cust_token = gen_token(client, email="cust_hacker@revivo.internal", role="customer", name="Hacker")
    cust_verify = client.patch(
        f"/api/v1/technicians/{tech_id}/verify",
        headers={"Authorization": f"Bearer {cust_token}"},
        json={"verification_status": "verified"}
    )
    assert cust_verify.status_code == status.HTTP_403_FORBIDDEN

    # Admin verifies tech -> 200
    admin_verify = client.patch(
        f"/api/v1/technicians/{tech_id}/verify",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"verification_status": "verified"}
    )
    assert admin_verify.status_code == status.HTTP_200_OK
    assert admin_verify.json()["verification_status"] == "verified"


def test_customer_only_sees_verified_technicians(client):
    admin_token = gen_token(client, email="admin_market@revivo.internal", role="admin", name="Market Admin")
    
    # Tech 1: Verified
    t1_token = gen_token(client, email="tech_v1@revivo.internal", role="technician", name="Verified Tech")
    t1_res = client.patch(
        "/api/v1/technicians/profile",
        headers={"Authorization": f"Bearer {t1_token}"},
        json={"business_name": "Verified Pro", "service_area": "Seattle, WA"}
    )
    t1_id = t1_res.json()["id"]
    client.patch(
        f"/api/v1/technicians/{t1_id}/verify",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"verification_status": "verified"}
    )

    # Tech 2: Unverified / Pending
    t2_token = gen_token(client, email="tech_pending@revivo.internal", role="technician", name="Pending Tech")
    client.patch(
        "/api/v1/technicians/profile",
        headers={"Authorization": f"Bearer {t2_token}"},
        json={"business_name": "Unverified Beginner", "service_area": "Seattle, WA"}
    )

    # Customer searches -> should only see Verified Tech
    cust_token = gen_token(client, email="search_cust@revivo.internal", role="customer", name="Searcher")
    res = client.get("/api/v1/technicians", headers={"Authorization": f"Bearer {cust_token}"})
    assert res.status_code == status.HTTP_200_OK
    data = res.json()
    
    business_names = [t["business_name"] for t in data]
    assert "Verified Pro" in business_names
    assert "Unverified Beginner" not in business_names


def test_technician_marketplace_filters(client):
    admin_token = gen_token(client, email="admin_filter@revivo.internal", role="admin", name="Admin Filters")

    # Create Tech A: Laptop + Micro-soldering + Chicago + 4.9 rating + available
    ta_token = gen_token(client, email="tech_a@revivo.internal", role="technician", name="Tech A")
    ta_res = client.patch(
        "/api/v1/technicians/profile",
        headers={"Authorization": f"Bearer {ta_token}"},
        json={
            "business_name": "Chicago Laptop Labs",
            "skills": ["Micro-soldering", "Liquid Damage"],
            "device_categories": ["laptop"],
            "service_area": "Chicago, IL",
            "availability": "available",
        }
    )
    ta_id = ta_res.json()["id"]
    client.patch(f"/api/v1/technicians/{ta_id}/verify", headers={"Authorization": f"Bearer {admin_token}"}, json={"verification_status": "verified"})

    # Create Tech B: Smartphone + Screen Replacement + Miami + busy
    tb_token = gen_token(client, email="tech_b@revivo.internal", role="technician", name="Tech B")
    tb_res = client.patch(
        "/api/v1/technicians/profile",
        headers={"Authorization": f"Bearer {tb_token}"},
        json={
            "business_name": "Miami Screen Repair",
            "skills": ["Screen Replacement", "Battery Replacement"],
            "device_categories": ["smartphone"],
            "service_area": "Miami, FL",
            "availability": "busy",
        }
    )
    tb_id = tb_res.json()["id"]
    client.patch(f"/api/v1/technicians/{tb_id}/verify", headers={"Authorization": f"Bearer {admin_token}"}, json={"verification_status": "verified"})

    # 1. Filter by device_category=laptop
    res_cat = client.get("/api/v1/technicians?device_category=laptop")
    names_cat = [t["business_name"] for t in res_cat.json()]
    assert "Chicago Laptop Labs" in names_cat
    assert "Miami Screen Repair" not in names_cat

    # 2. Filter by specialization=Screen
    res_spec = client.get("/api/v1/technicians?specialization=Screen")
    names_spec = [t["business_name"] for t in res_spec.json()]
    assert "Miami Screen Repair" in names_spec
    assert "Chicago Laptop Labs" not in names_spec

    # 3. Filter by service_area=Chicago
    res_area = client.get("/api/v1/technicians?service_area=Chicago")
    names_area = [t["business_name"] for t in res_area.json()]
    assert "Chicago Laptop Labs" in names_area
    assert "Miami Screen Repair" not in names_area

    # 4. Filter by availability=available
    res_avail = client.get("/api/v1/technicians?availability=available")
    names_avail = [t["business_name"] for t in res_avail.json()]
    assert "Chicago Laptop Labs" in names_avail
    assert "Miami Screen Repair" not in names_avail

    # 5. Filter by rating
    res_rating = client.get("/api/v1/technicians?rating=4.5")
    assert res_rating.status_code == status.HTTP_200_OK


def test_get_technician_by_id_visibility(client):
    admin_token = gen_token(client, email="admin_vis@revivo.internal", role="admin", name="Admin Vis")
    tech_token = gen_token(client, email="tech_hidden@revivo.internal", role="technician", name="Hidden Tech")
    cust_token = gen_token(client, email="cust_view@revivo.internal", role="customer", name="Customer Viewer")

    # Create unverified technician
    prof_res = client.patch(
        "/api/v1/technicians/profile",
        headers={"Authorization": f"Bearer {tech_token}"},
        json={"business_name": "Secret Lab", "service_area": "Denver, CO"}
    )
    tech_id = prof_res.json()["id"]

    # Customer viewing unverified technician -> 404 (hidden)
    res_cust = client.get(f"/api/v1/technicians/{tech_id}", headers={"Authorization": f"Bearer {cust_token}"})
    assert res_cust.status_code == status.HTTP_404_NOT_FOUND

    # Tech viewing their own profile -> 200
    res_self = client.get(f"/api/v1/technicians/{tech_id}", headers={"Authorization": f"Bearer {tech_token}"})
    assert res_self.status_code == status.HTTP_200_OK
    assert res_self.json()["business_name"] == "Secret Lab"

    # Admin viewing unverified tech -> 200
    res_admin = client.get(f"/api/v1/technicians/{tech_id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert res_admin.status_code == status.HTTP_200_OK

    # Once verified, customer can view -> 200
    client.patch(
        f"/api/v1/technicians/{tech_id}/verify",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"verification_status": "verified"}
    )
    res_cust_now = client.get(f"/api/v1/technicians/{tech_id}", headers={"Authorization": f"Bearer {cust_token}"})
    assert res_cust_now.status_code == status.HTTP_200_OK
    assert res_cust_now.json()["verification_status"] == "verified"
