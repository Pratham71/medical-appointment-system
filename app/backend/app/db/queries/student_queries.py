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
            v_appointment_details.appointment_id,
            v_appointment_details.slot_date,
            v_appointment_details.start_time,
            v_appointment_details.end_time,
            v_appointment_details.doctor_id,
            v_appointment_details.doctor_name,
            v_appointment_details.status
        FROM v_appointment_details
        WHERE v_appointment_details.student_id = %s
            AND v_appointment_details.status = %s
            AND v_appointment_details.slot_date >= CURRENT_DATE
        ORDER BY v_appointment_details.slot_date, v_appointment_details.start_time
        LIMIT 1
    """
    return fetch_one(connection, sql, (student_id, "booked"))


def list_appointments(connection: Any, student_id: int) -> list[dict[str, Any]]:
    sql = """
        SELECT
            v_appointment_details.appointment_id,
            v_appointment_details.slot_date,
            v_appointment_details.start_time,
            v_appointment_details.end_time,
            v_appointment_details.doctor_id,
            v_appointment_details.doctor_name,
            v_appointment_details.status,
            v_appointment_details.reason
        FROM v_appointment_details
        WHERE v_appointment_details.student_id = %s
        ORDER BY
            v_appointment_details.slot_date DESC,
            v_appointment_details.start_time DESC
    """
    return fetch_all(connection, sql, (student_id,))


def list_reports(connection: Any, student_id: int) -> list[dict[str, Any]]:
    sql = """
        SELECT
            v_student_report_summaries.appointment_id,
            v_student_report_summaries.appointment_date,
            v_student_report_summaries.doctor_id,
            v_student_report_summaries.doctor_name,
            v_student_report_summaries.diagnosis,
            v_student_report_summaries.remarks,
            v_student_report_summaries.prescription_count
        FROM v_student_report_summaries
        WHERE v_student_report_summaries.student_id = %s
        ORDER BY v_student_report_summaries.appointment_date DESC
    """
    return fetch_all(connection, sql, (student_id,))


def list_certificates(connection: Any, student_id: int) -> list[dict[str, Any]]:
    sql = """
        SELECT
            v_student_certificate_summaries.certificate_id,
            v_student_certificate_summaries.appointment_id,
            v_student_certificate_summaries.certificate_type_id,
            v_student_certificate_summaries.certificate_type,
            v_student_certificate_summaries.issue_date,
            v_student_certificate_summaries.doctor_id,
            v_student_certificate_summaries.doctor_name,
            v_student_certificate_summaries.appointment_date
        FROM v_student_certificate_summaries
        WHERE v_student_certificate_summaries.student_id = %s
        ORDER BY v_student_certificate_summaries.issue_date DESC
    """
    return fetch_all(connection, sql, (student_id,))
