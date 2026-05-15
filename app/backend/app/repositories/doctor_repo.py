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


def search_patients(search_text: str, staff_id: int | None) -> list[dict[str, Any]]:
    with session.connection_scope() as connection:
        if staff_id is None:
            return doctor_queries.search_patients(connection, search_text)
        return doctor_queries.search_patients_for_doctor(
            connection,
            search_text,
            staff_id,
        )


def has_doctor_seen_student(staff_id: int, student_id: int) -> bool:
    with session.connection_scope() as connection:
        return doctor_queries.has_doctor_seen_student(connection, staff_id, student_id)
