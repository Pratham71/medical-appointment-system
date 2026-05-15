from fastapi import APIRouter, Depends, Path

from app.backend.app.api.dependencies import ensure_appointment_access, require_roles
from app.backend.app.api.errors import service_error_to_http
from app.backend.app.schemas.auth import AuthenticatedUser
from app.backend.app.schemas.report import (
    MedicalNoteCreate,
    MedicalNoteResponse,
    PrescriptionCreate,
    PrescriptionResponse,
    ReportDetail,
)
from app.backend.app.services import report_service

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.post("/{appointment_id}/notes", response_model=MedicalNoteResponse, status_code=201)
def add_notes(
    payload: MedicalNoteCreate,
    appointment_id: int = Path(..., gt=0),
    current_user: AuthenticatedUser = Depends(require_roles("doctor", "admin")),
) -> MedicalNoteResponse:
    try:
        ensure_appointment_access(
            current_user,
            appointment_id,
            allow_student=False,
            allow_doctor=True,
            allow_admin=True,
        )
        return report_service.add_medical_note(appointment_id, payload)
    except Exception as exc:
        raise service_error_to_http(exc) from exc


@router.post(
    "/{appointment_id}/prescription",
    response_model=PrescriptionResponse,
    status_code=201,
)
def add_prescription(
    payload: PrescriptionCreate,
    appointment_id: int = Path(..., gt=0),
    current_user: AuthenticatedUser = Depends(require_roles("doctor", "admin")),
) -> PrescriptionResponse:
    try:
        ensure_appointment_access(
            current_user,
            appointment_id,
            allow_student=False,
            allow_doctor=True,
            allow_admin=True,
        )
        return report_service.add_prescription(appointment_id, payload)
    except Exception as exc:
        raise service_error_to_http(exc) from exc


@router.get("/{appointment_id}", response_model=ReportDetail)
def report_detail(
    appointment_id: int = Path(..., gt=0),
    current_user: AuthenticatedUser = Depends(
        require_roles("student", "doctor", "admin"),
    ),
) -> ReportDetail:
    try:
        ensure_appointment_access(
            current_user,
            appointment_id,
            allow_student=True,
            allow_doctor=True,
            allow_admin=True,
        )
        return report_service.get_report(appointment_id)
    except Exception as exc:
        raise service_error_to_http(exc) from exc
