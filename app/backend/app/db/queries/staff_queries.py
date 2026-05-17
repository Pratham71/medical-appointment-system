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
