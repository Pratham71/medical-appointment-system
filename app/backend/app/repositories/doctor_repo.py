from typing import Any

from app.backend.app.repositories._deferred import database_deferred


def get_dashboard_counts(staff_id: int) -> dict[str, Any] | None:
    database_deferred()


def list_appointments(staff_id: int) -> list[dict[str, Any]]:
    database_deferred()


def get_appointment_detail(appointment_id: int) -> dict[str, Any] | None:
    database_deferred()


def list_patient_history(student_id: int) -> list[dict[str, Any]]:
    database_deferred()
