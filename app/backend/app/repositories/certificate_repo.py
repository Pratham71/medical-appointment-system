from typing import Any

from app.backend.app.db import session
from app.backend.app.db.queries import certificate_queries
from app.backend.app.schemas.certificate import CertificateCreate


def create_certificate(
    appointment_id: int, payload: CertificateCreate
) -> dict[str, Any] | None:
    with session.transaction_scope() as connection:
        if certificate_queries.get_appointment_exists(connection, appointment_id) is None:
            return None

        certificate_queries.upsert_certificate(
            connection,
            appointment_id=appointment_id,
            certificate_type_id=payload.certificate_type_id,
            issue_date=payload.issue_date,
        )
        return certificate_queries.get_certificate_by_appointment_type(
            connection,
            appointment_id=appointment_id,
            certificate_type_id=payload.certificate_type_id,
        )


def list_by_student(student_id: int) -> list[dict[str, Any]]:
    with session.connection_scope() as connection:
        return certificate_queries.list_by_student(connection, student_id)
