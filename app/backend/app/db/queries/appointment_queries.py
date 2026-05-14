from datetime import date
from typing import Any

from app.backend.app.db.queries._helpers import execute, fetch_all, fetch_one


def list_available_slots(connection: Any, from_date: date) -> list[dict[str, Any]]:
    sql = """
        SELECT
            v_available_appointment_slots.slot_id,
            v_available_appointment_slots.doctor_id,
            v_available_appointment_slots.doctor_name,
            v_available_appointment_slots.slot_date,
            v_available_appointment_slots.start_time,
            v_available_appointment_slots.end_time
        FROM v_available_appointment_slots
        WHERE v_available_appointment_slots.slot_date >= %s
        ORDER BY
            v_available_appointment_slots.slot_date,
            v_available_appointment_slots.start_time,
            v_available_appointment_slots.doctor_name
    """
    return fetch_all(connection, sql, (from_date,))


def get_available_slot_for_update(
    connection: Any,
    slot_id: int,
) -> dict[str, Any] | None:
    sql = """
        SELECT
            appointment_slots.slot_id,
            appointment_slots.staff_id
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
    sql = """
        SELECT
            appointments.appointment_id,
            appointments.slot_id
        FROM appointments
        WHERE appointments.appointment_id = %s
        FOR UPDATE
    """
    return fetch_one(connection, sql, (appointment_id,))


def get_appointment_status_id(connection: Any, status_name: str) -> int | None:
    sql = """
        SELECT appointment_statuses.status_id
        FROM appointment_statuses
        WHERE appointment_statuses.status_name = %s
    """
    row = fetch_one(connection, sql, (status_name,))
    return int(row["status_id"]) if row else None


def get_slot_status_id(connection: Any, status_name: str) -> int | None:
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
    sql = """
        UPDATE appointments
        SET status_id = %s
        WHERE appointment_id = %s
    """
    execute(connection, sql, (status_id, appointment_id))


def get_booking_result(
    connection: Any,
    appointment_id: int,
) -> dict[str, Any] | None:
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
