# Issue 11 Admin Backend Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the backend API surface for the admin dashboard, admin workflows, default patient signup, professor role support, and admin role assignment in GitHub issue #11, without implementing frontend UI.

**Architecture:** Add a dedicated admin route layer and keep the existing project boundary: routes -> services -> repositories -> queries -> db. Admin dashboard/list endpoints are read-only; admin role assignment is a single transactional write. Public signup must always create a `student` role account by default, because "patient" maps to the existing college infirmary `student` role in this schema. The `professor` role uses the same patient/student backend permissions and profile table while exposing a different `role_name` for frontend labeling. All admin routes must require the `admin` role through JWT context.

**Tech Stack:** FastAPI, Pydantic, raw parameterized MySQL SQL, pytest, uv, existing project security middleware.

---

## Scope

Implement backend-only support for:

- `POST /auth/signup`
- `GET /admin/dashboard`
- `GET /admin/users`
- `GET /admin/appointments`
- `GET /admin/students`
- `GET /admin/doctors`
- `GET /admin/staff`
- `GET /admin/emergency-alerts`
- `PATCH /admin/users/{user_id}/role`

Do not build frontend pages in this plan. Claude/Stitch will handle UI later against this API.

Do not add new database tables for issue #11. Use existing tables:

- `users`
- `roles`
- `students`
- `staff`
- `appointments`
- `appointment_slots`
- `appointment_statuses`
- `medical_notes`
- `medical_certificates`
- `emergency_alerts`
- `doctor_weekly_availability`
- `doctor_availability_overrides`

Role behavior:

- New signup creates a `student` account only. The signup request must not accept a caller-supplied role.
- Admins can list users and assign a user to `student`, `professor`, `doctor`, `staff`, or `admin`.
- Assigning `doctor` or `staff` must create/update the existing `staff` profile row with `is_doctor = TRUE` for doctors and `is_doctor = FALSE` for non-doctor staff.
- Assigning `student` or `professor` must create/update the existing `students` profile row.
- Role changes that would orphan existing operational records must return `409 Conflict` instead of deleting linked history.

## File Structure

- Create `app/backend/app/schemas/admin.py`
  - Pydantic response models and query filter models for admin dashboard data.
- Modify `app/backend/app/schemas/auth.py`
  - Add signup request/response models. Signup has no role field and defaults to student/patient.
- Create `app/backend/app/db/queries/admin_queries.py`
  - Raw SQL only. One function per query.
- Modify `app/backend/app/db/queries/auth_queries.py`
  - Add signup insert queries for `users` and `students`; keep default role as `student`.
- Create `app/backend/app/repositories/admin_repo.py`
  - Session management only. Calls admin query functions.
- Modify `app/backend/app/repositories/user_repo.py`
  - Add transactional signup repository wrapper.
- Create `app/backend/app/services/admin_service.py`
  - Converts query rows to schemas and applies small validation/defaulting logic.
- Modify `app/backend/app/services/auth_service.py`
  - Add signup service that hashes the password and creates a student account.
- Create `app/backend/app/api/routes/admin.py`
  - Thin FastAPI route handlers with admin RBAC.
- Modify `app/backend/app/api/routes/auth.py`
  - Add signup route.
- Modify `app/backend/app/api/api_router.py`
  - Include `admin.router`.
- Modify `app/backend/app/services/__init__.py`
  - Export admin service if the package currently uses service imports from `app.backend.app.services`.
- Modify `app/backend/app/repositories/__init__.py`
  - Export admin repo if needed by local import style.
- Modify `tests/test_api_surface.py`
  - Add admin routes to OpenAPI coverage.
- Create `tests/test_admin_api.py`
  - FastAPI route, RBAC, and service delegation tests.
- Modify `tests/test_mysql_database.py`
  - Add static checks for admin query file boundaries and SQL shape.
- Modify `docs/API_NOTES.md`
  - Document admin endpoints for frontend integration.
- Modify `TODO.md`
  - Mark backend admin routes complete while leaving frontend admin UI open if still pending.
- Modify `CHANGELOG.md`
  - Add an issue #11 backend entry.

---

### Task 1: Admin API Route Tests

**Files:**
- Create: `tests/test_admin_api.py`
- Modify: `tests/test_api_surface.py`

- [ ] **Step 1: Write failing admin route tests**

Create `tests/test_admin_api.py`:

```python
from datetime import date, datetime, time

from fastapi.testclient import TestClient

from app.backend.app.main import app
from app.backend.app.schemas.auth import AuthenticatedUser
from app.backend.app.services import admin_service, auth_service


def _user(role_name: str, user_id: int = 30) -> AuthenticatedUser:
    return AuthenticatedUser(
        user_id=user_id,
        name="Clinic Admin",
        email="admin@college.edu",
        role_name=role_name,
    )


def _auth_header() -> dict[str, str]:
    return {"Authorization": "Bearer test-token"}


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
    monkeypatch.setattr(
        auth_service,
        "get_current_user",
        lambda token: _user("admin"),
    )

    def fake_dashboard():
        return {
            "total_students": 12,
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
    assert response.json()["appointments_today"] == 4


def test_admin_appointments_support_filters(monkeypatch):
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
                "message": "Need urgent medical help",
                "created_at": datetime(2026, 5, 17, 9, 15),
            }
        ],
    )

    client = TestClient(app)
    response = client.get("/admin/emergency-alerts?limit=10", headers=_auth_header())

    assert response.status_code == 200
    assert response.json()[0]["alert_id"] == 10
```

- [ ] **Step 2: Add OpenAPI route coverage**

Modify `tests/test_api_surface.py` and add these paths to `expected_paths`:

```python
        "/auth/signup",
        "/admin/dashboard",
        "/admin/users",
        "/admin/users/{user_id}/role",
        "/admin/appointments",
        "/admin/students",
        "/admin/doctors",
        "/admin/staff",
        "/admin/emergency-alerts",
```

- [ ] **Step 3: Run tests to verify they fail**

Run:

```powershell
uv run --group dev pytest tests/test_admin_api.py tests/test_api_surface.py -q -p no:cacheprovider
```

Expected: fail with an import or route error because `admin_service` and `/admin/*` routes do not exist yet.

---

### Task 1A: Signup and Admin Role Assignment Tests

**Files:**
- Modify: `tests/test_admin_api.py`
- Modify: `tests/test_api_surface.py`

