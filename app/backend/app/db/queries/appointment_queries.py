from datetime import date, time
from typing import Any

from app.backend.app.db.queries._helpers import execute, fetch_all, fetch_one


def list_doctors_with_availability(
    connection: Any,
    for_date: date,
) -> list[dict[str, Any]]:
    """Return all doctors with their computed availability status for a given date.

    Args:
        for_date: The calendar date to evaluate availability for.

    Returns:
        List of dicts with doctor_id, doctor_name, specialization, is_available,
        unavailability_note, and available_slots count.
    """
    sql = """
        SELECT
            staff.staff_id AS doctor_id,
            users.name AS doctor_name,
            staff.specialization,
            CASE
                WHEN doctor_availability_overrides.override_id IS NOT NULL
                    THEN IF(doctor_availability_overrides.is_available, 1, 0)
                WHEN doctor_weekly_availability.staff_id IS NOT NULL
                    THEN IF(doctor_weekly_availability.is_available, 1, 0)
                ELSE IF(WEEKDAY(%s) < 6, 1, 0)
            END AS is_available,
            CASE
                WHEN doctor_availability_overrides.override_id IS NOT NULL
                    AND doctor_availability_overrides.is_available = FALSE
                    THEN doctor_availability_overrides.note
                ELSE NULL
            END AS unavailability_note,
            (
                SELECT COUNT(*)
                FROM appointment_slots
                INNER JOIN slot_statuses
                    ON slot_statuses.slot_status_id = appointment_slots.slot_status_id
                WHERE appointment_slots.staff_id = staff.staff_id
                    AND appointment_slots.slot_date = %s
                    AND slot_statuses.status_name = %s
            ) AS available_slots
        FROM staff
        INNER JOIN users
            ON users.user_id = staff.user_id
        LEFT JOIN doctor_availability_overrides
            ON doctor_availability_overrides.staff_id = staff.staff_id
            AND doctor_availability_overrides.override_date = %s
        LEFT JOIN doctor_weekly_availability
            ON doctor_weekly_availability.staff_id = staff.staff_id
            AND doctor_weekly_availability.weekday = WEEKDAY(%s)
        WHERE staff.is_doctor = TRUE
        ORDER BY users.name
    """
    return fetch_all(
        connection,
        sql,
        (for_date, for_date, "available", for_date, for_date),
    )


def list_doctor_slot_generation_windows(
    connection: Any,
    slot_date: date,
) -> list[dict[str, Any]]:
    """Return each available doctor's working window that should have slots generated.

    Args:
        slot_date: The date for which slot windows are being generated.

    Returns:
        List of dicts with staff_id, is_available, start_time, and end_time
        for every doctor that is available on slot_date.
    """
    sql = """
        SELECT
            staff.staff_id,
            CASE
                WHEN doctor_availability_overrides.override_id IS NOT NULL
                    THEN doctor_availability_overrides.is_available
                WHEN doctor_weekly_availability.staff_id IS NOT NULL
                    THEN doctor_weekly_availability.is_available
                ELSE WEEKDAY(%s) < 6
            END AS is_available,
            CASE
                WHEN doctor_availability_overrides.override_id IS NOT NULL
                    THEN COALESCE(doctor_availability_overrides.start_time, '09:00:00')
                WHEN doctor_weekly_availability.staff_id IS NOT NULL
                    THEN COALESCE(doctor_weekly_availability.start_time, '09:00:00')
                ELSE '09:00:00'
            END AS start_time,
            CASE
                WHEN doctor_availability_overrides.override_id IS NOT NULL
                    THEN COALESCE(doctor_availability_overrides.end_time, '17:00:00')
                WHEN doctor_weekly_availability.staff_id IS NOT NULL
                    THEN COALESCE(doctor_weekly_availability.end_time, '17:00:00')
                ELSE '17:00:00'
            END AS end_time
        FROM staff
        LEFT JOIN doctor_availability_overrides
            ON doctor_availability_overrides.staff_id = staff.staff_id
            AND doctor_availability_overrides.override_date = %s
        LEFT JOIN doctor_weekly_availability
            ON doctor_weekly_availability.staff_id = staff.staff_id
            AND doctor_weekly_availability.weekday = WEEKDAY(%s)
        WHERE staff.is_doctor = TRUE
        HAVING is_available = TRUE
        ORDER BY staff.staff_id
    """
    return fetch_all(connection, sql, (slot_date, slot_date, slot_date))


