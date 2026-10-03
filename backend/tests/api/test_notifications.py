import pytest
from fastapi import status

def gen_token(client, email="notify_user@example.com", role="customer"):
    client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "password", "role": role, "name": "Notify User"}
    )
    res = client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": "password"}
    )
    return res.json()["access_token"]


def test_trigger_all_10_events(client):
    token = gen_token(client, email="events_tester@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    events = [
        ("REPAIR_REQUEST_CREATED", "Repair Request Created"),
        ("TECHNICIAN_ACCEPTED", "Technician Assigned"),
        ("QUOTE_RECEIVED", "New Repair Quote Ready"),
        ("QUOTE_APPROVED", "Quote Approved by Customer"),
        ("REPAIR_STARTED", "Repair Started"),
        ("PARTS_REQUIRED", "Replacement Parts Ordered"),
        ("REPAIR_COMPLETED", "Repair Completed & QA Passed"),
        ("WARRANTY_STARTED", "Warranty Protection Activated"),
        ("RESALE_QUOTE_AVAILABLE", "Resale Valuation Ready"),
        ("RESALE_STATUS_CHANGED", "Resale Status Updated"),
    ]

    for event_type, expected_title in events:
        res = client.post(
            "/api/v1/notifications/test-event",
            headers=headers,
            json={
                "event_type": event_type,
                "device_name": "Samsung Galaxy S23",
                "technician_name": "Bob's Micro Repairs",
                "amount": 220.0,
                "part_name": "AMOLED Screen Assembly"
            }
        )
        assert res.status_code == status.HTTP_201_CREATED, f"Failed for {event_type}: {res.text}"
        data = res.json()
        assert data["event_type"] == event_type
        assert data["title"] == expected_title
        assert data["is_read"] is False

    # Check unread count is 10
    count_res = client.get("/api/v1/notifications/unread-count", headers=headers)
    assert count_res.status_code == status.HTTP_200_OK
    assert count_res.json()["unread_count"] == 10

    # List all notifications
    list_res = client.get("/api/v1/notifications", headers=headers)
    assert list_res.status_code == status.HTTP_200_OK
    list_data = list_res.json()
    assert list_data["total"] == 10
    assert list_data["unread_count"] == 10


def test_mark_as_read_and_read_all(client):
    token = gen_token(client, email="reader_user@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    # Trigger 3 events
    for evt in ["REPAIR_REQUEST_CREATED", "TECHNICIAN_ACCEPTED", "QUOTE_RECEIVED"]:
        client.post(
            "/api/v1/notifications/test-event",
            headers=headers,
            json={"event_type": evt, "device_name": "Dell XPS 13"}
        )

    # List items to get an ID
    list_res = client.get("/api/v1/notifications", headers=headers)
    items = list_res.json()["items"]
    assert len(items) == 3
    first_id = items[0]["id"]

    # Mark first as read
    patch_res = client.patch(f"/api/v1/notifications/{first_id}/read", headers=headers)
    assert patch_res.status_code == status.HTTP_200_OK
    assert patch_res.json()["is_read"] is True

    # Check unread count is 2
    count_res = client.get("/api/v1/notifications/unread-count", headers=headers)
    assert count_res.json()["unread_count"] == 2

    # Filter by is_read=False
    unread_res = client.get("/api/v1/notifications?is_read=false", headers=headers)
    assert unread_res.json()["total"] == 2

    # Mark all as read
    read_all_res = client.post("/api/v1/notifications/read-all", headers=headers)
    assert read_all_res.status_code == status.HTTP_200_OK

    # Check unread count is 0
    count_res2 = client.get("/api/v1/notifications/unread-count", headers=headers)
    assert count_res2.json()["unread_count"] == 0


def test_delete_notification(client):
    token = gen_token(client, email="deleter_user@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    res = client.post(
        "/api/v1/notifications/test-event",
        headers=headers,
        json={"event_type": "WARRANTY_STARTED", "device_name": "iPad Pro"}
    )
    notif_id = res.json()["id"]

    # Delete it
    del_res = client.delete(f"/api/v1/notifications/{notif_id}", headers=headers)
    assert del_res.status_code == status.HTTP_204_NO_CONTENT

    # Verify not found now
    del_res2 = client.delete(f"/api/v1/notifications/{notif_id}", headers=headers)
    assert del_res2.status_code == status.HTTP_404_NOT_FOUND
