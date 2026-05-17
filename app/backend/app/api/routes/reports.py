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
    """Add or update the medical note for an appointment.

    Args:
        payload: Note data including diagnosis and optional remarks.
        appointment_id: Primary key of the appointment.
        current_user: An authenticated doctor (own appointments only) or admin.

    Returns:
        A MedicalNoteResponse with the saved note.

    Raises:
        HTTPException: 403 if access is denied; 404 if not found; 409 if locked.
    """
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
    """Replace the prescription for an appointment.

    Args:
        payload: Prescription items to write.
        appointment_id: Primary key of the appointment.
        current_user: An authenticated doctor (own appointments only) or admin.

    Returns:
        A PrescriptionResponse with the saved items.

    Raises:
        HTTPException: 403 if access is denied; 404 if not found; 409 if locked.
    """
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
        require_roles(
            "student",
            "professor",
            "college-staff",
            "hostel-staff",
            "doctor",
            "admin",
        ),
    ),
) -> ReportDetail:
    """Return the full report detail for an appointment.

    Args:
        appointment_id: Primary key of the appointment.
        current_user: An authenticated patient (own appointments only),
            treating doctor, or admin.

    Returns:
        A ReportDetail with appointment context, medical note, and prescription.

    Raises:
        HTTPException: 403 if access is denied; 404 if not found.
    """
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
