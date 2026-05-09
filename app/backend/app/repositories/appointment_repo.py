from datetime import date
from typing import Any

from app.backend.app.repositories._deferred import database_deferred


def list_available_slots(from_date: date) -> list[dict[str, Any]]:
    database_deferred()


def book_appointment(
    student_id: int, slot_id: int, reason: str | None
) -> dict[str, Any] | None:
    database_deferred()


def update_status(appointment_id: int, status_name: str) -> dict[str, Any] | None:
    database_deferred()
