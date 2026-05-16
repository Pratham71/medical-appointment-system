from datetime import date

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.backend.app.core.config import Settings
from app.backend.app.core.security_controls import FixedWindowRateLimiter, LoginAttemptTracker
from app.backend.app.main import app
from app.backend.app.schemas.appointment import AppointmentBookResponse
from app.backend.app.schemas.auth import AuthenticatedUser
from app.backend.app.schemas.student import StudentDashboard
from app.backend.app.services import (
    appointment_service,
    auth_service,
    doctor_service,
    student_service,
)


def _user(role_name: str, user_id: int = 10) -> AuthenticatedUser:
    return AuthenticatedUser(
        user_id=user_id,
        name="Test User",
        email="test@example.edu",
        role_name=role_name,
    )


def _auth_header() -> dict[str, str]:
    return {"Authorization": "Bearer test-token"}


@pytest.fixture(autouse=True)
def reset_security_state():
    from app.backend.app.core.security_controls import reset_security_state

    reset_security_state()
    yield
    reset_security_state()


def test_student_routes_require_bearer_token():
    client = TestClient(app)

    response = client.get("/students/dashboard")

    assert response.status_code == 401


def test_student_dashboard_uses_authenticated_student_context(monkeypatch):
    captured_student_ids = []

    monkeypatch.setattr(
        auth_service,
        "get_current_user",
        lambda token: _user("student", user_id=20),
    )
    monkeypatch.setattr(auth_service, "get_student_id_for_user", lambda user_id: 7)

    def fake_dashboard(student_id: int) -> StudentDashboard:
        captured_student_ids.append(student_id)
        return StudentDashboard(
            student_id=student_id,
            student_name="Aarav Sharma",
        )

    monkeypatch.setattr(student_service, "get_dashboard", fake_dashboard)

    client = TestClient(app)
    response = client.get("/students/dashboard", headers=_auth_header())

    assert response.status_code == 200
    assert response.json()["student_id"] == 7
    assert captured_student_ids == [7]


def test_student_role_cannot_access_doctor_dashboard(monkeypatch):
    monkeypatch.setattr(
        auth_service,
        "get_current_user",
        lambda token: _user("student", user_id=20),
    )

    client = TestClient(app)
    response = client.get("/doctors/dashboard", headers=_auth_header())

    assert response.status_code == 403


def test_doctor_patient_search_uses_authenticated_doctor_scope(monkeypatch):
    captured = []

    monkeypatch.setattr(
        auth_service,
        "get_current_user",
        lambda token: _user("doctor", user_id=20),
    )
    monkeypatch.setattr(auth_service, "get_staff_id_for_user", lambda user_id: 5)

    def fake_search_patients(query: str, staff_id: int | None):
        captured.append((query, staff_id))
        return [
            {
                "student_id": 7,
                "student_name": "Aarav Sharma",
                "roll_number": "CSE-2026-001",
                "department": "Computer Science",
                "year_level": 2,
            }
        ]

    monkeypatch.setattr(doctor_service, "search_patients", fake_search_patients)

    client = TestClient(app)
    response = client.get(
        "/doctors/patients/search?q=Aarav",
        headers=_auth_header(),
    )

    assert response.status_code == 200
    assert response.json()[0]["roll_number"] == "CSE-2026-001"
    assert captured == [("Aarav", 5)]


def test_doctor_availability_uses_authenticated_doctor_context(monkeypatch):
    captured = []

    monkeypatch.setattr(
        auth_service,
        "get_current_user",
        lambda token: _user("doctor", user_id=20),
    )
    monkeypatch.setattr(auth_service, "get_staff_id_for_user", lambda user_id: 5)

    def fake_get_availability(staff_id: int):
        captured.append(staff_id)
        return {
            "doctor_id": staff_id,
            "weekly_availability": [
                {
                    "weekday": 0,
                    "weekday_name": "Monday",
                    "is_available": True,
                    "start_time": None,
                    "end_time": None,
                },
                {
                    "weekday": 6,
                    "weekday_name": "Sunday",
                    "is_available": False,
                    "start_time": None,
                    "end_time": None,
                },
            ],
            "date_overrides": [],
        }

    monkeypatch.setattr(doctor_service, "get_availability", fake_get_availability)

    client = TestClient(app)
    response = client.get("/doctors/availability", headers=_auth_header())

    assert response.status_code == 200
    assert response.json()["doctor_id"] == 5
    assert captured == [5]