- [ ] **Step 1: Add failing signup and role assignment route tests**

Append to `tests/test_admin_api.py`:

```python
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


def test_admin_can_list_users_for_role_management(monkeypatch):
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

    monkeypatch.setattr(admin_service, "list_users", fake_list_users, raising=False)

    client = TestClient(app)
    response = client.get(
        "/admin/users?q=patient&role_name=student&limit=25",
        headers=_auth_header(),
    )

    assert response.status_code == 200
    assert response.json()[0]["role_name"] == "student"
    assert captured == [("patient", "student", 25)]


def test_admin_can_assign_student_to_doctor_role(monkeypatch):
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

    monkeypatch.setattr(
        admin_service,
        "assign_user_role",
        fake_assign_user_role,
        raising=False,
    )

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
```

- [ ] **Step 2: Confirm OpenAPI additions include signup and role management**

Make sure `tests/test_api_surface.py` includes:

```python
        "/auth/signup",
        "/admin/users",
        "/admin/users/{user_id}/role",
```

- [ ] **Step 3: Run tests to verify they fail**

Run:

```powershell
uv run --group dev pytest tests/test_admin_api.py tests/test_api_surface.py -q -p no:cacheprovider
```

Expected: fail because `/auth/signup`, `/admin/users`, and `/admin/users/{user_id}/role` are not implemented yet.

---

### Task 2: Admin Schemas

**Files:**
- Create: `app/backend/app/schemas/admin.py`
- Modify: `app/backend/app/schemas/auth.py`
- Test: `tests/test_admin_api.py`

- [ ] **Step 1: Add admin Pydantic models**

Create `app/backend/app/schemas/admin.py`:

```python
from datetime import date, datetime, time
from typing import Literal

from pydantic import BaseModel, Field, model_validator


class AdminDashboard(BaseModel):
    total_students: int = 0
    total_doctors: int = 0
    total_staff: int = 0
    appointments_today: int = 0
    booked_appointments: int = 0
    completed_appointments: int = 0
    cancelled_appointments: int = 0
    reports_available: int = 0
    certificates_issued: int = 0
    emergency_alerts: int = 0


AssignableRole = Literal["student", "doctor", "staff", "admin"]


class AdminUserSummary(BaseModel):
    user_id: int
    name: str
    email: str
    role_name: str
    is_active: bool
    student_id: int | None = None
    staff_id: int | None = None


class AdminRoleAssignmentRequest(BaseModel):
    role_name: AssignableRole
    roll_number: str | None = Field(default=None, max_length=50)
    department: str | None = Field(default=None, max_length=120)
    year_level: int | None = Field(default=None, ge=1, le=6)
    employee_number: str | None = Field(default=None, max_length=50)
    specialization: str | None = Field(default=None, max_length=120)

    @model_validator(mode="after")
    def validate_required_profile_fields(self) -> "AdminRoleAssignmentRequest":
        if self.role_name == "student":
            if not self.roll_number or not self.department or self.year_level is None:
                raise ValueError(
                    "roll_number, department, and year_level are required for student role"
                )
        if self.role_name in {"doctor", "staff"} and not self.employee_number:
            raise ValueError("employee_number is required for doctor/staff role")
        return self


class AdminRoleAssignmentResponse(BaseModel):
    user_id: int
    name: str
    email: str
    role_name: str
    student_id: int | None = None
    staff_id: int | None = None
    message: str = "User role updated"


class AdminAppointmentFilters(BaseModel):
    status: str | None = Field(default=None, max_length=50)
    from_date: date | None = None
    to_date: date | None = None
    doctor_id: int | None = Field(default=None, gt=0)
    student_id: int | None = Field(default=None, gt=0)
    limit: int = Field(default=100, ge=1, le=250)

    @model_validator(mode="after")
    def validate_date_range(self) -> "AdminAppointmentFilters":
        if (
            self.from_date is not None
            and self.to_date is not None
            and self.to_date < self.from_date
        ):
            raise ValueError("to_date cannot be before from_date")
        return self


class AdminAppointmentSummary(BaseModel):
    appointment_id: int
    slot_date: date
    start_time: time
    end_time: time
    student_id: int
    student_name: str
    roll_number: str
    doctor_id: int
    doctor_name: str
    status: str
    reason: str | None = None
    cancellation_reason: str | None = None


class AdminStudentSummary(BaseModel):
    student_id: int
    student_name: str
    email: str
    roll_number: str
    department: str
    year_level: int
    total_appointments: int = 0
    completed_appointments: int = 0


class AdminDoctorSummary(BaseModel):
    doctor_id: int
    doctor_name: str
    email: str
    employee_number: str
    specialization: str | None = None
    is_available_today: bool
    appointments_today: int = 0
    upcoming_appointments: int = 0


class AdminStaffSummary(BaseModel):
    staff_id: int
    staff_name: str
    email: str
    employee_number: str
    specialization: str | None = None
    is_doctor: bool


class AdminEmergencyAlertSummary(BaseModel):
    alert_id: int
    student_id: int
    student_name: str
    roll_number: str
    message: str
    created_at: datetime
```

- [ ] **Step 2: Add signup schemas**

Modify `app/backend/app/schemas/auth.py`:

```python
class SignupRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8)
    roll_number: str = Field(min_length=1, max_length=50)
    department: str = Field(min_length=1, max_length=120)
    year_level: int = Field(ge=1, le=6)
```

Do not add `role_name` to `SignupRequest`. Signup always creates a student/patient account.

- [ ] **Step 3: Run focused test**

Run:

```powershell
uv run --group dev pytest tests/test_admin_api.py -q -p no:cacheprovider
```

Expected: still fail because route/service files are not implemented.

---

### Task 3: Admin Query Module

**Files:**
- Create: `app/backend/app/db/queries/admin_queries.py`
- Modify: `tests/test_mysql_database.py`

- [ ] **Step 1: Add static query boundary tests**

Append to `tests/test_mysql_database.py`:

```python
def test_admin_queries_keep_sql_in_query_module():
    source = (QUERY_DIR / "admin_queries.py").read_text(encoding="utf-8").lower()

    assert "select *" not in source
    assert "def get_dashboard_counts" in source
    assert "def list_users" in source
    assert "def get_role_id" in source
    assert "def update_user_role" in source
    assert "def upsert_student_profile" in source
    assert "def upsert_staff_profile" in source
    assert "def list_appointments" in source
    assert "def list_students" in source
    assert "def list_doctors" in source
    assert "def list_staff" in source
    assert "def list_emergency_alerts" in source
    assert "fetch_all(connection, sql, tuple(params))" in source
```

