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
    row = doctor_repo.get_dashboard_counts(staff_id)
    if row is None:
        raise NotFoundError("Doctor was not found")
    return DoctorDashboard(**row)


def list_appointments(staff_id: int) -> list[DoctorAppointmentSummary]:
    rows = doctor_repo.list_appointments(staff_id)
    return [DoctorAppointmentSummary(**row) for row in rows]


def get_availability(staff_id: int) -> DoctorAvailabilitySettings:
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
    return DoctorAvailabilityOverride(**row)


def delete_availability_override(
    staff_id: int,
    override_date: date,
) -> DoctorAvailabilityDeleteResponse:
    doctor_repo.delete_availability_override(staff_id, override_date)
    return DoctorAvailabilityDeleteResponse(message="Availability override removed")


def get_appointment_detail(appointment_id: int) -> DoctorAppointmentDetail:
    row = doctor_repo.get_appointment_detail(appointment_id)
    if row is None:
        raise NotFoundError("Appointment was not found")
    return DoctorAppointmentDetail(**row)


def list_patient_history(student_id: int) -> list[PatientHistoryItem]:
    rows = doctor_repo.list_patient_history(student_id)
    return [PatientHistoryItem(**row) for row in rows]


def search_patients(
    search_text: str,
    staff_id: int | None,
) -> list[PatientSearchResult]:
    rows = doctor_repo.search_patients(search_text.strip(), staff_id)
    return [PatientSearchResult(**row) for row in rows]


def _weekly_availability_response(
    row: dict[str, Any] | None,
    weekday: int,
) -> DoctorWeeklyAvailability:
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
