from datetime import date
from typing import Any

from app.backend.app.db.queries._helpers import execute, fetch_all, fetch_one


def get_appointment_exists(connection: Any, appointment_id: int) -> dict[str, Any] | None:
    """Check whether an appointment row exists by its primary key.

    Args:
        appointment_id: Primary key of the appointment.

    Returns:
        A dict with appointment_id if the row exists, otherwise None.
    """
    sql = """
        SELECT appointments.appointment_id
        FROM appointments
        WHERE appointments.appointment_id = %s
    """
    return fetch_one(connection, sql, (appointment_id,))


def get_appointment_certificate_context(
    connection: Any,
    appointment_id: int,
) -> dict[str, Any] | None:
    """Fetch the appointment date and status needed before issuing a certificate.

    Args:
        appointment_id: Primary key of the appointment.

    Returns:
        A dict with appointment_id, appointment_date, and status,
        or None if the appointment does not exist.
    """
    sql = """
        SELECT
            appointments.appointment_id,
            appointment_slots.slot_date AS appointment_date,
            appointment_statuses.status_name AS status
        FROM appointments
        INNER JOIN appointment_slots
            ON appointment_slots.slot_id = appointments.slot_id
        INNER JOIN appointment_statuses
            ON appointment_statuses.status_id = appointments.status_id
        WHERE appointments.appointment_id = %s
    """
    return fetch_one(connection, sql, (appointment_id,))


def upsert_certificate(
    connection: Any,
    appointment_id: int,
    certificate_type_id: int,
    issue_date: date,
    leave_start_date: date | None,
    leave_end_date: date | None,
    certificate_notes: str | None,
) -> None:
    """Insert or update the medical certificate for an appointment.

    Args:
        appointment_id: Foreign-key ID of the appointment.
        certificate_type_id: Foreign-key ID of the certificate type.
        issue_date: Date the certificate is issued.
        leave_start_date: Optional start date of recommended leave.
        leave_end_date: Optional end date of recommended leave.
        certificate_notes: Optional free-text notes on the certificate.
    """
    sql = """
        INSERT INTO medical_certificates (
            appointment_id,
            certificate_type_id,
            issue_date,
            leave_start_date,
            leave_end_date,
            certificate_notes
        )
        VALUES (%s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            issue_date = VALUES(issue_date),
            leave_start_date = VALUES(leave_start_date),
            leave_end_date = VALUES(leave_end_date),
            certificate_notes = VALUES(certificate_notes)
    """
    execute(
        connection,
        sql,
        (
            appointment_id,
            certificate_type_id,
            issue_date,
            leave_start_date,
            leave_end_date,
            certificate_notes,
        ),
    )


def get_certificate_by_appointment_type(
    connection: Any,
    appointment_id: int,
    certificate_type_id: int,
) -> dict[str, Any] | None:
    """Fetch the full certificate summary for a specific appointment and type.

    Args:
        appointment_id: Foreign-key ID of the appointment.
        certificate_type_id: Foreign-key ID of the certificate type.

    Returns:
        A dict with all certificate summary fields, or None if not found.
    """
    sql = """
        SELECT
            v_student_certificate_summaries.certificate_id,
            v_student_certificate_summaries.appointment_id,
            v_student_certificate_summaries.student_id,
            v_student_certificate_summaries.student_name,
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
        WHERE v_student_certificate_summaries.appointment_id = %s
            AND v_student_certificate_summaries.certificate_type_id = %s
    """
    return fetch_one(connection, sql, (appointment_id, certificate_type_id))


def list_by_student(connection: Any, student_id: int) -> list[dict[str, Any]]:
    """Return all certificates issued for a student, newest first.

    Args:
        student_id: Primary key of the student profile.

    Returns:
        List of certificate summary dicts ordered by issue_date descending.
    """
    sql = """
        SELECT
            v_student_certificate_summaries.certificate_id,
            v_student_certificate_summaries.appointment_id,
            v_student_certificate_summaries.student_id,
            v_student_certificate_summaries.student_name,
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
