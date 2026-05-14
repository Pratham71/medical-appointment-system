from typing import Any

from app.backend.app.db import session
from app.backend.app.db.queries import report_queries
from app.backend.app.schemas.report import MedicalNoteCreate, PrescriptionCreate


def add_medical_note(
    appointment_id: int, payload: MedicalNoteCreate
) -> dict[str, Any] | None:
    with session.transaction_scope() as connection:
        if report_queries.get_appointment_exists(connection, appointment_id) is None:
            return None

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
    with session.transaction_scope() as connection:
        if report_queries.get_appointment_exists(connection, appointment_id) is None:
            return None

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
