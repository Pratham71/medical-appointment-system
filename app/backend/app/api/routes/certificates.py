from fastapi import APIRouter, Depends, Path

from app.backend.app.api.dependencies import (
    ensure_appointment_access,
    ensure_student_record_access,
    require_roles,
)
from app.backend.app.api.errors import service_error_to_http
from app.backend.app.schemas.auth import AuthenticatedUser
from app.backend.app.schemas.certificate import CertificateCreate, CertificateResponse
from app.backend.app.services import certificate_service

router = APIRouter(prefix="/certificates", tags=["Certificates"])


@router.post("/{appointment_id}", response_model=CertificateResponse, status_code=201)
def create_certificate(
    payload: CertificateCreate,
    appointment_id: int = Path(..., gt=0),
    current_user: AuthenticatedUser = Depends(require_roles("doctor", "admin")),
) -> CertificateResponse:
    try:
        ensure_appointment_access(
            current_user,
            appointment_id,
            allow_student=False,
            allow_doctor=True,
            allow_admin=True,
        )
        return certificate_service.create_certificate(appointment_id, payload)
    except Exception as exc:
        raise service_error_to_http(exc) from exc


@router.get("/student/{student_id}", response_model=list[CertificateResponse])
def student_certificates(
    student_id: int = Path(..., gt=0),
    current_user: AuthenticatedUser = Depends(
        require_roles(
            "student",
            "professor",
            "college-staff",
            "hostel-staff",
            "doctor",
            "admin",
        ),
    ),
) -> list[CertificateResponse]:
    try:
        ensure_student_record_access(current_user, student_id)
        return certificate_service.list_student_certificates(student_id)
    except Exception as exc:
        raise service_error_to_http(exc) from exc
