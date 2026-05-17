from mysql.connector import IntegrityError

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
    role_filter = role_name.strip().lower() if role_name else None
    rows = admin_repo.list_users(search_text, role_filter, limit)
    return [AdminUserSummary(**row) for row in rows]


def assign_user_role(
    user_id: int,
    payload: AdminRoleAssignmentRequest,
    actor_user_id: int,
) -> AdminRoleAssignmentResponse:
    if user_id == actor_user_id:
        raise ConflictError("Admins cannot change their own role")

    try:
        result = admin_repo.assign_user_role(
            user_id=user_id,
            role_name=payload.role_name,
            roll_number=payload.roll_number,
            department=payload.department,
            year_level=payload.year_level,
            employee_number=payload.employee_number,
            specialization=payload.specialization,
        )
    except IntegrityError as exc:
        raise ConflictError("Profile identifier already exists") from exc

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
