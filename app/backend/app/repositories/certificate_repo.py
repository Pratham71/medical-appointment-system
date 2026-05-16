from typing import Any

from app.backend.app.db import session
from app.backend.app.db.queries import certificate_queries
from app.backend.app.schemas.certificate import CertificateCreate


_LOCKED_EDIT_STATUSES = {"completed", "cancelled"}


def get_appointment_certificate_context(appointment_id: int) -> dict[str, Any] | None:
    with session.connection_scope() as connection:
        return certificate_queries.get_appointment_certificate_context(
            connection,
            appointment_id,
        )


def create_certificate(
    appointment_id: int, payload: CertificateCreate
) -> dict[str, Any] | None:
    with session.transaction_scope() as connection:
        appointment = certificate_queries.get_appointment_certificate_context(
            connection,
            appointment_id,
        )
        if appointment is None:
            return None
        if appointment.get("status", "").lower() in _LOCKED_EDIT_STATUSES:
            return {
                "appointment_id": appointment_id,
                "blocked_status": appointment["status"],
            }

        certificate_queries.upsert_certificate(
            connection,
            appointment_id=appointment_id,
            certificate_type_id=payload.certificate_type_id,
            issue_date=payload.issue_date,
            leave_start_date=payload.leave_start_date,
            leave_end_date=payload.leave_end_date,
            certificate_notes=payload.certificate_notes,
        )
        return certificate_queries.get_certificate_by_appointment_type(
            connection,
            appointment_id=appointment_id,
            certificate_type_id=payload.certificate_type_id,
        )


def list_by_student(student_id: int) -> list[dict[str, Any]]:
    with session.connection_scope() as connection:
        return certificate_queries.list_by_student(connection, student_id)
