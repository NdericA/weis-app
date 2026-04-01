from fastapi.testclient import TestClient

from app.main import app
from app.services.live_ops_service import live_ops_service


def test_healthcheck() -> None:
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_homepage_renders() -> None:
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert "WEIS" in response.text


def test_login_page_renders() -> None:
    client = TestClient(app)
    response = client.get("/login")
    assert response.status_code == 200
    assert "Login" in response.text


def test_signup_page_renders() -> None:
    client = TestClient(app)
    response = client.get("/signup")
    assert response.status_code == 200
    assert "Create your account" in response.text


def test_dashboard_page_renders() -> None:
    client = TestClient(app)
    response = client.get("/dashboard")
    assert response.status_code == 200
    assert "Redirecting to your dashboard" in response.text


def test_rider_dashboard_page_renders() -> None:
    client = TestClient(app)
    response = client.get("/dashboard/rider")
    assert response.status_code == 200
    assert "Rider dashboard" in response.text


def test_driver_dashboard_page_renders() -> None:
    client = TestClient(app)
    response = client.get("/dashboard/driver")
    assert response.status_code == 200
    assert "Driver dashboard" in response.text


def test_admin_dashboard_page_renders() -> None:
    client = TestClient(app)
    response = client.get("/dashboard/admin")
    assert response.status_code == 200
    assert "Admin dashboard" in response.text


def test_driver_review_page_renders() -> None:
    client = TestClient(app)
    response = client.get("/dashboard/driver-review")
    assert response.status_code == 200
    assert "Driver application review" in response.text


def test_driver_application_review_api_flow() -> None:
    client = TestClient(app)

    onboarding = client.post(
        "/api/v1/drivers/onboarding",
        json={
            "full_name": "Review Driver",
            "phone_number": "+237677001122",
            "license_number": "DL-CM-55555",
            "national_id_number": "CMR-55555",
            "vehicle_make": "Toyota",
            "vehicle_model": "Corolla",
            "vehicle_color": "Black",
            "plate_number": "LT-555-AA",
        },
    )
    assert onboarding.status_code == 200
    assert onboarding.json()["approval_status"] == "pending"

    applications = client.get("/api/v1/drivers/applications")
    assert applications.status_code == 200
    assert any(item["phone_number"] == "+237677001122" for item in applications.json())

    rejected = client.post(
        "/api/v1/drivers/applications/reject",
        json={
            "phone_number": "+237677001122",
            "reason": "Insurance document is missing.",
            "additional_info_required": True,
        },
    )
    assert rejected.status_code == 200
    assert rejected.json()["approval_status"] == "rejected"
    assert rejected.json()["rejection_reason"] == "Insurance document is missing."

    resubmitted = client.post(
        "/api/v1/drivers/applications/additional-info",
        json={
            "phone_number": "+237677001122",
            "additional_info": "Insurance certificate uploaded and plate photo updated.",
        },
    )
    assert resubmitted.status_code == 200
    assert resubmitted.json()["approval_status"] == "pending"

    approved = client.post(
        "/api/v1/drivers/applications/approve",
        json={
            "phone_number": "+237677001122",
            "reason": "",
            "additional_info_required": False,
        },
    )
    assert approved.status_code == 200
    assert approved.json()["approval_status"] == "approved"


def test_live_trip_flow_updates_all_stages() -> None:
    live_ops_service.reset()
    client = TestClient(app)

    estimate_response = client.post(
        "/api/v1/trips/estimate",
        json={
            "city": "Douala",
            "ride_type": "economy",
            "pickup_address": "Bonapriso, Douala",
            "destination_address": "Akwa, Douala",
            "distance_km": 6.4,
            "duration_minutes": 16,
            "surge_multiplier": 1.0,
        },
    )
    assert estimate_response.status_code == 200
    estimated_fare = estimate_response.json()["estimated_fare"]

    online_response = client.post(
        "/api/v1/live/driver-status",
        json={"driver_user_id": "driver-123", "status": "online"},
    )
    assert online_response.status_code == 200
    assert online_response.json()["driver_statuses"]["driver-123"] == "online"

    request_response = client.post(
        "/api/v1/live/request",
        json={
            "rider_id": "rider-123",
            "rider_name": "Test Rider",
            "pickup_address": "Bonapriso, Douala",
            "destination_address": "Akwa, Douala",
            "ride_type": "economy",
            "distance_km": 6.4,
            "duration_minutes": 16,
            "payment_method": "cash",
            "notes": "Meet by the gate",
            "estimated_fare": estimated_fare,
        },
    )
    assert request_response.status_code == 200
    assert request_response.json()["request"]["rider_name"] == "Test Rider"

    accept_response = client.post(
        "/api/v1/live/accept",
        json={
            "driver_user_id": "driver-123",
            "driver_name": "Live Driver",
            "vehicle_summary": "Black Toyota Corolla",
        },
    )
    assert accept_response.status_code == 200
    assert accept_response.json()["trip"]["stage"] == "accepted"
    assert accept_response.json()["trip"]["driver_name"] == "Live Driver"

    arrived_response = client.post("/api/v1/live/arrived", json={"driver_user_id": "driver-123"})
    assert arrived_response.status_code == 200
    assert arrived_response.json()["trip"]["stage"] == "driver_arrived"

    start_response = client.post("/api/v1/live/start", json={"driver_user_id": "driver-123"})
    assert start_response.status_code == 200
    assert start_response.json()["trip"]["stage"] == "on_trip"

    complete_response = client.post("/api/v1/live/complete", json={"driver_user_id": "driver-123"})
    assert complete_response.status_code == 200
    assert complete_response.json()["trip"]["stage"] == "completed"

    tip_response = client.post("/api/v1/live/tip", json={"amount": 1000})
    assert tip_response.status_code == 200
    assert tip_response.json()["confirmed_tip_amount"] == "1000"

    reply_response = client.post(
        "/api/v1/live/reply",
        json={"driver_user_id": "driver-123", "message": "Thank you for riding with WEIS."},
    )
    assert reply_response.status_code == 200
    assert reply_response.json()["driver_reply_sent"] == "Thank you for riding with WEIS."