- [ ] **Step 2: Run static test to verify it fails**

Run:

```powershell
uv run --group dev pytest tests/test_mysql_database.py::test_admin_queries_keep_sql_in_query_module -q -p no:cacheprovider
```

Expected: fail because `admin_queries.py` does not exist.

- [ ] **Step 3: Implement admin raw SQL queries**

Create `app/backend/app/db/queries/admin_queries.py`:

```python
from datetime import date
from typing import Any

from app.backend.app.db.queries._helpers import execute, fetch_all, fetch_one


def get_dashboard_counts(connection: Any) -> dict[str, Any] | None:
    sql = """
        SELECT
            (SELECT COUNT(students.student_id) FROM students) AS total_students,
            (
                SELECT COUNT(staff.staff_id)
                FROM staff
                WHERE staff.is_doctor = TRUE
            ) AS total_doctors,
            (
                SELECT COUNT(staff.staff_id)
                FROM staff
                WHERE staff.is_doctor = FALSE
            ) AS total_staff,
            (
                SELECT COUNT(appointments.appointment_id)
                FROM appointments
                INNER JOIN appointment_slots
                    ON appointment_slots.slot_id = appointments.slot_id
                WHERE appointment_slots.slot_date = CURRENT_DATE
            ) AS appointments_today,
            (
                SELECT COUNT(appointments.appointment_id)
                FROM appointments
                INNER JOIN appointment_statuses
                    ON appointment_statuses.status_id = appointments.status_id
                WHERE appointment_statuses.status_name = %s
            ) AS booked_appointments,
            (
                SELECT COUNT(appointments.appointment_id)
                FROM appointments
                INNER JOIN appointment_statuses
                    ON appointment_statuses.status_id = appointments.status_id
                WHERE appointment_statuses.status_name = %s
            ) AS completed_appointments,
            (
                SELECT COUNT(appointments.appointment_id)
                FROM appointments
                INNER JOIN appointment_statuses
                    ON appointment_statuses.status_id = appointments.status_id
                WHERE appointment_statuses.status_name = %s
            ) AS cancelled_appointments,
            (SELECT COUNT(medical_notes.note_id) FROM medical_notes)
                AS reports_available,
            (
                SELECT COUNT(medical_certificates.certificate_id)
                FROM medical_certificates
            ) AS certificates_issued,
            (
                SELECT COUNT(emergency_alerts.alert_id)
                FROM emergency_alerts
            ) AS emergency_alerts
    """
    return fetch_one(connection, sql, ("booked", "completed", "cancelled"))


def list_users(
    connection: Any,
    *,
    search_text: str | None,
    role_name: str | None,
    limit: int,
) -> list[dict[str, Any]]:
    pattern = f"%{search_text}%" if search_text else None
    sql = """
        SELECT
            users.user_id,
            users.name,
            users.email,
            roles.role_name,
            users.is_active,
            students.student_id,
            staff.staff_id
        FROM users
        INNER JOIN roles
            ON roles.role_id = users.role_id
        LEFT JOIN students
            ON students.user_id = users.user_id
        LEFT JOIN staff
            ON staff.user_id = users.user_id
        WHERE (%s IS NULL OR roles.role_name = %s)
            AND (
                %s IS NULL
                OR users.name LIKE %s
                OR users.email LIKE %s
            )
        ORDER BY users.name, users.email
        LIMIT %s
    """
    params = [role_name, role_name, pattern, pattern, pattern, limit]
    return fetch_all(connection, sql, tuple(params))


def get_role_id(connection: Any, role_name: str) -> dict[str, Any] | None:
    sql = """
        SELECT roles.role_id
        FROM roles
        WHERE roles.role_name = %s
    """
    return fetch_one(connection, sql, (role_name,))


def get_user_role_context(connection: Any, user_id: int) -> dict[str, Any] | None:
    sql = """
        SELECT
            users.user_id,
            users.name,
            users.email,
            roles.role_name,
            students.student_id,
            staff.staff_id,
            (
                SELECT COUNT(appointments.appointment_id)
                FROM appointments
                WHERE appointments.student_id = students.student_id
            ) AS student_appointment_count,
            (
                SELECT COUNT(appointment_slots.slot_id)
                FROM appointment_slots
                WHERE appointment_slots.staff_id = staff.staff_id
            ) AS staff_slot_count
        FROM users
        INNER JOIN roles
            ON roles.role_id = users.role_id
        LEFT JOIN students
            ON students.user_id = users.user_id
        LEFT JOIN staff
            ON staff.user_id = users.user_id
        WHERE users.user_id = %s
            AND users.is_active = TRUE
    """
    return fetch_one(connection, sql, (user_id,))


def update_user_role(connection: Any, user_id: int, role_id: int) -> None:
    sql = """
        UPDATE users
        SET users.role_id = %s
        WHERE users.user_id = %s
    """
    execute(connection, sql, (role_id, user_id))


def upsert_student_profile(
    connection: Any,
    *,
    user_id: int,
    roll_number: str,
    department: str,
    year_level: int,
) -> None:
    sql = """
        INSERT INTO students (
            user_id,
            roll_number,
            department,
            year_level
        )
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            roll_number = VALUES(roll_number),
            department = VALUES(department),
            year_level = VALUES(year_level)
    """
    execute(connection, sql, (user_id, roll_number, department, year_level))


def upsert_staff_profile(
    connection: Any,
    *,
    user_id: int,
    employee_number: str,
    specialization: str | None,
    is_doctor: bool,
) -> None:
    sql = """
        INSERT INTO staff (
            user_id,
            employee_number,
            specialization,
            is_doctor
        )
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            employee_number = VALUES(employee_number),
            specialization = VALUES(specialization),
            is_doctor = VALUES(is_doctor)
    """
    execute(connection, sql, (user_id, employee_number, specialization, is_doctor))


def delete_student_profile(connection: Any, user_id: int) -> None:
    sql = """
        DELETE FROM students
        WHERE students.user_id = %s
    """
    execute(connection, sql, (user_id,))


def delete_staff_profile(connection: Any, user_id: int) -> None:
    sql = """
        DELETE FROM staff
        WHERE staff.user_id = %s
    """
    execute(connection, sql, (user_id,))


def get_role_assignment_result(connection: Any, user_id: int) -> dict[str, Any] | None:
    sql = """
        SELECT
            users.user_id,
            users.name,
            users.email,
            roles.role_name,
            students.student_id,
            staff.staff_id
        FROM users
        INNER JOIN roles
            ON roles.role_id = users.role_id
        LEFT JOIN students
            ON students.user_id = users.user_id
        LEFT JOIN staff
            ON staff.user_id = users.user_id
        WHERE users.user_id = %s
    """
    return fetch_one(connection, sql, (user_id,))


def list_appointments(
    connection: Any,
    *,
    status: str | None,
    from_date: date | None,
    to_date: date | None,
    doctor_id: int | None,
    student_id: int | None,
    limit: int,
) -> list[dict[str, Any]]:
    sql = """
        SELECT
            appointments.appointment_id,
            appointment_slots.slot_date,
            appointment_slots.start_time,
            appointment_slots.end_time,
            students.student_id,
            student_users.name AS student_name,
            students.roll_number,
            staff.staff_id AS doctor_id,
            doctor_users.name AS doctor_name,
            appointment_statuses.status_name AS status,
            appointments.reason,
            appointments.cancellation_reason
        FROM appointments
        INNER JOIN students
            ON students.student_id = appointments.student_id
        INNER JOIN users AS student_users
            ON student_users.user_id = students.user_id
        INNER JOIN appointment_slots
            ON appointment_slots.slot_id = appointments.slot_id
        INNER JOIN staff
            ON staff.staff_id = appointment_slots.staff_id
        INNER JOIN users AS doctor_users
            ON doctor_users.user_id = staff.user_id
        INNER JOIN appointment_statuses
            ON appointment_statuses.status_id = appointments.status_id
        WHERE (%s IS NULL OR appointment_statuses.status_name = %s)
            AND (%s IS NULL OR appointment_slots.slot_date >= %s)
            AND (%s IS NULL OR appointment_slots.slot_date <= %s)
            AND (%s IS NULL OR staff.staff_id = %s)
            AND (%s IS NULL OR students.student_id = %s)
        ORDER BY
            appointment_slots.slot_date DESC,
            appointment_slots.start_time DESC,
            appointments.appointment_id DESC
        LIMIT %s
    """
    params = [
        status,
        status,
        from_date,
        from_date,
        to_date,
        to_date,
        doctor_id,
        doctor_id,
        student_id,
        student_id,
        limit,
    ]
    return fetch_all(connection, sql, tuple(params))


def list_students(
    connection: Any,
    *,
    search_text: str | None,
    limit: int,
) -> list[dict[str, Any]]:
    pattern = f"%{search_text}%" if search_text else None
    sql = """
        SELECT
            students.student_id,
            users.name AS student_name,
            users.email,
            students.roll_number,
            students.department,
            students.year_level,
            COUNT(appointments.appointment_id) AS total_appointments,
            SUM(
                CASE
                    WHEN appointment_statuses.status_name = 'completed'
                    THEN 1
                    ELSE 0
                END
            ) AS completed_appointments
        FROM students
        INNER JOIN users
            ON users.user_id = students.user_id
        LEFT JOIN appointments
            ON appointments.student_id = students.student_id
        LEFT JOIN appointment_statuses
            ON appointment_statuses.status_id = appointments.status_id
        WHERE (
            %s IS NULL
            OR users.name LIKE %s
            OR users.email LIKE %s
            OR students.roll_number LIKE %s
        )
        GROUP BY
            students.student_id,
            users.name,
            users.email,
            students.roll_number,
            students.department,
            students.year_level
        ORDER BY users.name, students.roll_number
        LIMIT %s
    """
    return fetch_all(connection, sql, (pattern, pattern, pattern, pattern, limit))


def list_doctors(
    connection: Any,
    *,
    search_text: str | None,
    limit: int,
) -> list[dict[str, Any]]:
    pattern = f"%{search_text}%" if search_text else None
    sql = """
        SELECT
            staff.staff_id AS doctor_id,
            users.name AS doctor_name,
            users.email,
            staff.employee_number,
            staff.specialization,
            CASE
                WHEN doctor_availability_overrides.override_id IS NOT NULL
                THEN doctor_availability_overrides.is_available
                ELSE COALESCE(
                    doctor_weekly_availability.is_available,
                    WEEKDAY(CURRENT_DATE) < 6
                )
            END AS is_available_today,
            COUNT(
                CASE
                    WHEN appointment_slots.slot_date = CURRENT_DATE
                    THEN appointments.appointment_id
                    ELSE NULL
                END
            ) AS appointments_today,
            COUNT(
                CASE
                    WHEN appointment_slots.slot_date >= CURRENT_DATE
                        AND appointment_statuses.status_name = 'booked'
                    THEN appointments.appointment_id
                    ELSE NULL
                END
            ) AS upcoming_appointments
        FROM staff
        INNER JOIN users
            ON users.user_id = staff.user_id
        LEFT JOIN doctor_weekly_availability
            ON doctor_weekly_availability.staff_id = staff.staff_id
            AND doctor_weekly_availability.weekday = WEEKDAY(CURRENT_DATE)
        LEFT JOIN doctor_availability_overrides
            ON doctor_availability_overrides.staff_id = staff.staff_id
            AND doctor_availability_overrides.override_date = CURRENT_DATE
        LEFT JOIN appointment_slots
            ON appointment_slots.staff_id = staff.staff_id
        LEFT JOIN appointments
            ON appointments.slot_id = appointment_slots.slot_id
        LEFT JOIN appointment_statuses
            ON appointment_statuses.status_id = appointments.status_id
        WHERE staff.is_doctor = TRUE
            AND (
                %s IS NULL
                OR users.name LIKE %s
                OR users.email LIKE %s
                OR staff.employee_number LIKE %s
                OR staff.specialization LIKE %s
            )
        GROUP BY
            staff.staff_id,
            users.name,
            users.email,
            staff.employee_number,
            staff.specialization,
            doctor_availability_overrides.override_id,
            doctor_availability_overrides.is_available,
            doctor_weekly_availability.is_available
        ORDER BY users.name, staff.employee_number
        LIMIT %s
    """
    return fetch_all(
        connection,
        sql,
        (pattern, pattern, pattern, pattern, pattern, limit),
    )


def list_staff(
    connection: Any,
    *,
    search_text: str | None,
    limit: int,
) -> list[dict[str, Any]]:
    pattern = f"%{search_text}%" if search_text else None
    sql = """
        SELECT
            staff.staff_id,
            users.name AS staff_name,
            users.email,
            staff.employee_number,
            staff.specialization,
            staff.is_doctor
        FROM staff
        INNER JOIN users
            ON users.user_id = staff.user_id
        WHERE staff.is_doctor = FALSE
            AND (
                %s IS NULL
                OR users.name LIKE %s
                OR users.email LIKE %s
                OR staff.employee_number LIKE %s
            )
        ORDER BY users.name, staff.employee_number
        LIMIT %s
    """
    return fetch_all(connection, sql, (pattern, pattern, pattern, pattern, limit))


def list_emergency_alerts(
    connection: Any,
    *,
    limit: int,
) -> list[dict[str, Any]]:
    sql = """
        SELECT
            emergency_alerts.alert_id,
            emergency_alerts.student_id,
            users.name AS student_name,
            students.roll_number,
            emergency_alerts.message,
            emergency_alerts.created_at
        FROM emergency_alerts
        INNER JOIN students
            ON students.student_id = emergency_alerts.student_id
        INNER JOIN users
            ON users.user_id = students.user_id
        ORDER BY emergency_alerts.created_at DESC, emergency_alerts.alert_id DESC
        LIMIT %s
    """
    return fetch_all(connection, sql, tuple([limit]))
```

