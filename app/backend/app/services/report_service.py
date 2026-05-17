from app.backend.app.api.errors import ConflictError, NotFoundError
from app.backend.app.repositories import report_repo
from app.backend.app.schemas.report import (
    MedicalNoteCreate,
    MedicalNoteResponse,
    PrescriptionCreate,
    PrescriptionResponse,
    ReportDetail,
)
from app.backend.app.services import notification_service


_LOCKED_EDIT_STATUSES = {"completed", "cancelled"}


def add_medical_note(
    appointment_id: int, payload: MedicalNoteCreate
) -> MedicalNoteResponse:
    _ensure_appointment_can_be_edited(appointment_id)
    row = report_repo.add_medical_note(appointment_id, payload)
    if row is None:
        raise NotFoundError("Appointment was not found")
    _raise_if_locked_edit(row)
    response = MedicalNoteResponse(**row)
    notification_service.send_report_available(appointment_id)
    return response


def add_prescription(
    appointment_id: int, payload: PrescriptionCreate
) -> PrescriptionResponse:
    _ensure_appointment_can_be_edited(appointment_id)
    row = report_repo.add_prescription(appointment_id, payload)
    if row is None:
        raise NotFoundError("Appointment was not found")
    _raise_if_locked_edit(row)
    response = PrescriptionResponse(**row)
    notification_service.send_report_available(appointment_id)
    return response


def get_report(appointment_id: int) -> ReportDetail:
    row = report_repo.get_report(appointment_id)
    if row is None:
        raise NotFoundError("Appointment was not found")
    return ReportDetail(**row)


def _ensure_appointment_can_be_edited(appointment_id: int) -> None:
    appointment = report_repo.get_appointment_write_context(appointment_id)
    if appointment is None:
        raise NotFoundError("Appointment was not found")
    _raise_if_locked_status(appointment["status"])


def _raise_if_locked_edit(row: dict) -> None:
    status = row.get("blocked_status")
    if status:
        _raise_if_locked_status(status)


def _raise_if_locked_status(status: str) -> None:
    normalized_status = status.lower()
    if normalized_status in _LOCKED_EDIT_STATUSES:
        raise ConflictError(f"{normalized_status.title()} appointments cannot be edited")
