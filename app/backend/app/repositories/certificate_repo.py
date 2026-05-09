from typing import Any

from app.backend.app.repositories._deferred import database_deferred
from app.backend.app.schemas.certificate import CertificateCreate


def create_certificate(
    appointment_id: int, payload: CertificateCreate
) -> dict[str, Any] | None:
    database_deferred()


def list_by_student(student_id: int) -> list[dict[str, Any]]:
    database_deferred()
