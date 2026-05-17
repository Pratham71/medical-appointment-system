from datetime import date, datetime, time
from importlib import import_module

import pytest
from fastapi.testclient import TestClient

from app.backend.app.main import app
from app.backend.app.schemas.auth import AuthenticatedUser
from app.backend.app.schemas.student import StudentDashboard
from app.backend.app.services import auth_service, student_service


def _admin_service():
    try:
        return import_module("app.backend.app.services.admin_service")
    except ModuleNotFoundError as exc:
        pytest.fail(f"admin_service module is missing: {exc}")


def _user(role_name: str, user_id: int = 30) -> AuthenticatedUser:
    return AuthenticatedUser(
        user_id=user_id,
        name="Clinic Admin",
        email="admin@college.edu",
        role_name=role_name,
    )


def _auth_header() -> dict[str, str]:
    return {"Authorization": "Bearer test-token"}


def test_signup_defaults_to_student_patient_role(monkeypatch):
    captured = []

    def fake_signup(payload):
        captured.append(payload)
        return {
            "access_token": "signup-token",
            "token_type": "bearer",
            "user": {
                "user_id": 88,
                "name": payload.name,
                "email": str(payload.email),
                "role_name": "student",
            },
        }

    monkeypatch.setattr(auth_service, "signup", fake_signup, raising=False)

    client = TestClient(app)
    response = client.post(
        "/auth/signup",
        json={
            "name": "New Patient",
            "email": "new.patient@college.edu",
            "password": "password123",
            "roll_number": "CSE-2026-088",
            "department": "Computer Science",
            "year_level": 2,
        },
    )

    assert response.status_code == 201
    assert response.json()["user"]["role_name"] == "student"
    assert not hasattr(captured[0], "role_name")


def test_professor_can_use_student_dashboard_context(monkeypatch):
    captured_student_ids = []
    monkeypatch.setattr(
        auth_service,
        "get_current_user",
        lambda token: _user("professor", user_id=88),
    )
    monkeypatch.setattr(auth_service, "get_student_id_for_user", lambda user_id: 8)

    def fake_dashboard(student_id: int) -> StudentDashboard:
        captured_student_ids.append(student_id)
        return StudentDashboard(student_id=student_id, student_name="Prof. Rao")

    monkeypatch.setattr(student_service, "get_dashboard", fake_dashboard)

    client = TestClient(app)
    response = client.get("/students/dashboard", headers=_auth_header())

    assert response.status_code == 200
    assert response.json()["student_id"] == 8
    assert captured_student_ids == [8]


def test_admin_dashboard_requires_admin_role(monkeypatch):
    monkeypatch.setattr(
        auth_service,
        "get_current_user",
        lambda token: _user("student", user_id=20),
    )

    client = TestClient(app)
    response = client.get("/admin/dashboard", headers=_auth_header())

    assert response.status_code == 403


def test_admin_dashboard_calls_service_for_admin(monkeypatch):
    admin_service = _admin_service()
    monkeypatch.setattr(
        auth_service,
        "get_current_user",
        lambda token: _user("admin"),
    )

    def fake_dashboard():
        return {
            "total_students": 12,
            "total_professors": 4,
            "total_doctors": 3,
            "total_staff": 2,
            "appointments_today": 4,
            "booked_appointments": 9,
            "completed_appointments": 15,
            "cancelled_appointments": 1,
            "reports_available": 7,
            "certificates_issued": 5,
            "emergency_alerts": 2,
        }

    monkeypatch.setattr(admin_service, "get_dashboard", fake_dashboard)

    client = TestClient(app)
    response = client.get("/admin/dashboard", headers=_auth_header())

    assert response.status_code == 200
    assert response.json()["total_students"] == 12
    assert response.json()["total_professors"] == 4
    assert response.json()["appointments_today"] == 4


def test_admin_can_list_users_for_role_management(monkeypatch):
    admin_service = _admin_service()
    captured = []
    monkeypatch.setattr(
        auth_service,
        "get_current_user",
        lambda token: _user("admin"),
    )

    def fake_list_users(q, role_name, limit):
        captured.append((q, role_name, limit))
        return [
            {
                "user_id": 88,
                "name": "New Patient",
                "email": "new.patient@college.edu",
                "role_name": "student",
                "is_active": True,
                "student_id": 8,
                "staff_id": None,
            }
        ]

    monkeypatch.setattr(admin_service, "list_users", fake_list_users)

    client = TestClient(app)
    response = client.get(
        "/admin/users?q=patient&role_name=student&limit=25",
        headers=_auth_header(),
    )

    assert response.status_code == 200
    assert response.json()[0]["role_name"] == "student"
    assert captured == [("patient", "student", 25)]


