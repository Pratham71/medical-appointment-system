from typing import Any

from app.backend.app.db.queries._helpers import fetch_all, fetch_one


def get_dashboard_counts(connection: Any, student_id: int) -> dict[str, Any] | None:
    """Fetch aggregated dashboard statistics for a single student.

    Args:
        student_id: Primary key of the student profile.

    Returns:
        A dict with student_id, student_name, upcoming_appointments,
        completed_appointments, reports_available, and certificates_available,
        or None if the student does not exist.
    """
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
    """Fetch the earliest upcoming booked appointment for a student.

    Args:
        student_id: Primary key of the student profile.

    Returns:
        A dict with appointment_id, slot_date, start_time, end_time, doctor info,
        and status, or None if no upcoming appointment exists.
    """
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
    """Return all appointments for a student in reverse chronological order.

    Args:
        student_id: Primary key of the student profile.

    Returns:
        List of dicts with appointment_id, slot_date, start/end times, doctor info,
        status, reason, and cancellation_reason.
    """
    sql = """
        SELECT
            v_appointment_details.appointment_id,
            v_appointment_details.slot_date,
            v_appointment_details.start_time,
            v_appointment_details.end_time,
            v_appointment_details.doctor_id,
            v_appointment_details.doctor_name,
            v_appointment_details.status,
            v_appointment_details.reason,
            v_appointment_details.cancellation_reason
        FROM v_appointment_details
        WHERE v_appointment_details.student_id = %s
        ORDER BY
            v_appointment_details.slot_date DESC,
            v_appointment_details.start_time DESC
    """
    return fetch_all(connection, sql, (student_id,))


def list_reports(connection: Any, student_id: int) -> list[dict[str, Any]]:
    """Return all medical report summaries for a student, newest first.

    Args:
        student_id: Primary key of the student profile.

    Returns:
        List of dicts with appointment_id, appointment_date, doctor info,
        diagnosis, remarks, and prescription_count.
    """
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
    """Return all certificate summaries for a student, newest first.

    Args:
        student_id: Primary key of the student profile.

    Returns:
        List of certificate summary dicts ordered by issue_date descending.
    """
    sql = """
        SELECT
            v_student_certificate_summaries.certificate_id,
            v_student_certificate_summaries.appointment_id,
            v_student_certificate_summaries.certificate_type_id,
            v_student_certificate_summaries.certificate_type,
            v_student_certificate_summaries.issue_date,
            v_student_certificate_summaries.doctor_id,
            v_student_certificate_summaries.doctor_name,
            v_student_certificate_summaries.appointment_date,
            v_student_certificate_summaries.appointment_reason,
            v_student_certificate_summaries.diagnosis,
            v_student_certificate_summaries.remarks,
            v_student_certificate_summaries.leave_start_date,
            v_student_certificate_summaries.leave_end_date,
            v_student_certificate_summaries.certificate_notes
        FROM v_student_certificate_summaries
        WHERE v_student_certificate_summaries.student_id = %s
        ORDER BY v_student_certificate_summaries.issue_date DESC
    """
    return fetch_all(connection, sql, (student_id,))


def list_emergency_alerts(connection: Any, student_id: int) -> list[dict[str, Any]]:
    """Return all emergency alerts submitted by a student, newest first.

    Args:
        student_id: Primary key of the student profile.

    Returns:
        List of dicts with alert_id, reason, location, contact_number, message,
        status, created_at, acknowledged_at, resolved_at, and resolution_note.
    """
    sql = """
        SELECT
            emergency_alerts.alert_id,
            emergency_alerts.reason,
            emergency_alerts.location,
            emergency_alerts.contact_number,
            emergency_alerts.message,
            CASE
                WHEN emergency_alerts.resolved_at IS NOT NULL THEN 'resolved'
                WHEN emergency_alerts.acknowledged_at IS NOT NULL THEN 'acknowledged'
                ELSE 'unread'
            END AS status,
            emergency_alerts.created_at,
            emergency_alerts.acknowledged_at,
            emergency_alerts.resolved_at,
            emergency_alerts.resolution_note
        FROM emergency_alerts
        WHERE emergency_alerts.student_id = %s
        ORDER BY emergency_alerts.created_at DESC, emergency_alerts.alert_id DESC
    """
    return fetch_all(connection, sql, (student_id,))
