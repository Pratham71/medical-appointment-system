from typing import Any

from app.backend.app.repositories._deferred import database_deferred
from app.backend.app.schemas.report import MedicalNoteCreate, PrescriptionCreate


def add_medical_note(
    appointment_id: int, payload: MedicalNoteCreate
) -> dict[str, Any] | None:
    database_deferred()


def add_prescription(
    appointment_id: int, payload: PrescriptionCreate
) -> dict[str, Any] | None:
    database_deferred()


def get_report(appointment_id: int) -> dict[str, Any] | None:
    database_deferred()
