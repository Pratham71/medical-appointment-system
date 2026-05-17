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
    AdminUserStatusResponse,
    AdminUserSummary,
    EmergencyAlertResolveRequest,
)


def get_dashboard() -> AdminDashboard:
    """Return system-wide aggregate statistics for the admin dashboard.

    Returns:
        An AdminDashboard object with counts across all entities.
    """
    row = admin_repo.get_dashboard_counts() or {}
    return AdminDashboard(**row)


def list_users(
    q: str | None,
    role_name: str | None,
    limit: int,
) -> list[AdminUserSummary]:
    """Return a filtered, paginated list of users for admin user management.

    Args:
        q: Optional search term matched against name and email.
        role_name: Optional role to filter by.
        limit: Maximum number of results to return.

    Returns:
        List of AdminUserSummary objects.
    """
    search_text = q.strip() if q else None
    role_filter = role_name.strip().lower() if role_name else None
    rows = admin_repo.list_users(search_text, role_filter, limit)
    return [AdminUserSummary(**row) for row in rows]


def assign_user_role(
    user_id: int,
    payload: AdminRoleAssignmentRequest,
    actor_user_id: int,
) -> AdminRoleAssignmentResponse:
    """Reassign a user to a new role, updating the linked profile accordingly.

    Args:
        user_id: Primary key of the user to reassign.
        payload: Role assignment data including role name and optional profile fields.
        actor_user_id: user_id of the admin performing the action.

    Returns:
        An AdminRoleAssignmentResponse with the updated user and profile info.

    Raises:
        ConflictError: If the admin tries to change their own role, or there is a
            profile identifier conflict.
        NotFoundError: If the target user is not found.
    """
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


def deactivate_user(
    user_id: int,
    actor_user_id: int,
) -> AdminUserStatusResponse:
    """Deactivate a user account.

    Args:
        user_id: Primary key of the user to deactivate.
        actor_user_id: user_id of the admin performing the action.

    Returns:
        An AdminUserStatusResponse confirming deactivation.

    Raises:
        ConflictError: If the admin tries to deactivate their own account.
        NotFoundError: If the target user is not found.
    """
    return _set_user_active_status(
        user_id,
        actor_user_id=actor_user_id,
        is_active=False,
        message="User deactivated",
    )


def activate_user(
    user_id: int,
    actor_user_id: int,
) -> AdminUserStatusResponse:
    """Activate a previously deactivated user account.

    Args:
        user_id: Primary key of the user to activate.
        actor_user_id: user_id of the admin performing the action.

    Returns:
        An AdminUserStatusResponse confirming activation.

    Raises:
        NotFoundError: If the target user is not found.
    """
    return _set_user_active_status(
        user_id,
        actor_user_id=actor_user_id,
        is_active=True,
        message="User activated",
    )


def _set_user_active_status(
    user_id: int,
    *,
    actor_user_id: int,
    is_active: bool,
    message: str,
) -> AdminUserStatusResponse:
    """Set the active status of a user account and return the result.

    Args:
        user_id: Primary key of the user account.
        actor_user_id: user_id of the admin performing the action.
        is_active: True to activate, False to deactivate.
        message: Confirmation message to include in the response.

    Returns:
        An AdminUserStatusResponse with the updated status and message.

    Raises:
        ConflictError: If an admin attempts to deactivate their own account.
        NotFoundError: If the target user is not found.
    """
    if user_id == actor_user_id and not is_active:
        raise ConflictError("Admins cannot deactivate their own account")

    result = admin_repo.set_user_active_status(
        user_id=user_id,
        is_active=is_active,
    )
    if result is None:
        raise NotFoundError("User was not found")
    return AdminUserStatusResponse(**result, message=message)


def list_appointments(
    filters: AdminAppointmentFilters,
) -> list[AdminAppointmentSummary]:
    """Return a filtered list of appointments for admin review.

    Args:
        filters: Filter criteria including status, date range, doctor/student IDs,
            and pagination limit.

    Returns:
        List of AdminAppointmentSummary objects.
    """
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
    """Return a filtered list of student/patient users.

    Args:
        q: Optional search term matched against name, email, or roll number.
        limit: Maximum number of results to return.

    Returns:
        List of AdminStudentSummary objects.
    """
    search_text = q.strip() if q else None
    rows = admin_repo.list_students(search_text, limit)
    return [AdminStudentSummary(**row) for row in rows]


def list_doctors(q: str | None, limit: int) -> list[AdminDoctorSummary]:
    """Return a filtered list of doctors with today's availability summary.

    Args:
        q: Optional search term matched against name, email, employee number, or specialization.
        limit: Maximum number of results to return.

    Returns:
        List of AdminDoctorSummary objects.
    """
    search_text = q.strip() if q else None
    rows = admin_repo.list_doctors(search_text, limit)
    return [AdminDoctorSummary(**row) for row in rows]


def list_staff(q: str | None, limit: int) -> list[AdminStaffSummary]:
    """Return a filtered list of non-doctor staff members.

    Args:
        q: Optional search term matched against name, email, or employee number.
        limit: Maximum number of results to return.

    Returns:
        List of AdminStaffSummary objects.
    """
    search_text = q.strip() if q else None
    rows = admin_repo.list_staff(search_text, limit)
    return [AdminStaffSummary(**row) for row in rows]


def list_emergency_alerts(limit: int) -> list[AdminEmergencyAlertSummary]:
    """Return the most recent emergency alerts across all students.

    Args:
        limit: Maximum number of results to return.

    Returns:
        List of AdminEmergencyAlertSummary objects.
    """
    rows = admin_repo.list_emergency_alerts(limit)
    return [AdminEmergencyAlertSummary(**row) for row in rows]


def acknowledge_emergency_alert(
    alert_id: int,
    *,
    actor_user_id: int,
) -> AdminEmergencyAlertSummary:
    """Mark an emergency alert as acknowledged and return the updated summary.

    Args:
        alert_id: Primary key of the emergency alert.
        actor_user_id: user_id of the staff/admin acknowledging the alert.

    Returns:
        An AdminEmergencyAlertSummary with updated timestamps.

    Raises:
        NotFoundError: If the alert does not exist.
    """
    result = admin_repo.acknowledge_emergency_alert(
        alert_id=alert_id,
        actor_user_id=actor_user_id,
    )
    if result is None:
        raise NotFoundError("Emergency alert was not found")
    return AdminEmergencyAlertSummary(**result)


def resolve_emergency_alert(
    alert_id: int,
    payload: EmergencyAlertResolveRequest,
    *,
    actor_user_id: int,
) -> AdminEmergencyAlertSummary:
    """Mark an emergency alert as resolved and return the updated summary.

    Args:
        alert_id: Primary key of the emergency alert.
        payload: Resolution data containing an optional resolution note.
        actor_user_id: user_id of the staff/admin resolving the alert.

    Returns:
        An AdminEmergencyAlertSummary with updated timestamps and resolution note.

    Raises:
        NotFoundError: If the alert does not exist.
    """
    result = admin_repo.resolve_emergency_alert(
        alert_id=alert_id,
        actor_user_id=actor_user_id,
        resolution_note=(
            payload.resolution_note.strip()
            if payload.resolution_note and payload.resolution_note.strip()
            else None
        ),
    )
    if result is None:
        raise NotFoundError("Emergency alert was not found")
    return AdminEmergencyAlertSummary(**result)
