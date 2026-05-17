from datetime import date, datetime, time, timedelta
from typing import Any

from mysql.connector import IntegrityError, errorcode

from app.backend.app.db import session
from app.backend.app.db.queries import appointment_queries


class _BookingConflict(Exception):
    pass


_ALLOWED_STATUS_TRANSITIONS = {
    "booked": {"cancelled", "completed"},
}
_SLOT_INTERVAL = timedelta(minutes=30)
_DEFAULT_START_TIME = time(9, 0)
_DEFAULT_END_TIME = time(17, 0)


def ensure_slots_for_date(slot_date: date) -> None:
    """Generate 30-minute appointment slots for every available doctor on the given date.

    Args:
        slot_date: The calendar date for which slots should be created.
    """
    with session.transaction_scope() as connection:
        available_status_id = appointment_queries.get_slot_status_id(
            connection,
            "available",
        )
        if available_status_id is None:
            return

        windows = appointment_queries.list_doctor_slot_generation_windows(
            connection,
            slot_date,
        )
        for window in windows:
            for start_time, end_time in _iter_half_hour_slots(
                _coerce_time(window.get("start_time"), _DEFAULT_START_TIME),
                _coerce_time(window.get("end_time"), _DEFAULT_END_TIME),
            ):
                appointment_queries.insert_slot_if_missing(
                    connection,
                    staff_id=int(window["staff_id"]),
                    slot_status_id=available_status_id,
                    slot_date=slot_date,
                    start_time=start_time,
                    end_time=end_time,
                )


def list_available_slots(
    from_date: date,
    current_time: time | None = None,
) -> list[dict[str, Any]]:
    """Return bookable appointment slots for a date, optionally filtered by current time.

    Args:
        from_date: Calendar date to query.
        current_time: If provided, only slots starting after this time are returned.

    Returns:
        List of available slot dicts with slot_id, doctor info, date, and times.
    """
    with session.connection_scope() as connection:
        return appointment_queries.list_available_slots(
            connection,
            from_date,
            current_time,
        )


def list_all_slots_for_doctor(doctor_id: int, slot_date: date) -> list[dict[str, Any]]:
    """Return all slots for a doctor on a given date, including booked ones.

    Args:
        doctor_id: Primary key of the doctor's staff record.
        slot_date: Calendar date to query.

    Returns:
        List of slot dicts with availability and appointment status information.
    """
    with session.connection_scope() as connection:
        return appointment_queries.list_all_slots_for_doctor(connection, doctor_id, slot_date)


def list_doctors_with_availability(for_date: date) -> list[dict[str, Any]]:
    """Return all doctors with their computed availability status for a date.

    Args:
        for_date: The calendar date to evaluate availability for.

    Returns:
        List of dicts with doctor_id, doctor_name, specialization, is_available,
        unavailability_note, and available_slots count.
    """
    with session.connection_scope() as connection:
        return appointment_queries.list_doctors_with_availability(
            connection,
            for_date,
        )


def book_appointment(
    student_id: int, slot_id: int, reason: str | None
) -> dict[str, Any] | None:
    """Atomically reserve a slot and create an appointment for a student.

    Args:
        student_id: Primary key of the student making the booking.
        slot_id: Primary key of the slot to reserve.
        reason: Optional free-text reason for the visit.

    Returns:
        A dict with appointment_id, slot_id, and status on success;
        a dict with conflict=True if the slot was already booked;
        a dict with expired=True if the slot start time has passed;
        or None if the slot or required status rows are not found.
    """
    try:
        with session.transaction_scope() as connection:
            slot = appointment_queries.get_available_slot_for_update(connection, slot_id)
            if slot is None:
                return None
            if _slot_has_elapsed(slot):
                return {"expired": True, "slot_id": slot_id, "status": "available"}

            booked_status_id = appointment_queries.get_appointment_status_id(
                connection,
                "booked",
            )
            booked_slot_status_id = appointment_queries.get_slot_status_id(
                connection,
                "booked",
            )
            if booked_status_id is None or booked_slot_status_id is None:
                return None

            try:
                appointment_id = appointment_queries.insert_appointment(
                    connection,
                    student_id=student_id,
                    slot_id=slot_id,
                    status_id=booked_status_id,
                    reason=reason,
                )
            except IntegrityError as exc:
                if getattr(exc, "errno", None) == errorcode.ER_DUP_ENTRY:
                    raise _BookingConflict from exc
                raise

            appointment_queries.update_slot_status(
                connection,
                slot_id=slot_id,
                slot_status_id=booked_slot_status_id,
            )
            return appointment_queries.get_booking_result(connection, appointment_id)
    except _BookingConflict:
        return {"conflict": True, "slot_id": slot_id, "status": "booked"}


