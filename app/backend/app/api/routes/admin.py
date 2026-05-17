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
    AdminUserStatusResponse,
    AdminUserSummary,
    EmergencyAlertResolveRequest,
)
from app.backend.app.schemas.auth import AuthenticatedUser
from app.backend.app.services import admin_service

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/dashboard", response_model=AdminDashboard)
def dashboard(
    current_user: AuthenticatedUser = Depends(require_roles("admin")),
) -> AdminDashboard:
    """Return system-wide aggregate statistics for the admin dashboard.

    Args:
        current_user: An authenticated admin user.

    Returns:
        An AdminDashboard with all entity counts.
    """
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
    """Return a filtered list of users for admin user management.

    Args:
        q: Optional search term matched against name and email.
        role_name: Optional role to filter by.
        limit: Maximum number of results (1-250, default 100).
        current_user: An authenticated admin user.

    Returns:
        List of AdminUserSummary objects.
    """
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
    """Reassign a user to a new role and update the linked profile.

    Args:
        payload: Role assignment data including role name and profile fields.
        user_id: Primary key of the user to reassign.
        current_user: An authenticated admin user.

    Returns:
        An AdminRoleAssignmentResponse with the updated user and profile info.

    Raises:
        HTTPException: 409 if the admin tries to change their own role or there
            is a profile conflict; 404 if the user is not found.
    """
    try:
        return admin_service.assign_user_role(
            user_id,
            payload,
            actor_user_id=current_user.user_id,
        )
    except Exception as exc:
        raise service_error_to_http(exc) from exc


@router.patch("/users/{user_id}/deactivate", response_model=AdminUserStatusResponse)
def deactivate_user(
    user_id: int = Path(..., gt=0),
    current_user: AuthenticatedUser = Depends(require_roles("admin")),
) -> AdminUserStatusResponse:
    """Deactivate a user account.

    Args:
        user_id: Primary key of the user to deactivate.
        current_user: An authenticated admin user.

    Returns:
        An AdminUserStatusResponse confirming deactivation.

    Raises:
        HTTPException: 409 if the admin tries to deactivate their own account;
            404 if the user is not found.
    """
    try:
        return admin_service.deactivate_user(
            user_id,
            actor_user_id=current_user.user_id,
        )
    except Exception as exc:
        raise service_error_to_http(exc) from exc


@router.patch("/users/{user_id}/activate", response_model=AdminUserStatusResponse)
def activate_user(
    user_id: int = Path(..., gt=0),
    current_user: AuthenticatedUser = Depends(require_roles("admin")),
) -> AdminUserStatusResponse:
    """Activate a previously deactivated user account.

    Args:
        user_id: Primary key of the user to activate.
        current_user: An authenticated admin user.

    Returns:
        An AdminUserStatusResponse confirming activation.

    Raises:
        HTTPException: 404 if the user is not found.
    """
    try:
        return admin_service.activate_user(
            user_id,
            actor_user_id=current_user.user_id,
        )
    except Exception as exc:
        raise service_error_to_http(exc) from exc


