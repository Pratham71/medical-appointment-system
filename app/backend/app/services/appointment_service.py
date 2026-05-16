from datetime import date, datetime

from app.backend.app.api.errors import ConflictError, NotFoundError
from app.backend.app.repositories import appointment_repo
from app.backend.app.schemas.appointment import (
    AppointmentBookRequest,
    AppointmentBookResponse,
    AppointmentSlot,
    AppointmentStatusResponse,
)


def list_available_slots(from_date: date | None = None) -> list[AppointmentSlot]:
    local_now = _get_local_now()
    start_date = from_date or local_now.date()
    current_time = local_now.time().replace(microsecond=0) if start_date == local_now.date() else None
    rows = appointment_repo.list_available_slots(start_date, current_time)
    return [AppointmentSlot(**row) for row in rows]


def book_appointment(
    payload: AppointmentBookRequest,
    student_id: int,
) -> AppointmentBookResponse:
    result = appointment_repo.book_appointment(
        student_id=student_id,
        slot_id=payload.slot_id,
        reason=payload.reason,
    )

    if result is None:
        raise NotFoundError("Appointment slot was not found")
    if result.get("conflict"):
        raise ConflictError("Appointment slot is already booked")
    if result.get("expired"):
        raise ConflictError("Appointment slot is no longer available")

    return AppointmentBookResponse(
        appointment_id=result.get("appointment_id"),
        slot_id=result["slot_id"],
        status=result["status"],
        message="Appointment booked",
    )


def cancel_appointment(appointment_id: int) -> AppointmentStatusResponse:
    return _update_appointment_status(appointment_id, "cancelled", "Appointment cancelled")


def complete_appointment(appointment_id: int) -> AppointmentStatusResponse:
    return _update_appointment_status(appointment_id, "completed", "Appointment completed")


def _update_appointment_status(
    appointment_id: int, status_name: str, message: str
) -> AppointmentStatusResponse:
    result = appointment_repo.update_status(appointment_id, status_name)
    if result is None:
        raise NotFoundError("Appointment was not found")
    if result.get("invalid_transition"):
        raise ConflictError(
            f"Cannot change appointment from {result['status']} to {status_name}"
        )

    return AppointmentStatusResponse(
        appointment_id=result["appointment_id"],
        status=result["status"],
        message=message,
    )


def _get_local_now() -> datetime:
    return datetime.now()