def insert_slot_if_missing(
    connection: Any,
    staff_id: int,
    slot_status_id: int,
    slot_date: date,
    start_time: time,
    end_time: time,
) -> None:
    """Insert a new appointment slot only if an identical slot does not already exist.

    Args:
        staff_id: Primary key of the doctor's staff record.
        slot_status_id: Foreign-key ID of the initial slot status (typically "available").
        slot_date: Calendar date of the slot.
        start_time: Slot start time.
        end_time: Slot end time.
    """
    sql = """
        INSERT INTO appointment_slots (
            staff_id,
            slot_status_id,
            slot_date,
            start_time,
            end_time
        )
        SELECT %s, %s, %s, %s, %s
        WHERE NOT EXISTS (
            SELECT 1
            FROM appointment_slots
            WHERE appointment_slots.staff_id = %s
                AND appointment_slots.slot_date = %s
                AND appointment_slots.start_time = %s
                AND appointment_slots.end_time = %s
        )
    """
    execute(
        connection,
        sql,
        (
            staff_id,
            slot_status_id,
            slot_date,
            start_time,
            end_time,
            staff_id,
            slot_date,
            start_time,
            end_time,
        ),
    )


def list_all_slots_for_doctor(
    connection: Any,
    doctor_id: int,
    slot_date: date,
) -> list[dict[str, Any]]:
    """Return all slots for a doctor on a date, including booked and available.

    Args:
        doctor_id: Primary key of the doctor's staff record.
        slot_date: Calendar date to query.

    Returns:
        List of dicts with slot_id, doctor_id, doctor_name, slot_date,
        start_time, end_time, is_available, and appointment_status.
    """
    sql = """
        SELECT
            appointment_slots.slot_id,
            appointment_slots.staff_id AS doctor_id,
            users.name AS doctor_name,
            appointment_slots.slot_date,
            appointment_slots.start_time,
            appointment_slots.end_time,
            IF(apt.status_name IS NULL, 1, 0) AS is_available,
            apt.status_name AS appointment_status
        FROM appointment_slots
        INNER JOIN staff ON staff.staff_id = appointment_slots.staff_id
        INNER JOIN users ON users.user_id = staff.user_id
        LEFT JOIN (
            SELECT appointments.slot_id, appointment_statuses.status_name
            FROM appointments
            INNER JOIN appointment_statuses
                ON appointment_statuses.status_id = appointments.status_id
            WHERE appointment_statuses.status_name IN ('booked', 'completed')
        ) AS apt ON apt.slot_id = appointment_slots.slot_id
        WHERE appointment_slots.staff_id = %s
            AND appointment_slots.slot_date = %s
        ORDER BY appointment_slots.start_time
    """
    return fetch_all(connection, sql, (doctor_id, slot_date))


def list_available_slots(
    connection: Any,
    from_date: date,
    current_time: time | None = None,
) -> list[dict[str, Any]]:
    """Return bookable slots for the specified date, optionally filtered by current time.

    Args:
        from_date: Calendar date to query available slots for.
        current_time: If provided, only slots starting after this time are returned
            (used to hide past slots on today's date).

    Returns:
        List of dicts with slot_id, doctor_id, doctor_name, slot_date,
        start_time, and end_time.
    """
    sql = """
        SELECT
            v_available_appointment_slots.slot_id,
            v_available_appointment_slots.doctor_id,
            v_available_appointment_slots.doctor_name,
            v_available_appointment_slots.slot_date,
            v_available_appointment_slots.start_time,
            v_available_appointment_slots.end_time
        FROM v_available_appointment_slots
        WHERE v_available_appointment_slots.slot_date = %s
    """
    params: tuple[Any, ...] = (from_date,)
    if current_time is not None:
        sql += """
            AND v_available_appointment_slots.start_time > %s
        """
        params = (from_date, current_time)
    sql += """
        ORDER BY
            v_available_appointment_slots.slot_date,
            v_available_appointment_slots.start_time,
            v_available_appointment_slots.doctor_name
    """
    return fetch_all(connection, sql, params)


