from typing import Any

from app.backend.app.repositories._deferred import database_deferred


def get_dashboard_counts(student_id: int) -> dict[str, Any] | None:
    database_deferred()


def get_next_appointment(student_id: int) -> dict[str, Any] | None:
    database_deferred()


def list_appointments(student_id: int) -> list[dict[str, Any]]:
    database_deferred()


def list_reports(student_id: int) -> list[dict[str, Any]]:
    database_deferred()


def list_certificates(student_id: int) -> list[dict[str, Any]]:
    database_deferred()
