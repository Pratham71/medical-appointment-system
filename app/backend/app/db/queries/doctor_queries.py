from typing import Any

from app.backend.app.db.queries._helpers import fetch_all, fetch_one


def get_dashboard_counts(connection: Any, staff_id: int) -> dict[str, Any] | None:
    sql = """
        SELECT
            staff.staff_id AS doctor_id,
            users.name AS doctor_name,
            (
                SELECT COUNT(appointments.appointment_id)
                FROM appointments
                INNER JOIN appointment_slots
                    ON appointment_slots.slot_id = appointments.slot_id
                WHERE appointment_slots.staff_id = staff.staff_id
                    AND appointment_slots.slot_date = CURRENT_DATE
            ) AS todays_appointments,
            (
                SELECT COUNT(appointments.appointment_id)
                FROM appointments
                INNER JOIN appointment_slots
                    ON appointment_slots.slot_id = appointments.slot_id
                INNER JOIN appointment_statuses
                    ON appointment_statuses.status_id = appointments.status_id
                WHERE appointment_slots.staff_id = staff.staff_id
                    AND appointment_slots.slot_date >= CURRENT_DATE
                    AND appointment_statuses.status_name = %s
            ) AS upcoming_appointments,
            (
                SELECT COUNT(appointments.appointment_id)
                FROM appointments
                INNER JOIN appointment_slots
                    ON appointment_slots.slot_id = appointments.slot_id
                INNER JOIN appointment_statuses
                    ON appointment_statuses.status_id = appointments.status_id
                WHERE appointment_slots.staff_id = staff.staff_id
                    AND appointment_statuses.status_name = %s
            ) AS completed_appointments,
            (
                SELECT COUNT(DISTINCT appointments.student_id)
                FROM appointments
                INNER JOIN appointment_slots
                    ON appointment_slots.slot_id = appointments.slot_id
                WHERE appointment_slots.staff_id = staff.staff_id
            ) AS total_patients
        FROM staff
        INNER JOIN users ON users.user_id = staff.user_id
        WHERE staff.staff_id = %s
            AND staff.is_doctor = TRUE
    """
    return fetch_one(connection, sql, ("booked", "completed", staff_id))


def list_appointments(connection: Any, staff_id: int) -> list[dict[str, Any]]:
    sql = """
        SELECT
            v_doctor_appointment_summaries.appointment_id,
            v_doctor_appointment_summaries.slot_date,
            v_doctor_appointment_summaries.start_time,
            v_doctor_appointment_summaries.end_time,
            v_doctor_appointment_summaries.student_id,
            v_doctor_appointment_summaries.student_name,
            v_doctor_appointment_summaries.status
        FROM v_doctor_appointment_summaries
        WHERE v_doctor_appointment_summaries.doctor_id = %s
        ORDER BY
            v_doctor_appointment_summaries.slot_date,
            v_doctor_appointment_summaries.start_time
    """
    return fetch_all(connection, sql, (staff_id,))


def get_appointment_detail(
    connection: Any,
    appointment_id: int,
) -> dict[str, Any] | None:
    sql = """
        SELECT
            v_appointment_details.appointment_id,
            v_appointment_details.slot_date,
            v_appointment_details.start_time,
            v_appointment_details.end_time,
            v_appointment_details.status,
            v_appointment_details.student_id,
            v_appointment_details.student_name,
            v_appointment_details.student_email,
            v_appointment_details.doctor_id,
            v_appointment_details.doctor_name,
            v_appointment_details.diagnosis,
            v_appointment_details.remarks,
            v_appointment_details.certificate_id,
            v_appointment_details.certificate_type
        FROM v_appointment_details
        WHERE v_appointment_details.appointment_id = %s
    """
    return fetch_one(connection, sql, (appointment_id,))


def list_patient_history(connection: Any, student_id: int) -> list[dict[str, Any]]:
    sql = """
        SELECT
            v_appointment_details.appointment_id,
            v_appointment_details.slot_date,
            v_appointment_details.start_time,
            v_appointment_details.end_time,
            v_appointment_details.doctor_id,
            v_appointment_details.doctor_name,
            v_appointment_details.status,
            v_appointment_details.diagnosis,
            v_appointment_details.remarks,
            v_appointment_details.certificate_id,
            v_appointment_details.certificate_type
        FROM v_appointment_details
        WHERE v_appointment_details.student_id = %s
        ORDER BY
            v_appointment_details.slot_date DESC,
            v_appointment_details.start_time DESC
    """
    return fetch_all(connection, sql, (student_id,))


def has_doctor_seen_student(
    connection: Any,
    staff_id: int,
    student_id: int,
) -> bool:
    sql = """
        SELECT appointments.appointment_id
        FROM appointments
        INNER JOIN appointment_slots
            ON appointment_slots.slot_id = appointments.slot_id
        WHERE appointment_slots.staff_id = %s
            AND appointments.student_id = %s
        LIMIT 1
    """
    return fetch_one(connection, sql, (staff_id, student_id)) is not None
