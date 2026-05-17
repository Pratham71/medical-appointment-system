from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Path, Query

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
    if from_date is not None and to_date is not None and to_date < from_date:
        raise HTTPException(status_code=422, detail="to_date cannot be before from_date")
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