def test_live_trip_flow_blocks_out_of_order_stage_updates() -> None:
    live_ops_service.reset()
    client = TestClient(app)

    client.post("/api/v1/live/driver-status", json={"driver_user_id": "driver-789", "status": "online"})
    client.post(
        "/api/v1/live/request",
        json={
            "rider_id": "rider-789",
            "rider_name": "Ordered Rider",
            "pickup_address": "Bonapriso, Douala",
            "destination_address": "Akwa, Douala",
            "ride_type": "economy",
            "distance_km": 6.4,
            "duration_minutes": 16,
            "payment_method": "cash",
            "notes": None,
            "estimated_fare": 3160,
        },
    )
    client.post(
        "/api/v1/live/accept",
        json={
            "driver_user_id": "driver-789",
            "driver_name": "Order Driver",
            "vehicle_summary": "Black Toyota Corolla",
        },
    )

    start_before_arrival = client.post("/api/v1/live/start", json={"driver_user_id": "driver-789"})
    assert start_before_arrival.status_code == 200
    assert start_before_arrival.json()["trip"]["stage"] == "accepted"

    complete_before_start = client.post("/api/v1/live/complete", json={"driver_user_id": "driver-789"})
    assert complete_before_start.status_code == 200
    assert complete_before_start.json()["trip"]["stage"] == "accepted"

    arrived_response = client.post("/api/v1/live/arrived", json={"driver_user_id": "driver-789"})
    assert arrived_response.json()["trip"]["stage"] == "driver_arrived"


def test_live_state_moves_driver_toward_pickup_and_dropoff() -> None:
    live_ops_service.reset()
    client = TestClient(app)

    client.post("/api/v1/live/driver-status", json={"driver_user_id": "driver-map", "status": "online"})
    client.post(
        "/api/v1/live/request",
        json={
            "rider_id": "rider-map",
            "rider_name": "Map Rider",
            "pickup_address": "Bonapriso, Douala",
            "destination_address": "Akwa, Douala",
            "ride_type": "economy",
            "distance_km": 6.4,
            "duration_minutes": 16,
            "payment_method": "cash",
            "notes": None,
            "estimated_fare": 3160,
        },
    )
    client.post(
        "/api/v1/live/accept",
        json={
            "driver_user_id": "driver-map",
            "driver_name": "Map Driver",
            "vehicle_summary": "Black Toyota Corolla",
        },
    )

    first_state = client.get("/api/v1/live/state").json()
    second_state = client.get("/api/v1/live/state").json()
    assert second_state["driver_position"] != first_state["driver_position"]

    while True:
        polled_state = client.get("/api/v1/live/state").json()
        if polled_state["arrival_ready"]:
            break

    assert polled_state["driver_position"] == polled_state["pickup_position"]

    client.post("/api/v1/live/arrived", json={"driver_user_id": "driver-map"})
    client.post("/api/v1/live/start", json={"driver_user_id": "driver-map"})
    trip_state_before = client.get("/api/v1/live/state").json()
    trip_state_after = client.get("/api/v1/live/state").json()
    assert trip_state_after["driver_position"] != trip_state_before["driver_position"]
    assert trip_state_after["rider_position"] == trip_state_after["driver_position"]


def test_live_messages_allowed_before_pickup_only() -> None:
    live_ops_service.reset()
    client = TestClient(app)

    client.post("/api/v1/live/driver-status", json={"driver_user_id": "driver-chat", "status": "online"})
    client.post(
        "/api/v1/live/request",
        json={
            "rider_id": "rider-chat",
            "rider_name": "Chat Rider",
            "pickup_address": "Bonapriso, Douala",
            "destination_address": "Akwa, Douala",
            "ride_type": "economy",
            "distance_km": 6.4,
            "duration_minutes": 16,
            "payment_method": "cash",
            "notes": None,
            "estimated_fare": 3160,
        },
    )

    request_message = client.post(
        "/api/v1/live/message",
        json={
            "sender_id": "rider-chat",
            "sender_role": "rider",
            "sender_name": "Chat Rider",
            "message": "I am at the main gate.",
        },
    )
    assert request_message.status_code == 200
    assert len(request_message.json()["messages"]) == 1

    client.post(
        "/api/v1/live/accept",
        json={
            "driver_user_id": "driver-chat",
            "driver_name": "Chat Driver",
            "vehicle_summary": "Black Toyota Corolla",
        },
    )

    accepted_message = client.post(
        "/api/v1/live/message",
        json={
            "sender_id": "driver-chat",
            "sender_role": "driver",
            "sender_name": "Chat Driver",
            "message": "I am two minutes away.",
        },
    )
    assert accepted_message.status_code == 200
    assert len(accepted_message.json()["messages"]) == 2

    client.post("/api/v1/live/arrived", json={"driver_user_id": "driver-chat"})
    client.post("/api/v1/live/start", json={"driver_user_id": "driver-chat"})

    on_trip_message = client.post(
        "/api/v1/live/message",
        json={
            "sender_id": "driver-chat",
            "sender_role": "driver",
            "sender_name": "Chat Driver",
            "message": "This should not send during the trip.",
        },
    )
    assert on_trip_message.status_code == 200
    assert len(on_trip_message.json()["messages"]) == 2