- [ ] **Step 4: Run query static test**

Run:

```powershell
uv run --group dev pytest tests/test_mysql_database.py::test_admin_queries_keep_sql_in_query_module -q -p no:cacheprovider
```

Expected: pass.

---

### Task 3A: Signup Query and Repository Support

**Files:**
- Modify: `app/backend/app/db/queries/auth_queries.py`
- Modify: `app/backend/app/repositories/user_repo.py`

- [ ] **Step 1: Add signup query functions**

Modify `app/backend/app/db/queries/auth_queries.py`:

```python
from app.backend.app.db.queries._helpers import execute, fetch_one
```

Add:

```python
def get_role_id_by_name(connection: Any, role_name: str) -> dict[str, Any] | None:
    sql = """
        SELECT roles.role_id
        FROM roles
        WHERE roles.role_name = %s
    """
    return fetch_one(connection, sql, (role_name,))


def insert_user(
    connection: Any,
    *,
    role_id: int,
    name: str,
    email: str,
    password_hash: str,
) -> int:
    sql = """
        INSERT INTO users (
            role_id,
            name,
            email,
            password_hash
        )
        VALUES (%s, %s, %s, %s)
    """
    return execute(connection, sql, (role_id, name, email, password_hash))


def insert_student_profile(
    connection: Any,
    *,
    user_id: int,
    roll_number: str,
    department: str,
    year_level: int,
) -> int:
    sql = """
        INSERT INTO students (
            user_id,
            roll_number,
            department,
            year_level
        )
        VALUES (%s, %s, %s, %s)
    """
    return execute(connection, sql, (user_id, roll_number, department, year_level))
```

