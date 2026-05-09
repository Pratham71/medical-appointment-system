from datetime import date

from app.backend.app.api.errors import NotFoundError
from app.backend.app.repositories import certificate_repo
from app.backend.app.schemas.certificate import CertificateCreate, CertificateResponse


def create_certificate(
    appointment_id: int, payload: CertificateCreate
) -> CertificateResponse:
    payload.issue_date = payload.issue_date or date.today()
    row = certificate_repo.create_certificate(appointment_id, payload)
    if row is None:
        raise NotFoundError("Appointment was not found")
    return CertificateResponse(**row)


def list_student_certificates(student_id: int) -> list[CertificateResponse]:
    rows = certificate_repo.list_by_student(student_id)
    return [CertificateResponse(**row) for row in rows]
