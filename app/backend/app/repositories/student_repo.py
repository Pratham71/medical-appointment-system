from typing import Any

from app.backend.app.db import session
from app.backend.app.db.queries import student_queries


def get_dashboard_counts(student_id: int) -> dict[str, Any] | None:
    """Fetch aggregated dashboard statistics for a student.

    Args:
        student_id: Primary key of the student profile.

    Returns:
        A dict with upcoming/completed appointment counts and available
        reports/certificates, or None if the student does not exist.
    """
    with session.connection_scope() as connection:
        return student_queries.get_dashboard_counts(connection, student_id)


def get_next_appointment(student_id: int) -> dict[str, Any] | None:
    """Fetch the earliest upcoming booked appointment for a student.

    Args:
        student_id: Primary key of the student profile.

    Returns:
        The next appointment dict, or None if no upcoming appointment exists.
    """
    with session.connection_scope() as connection:
        return student_queries.get_next_appointment(connection, student_id)


def list_appointments(student_id: int) -> list[dict[str, Any]]:
    """Return all appointments for a student in reverse chronological order.

    Args:
        student_id: Primary key of the student profile.

    Returns:
        List of appointment summary dicts.
    """
    with session.connection_scope() as connection:
        return student_queries.list_appointments(connection, student_id)


def list_reports(student_id: int) -> list[dict[str, Any]]:
    """Return all medical report summaries for a student, newest first.

    Args:
        student_id: Primary key of the student profile.

    Returns:
        List of report summary dicts.
    """
    with session.connection_scope() as connection:
        return student_queries.list_reports(connection, student_id)


def list_certificates(student_id: int) -> list[dict[str, Any]]:
    """Return all certificate summaries for a student, newest first.

    Args:
        student_id: Primary key of the student profile.

    Returns:
        List of certificate summary dicts.
    """
    with session.connection_scope() as connection:
        return student_queries.list_certificates(connection, student_id)


def list_emergency_alerts(student_id: int) -> list[dict[str, Any]]:
    """Return all emergency alerts submitted by a student, newest first.

    Args:
        student_id: Primary key of the student profile.

    Returns:
        List of emergency alert dicts.
    """
    with session.connection_scope() as connection:
        return student_queries.list_emergency_alerts(connection, student_id)