- [ ] **Step 2: Add transactional signup repository**

Modify `app/backend/app/repositories/user_repo.py`:

```python
def create_student_user(
    *,
    name: str,
    email: str,
    password_hash: str,
    roll_number: str,
    department: str,
    year_level: int,
) -> dict[str, Any] | None:
    with session.transaction_scope() as connection:
        role = auth_queries.get_role_id_by_name(connection, "student")
        if role is None:
            return None
        user_id = auth_queries.insert_user(
            connection,
            role_id=int(role["role_id"]),
            name=name,
            email=email,
            password_hash=password_hash,
        )
        auth_queries.insert_student_profile(
            connection,
            user_id=user_id,
            roll_number=roll_number,
            department=department,
            year_level=year_level,
        )
        return auth_queries.get_user_by_id(connection, user_id)
```

- [ ] **Step 3: Run focused signup route tests**

Run:

```powershell
uv run --group dev pytest tests/test_admin_api.py::test_signup_defaults_to_student_patient_role -q -p no:cacheprovider
```

Expected: still fail because `auth_service.signup` and `POST /auth/signup` are not implemented.

---

### Task 4: Admin Repository

**Files:**
- Create: `app/backend/app/repositories/admin_repo.py`

- [ ] **Step 1: Implement repository wrapper**

Create `app/backend/app/repositories/admin_repo.py`:

