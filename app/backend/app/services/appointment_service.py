from datetime import date

from app.backend.app.api.errors import ConflictError, NotFoundError
from app.backend.app.repositories import appointment_repo
from app.backend.app.schemas.appointment import (
    AppointmentBookRequest,
    AppointmentBookResponse,
    AppointmentSlot,
    AppointmentStatusResponse,
)


def list_available_slots(from_date: date | None = None) -> list[AppointmentSlot]:
    start_date = from_date or date.today()
    rows = appointment_repo.list_available_slots(start_date)
    return [AppointmentSlot(**row) for row in rows]


def book_appointment(payload: AppointmentBookRequest) -> AppointmentBookResponse:
    result = appointment_repo.book_appointment(
        student_id=payload.student_id,
        slot_id=payload.slot_id,
        reason=payload.reason,
    )

    if result is None:
        raise NotFoundError("Appointment slot was not found")
    if result.get("conflict"):
        raise ConflictError("Appointment slot is already booked")

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

    return AppointmentStatusResponse(
        appointment_id=result["appointment_id"],
        status=result["status"],
        message=message,
    )