def test_admin_can_assign_student_to_doctor_role(monkeypatch):
    admin_service = _admin_service()
    captured = []
    monkeypatch.setattr(
        auth_service,
        "get_current_user",
        lambda token: _user("admin", user_id=30),
    )

    def fake_assign_user_role(user_id, payload, actor_user_id):
        captured.append((user_id, payload.role_name, payload.employee_number, actor_user_id))
        return {
            "user_id": user_id,
            "name": "New Doctor",
            "email": "new.doctor@college.edu",
            "role_name": "doctor",
            "student_id": None,
            "staff_id": 9,
            "message": "User role updated",
        }

    monkeypatch.setattr(admin_service, "assign_user_role", fake_assign_user_role)

    client = TestClient(app)
    response = client.patch(
        "/admin/users/88/role",
        headers={**_auth_header(), "Idempotency-Key": "assign-role-88"},
        json={
            "role_name": "doctor",
            "employee_number": "DOC-088",
            "specialization": "General Medicine",
        },
    )

    assert response.status_code == 200
    assert response.json()["role_name"] == "doctor"
    assert response.json()["staff_id"] == 9
    assert captured == [(88, "doctor", "DOC-088", 30)]


def test_admin_can_assign_student_to_professor_role(monkeypatch):
    admin_service = _admin_service()
    captured = []
    monkeypatch.setattr(
        auth_service,
        "get_current_user",
        lambda token: _user("admin", user_id=30),
    )

    def fake_assign_user_role(user_id, payload, actor_user_id):
        captured.append((user_id, payload.role_name, actor_user_id))
        return {
            "user_id": user_id,
            "name": "Prof. Rao",
            "email": "professor@college.edu",
            "role_name": "professor",
            "student_id": 8,
            "staff_id": None,
            "message": "User role updated",
        }

    monkeypatch.setattr(admin_service, "assign_user_role", fake_assign_user_role)

    client = TestClient(app)
    response = client.patch(
        "/admin/users/88/role",
        headers={**_auth_header(), "Idempotency-Key": "assign-role-professor-88"},
        json={
            "role_name": "professor",
            "roll_number": "PROF-088",
            "department": "Computer Science",
            "year_level": 1,
        },
    )

    assert response.status_code == 200
    assert response.json()["role_name"] == "professor"
    assert response.json()["student_id"] == 8
    assert captured == [(88, "professor", 30)]


@pytest.mark.parametrize("role_name", ["college-staff", "hostel-staff"])
def test_admin_can_assign_patient_equivalent_staff_roles(monkeypatch, role_name):
    admin_service = _admin_service()
    captured = []
    monkeypatch.setattr(
        auth_service,
        "get_current_user",
        lambda token: _user("admin", user_id=30),
    )

    def fake_assign_user_role(user_id, payload, actor_user_id):
        captured.append((user_id, payload.role_name, payload.roll_number, actor_user_id))
        return {
            "user_id": user_id,
            "name": "Hostel Staff",
            "email": f"{role_name}@college.edu",
            "role_name": role_name,
            "student_id": 18,
            "staff_id": None,
            "message": "User role updated",
        }

    monkeypatch.setattr(admin_service, "assign_user_role", fake_assign_user_role)

    client = TestClient(app)
    response = client.patch(
        "/admin/users/88/role",
        headers={**_auth_header(), "Idempotency-Key": f"assign-role-{role_name}-88"},
        json={
            "role_name": role_name,
            "roll_number": "NST-088",
            "department": "Administration",
            "year_level": 1,
        },
    )

    assert response.status_code == 200
    assert response.json()["role_name"] == role_name
    assert response.json()["student_id"] == 18
    assert captured == [(88, role_name, "NST-088", 30)]


def test_non_admin_cannot_assign_roles(monkeypatch):
    monkeypatch.setattr(
        auth_service,
        "get_current_user",
        lambda token: _user("doctor", user_id=20),
    )

    client = TestClient(app)
    response = client.patch(
        "/admin/users/88/role",
        headers={**_auth_header(), "Idempotency-Key": "assign-role-denied"},
        json={
            "role_name": "staff",
            "employee_number": "STAFF-088",
        },
    )

    assert response.status_code == 403


