from fastapi import APIRouter, Path

from app.backend.app.api.errors import service_error_to_http
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
) -> MedicalNoteResponse:
    try:
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
) -> PrescriptionResponse:
    try:
        return report_service.add_prescription(appointment_id, payload)
    except Exception as exc:
        raise service_error_to_http(exc) from exc


@router.get("/{appointment_id}", response_model=ReportDetail)
def report_detail(appointment_id: int = Path(..., gt=0)) -> ReportDetail:
    try:
        return report_service.get_report(appointment_id)
    except Exception as exc:
        raise service_error_to_http(exc) from exc