def get_available_slot_for_update(
    connection: Any,
    slot_id: int,
) -> dict[str, Any] | None:
    """Lock an available slot row for the duration of a booking transaction.

    Args:
        slot_id: Primary key of the appointment slot.

    Returns:
        A dict with slot_id, staff_id, slot_date, and start_time if the slot
        exists and is available, otherwise None.
    """
    sql = """
        SELECT
            appointment_slots.slot_id,
            appointment_slots.staff_id,
            appointment_slots.slot_date,
            appointment_slots.start_time
        FROM appointment_slots
        INNER JOIN slot_statuses
            ON slot_statuses.slot_status_id = appointment_slots.slot_status_id
        WHERE appointment_slots.slot_id = %s
            AND slot_statuses.status_name = %s
        FOR UPDATE
    """
    return fetch_one(connection, sql, (slot_id, "available"))


def get_appointment_for_update(
    connection: Any,
    appointment_id: int,
) -> dict[str, Any] | None:
    """Lock an appointment row for the duration of a status-update transaction.

    Args:
        appointment_id: Primary key of the appointment.

    Returns:
        A dict with appointment_id, slot_id, and status, or None if not found.
    """
    sql = """
        SELECT
            appointments.appointment_id,
            appointments.slot_id,
            appointment_statuses.status_name AS status
        FROM appointments
        INNER JOIN appointment_statuses
            ON appointment_statuses.status_id = appointments.status_id
        WHERE appointments.appointment_id = %s
        FOR UPDATE
    """
    return fetch_one(connection, sql, (appointment_id,))


def get_appointment_status_id(connection: Any, status_name: str) -> int | None:
    """Look up the numeric status ID for the given appointment status name.

    Args:
        status_name: Status name such as "booked", "completed", or "cancelled".

    Returns:
        The integer status_id, or None if the status name is not found.
    """
    sql = """
        SELECT appointment_statuses.status_id
        FROM appointment_statuses
        WHERE appointment_statuses.status_name = %s
    """
    row = fetch_one(connection, sql, (status_name,))
    return int(row["status_id"]) if row else None


def get_slot_status_id(connection: Any, status_name: str) -> int | None:
    """Look up the numeric status ID for the given slot status name.

    Args:
        status_name: Slot status name such as "available" or "booked".

    Returns:
        The integer slot_status_id, or None if the status name is not found.
    """
    sql = """
        SELECT slot_statuses.slot_status_id
        FROM slot_statuses
        WHERE slot_statuses.status_name = %s
    """
    row = fetch_one(connection, sql, (status_name,))
    return int(row["slot_status_id"]) if row else None


def insert_appointment(
    connection: Any,
    student_id: int,
    slot_id: int,
    status_id: int,
    reason: str | None,
) -> int:
    """Insert a new appointment row and return the generated appointment ID.

    Args:
        student_id: Foreign-key ID of the student making the booking.
        slot_id: Foreign-key ID of the slot being reserved.
        status_id: Foreign-key ID of the initial appointment status.
        reason: Optional free-text reason the student provided.

    Returns:
        The auto-generated appointment_id of the new row.
    """
    sql = """
        INSERT INTO appointments (
            student_id,
            slot_id,
            status_id,
            reason
        )
        VALUES (%s, %s, %s, %s)
    """
    return execute(connection, sql, (student_id, slot_id, status_id, reason))


def update_slot_status(
    connection: Any,
    slot_id: int,
    slot_status_id: int,
) -> None:
    """Update the status of an appointment slot.

    Args:
        slot_id: Primary key of the slot to update.
        slot_status_id: Foreign-key ID of the new slot status.
    """
    sql = """
        UPDATE appointment_slots
        SET slot_status_id = %s
        WHERE slot_id = %s
    """
    execute(connection, sql, (slot_status_id, slot_id))


def update_appointment_status(
    connection: Any,
    appointment_id: int,
    status_id: int,
) -> None:
    """Update the status of an appointment record.

    Args:
        appointment_id: Primary key of the appointment to update.
        status_id: Foreign-key ID of the new appointment status.
    """
    sql = """
        UPDATE appointments
        SET status_id = %s
        WHERE appointment_id = %s
    """
    execute(connection, sql, (status_id, appointment_id))


