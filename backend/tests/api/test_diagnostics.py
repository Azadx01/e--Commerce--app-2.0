import pytest
from fastapi import status

# Helper function to register and login user to get token
def gen_token(client, email="customer@revivo.internal"):
    client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "securepassword", "role": "customer", "name": "Diagnostic Customer"}
    )
    res = client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": "securepassword"}
    )
    return res.json()["access_token"]


def test_create_diagnostic_battery_symptom(client):
    token = gen_token(client)
    res = client.post(
        "/api/v1/diagnostics",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "selected_symptoms": ["Battery"],
            "reported_problem": "Battery percentage drops rapidly and dies within two hours."
        }
    )
    assert res.status_code == status.HTTP_201_CREATED
    data = res.json()
    assert "id" in data
    assert data["selected_symptoms"] == ["Battery"]
    assert "Battery" in data["possible_issue"]
    assert data["estimated_severity"] in ["Medium", "High"]
    assert len(data["recommended_next_action"]) > 0
    assert 0.0 < data["confidence"] < 1.0  # Must not claim 100% certainty
    assert data["requirement_for_technician_inspection"] is True
    assert "engine_version" in data
    assert "disclaimer" in data
    assert "diagnosis_result" in data


def test_create_diagnostic_all_allowed_symptoms(client):
    allowed = [
        "Battery", "Screen", "Charging", "Heating", "Performance",
        "Keyboard", "Camera", "Speaker", "Network", "Other"
    ]
    for symptom in allowed:
        res = client.post(
            "/api/v1/diagnostics",
            json={
                "selected_symptoms": [symptom.lower()],  # Test case-insensitivity
                "reported_problem": f"Testing symptom {symptom}"
            }
        )
        assert res.status_code == status.HTTP_201_CREATED
        data = res.json()
        assert data["selected_symptoms"] == [symptom]
        assert "possible_issue" in data
        assert "estimated_severity" in data
        assert "recommended_next_action" in data
        assert "confidence" in data
        assert "requirement_for_technician_inspection" in data


def test_create_diagnostic_invalid_symptom(client):
    res = client.post(
        "/api/v1/diagnostics",
        json={
            "selected_symptoms": ["RocketBoosterMalfunction"],
            "reported_problem": "Something totally out of scope"
        }
    )
    assert res.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_create_diagnostic_empty_symptoms_fails(client):
    res = client.post(
        "/api/v1/diagnostics",
        json={
            "selected_symptoms": [],
            "reported_problem": "Nothing selected"
        }
    )
    assert res.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_create_diagnostic_with_device_and_images(client):
    token = gen_token(client, "device_owner@example.com")
    
    # 1. Create a device
    dev_res = client.post(
        "/api/v1/devices",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "category": "smartphone",
            "brand": "Samsung",
            "model": "Galaxy S21"
        }
    )
    assert dev_res.status_code == status.HTTP_201_CREATED
    device_id = dev_res.json()["id"]

    # 2. Run diagnostic linked to device with optional images
    res = client.post(
        "/api/v1/diagnostics",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "device_id": device_id,
            "selected_symptoms": ["Screen"],
            "reported_problem": "Screen shattered after dropping, glass is cracked with lines.",
            "image_references": [
                "https://storage.example.com/revivo/screen_crack1.jpg",
                "https://storage.example.com/revivo/screen_crack2.jpg"
            ]
        }
    )
    assert res.status_code == status.HTTP_201_CREATED
    data = res.json()
    assert data["device_id"] == device_id
    assert len(data["image_references"]) == 2
    assert "Display" in data["possible_issue"] or "Screen" in data["possible_issue"]
    assert data["estimated_severity"] in ["High", "Medium"]
    assert data["requirement_for_technician_inspection"] is True


def test_create_diagnostic_device_not_found(client):
    res = client.post(
        "/api/v1/diagnostics",
        json={
            "device_id": 999999,
            "selected_symptoms": ["Screen"]
        }
    )
    assert res.status_code == status.HTTP_404_NOT_FOUND


