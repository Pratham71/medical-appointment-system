from datetime import date, time
from typing import Any

from app.backend.app.db import session
from app.backend.app.db.queries import appointment_queries, doctor_queries


def get_dashboard_counts(staff_id: int) -> dict[str, Any] | None:
    """Fetch aggregated dashboard statistics for a doctor.

    Args:
        staff_id: Primary key of the doctor's staff record.

    Returns:
        A dict with dashboard counts, or None if the doctor does not exist.
    """
    with session.connection_scope() as connection:
        return doctor_queries.get_dashboard_counts(connection, staff_id)


def list_appointments(staff_id: int) -> list[dict[str, Any]]:
    """Return all appointments assigned to a doctor.

    Args:
        staff_id: Primary key of the doctor's staff record.

    Returns:
        List of appointment summary dicts ordered by date and time.
    """
    with session.connection_scope() as connection:
        return doctor_queries.list_appointments(connection, staff_id)


def get_availability(staff_id: int) -> dict[str, list[dict[str, Any]]]:
    """Return the complete availability configuration for a doctor.

    Args:
        staff_id: Primary key of the doctor's staff record.

    Returns:
        A dict with "weekly_availability" (list of weekday rules) and
        "date_overrides" (list of date-specific override rules).
    """
    with session.connection_scope() as connection:
        return {
            "weekly_availability": doctor_queries.list_weekly_availability(
                connection,
                staff_id,
            ),
            "date_overrides": doctor_queries.list_availability_overrides(
                connection,
                staff_id,
            ),
        }


def upsert_weekly_availability(
    staff_id: int,
    weekday: int,
    is_available: bool,
    start_time: time | None,
    end_time: time | None,
) -> dict[str, Any] | None:
    """Save a weekly availability rule and return the updated record.

    Args:
        staff_id: Primary key of the doctor's staff record.
        weekday: Day of the week (0 = Monday, 6 = Sunday).
        is_available: Whether the doctor is available on this weekday.
        start_time: Working hours start time, or None to use the default.
        end_time: Working hours end time, or None to use the default.

    Returns:
        The saved rule as a dict, or None if retrieval fails.
    """
    with session.transaction_scope() as connection:
        doctor_queries.upsert_weekly_availability(
            connection,
            staff_id=staff_id,
            weekday=weekday,
            is_available=is_available,
            start_time=start_time,
            end_time=end_time,
        )
        return doctor_queries.get_weekly_availability_rule(
            connection,
            staff_id=staff_id,
            weekday=weekday,
        )


def upsert_availability_override(
    staff_id: int,
    override_date: date,
    is_available: bool,
    start_time: time | None,
    end_time: time | None,
    note: str | None,
) -> dict[str, Any] | None:
    """Save a date override and cancel any conflicting booked appointments.

    When is_available is False, all booked appointments on that date (within the
    optional time window) are cancelled and the affected appointment IDs are
    included in the returned dict under "cancelled_appointment_ids".

    Args:
        staff_id: Primary key of the doctor's staff record.
        override_date: The calendar date being overridden.
        is_available: Whether the doctor is available on this date.
        start_time: Override window start, or None to cover the whole day.
        end_time: Override window end, or None to cover the whole day.
        note: Optional reason for the override.

    Returns:
        The saved override dict with an additional "cancelled_appointment_ids" list,
        or None if retrieval fails.
    """
    with session.transaction_scope() as connection:
        cancelled_appointment_ids = []
        doctor_queries.upsert_availability_override(
            connection,
            staff_id=staff_id,
            override_date=override_date,
            is_available=is_available,
            start_time=start_time,
            end_time=end_time,
            note=note,
        )
        if not is_available:
            cancelled_status_id = appointment_queries.get_appointment_status_id(
                connection,
                "cancelled",
            )
            available_slot_status_id = appointment_queries.get_slot_status_id(
                connection,
                "available",
            )
            if cancelled_status_id is not None and available_slot_status_id is not None:
                cancellation_reason = "Doctor unavailable"
                if note:
                    cancellation_reason = f"{cancellation_reason}: {note}"
                appointments = appointment_queries.list_appointments_to_cancel(
                    connection,
                    staff_id=staff_id,
                    override_date=override_date,
                    start_time=start_time,
                    end_time=end_time,
                )
                for appointment in appointments:
                    cancelled_appointment_ids.append(int(appointment["appointment_id"]))
                    appointment_queries.cancel_appointment_with_reason(
                        connection,
                        appointment_id=appointment["appointment_id"],
                        cancelled_status_id=cancelled_status_id,
                        available_slot_status_id=available_slot_status_id,
                        slot_id=appointment["slot_id"],
                        cancellation_reason=cancellation_reason,
                    )
        row = doctor_queries.get_availability_override(
            connection,
            staff_id=staff_id,
            override_date=override_date,
        )
        if row is not None:
            row["cancelled_appointment_ids"] = cancelled_appointment_ids
        return row


def delete_availability_override(staff_id: int, override_date: date) -> None:
    """Remove a date-specific availability override for a doctor.

    Args:
        staff_id: Primary key of the doctor's staff record.
        override_date: The calendar date whose override to remove.
    """
    with session.transaction_scope() as connection:
        doctor_queries.delete_availability_override(
            connection,
            staff_id=staff_id,
            override_date=override_date,
        )


def get_appointment_detail(appointment_id: int) -> dict[str, Any] | None:
    """Return full appointment detail including student, doctor, and certificate info.

    Args:
        appointment_id: Primary key of the appointment.

    Returns:
        A full appointment detail dict, or None if not found.
    """
    with session.connection_scope() as connection:
        return doctor_queries.get_appointment_detail(connection, appointment_id)


def list_patient_history(student_id: int) -> list[dict[str, Any]]:
    """Return a student's full appointment history in reverse chronological order.

    Args:
        student_id: Primary key of the student profile.

    Returns:
        List of appointment history dicts.
    """
    with session.connection_scope() as connection:
        return doctor_queries.list_patient_history(connection, student_id)


def search_patients(search_text: str, staff_id: int | None) -> list[dict[str, Any]]:
    """Search patients by name or roll number, optionally scoped to a single doctor.

    Args:
        search_text: Partial name or roll number to search for.
        staff_id: If provided, restrict results to patients seen by this doctor.

    Returns:
        Up to 10 patient summary dicts.
    """
    with session.connection_scope() as connection:
        if staff_id is None:
            return doctor_queries.search_patients(connection, search_text)
        return doctor_queries.search_patients_for_doctor(
            connection,
            search_text,
            staff_id,
        )


def has_doctor_seen_student(staff_id: int, student_id: int) -> bool:
    """Check whether a doctor has ever shared an appointment with a student.

    Args:
        staff_id: Primary key of the doctor's staff record.
        student_id: Primary key of the student profile.

    Returns:
        True if at least one shared appointment exists, False otherwise.
    """
    with session.connection_scope() as connection:
        return doctor_queries.has_doctor_seen_student(connection, staff_id, student_id)