def list_appointments_to_cancel(
    connection: Any,
    staff_id: int,
    override_date: date,
    start_time: time | None,
    end_time: time | None,
) -> list[dict[str, Any]]:
    """Return booked appointments on a date that fall within an optional time window.

    Args:
        staff_id: Primary key of the doctor's staff record.
        override_date: The date being blocked by an availability override.
        start_time: If provided with end_time, restricts to slots starting at or after this time.
        end_time: If provided with start_time, restricts to slots ending at or before this time.

    Returns:
        List of dicts with appointment_id, student_id, and slot_id for each
        booked appointment that matches the criteria.
    """
    sql = """
        SELECT
            appointments.appointment_id,
            appointments.student_id,
            appointment_slots.slot_id
        FROM appointments
        INNER JOIN appointment_slots
            ON appointment_slots.slot_id = appointments.slot_id
        INNER JOIN appointment_statuses
            ON appointment_statuses.status_id = appointments.status_id
        WHERE appointment_slots.staff_id = %s
            AND appointment_slots.slot_date = %s
            AND appointment_statuses.status_name = %s
    """
    params: tuple[Any, ...] = (staff_id, override_date, "booked")
    if start_time is not None and end_time is not None:
        sql += """
            AND appointment_slots.start_time >= %s
            AND appointment_slots.end_time <= %s
        """
        params = (staff_id, override_date, "booked", start_time, end_time)
    sql += """
        ORDER BY appointment_slots.start_time
    """
    return fetch_all(connection, sql, params)


def cancel_appointment_with_reason(
    connection: Any,
    appointment_id: int,
    cancelled_status_id: int,
    available_slot_status_id: int,
    slot_id: int,
    cancellation_reason: str,
) -> None:
    """Cancel an appointment and restore the slot to available in a single call.

    Args:
        appointment_id: Primary key of the appointment to cancel.
        cancelled_status_id: Foreign-key ID of the "cancelled" appointment status.
        available_slot_status_id: Foreign-key ID of the "available" slot status.
        slot_id: Primary key of the slot to reopen.
        cancellation_reason: Human-readable explanation stored on the appointment.
    """
    sql = """
        UPDATE appointments
        SET
            status_id = %s,
            cancellation_reason = %s
        WHERE appointment_id = %s
    """
    execute(
        connection,
        sql,
        (cancelled_status_id, cancellation_reason, appointment_id),
    )
    update_slot_status(
        connection,
        slot_id=slot_id,
        slot_status_id=available_slot_status_id,
    )


def get_booking_result(
    connection: Any,
    appointment_id: int,
) -> dict[str, Any] | None:
    """Fetch the minimal booking confirmation data for a completed booking.

    Args:
        appointment_id: Primary key of the appointment.

    Returns:
        A dict with appointment_id, slot_id, and status, or None if not found.
    """
    sql = """
        SELECT
            appointments.appointment_id,
            appointments.slot_id,
            appointment_statuses.status_name AS status
        FROM appointments
        INNER JOIN appointment_statuses
            ON appointment_statuses.status_id = appointments.status_id
        WHERE appointments.appointment_id = %s
    """
    return fetch_one(connection, sql, (appointment_id,))


def get_status_result(
    connection: Any,
    appointment_id: int,
) -> dict[str, Any] | None:
    """Fetch the current status of an appointment after a status transition.

    Args:
        appointment_id: Primary key of the appointment.

    Returns:
        A dict with appointment_id and status, or None if not found.
    """
    sql = """
        SELECT
            appointments.appointment_id,
            appointment_statuses.status_name AS status
        FROM appointments
        INNER JOIN appointment_statuses
            ON appointment_statuses.status_id = appointments.status_id
        WHERE appointments.appointment_id = %s
    """
    return fetch_one(connection, sql, (appointment_id,))


def get_appointment_access_context(
    connection: Any,
    appointment_id: int,
) -> dict[str, Any] | None:
    """Fetch ownership and status info needed for appointment access control.

    Args:
        appointment_id: Primary key of the appointment.

    Returns:
        A dict with appointment_id, student_id, doctor_id, and status,
        or None if the appointment does not exist.
    """
    sql = """
        SELECT
            appointments.appointment_id,
            appointments.student_id,
            appointment_slots.staff_id AS doctor_id,
            appointment_statuses.status_name AS status
        FROM appointments
        INNER JOIN appointment_slots
            ON appointment_slots.slot_id = appointments.slot_id
        INNER JOIN appointment_statuses
            ON appointment_statuses.status_id = appointments.status_id
        WHERE appointments.appointment_id = %s
    """
    return fetch_one(connection, sql, (appointment_id,))
