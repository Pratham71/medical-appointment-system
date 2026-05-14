from typing import Any

from app.backend.app.db.queries._helpers import fetch_all, fetch_one


def get_dashboard_counts(connection: Any, student_id: int) -> dict[str, Any] | None:
    sql = """
        SELECT
            students.student_id,
            users.name AS student_name,
            (
                SELECT COUNT(appointments.appointment_id)
                FROM appointments
                INNER JOIN appointment_slots
                    ON appointment_slots.slot_id = appointments.slot_id
                INNER JOIN appointment_statuses
                    ON appointment_statuses.status_id = appointments.status_id
                WHERE appointments.student_id = students.student_id
                    AND appointment_statuses.status_name = %s
                    AND appointment_slots.slot_date >= CURRENT_DATE
            ) AS upcoming_appointments,
            (
                SELECT COUNT(appointments.appointment_id)
                FROM appointments
                INNER JOIN appointment_statuses
                    ON appointment_statuses.status_id = appointments.status_id
                WHERE appointments.student_id = students.student_id
                    AND appointment_statuses.status_name = %s
            ) AS completed_appointments,
            (
                SELECT COUNT(medical_notes.note_id)
                FROM medical_notes
                INNER JOIN appointments
                    ON appointments.appointment_id = medical_notes.appointment_id
                WHERE appointments.student_id = students.student_id
            ) AS reports_available,
            (
                SELECT COUNT(medical_certificates.certificate_id)
                FROM medical_certificates
                INNER JOIN appointments
                    ON appointments.appointment_id = medical_certificates.appointment_id
                WHERE appointments.student_id = students.student_id
            ) AS certificates_available
        FROM students
        INNER JOIN users ON users.user_id = students.user_id
        WHERE students.student_id = %s
    """
    return fetch_one(connection, sql, ("booked", "completed", student_id))


def get_next_appointment(connection: Any, student_id: int) -> dict[str, Any] | None:
    sql = """
        SELECT
            appointments.appointment_id,
            appointment_slots.slot_date,
            appointment_slots.start_time,
            appointment_slots.end_time,
            staff.staff_id AS doctor_id,
            doctor_users.name AS doctor_name,
            appointment_statuses.status_name AS status
        FROM appointments
        INNER JOIN appointment_slots
            ON appointment_slots.slot_id = appointments.slot_id
        INNER JOIN appointment_statuses
            ON appointment_statuses.status_id = appointments.status_id
        INNER JOIN staff ON staff.staff_id = appointment_slots.staff_id
        INNER JOIN users AS doctor_users ON doctor_users.user_id = staff.user_id
        WHERE appointments.student_id = %s
            AND appointment_statuses.status_name = %s
            AND appointment_slots.slot_date >= CURRENT_DATE
        ORDER BY appointment_slots.slot_date, appointment_slots.start_time
        LIMIT 1
    """
    return fetch_one(connection, sql, (student_id, "booked"))


def list_appointments(connection: Any, student_id: int) -> list[dict[str, Any]]:
    sql = """
        SELECT
            appointments.appointment_id,
            appointment_slots.slot_date,
            appointment_slots.start_time,
            appointment_slots.end_time,
            staff.staff_id AS doctor_id,
            doctor_users.name AS doctor_name,
            appointment_statuses.status_name AS status
        FROM appointments
        INNER JOIN appointment_slots
            ON appointment_slots.slot_id = appointments.slot_id
        INNER JOIN appointment_statuses
            ON appointment_statuses.status_id = appointments.status_id
        INNER JOIN staff ON staff.staff_id = appointment_slots.staff_id
        INNER JOIN users AS doctor_users ON doctor_users.user_id = staff.user_id
        WHERE appointments.student_id = %s
        ORDER BY appointment_slots.slot_date DESC, appointment_slots.start_time DESC
    """
    return fetch_all(connection, sql, (student_id,))


def list_reports(connection: Any, student_id: int) -> list[dict[str, Any]]:
    sql = """
        SELECT
            appointments.appointment_id,
            appointment_slots.slot_date AS appointment_date,
            staff.staff_id AS doctor_id,
            doctor_users.name AS doctor_name,
            medical_notes.diagnosis,
            medical_notes.remarks,
            COUNT(prescription_items.item_id) AS prescription_count
        FROM appointments
        INNER JOIN appointment_slots
            ON appointment_slots.slot_id = appointments.slot_id
        INNER JOIN staff ON staff.staff_id = appointment_slots.staff_id
        INNER JOIN users AS doctor_users ON doctor_users.user_id = staff.user_id
        LEFT JOIN medical_notes
            ON medical_notes.appointment_id = appointments.appointment_id
        LEFT JOIN prescriptions
            ON prescriptions.appointment_id = appointments.appointment_id
        LEFT JOIN prescription_items
            ON prescription_items.prescription_id = prescriptions.prescription_id
        WHERE appointments.student_id = %s
            AND medical_notes.note_id IS NOT NULL
        GROUP BY
            appointments.appointment_id,
            appointment_slots.slot_date,
            staff.staff_id,
            doctor_users.name,
            medical_notes.diagnosis,
            medical_notes.remarks
        ORDER BY appointment_slots.slot_date DESC
    """
    return fetch_all(connection, sql, (student_id,))


def list_certificates(connection: Any, student_id: int) -> list[dict[str, Any]]:
    sql = """
        SELECT
            medical_certificates.certificate_id,
            appointments.appointment_id,
            certificate_types.certificate_type_id,
            certificate_types.certificate_type,
            medical_certificates.issue_date,
            staff.staff_id AS doctor_id,
            doctor_users.name AS doctor_name,
            appointment_slots.slot_date AS appointment_date
        FROM medical_certificates
        INNER JOIN appointments
            ON appointments.appointment_id = medical_certificates.appointment_id
        INNER JOIN certificate_types
            ON certificate_types.certificate_type_id =
                medical_certificates.certificate_type_id
        INNER JOIN appointment_slots
            ON appointment_slots.slot_id = appointments.slot_id
        INNER JOIN staff ON staff.staff_id = appointment_slots.staff_id
        INNER JOIN users AS doctor_users ON doctor_users.user_id = staff.user_id
        WHERE appointments.student_id = %s
        ORDER BY medical_certificates.issue_date DESC
    """
    return fetch_all(connection, sql, (student_id,))
