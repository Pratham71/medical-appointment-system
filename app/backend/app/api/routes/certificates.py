from fastapi import APIRouter, Path

from app.backend.app.api.errors import service_error_to_http
from app.backend.app.schemas.certificate import CertificateCreate, CertificateResponse
from app.backend.app.services import certificate_service

router = APIRouter(prefix="/certificates", tags=["Certificates"])


@router.post("/{appointment_id}", response_model=CertificateResponse, status_code=201)
def create_certificate(
    payload: CertificateCreate,
    appointment_id: int = Path(..., gt=0),
) -> CertificateResponse:
    try:
        return certificate_service.create_certificate(appointment_id, payload)
    except Exception as exc:
        raise service_error_to_http(exc) from exc


@router.get("/student/{student_id}", response_model=list[CertificateResponse])
def student_certificates(
    student_id: int = Path(..., gt=0),
) -> list[CertificateResponse]:
    try:
        return certificate_service.list_student_certificates(student_id)
    except Exception as exc:
        raise service_error_to_http(exc) from exc
