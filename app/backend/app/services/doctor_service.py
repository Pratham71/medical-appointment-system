from datetime import date
from typing import Any

from app.backend.app.api.errors import NotFoundError
from app.backend.app.repositories import doctor_repo
from app.backend.app.schemas.doctor import (
    DoctorAvailabilityDeleteResponse,
    DoctorAvailabilityOverride,
    DoctorAvailabilityOverrideUpdate,
    DoctorAvailabilitySettings,
    DoctorAvailabilityUpdate,
    DoctorWeeklyAvailability,
    DoctorAppointmentDetail,
    DoctorAppointmentSummary,
    DoctorDashboard,
    PatientHistoryItem,
    PatientSearchResult,
)
from app.backend.app.services import notification_service


_WEEKDAY_NAMES = {
    0: "Monday",
    1: "Tuesday",
    2: "Wednesday",
    3: "Thursday",
    4: "Friday",
    5: "Saturday",
    6: "Sunday",
}


def get_dashboard(staff_id: int) -> DoctorDashboard:
    """Return aggregated dashboard statistics for a doctor.

    Args:
        staff_id: Primary key of the doctor's staff record.

    Returns:
        A DoctorDashboard schema object with appointment counts.

    Raises:
        NotFoundError: If the doctor does not exist.
    """
    row = doctor_repo.get_dashboard_counts(staff_id)
    if row is None:
        raise NotFoundError("Doctor was not found")
    return DoctorDashboard(**row)


def list_appointments(staff_id: int) -> list[DoctorAppointmentSummary]:
    """Return all appointments assigned to a doctor.

    Args:
        staff_id: Primary key of the doctor's staff record.

    Returns:
        List of DoctorAppointmentSummary objects ordered by date and time.
    """
    rows = doctor_repo.list_appointments(staff_id)
    return [DoctorAppointmentSummary(**row) for row in rows]


def get_availability(staff_id: int) -> DoctorAvailabilitySettings:
    """Return the full availability configuration for a doctor.

    Args:
        staff_id: Primary key of the doctor's staff record.

    Returns:
        A DoctorAvailabilitySettings object with weekly rules and date overrides
        for all 7 days of the week (defaulting missing days to Mon-Fri available).
    """
    availability = doctor_repo.get_availability(staff_id)
    weekly_rows = {
        int(row["weekday"]): row
        for row in availability.get("weekly_availability", [])
    }
    weekly_availability = [
        _weekly_availability_response(weekly_rows.get(weekday), weekday)
        for weekday in range(7)
    ]
    date_overrides = [
        DoctorAvailabilityOverride(**row)
        for row in availability.get("date_overrides", [])
    ]
    return DoctorAvailabilitySettings(
        doctor_id=staff_id,
        weekly_availability=weekly_availability,
        date_overrides=date_overrides,
    )


def upsert_weekly_availability(
    staff_id: int,
    weekday: int,
    payload: DoctorAvailabilityUpdate,
) -> DoctorWeeklyAvailability:
    """Save a weekly availability rule and return the updated entry.

    Args:
        staff_id: Primary key of the doctor's staff record.
        weekday: Day of the week (0 = Monday, 6 = Sunday).
        payload: Availability update including is_available, start_time, and end_time.

    Returns:
        A DoctorWeeklyAvailability object reflecting the saved rule.
    """
    row = doctor_repo.upsert_weekly_availability(
        staff_id=staff_id,
        weekday=weekday,
        is_available=payload.is_available,
        start_time=payload.start_time if payload.is_available else None,
        end_time=payload.end_time if payload.is_available else None,
    )
    return _weekly_availability_response(row, weekday)


def upsert_availability_override(
    staff_id: int,
    override_date: date,
    payload: DoctorAvailabilityOverrideUpdate,
) -> DoctorAvailabilityOverride:
    """Save a date-specific availability override and send cancellation notifications if needed.

    Args:
        staff_id: Primary key of the doctor's staff record.
        override_date: The calendar date being overridden.
        payload: Override details including is_available, times, and note.

    Returns:
        A DoctorAvailabilityOverride object reflecting the saved override.

    Raises:
        NotFoundError: If the saved override cannot be retrieved.
    """
    row = doctor_repo.upsert_availability_override(
        staff_id=staff_id,
        override_date=override_date,
        is_available=payload.is_available,
        start_time=payload.start_time if payload.is_available else None,
        end_time=payload.end_time if payload.is_available else None,
        note=payload.note,
    )
    if row is None:
        raise NotFoundError("Doctor availability override was not found")
    for appointment_id in row.get("cancelled_appointment_ids", []):
        notification_service.send_appointment_cancelled(appointment_id)
    return DoctorAvailabilityOverride(**row)


def delete_availability_override(
    staff_id: int,
    override_date: date,
) -> DoctorAvailabilityDeleteResponse:
    """Remove a date-specific availability override.

    Args:
        staff_id: Primary key of the doctor's staff record.
        override_date: The calendar date whose override to remove.

    Returns:
        A DoctorAvailabilityDeleteResponse with a confirmation message.
    """
    doctor_repo.delete_availability_override(staff_id, override_date)
    return DoctorAvailabilityDeleteResponse(message="Availability override removed")


def get_appointment_detail(appointment_id: int) -> DoctorAppointmentDetail:
    """Return full appointment detail for the doctor view.

    Args:
        appointment_id: Primary key of the appointment.

    Returns:
        A DoctorAppointmentDetail schema object.

    Raises:
        NotFoundError: If the appointment does not exist.
    """
    row = doctor_repo.get_appointment_detail(appointment_id)
    if row is None:
        raise NotFoundError("Appointment was not found")
    return DoctorAppointmentDetail(**row)


def list_patient_history(student_id: int) -> list[PatientHistoryItem]:
    """Return a student's appointment history for the doctor's patient view.

    Args:
        student_id: Primary key of the student profile.

    Returns:
        List of PatientHistoryItem objects in reverse chronological order.
    """
    rows = doctor_repo.list_patient_history(student_id)
    return [PatientHistoryItem(**row) for row in rows]


def search_patients(
    search_text: str,
    staff_id: int | None,
) -> list[PatientSearchResult]:
    """Search patients by name or roll number, optionally scoped to one doctor.

    Args:
        search_text: Search term to match against patient name and roll number.
        staff_id: If provided, restrict results to patients seen by this doctor.

    Returns:
        Up to 10 PatientSearchResult objects.
    """
    rows = doctor_repo.search_patients(search_text.strip(), staff_id)
    return [PatientSearchResult(**row) for row in rows]


def _weekly_availability_response(
    row: dict[str, Any] | None,
    weekday: int,
) -> DoctorWeeklyAvailability:
    """Build a DoctorWeeklyAvailability response, defaulting to Mon-Fri available.

    Args:
        row: A raw availability row from the database, or None if no rule is set.
        weekday: The weekday integer (0 = Monday) used to fill in missing data.

    Returns:
        A DoctorWeeklyAvailability object with all fields populated.
    """
    data = row or {
        "weekday": weekday,
        "is_available": weekday < 6,
        "start_time": None,
        "end_time": None,
    }
    return DoctorWeeklyAvailability(
        weekday=weekday,
        weekday_name=_WEEKDAY_NAMES[weekday],
        is_available=bool(data["is_available"]),
        start_time=data.get("start_time"),
        end_time=data.get("end_time"),
    )
