from datetime import date
from typing import Any

from app.backend.app.db.queries._helpers import execute, fetch_all, fetch_one


def get_appointment_exists(connection: Any, appointment_id: int) -> dict[str, Any] | None:
    sql = """
        SELECT appointments.appointment_id
        FROM appointments
        WHERE appointments.appointment_id = %s
    """
    return fetch_one(connection, sql, (appointment_id,))


def upsert_certificate(
    connection: Any,
    appointment_id: int,
    certificate_type_id: int,
    issue_date: date,
) -> None:
    sql = """
        INSERT INTO medical_certificates (
            appointment_id,
            certificate_type_id,
            issue_date
        )
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE
            issue_date = VALUES(issue_date)
    """
    execute(connection, sql, (appointment_id, certificate_type_id, issue_date))


def get_certificate_by_appointment_type(
    connection: Any,
    appointment_id: int,
    certificate_type_id: int,
) -> dict[str, Any] | None:
    sql = """
        SELECT
            v_student_certificate_summaries.certificate_id,
            v_student_certificate_summaries.appointment_id,
            v_student_certificate_summaries.student_id,
            v_student_certificate_summaries.student_name,
            v_student_certificate_summaries.certificate_type_id,
            v_student_certificate_summaries.certificate_type,
            v_student_certificate_summaries.issue_date
        FROM v_student_certificate_summaries
        WHERE v_student_certificate_summaries.appointment_id = %s
            AND v_student_certificate_summaries.certificate_type_id = %s
    """
    return fetch_one(connection, sql, (appointment_id, certificate_type_id))


def list_by_student(connection: Any, student_id: int) -> list[dict[str, Any]]:
    sql = """
        SELECT
            v_student_certificate_summaries.certificate_id,
            v_student_certificate_summaries.appointment_id,
            v_student_certificate_summaries.student_id,
            v_student_certificate_summaries.student_name,
            v_student_certificate_summaries.certificate_type_id,
            v_student_certificate_summaries.certificate_type,
            v_student_certificate_summaries.issue_date
        FROM v_student_certificate_summaries
        WHERE v_student_certificate_summaries.student_id = %s
        ORDER BY v_student_certificate_summaries.issue_date DESC
    """
    return fetch_all(connection, sql, (student_id,))