def test_doctor_updates_weekly_availability_from_authenticated_context(monkeypatch):
    captured = []

    monkeypatch.setattr(
        auth_service,
        "get_current_user",
        lambda token: _user("doctor", user_id=20),
    )
    monkeypatch.setattr(auth_service, "get_staff_id_for_user", lambda user_id: 5)

    def fake_update(staff_id: int, weekday: int, payload):
        captured.append((staff_id, weekday, payload.is_available))
        return {
            "weekday": weekday,
            "weekday_name": "Sunday",
            "is_available": False,
            "start_time": None,
            "end_time": None,
        }

    monkeypatch.setattr(doctor_service, "upsert_weekly_availability", fake_update)

    client = TestClient(app)
    response = client.put(
        "/doctors/availability/weekly/6",
        headers={**_auth_header(), "Idempotency-Key": "doctor-weekly-sunday"},
        json={"is_available": False},
    )

    assert response.status_code == 200
    assert captured == [(5, 6, False)]


def test_admin_patient_search_is_not_scoped_to_doctor(monkeypatch):
    captured = []

    monkeypatch.setattr(
        auth_service,
        "get_current_user",
        lambda token: _user("admin", user_id=30),
    )

    def fake_search_patients(query: str, staff_id: int | None):
        captured.append((query, staff_id))
        return []

    monkeypatch.setattr(doctor_service, "search_patients", fake_search_patients)

    client = TestClient(app)
    response = client.get(
        "/doctors/patients/search?q=CSE",
        headers=_auth_header(),
    )

    assert response.status_code == 200
    assert captured == [("CSE", None)]


def test_student_booking_uses_authenticated_student_and_idempotency(monkeypatch):
    captured = []

    monkeypatch.setattr(
        auth_service,
        "get_current_user",
        lambda token: _user("student", user_id=20),
    )
    monkeypatch.setattr(auth_service, "get_student_id_for_user", lambda user_id: 7)

    def fake_book(payload, student_id: int) -> AppointmentBookResponse:
        captured.append((student_id, payload.slot_id, payload.reason))
        return AppointmentBookResponse(
            appointment_id=99,
            slot_id=payload.slot_id,
            status="booked",
            message="Appointment booked",
        )

    monkeypatch.setattr(appointment_service, "book_appointment", fake_book)

    client = TestClient(app)
    response = client.post(
        "/appointments/book",
        headers={**_auth_header(), "Idempotency-Key": "book-slot-1"},
        json={"slot_id": 1, "reason": "Headache"},
    )

    assert response.status_code == 201
    assert response.json()["appointment_id"] == 99
    assert captured == [(7, 1, "Headache")]


def test_appointment_doctor_status_route_uses_authenticated_context(monkeypatch):
    captured = []

    monkeypatch.setattr(
        auth_service,
        "get_current_user",
        lambda token: _user("student", user_id=20),
    )

    def fake_list_doctors(for_date):
        captured.append(for_date)
        return [
            {
                "doctor_id": 5,
                "doctor_name": "Dr. Meera Rao",
                "specialization": "General Medicine",
                "is_available": False,
                "available_slots": 0,
                "unavailability_note": "Conference duty",
            }
        ]

    monkeypatch.setattr(
        appointment_service,
        "list_doctors_with_availability",
        fake_list_doctors,
        raising=False,
    )

    client = TestClient(app)
    response = client.get(
        "/appointments/doctors?for_date=2026-05-18",
        headers=_auth_header(),
    )

    assert response.status_code == 200
    assert response.json() == [
        {
            "doctor_id": 5,
            "doctor_name": "Dr. Meera Rao",
            "specialization": "General Medicine",
            "is_available": False,
            "available_slots": 0,
            "unavailability_note": "Conference duty",
        }
    ]
    assert captured == [date(2026, 5, 18)]


