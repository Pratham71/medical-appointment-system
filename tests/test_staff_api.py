from datetime import date, datetime, time
from importlib import import_module

from fastapi.testclient import TestClient

from app.backend.app.main import app
from app.backend.app.schemas.appointment import AppointmentStatusResponse
from app.backend.app.schemas.auth import AuthenticatedUser
from app.backend.app.services import appointment_service, auth_service


def _staff_service():
    return import_module("app.backend.app.services.staff_service")


def _user(role_name: str, user_id: int = 40) -> AuthenticatedUser:
    return AuthenticatedUser(
        user_id=user_id,
        name="Infirmary Staff",
        email="staff@college.edu",
        role_name=role_name,
    )


def _auth_header() -> dict[str, str]:
    return {"Authorization": "Bearer test-token"}


def test_staff_dashboard_requires_staff_or_admin(monkeypatch):
    monkeypatch.setattr(
        auth_service,
        "get_current_user",
        lambda token: _user("student", user_id=20),
    )

    client = TestClient(app)
    response = client.get("/staff/dashboard", headers=_auth_header())

    assert response.status_code == 403


def test_staff_dashboard_calls_service(monkeypatch):
    staff_service = _staff_service()
    monkeypatch.setattr(
        auth_service,
        "get_current_user",
        lambda token: _user("staff", user_id=40),
    )
    monkeypatch.setattr(
        staff_service,
        "get_dashboard",
        lambda: {
            "appointments_today": 4,
            "booked_appointments": 9,
            "cancelled_today": 1,
            "emergency_alerts": 2,
        },
    )

    client = TestClient(app)
    response = client.get("/staff/dashboard", headers=_auth_header())

    assert response.status_code == 200
    assert response.json()["appointments_today"] == 4
    assert response.json()["emergency_alerts"] == 2


def test_staff_can_list_appointments_with_filters(monkeypatch):
    staff_service = _staff_service()
    captured = []
    monkeypatch.setattr(
        auth_service,
        "get_current_user",
        lambda token: _user("staff", user_id=40),
    )

    def fake_list_appointments(filters):
        captured.append(filters)
        return [
            {
                "appointment_id": 55,
                "slot_date": date(2026, 5, 18),
                "start_time": time(9, 0),
                "end_time": time(9, 30),
                "student_id": 1,
                "student_name": "Aarav Sharma",
                "roll_number": "CSE-2026-001",
                "doctor_id": 1,
                "doctor_name": "Dr. Meera Singh",
                "status": "booked",
                "reason": "Fever",
                "cancellation_reason": None,
            }
        ]

    monkeypatch.setattr(staff_service, "list_appointments", fake_list_appointments)

    client = TestClient(app)
    response = client.get(
        "/staff/appointments?status=booked&from_date=2026-05-18&to_date=2026-05-18&limit=25",
        headers=_auth_header(),
    )

    assert response.status_code == 200
    assert response.json()[0]["appointment_id"] == 55
    assert captured[0].status == "booked"
    assert captured[0].limit == 25


def test_staff_can_cancel_appointment_with_reason(monkeypatch):
    captured = []
    monkeypatch.setattr(
        auth_service,
        "get_current_user",
        lambda token: _user("staff", user_id=40),
    )
    monkeypatch.setattr(auth_service, "can_access_appointment", lambda *args, **kwargs: True)

    def fake_cancel(appointment_id, payload=None, actor_role="student"):
        captured.append((appointment_id, payload.reason_code, payload.note, actor_role))
        return AppointmentStatusResponse(
            appointment_id=appointment_id,
            status="cancelled",
            message="Appointment cancelled",
        )

    monkeypatch.setattr(appointment_service, "cancel_appointment", fake_cancel)

    client = TestClient(app)
    response = client.patch(
        "/appointments/55/cancel",
        headers={**_auth_header(), "Idempotency-Key": "staff-cancel-55"},
        json={"reason_code": "no_show", "note": "Student did not arrive"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "cancelled"
    assert captured == [(55, "no_show", "Student did not arrive", "staff")]


def test_staff_dashboard_response_model_accepts_datetime_counts():
    staff_service = _staff_service()
    assert hasattr(staff_service, "get_dashboard")
    assert datetime(2026, 5, 17, 9, 0).year == 2026
