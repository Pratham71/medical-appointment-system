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
            medical_certificates.certificate_id,
            appointments.appointment_id,
            students.student_id,
            student_users.name AS student_name,
            certificate_types.certificate_type_id,
            certificate_types.certificate_type,
            medical_certificates.issue_date
        FROM medical_certificates
        INNER JOIN appointments
            ON appointments.appointment_id = medical_certificates.appointment_id
        INNER JOIN students ON students.student_id = appointments.student_id
        INNER JOIN users AS student_users ON student_users.user_id = students.user_id
        INNER JOIN certificate_types
            ON certificate_types.certificate_type_id =
                medical_certificates.certificate_type_id
        WHERE medical_certificates.appointment_id = %s
            AND medical_certificates.certificate_type_id = %s
    """
    return fetch_one(connection, sql, (appointment_id, certificate_type_id))


def list_by_student(connection: Any, student_id: int) -> list[dict[str, Any]]:
    sql = """
        SELECT
            medical_certificates.certificate_id,
            appointments.appointment_id,
            students.student_id,
            student_users.name AS student_name,
            certificate_types.certificate_type_id,
            certificate_types.certificate_type,
            medical_certificates.issue_date
        FROM medical_certificates
        INNER JOIN appointments
            ON appointments.appointment_id = medical_certificates.appointment_id
        INNER JOIN students ON students.student_id = appointments.student_id
        INNER JOIN users AS student_users ON student_users.user_id = students.user_id
        INNER JOIN certificate_types
            ON certificate_types.certificate_type_id =
                medical_certificates.certificate_type_id
        WHERE students.student_id = %s
        ORDER BY medical_certificates.issue_date DESC
    """
    return fetch_all(connection, sql, (student_id,))