```python
from datetime import date
from typing import Any

from app.backend.app.db import session
from app.backend.app.db.queries import admin_queries


def get_dashboard_counts() -> dict[str, Any] | None:
    with session.connection_scope() as connection:
        return admin_queries.get_dashboard_counts(connection)


def list_users(
    search_text: str | None,
    role_name: str | None,
    limit: int,
) -> list[dict[str, Any]]:
    with session.connection_scope() as connection:
        return admin_queries.list_users(
            connection,
            search_text=search_text,
            role_name=role_name,
            limit=limit,
        )


def list_appointments(
    *,
    status: str | None,
    from_date: date | None,
    to_date: date | None,
    doctor_id: int | None,
    student_id: int | None,
    limit: int,
) -> list[dict[str, Any]]:
    with session.connection_scope() as connection:
        return admin_queries.list_appointments(
            connection,
            status=status,
            from_date=from_date,
            to_date=to_date,
            doctor_id=doctor_id,
            student_id=student_id,
            limit=limit,
        )


def list_students(search_text: str | None, limit: int) -> list[dict[str, Any]]:
    with session.connection_scope() as connection:
        return admin_queries.list_students(
            connection,
            search_text=search_text,
            limit=limit,
        )


def list_doctors(search_text: str | None, limit: int) -> list[dict[str, Any]]:
    with session.connection_scope() as connection:
        return admin_queries.list_doctors(
            connection,
            search_text=search_text,
            limit=limit,
        )


def list_staff(search_text: str | None, limit: int) -> list[dict[str, Any]]:
    with session.connection_scope() as connection:
        return admin_queries.list_staff(
            connection,
            search_text=search_text,
            limit=limit,
        )


def list_emergency_alerts(limit: int) -> list[dict[str, Any]]:
    with session.connection_scope() as connection:
        return admin_queries.list_emergency_alerts(connection, limit=limit)


def assign_user_role(
    *,
    user_id: int,
    role_name: str,
    roll_number: str | None,
    department: str | None,
    year_level: int | None,
    employee_number: str | None,
    specialization: str | None,
) -> dict[str, Any] | None:
    with session.transaction_scope() as connection:
        context = admin_queries.get_user_role_context(connection, user_id)
        if context is None:
            return None

        role = admin_queries.get_role_id(connection, role_name)
        if role is None:
            return None

        if role_name != "student" and int(context["student_appointment_count"] or 0) > 0:
            return {
                "conflict": True,
                "message": "Cannot remove student profile with appointment history",
            }

        if role_name not in {"doctor", "staff"} and int(context["staff_slot_count"] or 0) > 0:
            return {
                "conflict": True,
                "message": "Cannot remove staff profile with appointment slots",
            }

        admin_queries.update_user_role(
            connection,
            user_id=user_id,
            role_id=int(role["role_id"]),
        )

        if role_name == "student":
            admin_queries.upsert_student_profile(
                connection,
                user_id=user_id,
                roll_number=roll_number or "",
                department=department or "",
                year_level=year_level or 1,
            )
            if context["staff_id"] is not None:
                admin_queries.delete_staff_profile(connection, user_id)
        elif role_name in {"doctor", "staff"}:
            admin_queries.upsert_staff_profile(
                connection,
                user_id=user_id,
                employee_number=employee_number or "",
                specialization=specialization,
                is_doctor=role_name == "doctor",
            )
            if context["student_id"] is not None:
                admin_queries.delete_student_profile(connection, user_id)
        elif role_name == "admin":
            if context["student_id"] is not None:
                admin_queries.delete_student_profile(connection, user_id)
            if context["staff_id"] is not None:
                admin_queries.delete_staff_profile(connection, user_id)

        return admin_queries.get_role_assignment_result(connection, user_id)
```

- [ ] **Step 2: Run focused tests**

Run:

```powershell
uv run --group dev pytest tests/test_admin_api.py -q -p no:cacheprovider
```

Expected: still fail because `admin_service` and routes are not implemented.

---

### Task 5: Admin Service

**Files:**
- Create: `app/backend/app/services/admin_service.py`
- Modify: `app/backend/app/services/__init__.py` only if needed

- [ ] **Step 1: Implement admin service conversions**

Create `app/backend/app/services/admin_service.py`:

```python
from app.backend.app.api.errors import ConflictError, NotFoundError
from app.backend.app.repositories import admin_repo
from app.backend.app.schemas.admin import (
    AdminAppointmentFilters,
    AdminAppointmentSummary,
    AdminDashboard,
    AdminDoctorSummary,
    AdminEmergencyAlertSummary,
    AdminRoleAssignmentRequest,
    AdminRoleAssignmentResponse,
    AdminStaffSummary,
    AdminStudentSummary,
    AdminUserSummary,
)


def get_dashboard() -> AdminDashboard:
    row = admin_repo.get_dashboard_counts() or {}
    return AdminDashboard(**row)


def list_users(
    q: str | None,
    role_name: str | None,
    limit: int,
) -> list[AdminUserSummary]:
    search_text = q.strip() if q else None
    rows = admin_repo.list_users(search_text, role_name, limit)
    return [AdminUserSummary(**row) for row in rows]


def assign_user_role(
    user_id: int,
    payload: AdminRoleAssignmentRequest,
    actor_user_id: int,
) -> AdminRoleAssignmentResponse:
    if user_id == actor_user_id:
        raise ConflictError("Admins cannot change their own role")

    result = admin_repo.assign_user_role(
        user_id=user_id,
        role_name=payload.role_name,
        roll_number=payload.roll_number,
        department=payload.department,
        year_level=payload.year_level,
        employee_number=payload.employee_number,
        specialization=payload.specialization,
    )
    if result is None:
        raise NotFoundError("User was not found")
    if result.get("conflict"):
        raise ConflictError(result["message"])
    return AdminRoleAssignmentResponse(**result)


def list_appointments(
    filters: AdminAppointmentFilters,
) -> list[AdminAppointmentSummary]:
    rows = admin_repo.list_appointments(
        status=filters.status,
        from_date=filters.from_date,
        to_date=filters.to_date,
        doctor_id=filters.doctor_id,
        student_id=filters.student_id,
        limit=filters.limit,
    )
    return [AdminAppointmentSummary(**row) for row in rows]


def list_students(q: str | None, limit: int) -> list[AdminStudentSummary]:
    search_text = q.strip() if q else None
    rows = admin_repo.list_students(search_text, limit)
    return [AdminStudentSummary(**row) for row in rows]


def list_doctors(q: str | None, limit: int) -> list[AdminDoctorSummary]:
    search_text = q.strip() if q else None
    rows = admin_repo.list_doctors(search_text, limit)
    return [AdminDoctorSummary(**row) for row in rows]


def list_staff(q: str | None, limit: int) -> list[AdminStaffSummary]:
    search_text = q.strip() if q else None
    rows = admin_repo.list_staff(search_text, limit)
    return [AdminStaffSummary(**row) for row in rows]


def list_emergency_alerts(limit: int) -> list[AdminEmergencyAlertSummary]:
    rows = admin_repo.list_emergency_alerts(limit)
    return [AdminEmergencyAlertSummary(**row) for row in rows]
```

- [ ] **Step 2: Fix package exports if import fails**

If `from app.backend.app.services import admin_service` fails, modify `app/backend/app/services/__init__.py`:

```python
from app.backend.app.services import admin_service
```

If it is already an empty package and Python import works without edits, leave it alone.

- [ ] **Step 3: Run focused tests**

Run:

```powershell
uv run --group dev pytest tests/test_admin_api.py -q -p no:cacheprovider
```

Expected: still fail because `/admin/*` routes are not registered.

---

### Task 5A: Default Student Signup Service

**Files:**
- Modify: `app/backend/app/services/auth_service.py`
- Modify: `app/backend/app/api/routes/auth.py`

- [ ] **Step 1: Implement signup service with fixed student role**

Modify `app/backend/app/services/auth_service.py`:

```python
from mysql.connector import IntegrityError

from app.backend.app.api.errors import ConflictError, ServiceError
from app.backend.app.core.security import hash_password
from app.backend.app.schemas.auth import SignupRequest
```

Add:

