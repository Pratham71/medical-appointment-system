from datetime import date

from app.backend.app.api.errors import ConflictError, NotFoundError
from app.backend.app.repositories import certificate_repo
from app.backend.app.schemas.certificate import CertificateCreate, CertificateResponse
from app.backend.app.services import notification_service


_LOCKED_EDIT_STATUSES = {"completed", "cancelled"}


def create_certificate(
    appointment_id: int, payload: CertificateCreate
) -> CertificateResponse:
    """Create or update a medical certificate for an appointment.

    Args:
        appointment_id: Primary key of the appointment.
        payload: Certificate fields including type, issue date, leave dates, and notes.

    Returns:
        A CertificateResponse with the saved certificate details.

    Raises:
        NotFoundError: If the appointment does not exist.
        ConflictError: If the appointment is locked, the date is in the future,
            the issue date predates the appointment, or leave dates are inconsistent.
    """
    payload.issue_date = payload.issue_date or date.today()
    appointment = certificate_repo.get_appointment_certificate_context(appointment_id)
    if appointment is None:
        raise NotFoundError("Appointment was not found")

    _raise_if_locked_status(appointment.get("status"))

    appointment_date = appointment["appointment_date"]
    if appointment_date > date.today():
        raise ConflictError("Cannot issue certificate for a future appointment")
    if payload.issue_date < appointment_date:
        raise ConflictError(
            "Certificate issue date cannot be before appointment date"
        )
    if bool(payload.leave_start_date) != bool(payload.leave_end_date):
        raise ConflictError("Leave start date and leave end date must be provided together")
    if (
        payload.leave_start_date
        and payload.leave_end_date
        and payload.leave_end_date < payload.leave_start_date
    ):
        raise ConflictError("Leave end date cannot be before leave start date")

    row = certificate_repo.create_certificate(appointment_id, payload)
    if row is None:
        raise NotFoundError("Appointment was not found")
    _raise_if_locked_status(row.get("blocked_status"))
    response = CertificateResponse(**row)
    notification_service.send_certificate_available(
        appointment_id,
        response.certificate_type,
    )
    return response


def list_student_certificates(student_id: int) -> list[CertificateResponse]:
    """Return all certificates issued for a student.

    Args:
        student_id: Primary key of the student profile.

    Returns:
        List of CertificateResponse objects ordered by issue_date descending.
    """
    rows = certificate_repo.list_by_student(student_id)
    return [CertificateResponse(**row) for row in rows]


def _raise_if_locked_status(status: str | None) -> None:
    """Raise ConflictError if the given status is one that prevents editing.

    Args:
        status: An appointment or blocked status string, or None to no-op.

    Raises:
        ConflictError: If the status is "completed" or "cancelled".
    """
    if status is None:
        return
    normalized_status = status.lower()
    if normalized_status in _LOCKED_EDIT_STATUSES:
        raise ConflictError(f"{normalized_status.title()} appointments cannot be edited")