def update_status(
    appointment_id: int,
    status_name: str,
    cancellation_reason: str | None = None,
) -> dict[str, Any] | None:
    """Transition an appointment to a new status, enforcing allowed transitions.

    Args:
        appointment_id: Primary key of the appointment.
        status_name: Target status ("cancelled" or "completed").
        cancellation_reason: Human-readable reason required when cancelling.

    Returns:
        A dict with appointment_id and status on success;
        a dict with invalid_transition=True if the transition is not allowed;
        or None if the appointment or required status rows are not found.
    """
    with session.transaction_scope() as connection:
        appointment = appointment_queries.get_appointment_for_update(
            connection,
            appointment_id,
        )
        if appointment is None:
            return None

        current_status = appointment["status"]
        if current_status == status_name:
            return appointment_queries.get_status_result(connection, appointment_id)

        allowed_next_statuses = _ALLOWED_STATUS_TRANSITIONS.get(current_status, set())
        if status_name not in allowed_next_statuses:
            return {
                "appointment_id": appointment_id,
                "status": current_status,
                "invalid_transition": True,
            }

        status_id = appointment_queries.get_appointment_status_id(
            connection,
            status_name,
        )
        if status_id is None:
            return None

        available_slot_status_id = None
        if status_name == "cancelled":
            available_slot_status_id = appointment_queries.get_slot_status_id(
                connection,
                "available",
            )
            if available_slot_status_id is None:
                return None

        if status_name == "cancelled" and cancellation_reason:
            appointment_queries.cancel_appointment_with_reason(
                connection,
                appointment_id=appointment_id,
                cancelled_status_id=status_id,
                available_slot_status_id=available_slot_status_id,
                slot_id=appointment["slot_id"],
                cancellation_reason=cancellation_reason,
            )
        else:
            appointment_queries.update_appointment_status(
                connection,
                appointment_id=appointment_id,
                status_id=status_id,
            )

        if available_slot_status_id is not None and not cancellation_reason:
            appointment_queries.update_slot_status(
                connection,
                slot_id=appointment["slot_id"],
                slot_status_id=available_slot_status_id,
            )

        return appointment_queries.get_status_result(connection, appointment_id)


def get_access_context(appointment_id: int) -> dict[str, Any] | None:
    """Fetch ownership context needed to evaluate appointment access permissions.

    Args:
        appointment_id: Primary key of the appointment.

    Returns:
        A dict with appointment_id, student_id, doctor_id, and status,
        or None if the appointment does not exist.
    """
    with session.connection_scope() as connection:
        return appointment_queries.get_appointment_access_context(
            connection,
            appointment_id,
        )


def _slot_has_elapsed(slot: dict[str, Any]) -> bool:
    """Return True if the slot's start datetime is in the past.

    Args:
        slot: Dict containing slot_date and start_time fields.

    Returns:
        True if the slot has already started or passed, False otherwise.
    """
    slot_start = datetime.combine(slot["slot_date"], slot["start_time"])
    return slot_start <= _get_local_now()


def _iter_half_hour_slots(
    start_time: time,
    end_time: time,
) -> list[tuple[time, time]]:
    """Generate a sequence of 30-minute (start, end) time pairs within a window.

    Args:
        start_time: The beginning of the working window.
        end_time: The end of the working window.

    Returns:
        List of (slot_start, slot_end) time tuples covering the window.
    """
    slot_date = date(2000, 1, 1)
    current = datetime.combine(slot_date, start_time)
    end = datetime.combine(slot_date, end_time)
    slots = []
    while current + _SLOT_INTERVAL <= end:
        next_time = current + _SLOT_INTERVAL
        slots.append((current.time(), next_time.time()))
        current = next_time
    return slots


def _coerce_time(value: Any, fallback: time) -> time:
    """Convert a value to a time object, returning a fallback if conversion is not possible.

    Args:
        value: A time object, an ISO-format time string, or any other value.
        fallback: The time to return when value cannot be converted.

    Returns:
        The coerced time object, or fallback.
    """
    if isinstance(value, time):
        return value
    if isinstance(value, str):
        return time.fromisoformat(value)
    return fallback


def _get_local_now() -> datetime:
    """Return the current local datetime.

    Returns:
        The current datetime as returned by datetime.now().
    """
    return datetime.now()
