from typing import Any

from app.backend.app.db import session
from app.backend.app.db.queries import doctor_queries


def get_dashboard_counts(staff_id: int) -> dict[str, Any] | None:
    with session.connection_scope() as connection:
        return doctor_queries.get_dashboard_counts(connection, staff_id)


def list_appointments(staff_id: int) -> list[dict[str, Any]]:
    with session.connection_scope() as connection:
        return doctor_queries.list_appointments(connection, staff_id)


def get_appointment_detail(appointment_id: int) -> dict[str, Any] | None:
    with session.connection_scope() as connection:
        return doctor_queries.get_appointment_detail(connection, appointment_id)


def list_patient_history(student_id: int) -> list[dict[str, Any]]:
    with session.connection_scope() as connection:
        return doctor_queries.list_patient_history(connection, student_id)
