from typing import Any

from app.backend.app.db import session
from app.backend.app.db.queries import report_queries
from app.backend.app.schemas.report import MedicalNoteCreate, PrescriptionCreate


_LOCKED_EDIT_STATUSES = {"completed", "cancelled"}


def get_appointment_write_context(appointment_id: int) -> dict[str, Any] | None:
    """Fetch the appointment status needed before writing a medical note or prescription.

    Args:
        appointment_id: Primary key of the appointment.

    Returns:
        A dict with appointment_id and status, or None if not found.
    """
    with session.connection_scope() as connection:
        return report_queries.get_appointment_write_context(connection, appointment_id)


def add_medical_note(
    appointment_id: int, payload: MedicalNoteCreate
) -> dict[str, Any] | None:
    """Upsert the medical note for an appointment and return the saved record.

    Args:
        appointment_id: Primary key of the appointment.
        payload: Note fields including diagnosis and optional remarks.

    Returns:
        The saved note dict, a dict with blocked_status if the appointment is
        locked, or None if the appointment does not exist.
    """
    with session.transaction_scope() as connection:
        appointment = report_queries.get_appointment_write_context(
            connection,
            appointment_id,
        )
        if appointment is None:
            return None
        if appointment["status"].lower() in _LOCKED_EDIT_STATUSES:
            return {
                "appointment_id": appointment_id,
                "blocked_status": appointment["status"],
            }

        report_queries.upsert_medical_note(
            connection,
            appointment_id=appointment_id,
            diagnosis=payload.diagnosis,
            remarks=payload.remarks,
        )
        return report_queries.get_medical_note(connection, appointment_id)


def add_prescription(
    appointment_id: int, payload: PrescriptionCreate
) -> dict[str, Any] | None:
    """Replace the prescription items for an appointment and return the updated record.

    Args:
        appointment_id: Primary key of the appointment.
        payload: Prescription items to replace the existing ones with.

    Returns:
        A dict with prescription_id, appointment_id, and items on success;
        a dict with blocked_status if the appointment is locked;
        or None if the appointment does not exist.
    """
    with session.transaction_scope() as connection:
        appointment = report_queries.get_appointment_write_context(
            connection,
            appointment_id,
        )
        if appointment is None:
            return None
        if appointment["status"].lower() in _LOCKED_EDIT_STATUSES:
            return {
                "appointment_id": appointment_id,
                "blocked_status": appointment["status"],
            }

        prescription = report_queries.get_prescription_by_appointment(
            connection,
            appointment_id,
        )
        if prescription is None:
            prescription_id = report_queries.insert_prescription(
                connection,
                appointment_id,
            )
        else:
            prescription_id = prescription["prescription_id"]
            report_queries.delete_prescription_items(connection, prescription_id)

        for item in payload.items:
            report_queries.insert_prescription_item(
                connection,
                prescription_id=prescription_id,
                medicine_name=item.medicine_name,
                dosage=item.dosage,
            )

        return {
            "prescription_id": prescription_id,
            "appointment_id": appointment_id,
            "items": report_queries.list_prescription_items(
                connection,
                prescription_id,
            ),
        }


def get_report(appointment_id: int) -> dict[str, Any] | None:
    """Fetch the full report detail including appointment context, note, and prescription.

    Args:
        appointment_id: Primary key of the appointment.

    Returns:
        A dict with "appointment", "note", and "prescription" keys,
        or None if the appointment does not exist.
    """
    with session.connection_scope() as connection:
        appointment = report_queries.get_report_appointment(connection, appointment_id)
        if appointment is None:
            return None

        note = report_queries.get_medical_note(connection, appointment_id)
        prescription = report_queries.get_prescription_by_appointment(
            connection,
            appointment_id,
        )

        if prescription is not None:
            prescription = {
                "prescription_id": prescription["prescription_id"],
                "appointment_id": prescription["appointment_id"],
                "items": report_queries.list_prescription_items(
                    connection,
                    prescription["prescription_id"],
                ),
            }

        return {
            "appointment": appointment,
            "note": note,
            "prescription": prescription,
        }
