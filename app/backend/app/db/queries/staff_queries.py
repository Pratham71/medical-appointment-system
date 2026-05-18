from datetime import date
from typing import Any

from app.backend.app.db.queries._helpers import fetch_all, fetch_one


def get_dashboard_counts(connection: Any) -> dict[str, Any] | None:
    """Fetch system-wide appointment counts for the staff dashboard.

    Returns:
        A dict with appointments_today, booked_appointments, cancelled_today,
        and emergency_alerts, or None if the query returns no rows.
    """
    sql = """
        SELECT
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
                INNER JOIN appointment_slots
                    ON appointment_slots.slot_id = appointments.slot_id
                INNER JOIN appointment_statuses
                    ON appointment_statuses.status_id = appointments.status_id
                WHERE appointment_slots.slot_date = CURRENT_DATE
                    AND appointment_statuses.status_name = %s
            ) AS cancelled_today,
            (
                SELECT COUNT(emergency_alerts.alert_id)
                FROM emergency_alerts
            ) AS emergency_alerts
    """
    return fetch_one(connection, sql, ("booked", "cancelled"))


def list_appointments(
    connection: Any,
    *,
    status: str | None,
    from_date: date | None,
    to_date: date | None,
    limit: int,
) -> list[dict[str, Any]]:
    """Return a filtered, paginated list of appointments for staff review.

    Args:
        status: Optional appointment status to filter by.
        from_date: Optional start of the date range (inclusive).
        to_date: Optional end of the date range (inclusive).
        limit: Maximum number of rows to return.

    Returns:
        List of appointment summary dicts ordered by slot_date and time descending.
    """
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
        limit,
    ]
    return fetch_all(connection, sql, tuple(params))


def list_walk_ins(
    connection: Any,
    *,
    status: str | None,
    from_date: date | None,
    to_date: date | None,
    limit: int,
) -> list[dict[str, Any]]:
    """Return staff-created walk-in bookings.

    Args:
        status: Optional appointment status to filter by.
        from_date: Optional start of the date range (inclusive).
        to_date: Optional end of the date range (inclusive).
        limit: Maximum number of rows to return.

    Returns:
        List of walk-in appointment summary dicts ordered by newest slot first.
    """
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
        WHERE appointments.reason LIKE %s
            AND (%s IS NULL OR appointment_statuses.status_name = %s)
            AND (%s IS NULL OR appointment_slots.slot_date >= %s)
            AND (%s IS NULL OR appointment_slots.slot_date <= %s)
        ORDER BY
            appointment_slots.slot_date DESC,
            appointment_slots.start_time DESC,
            appointments.appointment_id DESC
        LIMIT %s
    """
    params = [
        "Walk-in consultation%",
        status,
        status,
        from_date,
        from_date,
        to_date,
        to_date,
        limit,
    ]
    return fetch_all(connection, sql, tuple(params))


def search_patients(
    connection: Any,
    search_text: str,
    limit: int,
) -> list[dict[str, Any]]:
    """Search existing patient profiles for staff walk-in booking.

    Args:
        search_text: Partial patient name, email, or roll number.
        limit: Maximum number of rows to return.

    Returns:
        List of existing patient profile summary dicts.
    """
    pattern = f"%{search_text}%"
    sql = """
        SELECT
            students.student_id,
            users.name AS student_name,
            users.email,
            students.roll_number,
            students.department,
            students.year_level,
            roles.role_name
        FROM students
        INNER JOIN users
            ON users.user_id = students.user_id
        INNER JOIN roles
            ON roles.role_id = users.role_id
        WHERE users.is_active = TRUE
            AND roles.role_name IN (
                'student',
                'professor',
                'college-staff',
                'hostel-staff'
            )
            AND (
                users.name LIKE %s
                OR users.email LIKE %s
                OR students.roll_number LIKE %s
            )
        ORDER BY users.name, students.roll_number
        LIMIT %s
    """
    return fetch_all(connection, sql, (pattern, pattern, pattern, limit))


def get_patient_by_student_id(
    connection: Any,
    student_id: int,
) -> dict[str, Any] | None:
    """Return an active patient profile by student_id.

    Args:
        student_id: Primary key of the patient profile.

    Returns:
        Patient profile dict if the student_id belongs to an active patient role,
        otherwise None.
    """
    sql = """
        SELECT
            students.student_id,
            users.name AS student_name,
            users.email,
            students.roll_number,
            students.department,
            students.year_level,
            roles.role_name
        FROM students
        INNER JOIN users
            ON users.user_id = students.user_id
        INNER JOIN roles
            ON roles.role_id = users.role_id
        WHERE students.student_id = %s
            AND users.is_active = TRUE
            AND roles.role_name IN (
                'student',
                'professor',
                'college-staff',
                'hostel-staff'
            )
    """
    return fetch_one(connection, sql, (student_id,))
