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
            appointments.appointment_id,
            appointment_slots.slot_date,
            appointment_slots.start_time,
            appointment_slots.end_time,
            students.student_id,
            student_users.name AS student_name,
            appointment_statuses.status_name AS status
        FROM appointments
        INNER JOIN appointment_slots
            ON appointment_slots.slot_id = appointments.slot_id
        INNER JOIN appointment_statuses
            ON appointment_statuses.status_id = appointments.status_id
        INNER JOIN students ON students.student_id = appointments.student_id
        INNER JOIN users AS student_users ON student_users.user_id = students.user_id
        WHERE appointment_slots.staff_id = %s
        ORDER BY appointment_slots.slot_date, appointment_slots.start_time
    """
    return fetch_all(connection, sql, (staff_id,))


def get_appointment_detail(
    connection: Any,
    appointment_id: int,
) -> dict[str, Any] | None:
    sql = """
        SELECT
            appointments.appointment_id,
            appointment_slots.slot_date,
            appointment_slots.start_time,
            appointment_slots.end_time,
            appointment_statuses.status_name AS status,
            students.student_id,
            student_users.name AS student_name,
            student_users.email AS student_email,
            staff.staff_id AS doctor_id,
            doctor_users.name AS doctor_name,
            medical_notes.diagnosis,
            medical_notes.remarks,
            medical_certificates.certificate_id,
            certificate_types.certificate_type
        FROM appointments
        INNER JOIN appointment_slots
            ON appointment_slots.slot_id = appointments.slot_id
        INNER JOIN appointment_statuses
            ON appointment_statuses.status_id = appointments.status_id
        INNER JOIN students ON students.student_id = appointments.student_id
        INNER JOIN users AS student_users ON student_users.user_id = students.user_id
        INNER JOIN staff ON staff.staff_id = appointment_slots.staff_id
        INNER JOIN users AS doctor_users ON doctor_users.user_id = staff.user_id
        LEFT JOIN medical_notes
            ON medical_notes.appointment_id = appointments.appointment_id
        LEFT JOIN medical_certificates
            ON medical_certificates.appointment_id = appointments.appointment_id
        LEFT JOIN certificate_types
            ON certificate_types.certificate_type_id =
                medical_certificates.certificate_type_id
        WHERE appointments.appointment_id = %s
    """
    return fetch_one(connection, sql, (appointment_id,))


def list_patient_history(connection: Any, student_id: int) -> list[dict[str, Any]]:
    sql = """
        SELECT
            appointments.appointment_id,
            appointment_slots.slot_date,
            appointment_slots.start_time,
            appointment_slots.end_time,
            staff.staff_id AS doctor_id,
            doctor_users.name AS doctor_name,
            appointment_statuses.status_name AS status,
            medical_notes.diagnosis,
            medical_notes.remarks,
            medical_certificates.certificate_id,
            certificate_types.certificate_type
        FROM appointments
        INNER JOIN appointment_slots
            ON appointment_slots.slot_id = appointments.slot_id
        INNER JOIN staff ON staff.staff_id = appointment_slots.staff_id
        INNER JOIN users AS doctor_users ON doctor_users.user_id = staff.user_id
        INNER JOIN appointment_statuses
            ON appointment_statuses.status_id = appointments.status_id
        LEFT JOIN medical_notes
            ON medical_notes.appointment_id = appointments.appointment_id
        LEFT JOIN medical_certificates
            ON medical_certificates.appointment_id = appointments.appointment_id
        LEFT JOIN certificate_types
            ON certificate_types.certificate_type_id =
                medical_certificates.certificate_type_id
        WHERE appointments.student_id = %s
        ORDER BY appointment_slots.slot_date DESC, appointment_slots.start_time DESC
    """
    return fetch_all(connection, sql, (student_id,))
