from typing import Any

from app.backend.app.db.queries._helpers import fetch_one


def get_appointment_notification_context(
    connection: Any,
    appointment_id: int,
) -> dict[str, Any] | None:
    """Fetch the data needed to compose an appointment email notification.

    Args:
        appointment_id: Primary key of the appointment.

    Returns:
        A dict with appointment_id, student_name, student_email, doctor_name,
        slot_date, start_time, end_time, reason, and cancellation_reason,
        or None if the appointment does not exist.
    """
    sql = """
        SELECT
            appointments.appointment_id,
            student_users.name AS student_name,
            student_users.email AS student_email,
            doctor_users.name AS doctor_name,
            appointment_slots.slot_date,
            appointment_slots.start_time,
            appointment_slots.end_time,
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
        WHERE appointments.appointment_id = %s
    """
    return fetch_one(connection, sql, (appointment_id,))
