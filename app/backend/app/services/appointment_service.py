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
    """Return bookable appointment slots for a date, defaulting to today.

    Args:
        from_date: Calendar date to query; defaults to today if not provided.

    Returns:
        List of AppointmentSlot objects for the given date.
    """
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
    """Return all slots for a doctor on a date, including booked ones.

    Args:
        doctor_id: Primary key of the doctor's staff record.
        slot_date: Calendar date to query.

    Returns:
        List of AppointmentSlotWithStatus objects with availability flags.
    """
    rows = appointment_repo.list_all_slots_for_doctor(doctor_id, slot_date)
    return [AppointmentSlotWithStatus(**row) for row in rows]


def list_doctors_with_availability(
    for_date: date | None = None,
) -> list[DoctorAvailabilityStatus]:
    """Return all doctors with computed availability status for a date.

    Args:
        for_date: Calendar date to evaluate; defaults to today if not provided.

    Returns:
        List of DoctorAvailabilityStatus objects.
    """
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
    """Book an appointment slot for a student and trigger a booking notification.

    Args:
        payload: Booking request with slot_id and optional reason.
        student_id: Primary key of the student making the booking.

    Returns:
        An AppointmentBookResponse with appointment_id, slot_id, status, and message.

    Raises:
        NotFoundError: If the slot does not exist.
        ConflictError: If the slot is already booked or has elapsed.
    """
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
    """Cancel an appointment, applying role-specific cancellation reason requirements.

    Args:
        appointment_id: Primary key of the appointment to cancel.
        payload: Cancellation details required for doctor/staff/admin actors.
        actor_role: Role of the user initiating the cancellation.

    Returns:
        An AppointmentStatusResponse with the new status and a confirmation message.

    Raises:
        ServiceError: If a cancellation reason is required but not provided.
        NotFoundError: If the appointment does not exist.
        ConflictError: If the status transition is not permitted.
    """
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
    """Mark an appointment as completed.

    Args:
        appointment_id: Primary key of the appointment.

    Returns:
        An AppointmentStatusResponse with the updated status.

    Raises:
        NotFoundError: If the appointment does not exist.
        ConflictError: If the appointment cannot be completed from its current status.
    """
    return _update_appointment_status(appointment_id, "completed", "Appointment completed")


def _update_appointment_status(
    appointment_id: int,
    status_name: str,
    message: str,
    cancellation_reason: str | None = None,
) -> AppointmentStatusResponse:
    """Transition an appointment to a new status and return the response.

    Args:
        appointment_id: Primary key of the appointment.
        status_name: Target status name.
        message: Human-readable confirmation message for the response.
        cancellation_reason: Reason string stored when cancelling.

    Returns:
        An AppointmentStatusResponse with appointment_id, status, and message.

    Raises:
        NotFoundError: If the appointment does not exist.
        ConflictError: If the status transition is not allowed.
    """
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
    """Build a human-readable cancellation reason string from the request payload.

    Args:
        payload: Cancellation request with a reason_code and optional free-text note.

    Returns:
        A formatted string combining the label for the reason code and the note.
    """
    reason = _CANCELLATION_REASON_LABELS[payload.reason_code]
    if payload.note:
        return f"{reason}: {payload.note}"
    return reason


def _get_local_now() -> datetime:
    """Return the current local datetime.

    Returns:
        The current datetime as returned by datetime.now().
    """
    return datetime.now()
