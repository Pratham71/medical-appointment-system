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
    """Add or update the medical note for an appointment and send a report notification.

    Args:
        appointment_id: Primary key of the appointment.
        payload: Note data including diagnosis and optional remarks.

    Returns:
        A MedicalNoteResponse with the saved note.

    Raises:
        NotFoundError: If the appointment does not exist.
        ConflictError: If the appointment is locked (completed or cancelled).
    """
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
    """Replace the prescription for an appointment and send a report notification.

    Args:
        appointment_id: Primary key of the appointment.
        payload: Prescription items to write.

    Returns:
        A PrescriptionResponse with the saved items.

    Raises:
        NotFoundError: If the appointment does not exist.
        ConflictError: If the appointment is locked (completed or cancelled).
    """
    _ensure_appointment_can_be_edited(appointment_id)
    row = report_repo.add_prescription(appointment_id, payload)
    if row is None:
        raise NotFoundError("Appointment was not found")
    _raise_if_locked_edit(row)
    response = PrescriptionResponse(**row)
    notification_service.send_report_available(appointment_id)
    return response


def get_report(appointment_id: int) -> ReportDetail:
    """Fetch the full report detail for an appointment.

    Args:
        appointment_id: Primary key of the appointment.

    Returns:
        A ReportDetail object with appointment context, note, and prescription.

    Raises:
        NotFoundError: If the appointment does not exist.
    """
    row = report_repo.get_report(appointment_id)
    if row is None:
        raise NotFoundError("Appointment was not found")
    return ReportDetail(**row)


def _ensure_appointment_can_be_edited(appointment_id: int) -> None:
    """Verify that an appointment exists and is not locked before writing.

    Args:
        appointment_id: Primary key of the appointment to check.

    Raises:
        NotFoundError: If the appointment does not exist.
        ConflictError: If the appointment status is locked.
    """
    appointment = report_repo.get_appointment_write_context(appointment_id)
    if appointment is None:
        raise NotFoundError("Appointment was not found")
    _raise_if_locked_status(appointment["status"])


def _raise_if_locked_edit(row: dict) -> None:
    """Raise ConflictError if the repo result indicates the appointment was locked.

    Args:
        row: Repository result dict that may contain a "blocked_status" key.

    Raises:
        ConflictError: If blocked_status is present and is a locked status.
    """
    status = row.get("blocked_status")
    if status:
        _raise_if_locked_status(status)


def _raise_if_locked_status(status: str) -> None:
    """Raise ConflictError if the status prevents editing the appointment.

    Args:
        status: The appointment status string to check.

    Raises:
        ConflictError: If the status is "completed" or "cancelled".
    """
    normalized_status = status.lower()
    if normalized_status in _LOCKED_EDIT_STATUSES:
        raise ConflictError(f"{normalized_status.title()} appointments cannot be edited")