```python
def signup(payload: SignupRequest) -> TokenResponse:
    try:
        user = user_repo.create_student_user(
            name=payload.name,
            email=str(payload.email).lower(),
            password_hash=hash_password(payload.password),
            roll_number=payload.roll_number,
            department=payload.department,
            year_level=payload.year_level,
        )
    except IntegrityError as exc:
        raise ConflictError("Email or roll number already exists") from exc

    if user is None:
        raise ServiceError("Student role is not configured")

    access_token = create_access_token(
        user_id=user["user_id"],
        role_name=user["role_name"],
    )
    return TokenResponse(
        access_token=access_token,
        user=AuthenticatedUser(
            user_id=user["user_id"],
            name=user["name"],
            email=user["email"],
            role_name=user["role_name"],
        ),
    )
```

`SignupRequest` has no role field. This prevents a caller from self-registering as doctor, staff, or admin.

- [ ] **Step 2: Add auth signup route**

Modify `app/backend/app/api/routes/auth.py` imports:

```python
from fastapi import APIRouter, Depends, status
```

```python
from app.backend.app.schemas.auth import (
    AuthenticatedUser,
    LoginRequest,
    LogoutResponse,
    SignupRequest,
    TokenResponse,
)
```

Add before `/login`:

```python
@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def signup(payload: SignupRequest) -> TokenResponse:
    try:
        return auth_service.signup(payload)
    except Exception as exc:
        raise service_error_to_http(exc) from exc
```

- [ ] **Step 3: Run signup test**

Run:

```powershell
uv run --group dev pytest tests/test_admin_api.py::test_signup_defaults_to_student_patient_role -q -p no:cacheprovider
```

Expected: pass.

---

### Task 6: Admin Routes and Router Registration

**Files:**
- Create: `app/backend/app/api/routes/admin.py`
- Modify: `app/backend/app/api/api_router.py`

- [ ] **Step 1: Implement admin routes**

Create `app/backend/app/api/routes/admin.py`:

```python
from datetime import date

from fastapi import APIRouter, Depends, Path, Query

from app.backend.app.api.dependencies import require_roles
from app.backend.app.api.errors import service_error_to_http
from app.backend.app.schemas.admin import (
    AdminAppointmentFilters,
    AdminAppointmentSummary,
    AdminDashboard,
    AdminDoctorSummary,
    AdminEmergencyAlertSummary,
    AdminRoleAssignmentRequest,
    AdminRoleAssignmentResponse,
    AdminStaffSummary,
    AdminStudentSummary,
    AdminUserSummary,
)
from app.backend.app.schemas.auth import AuthenticatedUser
from app.backend.app.services import admin_service

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/dashboard", response_model=AdminDashboard)
def dashboard(
    current_user: AuthenticatedUser = Depends(require_roles("admin")),
) -> AdminDashboard:
    try:
        return admin_service.get_dashboard()
    except Exception as exc:
        raise service_error_to_http(exc) from exc


@router.get("/users", response_model=list[AdminUserSummary])
def users(
    q: str | None = Query(default=None, min_length=2, max_length=120),
    role_name: str | None = Query(default=None, max_length=50),
    limit: int = Query(default=100, ge=1, le=250),
    current_user: AuthenticatedUser = Depends(require_roles("admin")),
) -> list[AdminUserSummary]:
    try:
        return admin_service.list_users(q, role_name, limit)
    except Exception as exc:
        raise service_error_to_http(exc) from exc


@router.patch("/users/{user_id}/role", response_model=AdminRoleAssignmentResponse)
def assign_user_role(
    payload: AdminRoleAssignmentRequest,
    user_id: int = Path(..., gt=0),
    current_user: AuthenticatedUser = Depends(require_roles("admin")),
) -> AdminRoleAssignmentResponse:
    try:
        return admin_service.assign_user_role(
            user_id,
            payload,
            actor_user_id=current_user.user_id,
        )
    except Exception as exc:
        raise service_error_to_http(exc) from exc


@router.get("/appointments", response_model=list[AdminAppointmentSummary])
def appointments(
    status: str | None = Query(default=None, max_length=50),
    from_date: date | None = Query(default=None),
    to_date: date | None = Query(default=None),
    doctor_id: int | None = Query(default=None, gt=0),
    student_id: int | None = Query(default=None, gt=0),
    limit: int = Query(default=100, ge=1, le=250),
    current_user: AuthenticatedUser = Depends(require_roles("admin")),
) -> list[AdminAppointmentSummary]:
    try:
        filters = AdminAppointmentFilters(
            status=status,
            from_date=from_date,
            to_date=to_date,
            doctor_id=doctor_id,
            student_id=student_id,
            limit=limit,
        )
        return admin_service.list_appointments(filters)
    except Exception as exc:
        raise service_error_to_http(exc) from exc


@router.get("/students", response_model=list[AdminStudentSummary])
def students(
    q: str | None = Query(default=None, min_length=2, max_length=120),
    limit: int = Query(default=100, ge=1, le=250),
    current_user: AuthenticatedUser = Depends(require_roles("admin")),
) -> list[AdminStudentSummary]:
    try:
        return admin_service.list_students(q, limit)
    except Exception as exc:
        raise service_error_to_http(exc) from exc


@router.get("/doctors", response_model=list[AdminDoctorSummary])
def doctors(
    q: str | None = Query(default=None, min_length=2, max_length=120),
    limit: int = Query(default=100, ge=1, le=250),
    current_user: AuthenticatedUser = Depends(require_roles("admin")),
) -> list[AdminDoctorSummary]:
    try:
        return admin_service.list_doctors(q, limit)
    except Exception as exc:
        raise service_error_to_http(exc) from exc


@router.get("/staff", response_model=list[AdminStaffSummary])
def staff(
    q: str | None = Query(default=None, min_length=2, max_length=120),
    limit: int = Query(default=100, ge=1, le=250),
    current_user: AuthenticatedUser = Depends(require_roles("admin")),
) -> list[AdminStaffSummary]:
    try:
        return admin_service.list_staff(q, limit)
    except Exception as exc:
        raise service_error_to_http(exc) from exc


@router.get("/emergency-alerts", response_model=list[AdminEmergencyAlertSummary])
def emergency_alerts(
    limit: int = Query(default=50, ge=1, le=250),
    current_user: AuthenticatedUser = Depends(require_roles("admin")),
) -> list[AdminEmergencyAlertSummary]:
    try:
        return admin_service.list_emergency_alerts(limit)
    except Exception as exc:
        raise service_error_to_http(exc) from exc
```

