from typing import Any

from app.backend.app.db.queries._helpers import execute, fetch_all, fetch_one


def get_appointment_exists(connection: Any, appointment_id: int) -> dict[str, Any] | None:
    sql = """
        SELECT appointments.appointment_id
        FROM appointments
        WHERE appointments.appointment_id = %s
    """
    return fetch_one(connection, sql, (appointment_id,))


def upsert_medical_note(
    connection: Any,
    appointment_id: int,
    diagnosis: str,
    remarks: str | None,
) -> None:
    sql = """
        INSERT INTO medical_notes (
            appointment_id,
            diagnosis,
            remarks
        )
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE
            diagnosis = VALUES(diagnosis),
            remarks = VALUES(remarks)
    """
    execute(connection, sql, (appointment_id, diagnosis, remarks))


def get_medical_note(connection: Any, appointment_id: int) -> dict[str, Any] | None:
    sql = """
        SELECT
            medical_notes.note_id,
            medical_notes.appointment_id,
            medical_notes.diagnosis,
            medical_notes.remarks
        FROM medical_notes
        WHERE medical_notes.appointment_id = %s
    """
    return fetch_one(connection, sql, (appointment_id,))


def get_prescription_by_appointment(
    connection: Any,
    appointment_id: int,
) -> dict[str, Any] | None:
    sql = """
        SELECT
            prescriptions.prescription_id,
            prescriptions.appointment_id
        FROM prescriptions
        WHERE prescriptions.appointment_id = %s
    """
    return fetch_one(connection, sql, (appointment_id,))


def insert_prescription(connection: Any, appointment_id: int) -> int:
    sql = """
        INSERT INTO prescriptions (appointment_id)
        VALUES (%s)
    """
    return execute(connection, sql, (appointment_id,))


def delete_prescription_items(connection: Any, prescription_id: int) -> None:
    sql = """
        DELETE FROM prescription_items
        WHERE prescription_id = %s
    """
    execute(connection, sql, (prescription_id,))


def insert_prescription_item(
    connection: Any,
    prescription_id: int,
    medicine_name: str,
    dosage: str,
) -> int:
    sql = """
        INSERT INTO prescription_items (
            prescription_id,
            medicine_name,
            dosage
        )
        VALUES (%s, %s, %s)
    """
    return execute(connection, sql, (prescription_id, medicine_name, dosage))


def list_prescription_items(
    connection: Any,
    prescription_id: int,
) -> list[dict[str, Any]]:
    sql = """
        SELECT
            prescription_items.item_id,
            prescription_items.medicine_name,
            prescription_items.dosage
        FROM prescription_items
        WHERE prescription_items.prescription_id = %s
        ORDER BY prescription_items.item_id
    """
    return fetch_all(connection, sql, (prescription_id,))


def get_report_appointment(
    connection: Any,
    appointment_id: int,
) -> dict[str, Any] | None:
    sql = """
        SELECT
            appointments.appointment_id,
            students.student_id,
            student_users.name AS student_name,
            staff.staff_id AS doctor_id,
            doctor_users.name AS doctor_name,
            appointment_slots.slot_date,
            appointment_slots.start_time,
            appointment_slots.end_time,
            appointment_statuses.status_name AS status
        FROM appointments
        INNER JOIN students ON students.student_id = appointments.student_id
        INNER JOIN users AS student_users ON student_users.user_id = students.user_id
        INNER JOIN appointment_slots
            ON appointment_slots.slot_id = appointments.slot_id
        INNER JOIN staff ON staff.staff_id = appointment_slots.staff_id
        INNER JOIN users AS doctor_users ON doctor_users.user_id = staff.user_id
        INNER JOIN appointment_statuses
            ON appointment_statuses.status_id = appointments.status_id
        WHERE appointments.appointment_id = %s
    """
    return fetch_one(connection, sql, (appointment_id,))