def test_admin_can_deactivate_user(monkeypatch):
    admin_service = _admin_service()
    captured = []
    monkeypatch.setattr(
        auth_service,
        "get_current_user",
        lambda token: _user("admin", user_id=30),
    )

    def fake_deactivate_user(user_id, actor_user_id):
        captured.append((user_id, actor_user_id))
        return {
            "user_id": user_id,
            "is_active": False,
            "message": "User deactivated",
        }

    monkeypatch.setattr(admin_service, "deactivate_user", fake_deactivate_user)

    client = TestClient(app)
    response = client.patch(
        "/admin/users/88/deactivate",
        headers={**_auth_header(), "Idempotency-Key": "deactivate-user-88"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "user_id": 88,
        "is_active": False,
        "message": "User deactivated",
    }
    assert captured == [(88, 30)]


def test_admin_can_reactivate_user(monkeypatch):
    admin_service = _admin_service()
    captured = []
    monkeypatch.setattr(
        auth_service,
        "get_current_user",
        lambda token: _user("admin", user_id=30),
    )

    def fake_activate_user(user_id, actor_user_id):
        captured.append((user_id, actor_user_id))
        return {
            "user_id": user_id,
            "is_active": True,
            "message": "User activated",
        }

    monkeypatch.setattr(admin_service, "activate_user", fake_activate_user)

    client = TestClient(app)
    response = client.patch(
        "/admin/users/88/activate",
        headers={**_auth_header(), "Idempotency-Key": "activate-user-88"},
    )

    assert response.status_code == 200
    assert response.json()["is_active"] is True
    assert captured == [(88, 30)]


def test_admin_delete_user_soft_deactivates_user(monkeypatch):
    admin_service = _admin_service()
    captured = []
    monkeypatch.setattr(
        auth_service,
        "get_current_user",
        lambda token: _user("admin", user_id=30),
    )

    def fake_deactivate_user(user_id, actor_user_id):
        captured.append((user_id, actor_user_id))
        return {
            "user_id": user_id,
            "is_active": False,
            "message": "User deactivated",
        }

    monkeypatch.setattr(admin_service, "deactivate_user", fake_deactivate_user)

    client = TestClient(app)
    response = client.delete(
        "/admin/users/88",
        headers={**_auth_header(), "Idempotency-Key": "delete-user-88"},
    )

    assert response.status_code == 200
    assert response.json()["message"] == "User deactivated"
    assert captured == [(88, 30)]


def test_admin_cannot_deactivate_self(monkeypatch):
    admin_service = _admin_service()
    monkeypatch.setattr(
        auth_service,
        "get_current_user",
        lambda token: _user("admin", user_id=30),
    )

    client = TestClient(app)
    response = client.patch(
        "/admin/users/30/deactivate",
        headers={**_auth_header(), "Idempotency-Key": "deactivate-self"},
    )

    assert response.status_code == 409
    assert hasattr(admin_service, "deactivate_user")


def test_admin_appointments_support_filters(monkeypatch):
    admin_service = _admin_service()
    captured = []
    monkeypatch.setattr(
        auth_service,
        "get_current_user",
        lambda token: _user("admin"),
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

    monkeypatch.setattr(admin_service, "list_appointments", fake_list_appointments)

    client = TestClient(app)
    response = client.get(
        "/admin/appointments?status=booked&from_date=2026-05-18&to_date=2026-05-18&doctor_id=1&student_id=1",
        headers=_auth_header(),
    )

    assert response.status_code == 200
    assert response.json()[0]["appointment_id"] == 55
    assert captured[0].status == "booked"
    assert captured[0].from_date == date(2026, 5, 18)
    assert captured[0].to_date == date(2026, 5, 18)
    assert captured[0].doctor_id == 1
    assert captured[0].student_id == 1


def test_admin_students_support_search(monkeypatch):
    admin_service = _admin_service()
    captured = []
    monkeypatch.setattr(
        auth_service,
        "get_current_user",
        lambda token: _user("admin"),
    )

    def fake_list_students(q, limit):
        captured.append((q, limit))
        return [
            {
                "student_id": 1,
                "student_name": "Aarav Sharma",
                "email": "student@college.edu",
                "roll_number": "CSE-2026-001",
                "department": "Computer Science",
                "year_level": 2,
                "role_name": "student",
                "total_appointments": 3,
                "completed_appointments": 1,
            }
        ]

    monkeypatch.setattr(admin_service, "list_students", fake_list_students)

    client = TestClient(app)
    response = client.get("/admin/students?q=Aarav&limit=25", headers=_auth_header())

    assert response.status_code == 200
    assert response.json()[0]["roll_number"] == "CSE-2026-001"
    assert captured == [("Aarav", 25)]


def test_admin_doctors_and_staff_are_separate_lists(monkeypatch):
    admin_service = _admin_service()
    monkeypatch.setattr(
        auth_service,
        "get_current_user",
        lambda token: _user("admin"),
    )
    monkeypatch.setattr(
        admin_service,
        "list_doctors",
        lambda q, limit: [
            {
                "doctor_id": 1,
                "doctor_name": "Dr. Meera Singh",
                "email": "doctor@college.edu",
                "employee_number": "DOC-001",
                "specialization": "General Medicine",
                "is_available_today": True,
                "appointments_today": 2,
                "upcoming_appointments": 5,
            }
        ],
    )
    monkeypatch.setattr(
        admin_service,
        "list_staff",
        lambda q, limit: [
            {
                "staff_id": 2,
                "staff_name": "Infirmary Staff",
                "email": "staff@college.edu",
                "employee_number": "STAFF-001",
                "specialization": None,
                "is_doctor": False,
            }
        ],
    )

    client = TestClient(app)
    doctors = client.get("/admin/doctors", headers=_auth_header())
    staff = client.get("/admin/staff", headers=_auth_header())

    assert doctors.status_code == 200
    assert doctors.json()[0]["doctor_id"] == 1
    assert staff.status_code == 200
    assert staff.json()[0]["is_doctor"] is False


def test_admin_can_list_emergency_alerts(monkeypatch):
    admin_service = _admin_service()
    monkeypatch.setattr(
        auth_service,
        "get_current_user",
        lambda token: _user("admin"),
    )
    monkeypatch.setattr(
        admin_service,
        "list_emergency_alerts",
        lambda limit: [
            {
                "alert_id": 10,
                "student_id": 1,
                "student_name": "Aarav Sharma",
                "roll_number": "CSE-2026-001",
                "reason": "Injury",
                "location": "Lab Block C",
                "contact_number": "+971501234567",
                "message": "Need urgent medical help",
                "status": "unread",
                "created_at": datetime(2026, 5, 17, 9, 15),
                "acknowledged_by": None,
                "acknowledged_at": None,
                "resolved_by": None,
                "resolved_at": None,
                "resolution_note": None,
            }
        ],
    )

    client = TestClient(app)
    response = client.get("/admin/emergency-alerts?limit=10", headers=_auth_header())

    assert response.status_code == 200
    assert response.json()[0]["alert_id"] == 10
    assert response.json()[0]["reason"] == "Injury"
    assert response.json()[0]["location"] == "Lab Block C"
    assert response.json()[0]["status"] == "unread"


def test_admin_can_acknowledge_emergency_alert(monkeypatch):
    admin_service = _admin_service()
    captured = []
    monkeypatch.setattr(
        auth_service,
        "get_current_user",
        lambda token: _user("admin", user_id=30),
    )

    def fake_acknowledge(alert_id: int, actor_user_id: int):
        captured.append((alert_id, actor_user_id))
        return {
            "alert_id": alert_id,
            "student_id": 1,
            "student_name": "Aarav Sharma",
            "roll_number": "CSE-2026-001",
            "reason": "Injury",
            "location": "Lab Block C",
            "contact_number": "+971501234567",
            "message": "Need urgent medical help",
            "status": "acknowledged",
            "created_at": datetime(2026, 5, 17, 9, 15),
            "acknowledged_by": actor_user_id,
            "acknowledged_at": datetime(2026, 5, 17, 9, 16),
            "resolved_by": None,
            "resolved_at": None,
            "resolution_note": None,
        }

    monkeypatch.setattr(
        admin_service,
        "acknowledge_emergency_alert",
        fake_acknowledge,
        raising=False,
    )

    client = TestClient(app)
    response = client.patch(
        "/admin/emergency-alerts/10/acknowledge",
        headers={**_auth_header(), "Idempotency-Key": "ack-alert-10"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "acknowledged"
    assert response.json()["acknowledged_by"] == 30
    assert captured == [(10, 30)]


def test_admin_can_resolve_emergency_alert(monkeypatch):
    admin_service = _admin_service()
    captured = []
    monkeypatch.setattr(
        auth_service,
        "get_current_user",
        lambda token: _user("admin", user_id=30),
    )

    def fake_resolve(alert_id: int, payload, actor_user_id: int):
        captured.append((alert_id, payload.resolution_note, actor_user_id))
        return {
            "alert_id": alert_id,
            "student_id": 1,
            "student_name": "Aarav Sharma",
            "roll_number": "CSE-2026-001",
            "reason": "Injury",
            "location": "Lab Block C",
            "contact_number": "+971501234567",
            "message": "Need urgent medical help",
            "status": "resolved",
            "created_at": datetime(2026, 5, 17, 9, 15),
            "acknowledged_by": actor_user_id,
            "acknowledged_at": datetime(2026, 5, 17, 9, 16),
            "resolved_by": actor_user_id,
            "resolved_at": datetime(2026, 5, 17, 9, 25),
            "resolution_note": payload.resolution_note,
        }

    monkeypatch.setattr(
        admin_service,
        "resolve_emergency_alert",
        fake_resolve,
        raising=False,
    )

    client = TestClient(app)
    response = client.patch(
        "/admin/emergency-alerts/10/resolve",
        headers={**_auth_header(), "Idempotency-Key": "resolve-alert-10"},
        json={"resolution_note": "Escorted to infirmary"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "resolved"
    assert response.json()["resolution_note"] == "Escorted to infirmary"
    assert captured == [(10, "Escorted to infirmary", 30)]