def test_state_changing_routes_require_idempotency_key(monkeypatch):
    monkeypatch.setattr(
        auth_service,
        "get_current_user",
        lambda token: _user("student", user_id=20),
    )
    monkeypatch.setattr(auth_service, "get_student_id_for_user", lambda user_id: 7)

    client = TestClient(app)
    response = client.post(
        "/appointments/book",
        headers=_auth_header(),
        json={"slot_id": 1, "reason": "Headache"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Idempotency-Key header is required"


def test_student_emergency_alert_uses_authenticated_student_context(monkeypatch):
    from app.backend.app.services import emergency_service

    captured = []

    monkeypatch.setattr(
        auth_service,
        "get_current_user",
        lambda token: _user("student", user_id=20),
    )
    monkeypatch.setattr(auth_service, "get_student_id_for_user", lambda user_id: 7)

    def fake_create_alert(student_id: int, message: str | None):
        captured.append((student_id, message))
        return {
            "alert_id": 99,
            "student_id": student_id,
            "student_name": "Aarav Sharma",
            "roll_number": "CSE-2026-001",
            "message": message or "Student requested emergency assistance",
            "created_at": "2026-05-16T12:00:00",
        }

    monkeypatch.setattr(emergency_service, "create_alert", fake_create_alert)

    client = TestClient(app)
    response = client.post(
        "/emergency/alert",
        headers={**_auth_header(), "Idempotency-Key": "emergency-alert"},
        json={"message": "Need urgent medical help"},
    )

    assert response.status_code == 201
    assert response.json()["alert_id"] == 99
    assert captured == [(7, "Need urgent medical help")]


def test_state_changing_routes_check_auth_before_idempotency():
    client = TestClient(app)

    response = client.post(
        "/appointments/book",
        json={"slot_id": 1, "reason": "Headache"},
    )

    assert response.status_code == 401


def test_idempotency_replays_cached_write_response(monkeypatch):
    call_count = 0

    monkeypatch.setattr(
        auth_service,
        "get_current_user",
        lambda token: _user("student", user_id=20),
    )
    monkeypatch.setattr(auth_service, "get_student_id_for_user", lambda user_id: 7)

    def fake_book(payload, student_id: int) -> AppointmentBookResponse:
        nonlocal call_count
        call_count += 1
        return AppointmentBookResponse(
            appointment_id=100 + call_count,
            slot_id=payload.slot_id,
            status="booked",
            message="Appointment booked",
        )

    monkeypatch.setattr(appointment_service, "book_appointment", fake_book)

    client = TestClient(app)
    headers = {**_auth_header(), "Idempotency-Key": "retry-book-slot"}
    body = {"slot_id": 1, "reason": "Headache"}

    first = client.post("/appointments/book", headers=headers, json=body)
    second = client.post("/appointments/book", headers=headers, json=body)

    assert first.status_code == 201
    assert second.status_code == 201
    assert first.json() == second.json()
    assert call_count == 1


def test_rate_limiter_blocks_after_limit():
    limiter = FixedWindowRateLimiter(limit=2, window_seconds=60)

    assert limiter.allow("client-1") is True
    assert limiter.allow("client-1") is True
    assert limiter.allow("client-1") is False


def test_login_attempt_tracker_blocks_after_failed_attempts():
    tracker = LoginAttemptTracker(max_attempts=2, lockout_seconds=60)

    assert tracker.is_blocked("student@college.edu") is False
    tracker.record_failure("student@college.edu")
    tracker.record_failure("student@college.edu")

    assert tracker.is_blocked("student@college.edu") is True

    tracker.record_success("student@college.edu")

    assert tracker.is_blocked("student@college.edu") is False


def test_production_rejects_default_jwt_secret():
    with pytest.raises(ValidationError):
        Settings(environment="production", jwt_secret_key="change-this-dev-secret")