def test_critical_hazards_detection(client):
    # Test liquid damage detection
    res_liquid = client.post(
        "/api/v1/diagnostics",
        json={
            "selected_symptoms": ["Charging"],
            "reported_problem": "Phone fell into the bathtub water and now won't turn on or charge"
        }
    )
    assert res_liquid.status_code == status.HTTP_201_CREATED
    data_liquid = res_liquid.json()
    assert data_liquid["estimated_severity"] == "Critical"
    assert "Liquid" in data_liquid["possible_issue"] or "Corrosion" in data_liquid["possible_issue"]
    assert data_liquid["requirement_for_technician_inspection"] is True

    # Test fire / smoke / swelling detection
    res_smoke = client.post(
        "/api/v1/diagnostics",
        json={
            "selected_symptoms": ["Battery", "Heating"],
            "reported_problem": "The battery is swollen, bulging, and there is a burning smell and smoke."
        }
    )
    assert res_smoke.status_code == status.HTTP_201_CREATED
    data_smoke = res_smoke.json()
    assert data_smoke["estimated_severity"] == "Critical"
    assert data_smoke["requirement_for_technician_inspection"] is True


def test_compound_symptoms_rule(client):
    # Battery + Heating
    res = client.post(
        "/api/v1/diagnostics",
        json={
            "selected_symptoms": ["Battery", "Heating"],
            "reported_problem": "Phone heats up significantly while discharging quickly."
        }
    )
    assert res.status_code == status.HTTP_201_CREATED
    data = res.json()
    assert data["estimated_severity"] == "High"
    assert "Thermal" in data["possible_issue"] or "Battery" in data["possible_issue"]

    # Battery + Charging
    res_bc = client.post(
        "/api/v1/diagnostics",
        json={
            "selected_symptoms": ["Battery", "Charging"],
            "reported_problem": "Won't hold a charge and the charging icon flickers."
        }
    )
    assert res_bc.status_code == status.HTTP_201_CREATED
    assert res_bc.json()["requirement_for_technician_inspection"] is True


def test_get_diagnostic_by_id(client):
    create_res = client.post(
        "/api/v1/diagnostics",
        json={
            "selected_symptoms": ["Camera"],
            "reported_problem": "Back camera lens is vibrating and blurry."
        }
    )
    assert create_res.status_code == status.HTTP_201_CREATED
    diagnostic_id = create_res.json()["id"]

    get_res = client.get(f"/api/v1/diagnostics/{diagnostic_id}")
    assert get_res.status_code == status.HTTP_200_OK
    get_data = get_res.json()
    assert get_data["id"] == diagnostic_id
    assert get_data["selected_symptoms"] == ["Camera"]
    assert "Camera" in get_data["possible_issue"] or "Sensor" in get_data["possible_issue"]
    assert "recommended_next_action" in get_data
    assert "confidence" in get_data
    assert "requirement_for_technician_inspection" in get_data
    assert "engine_version" in get_data


def test_get_diagnostic_not_found(client):
    res = client.get("/api/v1/diagnostics/999999")
    assert res.status_code == status.HTTP_404_NOT_FOUND


def test_device_isolation_on_diagnostics(client):
    token1 = gen_token(client, "user1@revivo.internal")
    token2 = gen_token(client, "user2@revivo.internal")

    # User 1 registers device
    dev_res = client.post(
        "/api/v1/devices",
        headers={"Authorization": f"Bearer {token1}"},
        json={"category": "laptop", "brand": "Apple", "model": "MacBook Pro"}
    )
    dev1_id = dev_res.json()["id"]

    # User 2 tries to run diagnosis on User 1's device
    bad_diag = client.post(
        "/api/v1/diagnostics",
        headers={"Authorization": f"Bearer {token2}"},
        json={"device_id": dev1_id, "selected_symptoms": ["Keyboard"]}
    )
    assert bad_diag.status_code == status.HTTP_403_FORBIDDEN

    # User 1 creates diagnostic successfully
    ok_diag = client.post(
        "/api/v1/diagnostics",
        headers={"Authorization": f"Bearer {token1}"},
        json={"device_id": dev1_id, "selected_symptoms": ["Keyboard"]}
    )
    assert ok_diag.status_code == status.HTTP_201_CREATED
    diag_id = ok_diag.json()["id"]

    # User 2 tries to read User 1's diagnostic
    read_diag = client.get(
        f"/api/v1/diagnostics/{diag_id}",
        headers={"Authorization": f"Bearer {token2}"}
    )
    assert read_diag.status_code == status.HTTP_403_FORBIDDEN


def test_no_guaranteed_diagnosis_disclaimer(client):
    res = client.post(
        "/api/v1/diagnostics",
        json={"selected_symptoms": ["Performance"], "reported_problem": "Apps opening slowly"}
    )
    assert res.status_code == status.HTTP_201_CREATED
    data = res.json()
    assert "disclaimer" in data
    # Ensure disclaimer does not claim absolute certainty
    assert "guaranteed" not in data["disclaimer"].lower() or "not" in data["disclaimer"].lower()
    assert data["confidence"] <= 0.95