@router.delete("/users/{user_id}", response_model=AdminUserStatusResponse)
def delete_user(
    user_id: int = Path(..., gt=0),
    current_user: AuthenticatedUser = Depends(require_roles("admin")),
) -> AdminUserStatusResponse:
    """Soft-delete (deactivate) a user account.

    This is an alias for the deactivate endpoint kept for REST convention.

    Args:
        user_id: Primary key of the user to deactivate.
        current_user: An authenticated admin user.

    Returns:
        An AdminUserStatusResponse confirming deactivation.

    Raises:
        HTTPException: 409 if the admin tries to delete their own account;
            404 if the user is not found.
    """
    try:
        return admin_service.deactivate_user(
            user_id,
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
    """Return a filtered list of appointments for admin review.

    Args:
        status: Optional appointment status to filter by.
        from_date: Optional start of the date range (inclusive).
        to_date: Optional end of the date range (inclusive).
        doctor_id: Optional staff_id to scope results to one doctor.
        student_id: Optional student_id to scope results to one student.
        limit: Maximum number of results (1-250, default 100).
        current_user: An authenticated admin user.

    Returns:
        List of AdminAppointmentSummary objects.

    Raises:
        HTTPException: 422 if to_date is before from_date.
    """
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
    """Return a filtered list of student/patient users.

    Args:
        q: Optional search term matched against name, email, or roll number.
        limit: Maximum number of results (1-250, default 100).
        current_user: An authenticated admin user.

    Returns:
        List of AdminStudentSummary objects with appointment counts.
    """
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
    """Return a filtered list of doctors with today's availability summary.

    Args:
        q: Optional search term matched against name, email, employee number,
            or specialization.
        limit: Maximum number of results (1-250, default 100).
        current_user: An authenticated admin user.

    Returns:
        List of AdminDoctorSummary objects.
    """
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
    """Return a filtered list of non-doctor staff members.

    Args:
        q: Optional search term matched against name, email, or employee number.
        limit: Maximum number of results (1-250, default 100).
        current_user: An authenticated admin user.

    Returns:
        List of AdminStaffSummary objects.
    """
    try:
        return admin_service.list_staff(q, limit)
    except Exception as exc:
        raise service_error_to_http(exc) from exc


@router.get("/emergency-alerts", response_model=list[AdminEmergencyAlertSummary])
def emergency_alerts(
    limit: int = Query(default=50, ge=1, le=250),
    current_user: AuthenticatedUser = Depends(require_roles("admin", "staff", "doctor")),
) -> list[AdminEmergencyAlertSummary]:
    """Return the most recent emergency alerts (accessible to admin, staff, and doctors).

    Args:
        limit: Maximum number of results (1-250, default 50).
        current_user: An authenticated admin, staff, or doctor user.

    Returns:
        List of AdminEmergencyAlertSummary objects ordered by created_at descending.
    """
    try:
        return admin_service.list_emergency_alerts(limit)
    except Exception as exc:
        raise service_error_to_http(exc) from exc


@router.patch(
    "/emergency-alerts/{alert_id}/acknowledge",
    response_model=AdminEmergencyAlertSummary,
)
def acknowledge_emergency_alert(
    alert_id: int = Path(..., gt=0),
    current_user: AuthenticatedUser = Depends(require_roles("admin", "staff", "doctor")),
) -> AdminEmergencyAlertSummary:
    """Mark an emergency alert as acknowledged.

    Args:
        alert_id: Primary key of the emergency alert.
        current_user: An authenticated admin, staff, or doctor user.

    Returns:
        An AdminEmergencyAlertSummary with updated acknowledgement timestamps.

    Raises:
        HTTPException: 404 if the alert does not exist.
    """
    try:
        return admin_service.acknowledge_emergency_alert(
            alert_id,
            actor_user_id=current_user.user_id,
        )
    except Exception as exc:
        raise service_error_to_http(exc) from exc


@router.patch(
    "/emergency-alerts/{alert_id}/resolve",
    response_model=AdminEmergencyAlertSummary,
)
def resolve_emergency_alert(
    payload: EmergencyAlertResolveRequest,
    alert_id: int = Path(..., gt=0),
    current_user: AuthenticatedUser = Depends(require_roles("admin", "staff", "doctor")),
) -> AdminEmergencyAlertSummary:
    """Mark an emergency alert as resolved with an optional resolution note.

    Args:
        payload: Resolution data containing an optional free-text note.
        alert_id: Primary key of the emergency alert.
        current_user: An authenticated admin, staff, or doctor user.

    Returns:
        An AdminEmergencyAlertSummary with updated resolution timestamps and note.

    Raises:
        HTTPException: 404 if the alert does not exist.
    """
    try:
        return admin_service.resolve_emergency_alert(
            alert_id,
            payload,
            actor_user_id=current_user.user_id,
        )
    except Exception as exc:
        raise service_error_to_http(exc) from exc
