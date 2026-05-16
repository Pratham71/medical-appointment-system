from datetime import date, time
from typing import Any

from app.backend.app.db import session
from app.backend.app.db.queries import doctor_queries


def get_dashboard_counts(staff_id: int) -> dict[str, Any] | None:
    with session.connection_scope() as connection:
        return doctor_queries.get_dashboard_counts(connection, staff_id)


def list_appointments(staff_id: int) -> list[dict[str, Any]]:
    with session.connection_scope() as connection:
        return doctor_queries.list_appointments(connection, staff_id)


def get_availability(staff_id: int) -> dict[str, list[dict[str, Any]]]:
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
    with session.transaction_scope() as connection:
        doctor_queries.upsert_availability_override(
            connection,
            staff_id=staff_id,
            override_date=override_date,
            is_available=is_available,
            start_time=start_time,
            end_time=end_time,
            note=note,
        )
        return doctor_queries.get_availability_override(
            connection,
            staff_id=staff_id,
            override_date=override_date,
        )


def delete_availability_override(staff_id: int, override_date: date) -> None:
    with session.transaction_scope() as connection:
        doctor_queries.delete_availability_override(
            connection,
            staff_id=staff_id,
            override_date=override_date,
        )


def get_appointment_detail(appointment_id: int) -> dict[str, Any] | None:
    with session.connection_scope() as connection:
        return doctor_queries.get_appointment_detail(connection, appointment_id)


def list_patient_history(student_id: int) -> list[dict[str, Any]]:
    with session.connection_scope() as connection:
        return doctor_queries.list_patient_history(connection, student_id)


def search_patients(search_text: str, staff_id: int | None) -> list[dict[str, Any]]:
    with session.connection_scope() as connection:
        if staff_id is None:
            return doctor_queries.search_patients(connection, search_text)
        return doctor_queries.search_patients_for_doctor(
            connection,
            search_text,
            staff_id,
        )


def has_doctor_seen_student(staff_id: int, student_id: int) -> bool:
    with session.connection_scope() as connection:
        return doctor_queries.has_doctor_seen_student(connection, staff_id, student_id)
