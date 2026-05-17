from datetime import date
from typing import Any

from app.backend.app.db import session
from app.backend.app.db.queries import admin_queries


_PATIENT_ROLES = {"student", "professor", "college-staff", "hostel-staff"}


def get_dashboard_counts() -> dict[str, Any] | None:
    """Fetch system-wide aggregate statistics for the admin dashboard.

    Returns:
        A dict with all admin dashboard counters, or None if no rows are returned.
    """
    with session.connection_scope() as connection:
        return admin_queries.get_dashboard_counts(connection)


def list_users(
    search_text: str | None,
    role_name: str | None,
    limit: int,
) -> list[dict[str, Any]]:
    """Return a filtered, paginated list of users for admin user management.

    Args:
        search_text: Optional partial name or email to match.
        role_name: Optional role to filter by.
        limit: Maximum number of rows to return.

    Returns:
        List of user summary dicts with profile IDs and active status.
    """
    with session.connection_scope() as connection:
        return admin_queries.list_users(
            connection,
            search_text=search_text,
            role_name=role_name,
            limit=limit,
        )


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
    """Reassign a user to a new role and update or swap the linked profile in one transaction.

    Args:
        user_id: Primary key of the user account.
        role_name: Target role name (e.g. "student", "doctor", "admin").
        roll_number: Required for patient roles; the enrollment number.
        department: Required for patient roles; the academic department.
        year_level: Required for patient roles; year of study (1-based).
        employee_number: Required for staff/doctor roles; the employee number.
        specialization: Optional for doctor roles; medical specialization.

    Returns:
        The post-assignment user summary dict, a conflict dict if the user has
        appointment/slot history that prevents profile removal, or None if the
        user or target role was not found.
    """
    with session.transaction_scope() as connection:
        context = admin_queries.get_user_role_context(connection, user_id)
        if context is None:
            return None

        role = admin_queries.get_role_id(connection, role_name)
        if role is None:
            return None

        student_appointments = int(context["student_appointment_count"] or 0)
        staff_slots = int(context["staff_slot_count"] or 0)
        if role_name not in _PATIENT_ROLES and student_appointments > 0:
            return {
                "conflict": True,
                "message": "Cannot remove patient profile with appointment history",
            }
        if role_name not in {"doctor", "staff"} and staff_slots > 0:
            return {
                "conflict": True,
                "message": "Cannot remove staff profile with appointment slots",
            }

        admin_queries.update_user_role(
            connection,
            user_id=user_id,
            role_id=int(role["role_id"]),
        )

        if role_name in _PATIENT_ROLES:
            _save_patient_profile(
                connection,
                user_id=user_id,
                roll_number=roll_number or "",
                department=department or "",
                year_level=year_level or 1,
            )
            if context["staff_id"] is not None:
                admin_queries.delete_staff_profile(connection, user_id)
        elif role_name in {"doctor", "staff"}:
            _save_staff_profile(
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


def set_user_active_status(
    *,
    user_id: int,
    is_active: bool,
) -> dict[str, Any] | None:
    """Set the is_active flag on a user account.

    Args:
        user_id: Primary key of the user account.
        is_active: True to activate, False to deactivate.

    Returns:
        A dict with user_id and is_active, or None if the user does not exist.
    """
    with session.transaction_scope() as connection:
        context = admin_queries.get_user_status_context(connection, user_id)
        if context is None:
            return None
        admin_queries.update_user_active_status(
            connection,
            user_id=user_id,
            is_active=is_active,
        )
        return {
            "user_id": user_id,
            "is_active": is_active,
        }


def list_appointments(
    *,
    status: str | None,
    from_date: date | None,
    to_date: date | None,
    doctor_id: int | None,
    student_id: int | None,
    limit: int,
) -> list[dict[str, Any]]:
    """Return a filtered, paginated list of appointments for admin review.

    Args:
        status: Optional appointment status to filter by.
        from_date: Optional start of the date range (inclusive).
        to_date: Optional end of the date range (inclusive).
        doctor_id: Optional staff_id to scope results to one doctor.
        student_id: Optional student_id to scope results to one student.
        limit: Maximum number of rows to return.

    Returns:
        List of appointment summary dicts ordered by slot_date descending.
    """
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
    """Return a filtered, paginated list of student/patient users.

    Args:
        search_text: Optional partial name, email, or roll number to match.
        limit: Maximum number of rows to return.

    Returns:
        List of student summary dicts with appointment counts.
    """
    with session.connection_scope() as connection:
        return admin_queries.list_students(
            connection,
            search_text=search_text,
            limit=limit,
        )


def list_doctors(search_text: str | None, limit: int) -> list[dict[str, Any]]:
    """Return a filtered, paginated list of doctors with today's availability summary.

    Args:
        search_text: Optional partial name, email, employee number, or specialization to match.
        limit: Maximum number of rows to return.

    Returns:
        List of doctor summary dicts with appointment counts.
    """
    with session.connection_scope() as connection:
        return admin_queries.list_doctors(
            connection,
            search_text=search_text,
            limit=limit,
        )


def list_staff(search_text: str | None, limit: int) -> list[dict[str, Any]]:
    """Return a filtered, paginated list of non-doctor staff members.

    Args:
        search_text: Optional partial name, email, or employee number to match.
        limit: Maximum number of rows to return.

    Returns:
        List of staff summary dicts.
    """
    with session.connection_scope() as connection:
        return admin_queries.list_staff(
            connection,
            search_text=search_text,
            limit=limit,
        )


def list_emergency_alerts(limit: int) -> list[dict[str, Any]]:
    """Return the most recent emergency alerts across all students.

    Args:
        limit: Maximum number of rows to return.

    Returns:
        List of emergency alert summary dicts.
    """
    with session.connection_scope() as connection:
        return admin_queries.list_emergency_alerts(connection, limit=limit)


def acknowledge_emergency_alert(
    *,
    alert_id: int,
    actor_user_id: int,
) -> dict[str, Any] | None:
    """Mark an emergency alert as acknowledged in a transaction and return the summary.

    Args:
        alert_id: Primary key of the emergency alert.
        actor_user_id: user_id of the staff/admin performing the acknowledgement.

    Returns:
        The updated alert summary dict, or None if the alert does not exist.
    """
    with session.transaction_scope() as connection:
        context = admin_queries.get_emergency_alert_for_update(connection, alert_id)
        if context is None:
            return None
        admin_queries.acknowledge_emergency_alert(
            connection,
            alert_id=alert_id,
            actor_user_id=actor_user_id,
        )
        return admin_queries.get_emergency_alert_summary(connection, alert_id)


def resolve_emergency_alert(
    *,
    alert_id: int,
    actor_user_id: int,
    resolution_note: str | None,
) -> dict[str, Any] | None:
    """Mark an emergency alert as resolved in a transaction and return the summary.

    Args:
        alert_id: Primary key of the emergency alert.
        actor_user_id: user_id of the staff/admin performing the resolution.
        resolution_note: Optional human-readable note about the resolution.

    Returns:
        The updated alert summary dict, or None if the alert does not exist.
    """
    with session.transaction_scope() as connection:
        context = admin_queries.get_emergency_alert_for_update(connection, alert_id)
        if context is None:
            return None
        admin_queries.resolve_emergency_alert(
            connection,
            alert_id=alert_id,
            actor_user_id=actor_user_id,
            resolution_note=resolution_note,
        )
        return admin_queries.get_emergency_alert_summary(connection, alert_id)


def _save_patient_profile(
    connection: Any,
    *,
    user_id: int,
    roll_number: str,
    department: str,
    year_level: int,
) -> None:
    """Insert or update the student profile for a user within an open transaction.

    Args:
        connection: Active MySQL connection from the pool.
        user_id: Foreign-key ID of the user account.
        roll_number: Enrollment/roll number.
        department: Academic department.
        year_level: Year of study (1-based).
    """
    profile = admin_queries.get_student_profile_by_user_id(connection, user_id)
    if profile is None:
        admin_queries.insert_student_profile(
            connection,
            user_id=user_id,
            roll_number=roll_number,
            department=department,
            year_level=year_level,
        )
    else:
        admin_queries.upsert_student_profile(
            connection,
            user_id=user_id,
            roll_number=roll_number,
            department=department,
            year_level=year_level,
        )


def _save_staff_profile(
    connection: Any,
    *,
    user_id: int,
    employee_number: str,
    specialization: str | None,
    is_doctor: bool,
) -> None:
    """Insert or update the staff profile for a user within an open transaction.

    Args:
        connection: Active MySQL connection from the pool.
        user_id: Foreign-key ID of the user account.
        employee_number: Institutional employee number.
        specialization: Medical specialization, or None for non-doctors.
        is_doctor: True if the staff member is a doctor.
    """
    profile = admin_queries.get_staff_profile_by_user_id(connection, user_id)
    if profile is None:
        admin_queries.insert_staff_profile(
            connection,
            user_id=user_id,
            employee_number=employee_number,
            specialization=specialization,
            is_doctor=is_doctor,
        )
    else:
        admin_queries.upsert_staff_profile(
            connection,
            user_id=user_id,
            employee_number=employee_number,
            specialization=specialization,
            is_doctor=is_doctor,
        )
