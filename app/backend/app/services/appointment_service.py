from datetime import date, datetime

from app.backend.app.api.errors import ConflictError, NotFoundError, ServiceError
from app.backend.app.repositories import appointment_repo
from app.backend.app.schemas.appointment import (
    AppointmentBookRequest,
    AppointmentBookResponse,
    AppointmentCancelRequest,
    AppointmentSlot,
    AppointmentSlotWithStatus,
    AppointmentStatusResponse,
    DoctorAvailabilityStatus,
)
from app.backend.app.services import notification_service


_CANCELLATION_REASON_LABELS = {
    "no_show": "No-show",
    "student_request": "Student requested cancellation",
    "doctor_unavailable": "Doctor unavailable",
    "emergency_priority": "Emergency case prioritized",
    "duplicate_booking": "Duplicate booking",
    "other": "Other",
}
_REASON_REQUIRED_ROLES = {"doctor", "staff", "admin"}


def list_available_slots(from_date: date | None = None) -> list[AppointmentSlot]:
    local_now = _get_local_now()
    start_date = from_date or local_now.date()
    current_time = local_now.time().replace(microsecond=0) if start_date == local_now.date() else None
    if start_date >= local_now.date():
        appointment_repo.ensure_slots_for_date(start_date)
    rows = appointment_repo.list_available_slots(start_date, current_time)
    return [AppointmentSlot(**row) for row in rows]


def list_all_slots_for_doctor(
    doctor_id: int, slot_date: date
) -> list[AppointmentSlotWithStatus]:
    rows = appointment_repo.list_all_slots_for_doctor(doctor_id, slot_date)
    return [AppointmentSlotWithStatus(**row) for row in rows]


def list_doctors_with_availability(
    for_date: date | None = None,
) -> list[DoctorAvailabilityStatus]:
    local_now = _get_local_now()
    target_date = for_date or local_now.date()
    if target_date >= local_now.date():
        appointment_repo.ensure_slots_for_date(target_date)
    rows = appointment_repo.list_doctors_with_availability(target_date)
    return [DoctorAvailabilityStatus(**row) for row in rows]


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

    appointment_id = result.get("appointment_id")
    if appointment_id is not None:
        notification_service.send_appointment_booked(int(appointment_id))

    return AppointmentBookResponse(
        appointment_id=result.get("appointment_id"),
        slot_id=result["slot_id"],
        status=result["status"],
        message="Appointment booked",
    )


def cancel_appointment(
    appointment_id: int,
    payload: AppointmentCancelRequest | None = None,
    actor_role: str = "student",
) -> AppointmentStatusResponse:
    cancellation_reason = None
    if actor_role.lower() in _REASON_REQUIRED_ROLES:
        if payload is None:
            raise ServiceError("Cancellation reason is required")
        cancellation_reason = _format_cancellation_reason(payload)

    response = _update_appointment_status(
        appointment_id,
        "cancelled",
        "Appointment cancelled",
        cancellation_reason=cancellation_reason,
    )
    notification_service.send_appointment_cancelled(appointment_id)
    return response


def complete_appointment(appointment_id: int) -> AppointmentStatusResponse:
    return _update_appointment_status(appointment_id, "completed", "Appointment completed")


def _update_appointment_status(
    appointment_id: int,
    status_name: str,
    message: str,
    cancellation_reason: str | None = None,
) -> AppointmentStatusResponse:
    result = appointment_repo.update_status(
        appointment_id,
        status_name,
        cancellation_reason=cancellation_reason,
    )
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


def _format_cancellation_reason(payload: AppointmentCancelRequest) -> str:
    reason = _CANCELLATION_REASON_LABELS[payload.reason_code]
    if payload.note:
        return f"{reason}: {payload.note}"
    return reason


def _get_local_now() -> datetime:
    return datetime.now()
