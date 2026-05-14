from typing import Any

from app.backend.app.db import session
from app.backend.app.db.queries import student_queries


def get_dashboard_counts(student_id: int) -> dict[str, Any] | None:
    with session.connection_scope() as connection:
        return student_queries.get_dashboard_counts(connection, student_id)


def get_next_appointment(student_id: int) -> dict[str, Any] | None:
    with session.connection_scope() as connection:
        return student_queries.get_next_appointment(connection, student_id)


def list_appointments(student_id: int) -> list[dict[str, Any]]:
    with session.connection_scope() as connection:
        return student_queries.list_appointments(connection, student_id)


def list_reports(student_id: int) -> list[dict[str, Any]]:
    with session.connection_scope() as connection:
        return student_queries.list_reports(connection, student_id)


def list_certificates(student_id: int) -> list[dict[str, Any]]:
    with session.connection_scope() as connection:
        return student_queries.list_certificates(connection, student_id)