- [ ] **Step 2: Register router**

Modify `app/backend/app/api/api_router.py`:

```python
from app.backend.app.api.routes import (
    admin,
    appointments,
    auth,
    certificates,
    doctors,
    emergencies,
    reports,
    students,
)

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(students.router)
api_router.include_router(doctors.router)
api_router.include_router(appointments.router)
api_router.include_router(emergencies.router)
api_router.include_router(reports.router)
api_router.include_router(certificates.router)
api_router.include_router(admin.router)
```

- [ ] **Step 3: Run admin API tests**

Run:

```powershell
uv run --group dev pytest tests/test_admin_api.py tests/test_api_surface.py -q -p no:cacheprovider
```

Expected: pass.

---

### Task 7: Documentation and TODO Updates

**Files:**
- Modify: `docs/API_NOTES.md`
- Modify: `TODO.md`
- Modify: `CHANGELOG.md`

- [ ] **Step 1: Document backend endpoints**

Add this section to `docs/API_NOTES.md`:

```markdown
## Admin Backend API

`POST /auth/signup` creates a student/patient account by default. The request does not accept a role field; role changes are admin-only.

All admin endpoints require a bearer token for a user with `role_name = admin`.

- `GET /admin/dashboard`
  - Returns high-level infirmary counts: students, doctors, staff, appointment status counts, report count, certificate count, and emergency alert count.
- `GET /admin/users`
  - Query params: `q`, `role_name`, `limit`.
  - Returns users with their current role and linked student/staff profile IDs for role management screens.
- `PATCH /admin/users/{user_id}/role`
  - Body for `student`: `role_name`, `roll_number`, `department`, `year_level`.
  - Body for `doctor`: `role_name`, `employee_number`, optional `specialization`.
  - Body for `staff`: `role_name`, `employee_number`, optional `specialization`.
  - Body for `admin`: `role_name`.
  - Updates the user role transactionally and returns `409 Conflict` if the change would orphan appointment or slot history.
- `GET /admin/appointments`
  - Query params: `status`, `from_date`, `to_date`, `doctor_id`, `student_id`, `limit`.
  - Returns appointment oversight rows with student, doctor, slot, status, reason, and cancellation reason.
- `GET /admin/students`
  - Query params: `q`, `limit`.
  - Returns student directory rows with appointment totals.
- `GET /admin/doctors`
  - Query params: `q`, `limit`.
  - Returns doctor directory rows with current-day availability and appointment counts.
- `GET /admin/staff`
  - Query params: `q`, `limit`.
  - Returns non-doctor staff directory rows.
- `GET /admin/emergency-alerts`
  - Query params: `limit`.
  - Returns latest student emergency alerts.
```

- [ ] **Step 2: Update TODO**

In `TODO.md`, change:

```markdown
[ ] [TOFIX] Build full admin dashboard and admin workflows — blocked on backend admin routes (GET /admin/dashboard, /admin/appointments, /admin/students, /admin/doctors) (GitHub issue #11)
```

to:

```markdown
[x] [TOFIX] [BACKEND] Add admin dashboard API routes — POST /auth/signup defaulting to student/patient plus GET /admin/dashboard, /admin/users, /admin/appointments, /admin/students, /admin/doctors, /admin/staff, /admin/emergency-alerts, and PATCH /admin/users/{user_id}/role with admin-only RBAC (GitHub issue #11)
```

Keep the final project TODO open if frontend UI is still not implemented:

```markdown
[ ] [FINAL] Admin workflow and implementation - frontend admin dashboard remains pending for Claude/Stitch; backend admin routes are available for dashboard metrics, user role assignment, appointment oversight, student/doctor/staff directories, and emergency alert review. (GitHub issue #11)
```

- [ ] **Step 3: Update changelog**

Add a recent entry to `CHANGELOG.md`:

```markdown
[2026-05-17] [ADDED] [Codex] [issue-11-admin-backend] - Added backend admin API plan/implementation for dashboard metrics, appointment oversight, student/doctor/staff directories, emergency alert review, and admin-only RBAC.
```

---

### Task 8: Full Verification

**Files:**
- No new files

- [ ] **Step 1: Run backend tests**

Run:

```powershell
uv run --group dev pytest -q -p no:cacheprovider
```

Expected: all tests pass.

- [ ] **Step 2: Run lint**

Run:

```powershell
uv run --group dev ruff check .
```

Expected:

```text
All checks passed!
```

- [ ] **Step 3: Optional live API smoke**

Start the app:

```powershell
uv run uvicorn app.backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

Login as seeded admin:

```text
admin@college.edu
password123
```

Use Swagger docs:

```text
http://127.0.0.1:8000/docs
```

Authorize with the bearer token and test:

- `POST /auth/signup`
- `GET /admin/dashboard`
- `GET /admin/users`
- `PATCH /admin/users/{user_id}/role`
- `GET /admin/appointments`
- `GET /admin/students`
- `GET /admin/doctors`
- `GET /admin/staff`
- `GET /admin/emergency-alerts`

Expected: admin endpoints return `200` for admin token and `403` for student/doctor tokens. `POST /auth/signup` returns `201` and the response user has `role_name = student`.

---

## Self-Review

Spec coverage:

- Admin dashboard metrics: Task 2, Task 3, Task 5, Task 6.
- Default student/patient signup: Task 1A, Task 2, Task 3A, Task 5A.
- Admin user role assignment: Task 1A, Task 2, Task 3, Task 4, Task 5, Task 6.
- Appointment oversight: Task 1, Task 2, Task 3, Task 5, Task 6.
- Student/doctor/staff directory views: Task 1 through Task 6.
- Emergency alert review: Task 1 through Task 6.
- Admin-only access: Task 1 and Task 6.
- No frontend implementation: explicit scope statement and docs/TODO separation.
- No new database tables: explicit scope statement and query-only implementation.

Placeholder scan:

- No `TBD`, `TODO`, or vague implementation-only placeholders are present.
- Every code-writing step includes concrete code blocks and file paths.

Type consistency:

- Route response models match `app/backend/app/schemas/admin.py`.
- Service function names match route calls and repository calls.
- Repository function names match query function names.
- Test monkeypatch names match `admin_service` functions.
