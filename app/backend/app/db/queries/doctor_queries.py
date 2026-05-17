from datetime import date, time
from typing import Any

from app.backend.app.db.queries._helpers import execute, fetch_all, fetch_one


def get_dashboard_counts(connection: Any, staff_id: int) -> dict[str, Any] | None:
    """Fetch aggregated dashboard statistics for a single doctor.

    Args:
        staff_id: Primary key of the doctor's staff record.

    Returns:
        A dict with doctor_id, doctor_name, todays_appointments,
        upcoming_appointments, completed_appointments, and total_patients,
        or None if the doctor does not exist.
    """
    sql = """
        SELECT
            staff.staff_id AS doctor_id,
            users.name AS doctor_name,
            (
                SELECT COUNT(appointments.appointment_id)
                FROM appointments
                INNER JOIN appointment_slots
                    ON appointment_slots.slot_id = appointments.slot_id
                WHERE appointment_slots.staff_id = staff.staff_id
                    AND appointment_slots.slot_date = CURRENT_DATE
            ) AS todays_appointments,
            (
                SELECT COUNT(appointments.appointment_id)
                FROM appointments
                INNER JOIN appointment_slots
                    ON appointment_slots.slot_id = appointments.slot_id
                INNER JOIN appointment_statuses
                    ON appointment_statuses.status_id = appointments.status_id
                WHERE appointment_slots.staff_id = staff.staff_id
                    AND appointment_slots.slot_date >= CURRENT_DATE
                    AND appointment_statuses.status_name = %s
            ) AS upcoming_appointments,
            (
                SELECT COUNT(appointments.appointment_id)
                FROM appointments
                INNER JOIN appointment_slots
                    ON appointment_slots.slot_id = appointments.slot_id
                INNER JOIN appointment_statuses
                    ON appointment_statuses.status_id = appointments.status_id
                WHERE appointment_slots.staff_id = staff.staff_id
                    AND appointment_statuses.status_name = %s
            ) AS completed_appointments,
            (
                SELECT COUNT(DISTINCT appointments.student_id)
                FROM appointments
                INNER JOIN appointment_slots
                    ON appointment_slots.slot_id = appointments.slot_id
                WHERE appointment_slots.staff_id = staff.staff_id
            ) AS total_patients
        FROM staff
        INNER JOIN users ON users.user_id = staff.user_id
        WHERE staff.staff_id = %s
            AND staff.is_doctor = TRUE
    """
    return fetch_one(connection, sql, ("booked", "completed", staff_id))


def list_appointments(connection: Any, staff_id: int) -> list[dict[str, Any]]:
    """Return all appointments assigned to a doctor, ordered by date and time.

    Args:
        staff_id: Primary key of the doctor's staff record.

    Returns:
        List of dicts with appointment_id, slot_date, start_time, end_time,
        student_id, student_name, and status.
    """
    sql = """
        SELECT
            v_doctor_appointment_summaries.appointment_id,
            v_doctor_appointment_summaries.slot_date,
            v_doctor_appointment_summaries.start_time,
            v_doctor_appointment_summaries.end_time,
            v_doctor_appointment_summaries.student_id,
            v_doctor_appointment_summaries.student_name,
            v_doctor_appointment_summaries.status
        FROM v_doctor_appointment_summaries
        WHERE v_doctor_appointment_summaries.doctor_id = %s
        ORDER BY
            v_doctor_appointment_summaries.slot_date,
            v_doctor_appointment_summaries.start_time
    """
    return fetch_all(connection, sql, (staff_id,))


def list_weekly_availability(
    connection: Any,
    staff_id: int,
) -> list[dict[str, Any]]:
    """Return the recurring weekly availability rules for a doctor.

    Args:
        staff_id: Primary key of the doctor's staff record.

    Returns:
        List of dicts with weekday, is_available, start_time, and end_time,
        ordered by weekday (0 = Monday).
    """
    sql = """
        SELECT
            doctor_weekly_availability.weekday,
            doctor_weekly_availability.is_available,
            doctor_weekly_availability.start_time,
            doctor_weekly_availability.end_time
        FROM doctor_weekly_availability
        WHERE doctor_weekly_availability.staff_id = %s
        ORDER BY doctor_weekly_availability.weekday
    """
    return fetch_all(connection, sql, (staff_id,))


def get_weekly_availability_rule(
    connection: Any,
    staff_id: int,
    weekday: int,
) -> dict[str, Any] | None:
    """Fetch a single weekly availability rule for a doctor on a specific weekday.

    Args:
        staff_id: Primary key of the doctor's staff record.
        weekday: Day of the week as an integer (0 = Monday, 6 = Sunday).

    Returns:
        A dict with weekday, is_available, start_time, and end_time,
        or None if no rule has been set for that weekday.
    """
    sql = """
        SELECT
            doctor_weekly_availability.weekday,
            doctor_weekly_availability.is_available,
            doctor_weekly_availability.start_time,
            doctor_weekly_availability.end_time
        FROM doctor_weekly_availability
        WHERE doctor_weekly_availability.staff_id = %s
            AND doctor_weekly_availability.weekday = %s
    """
    return fetch_one(connection, sql, (staff_id, weekday))


def upsert_weekly_availability(
    connection: Any,
    staff_id: int,
    weekday: int,
    is_available: bool,
    start_time: time | None,
    end_time: time | None,
) -> None:
    """Insert or update the weekly availability rule for a doctor on a given weekday.

    Args:
        staff_id: Primary key of the doctor's staff record.
        weekday: Day of the week (0 = Monday, 6 = Sunday).
        is_available: Whether the doctor is available on this weekday.
        start_time: Working hours start time, or None to use the default.
        end_time: Working hours end time, or None to use the default.
    """
    sql = """
        INSERT INTO doctor_weekly_availability (
            staff_id,
            weekday,
            is_available,
            start_time,
            end_time
        )
        VALUES (%s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            is_available = VALUES(is_available),
            start_time = VALUES(start_time),
            end_time = VALUES(end_time)
    """
    execute(connection, sql, (staff_id, weekday, is_available, start_time, end_time))


def list_availability_overrides(
    connection: Any,
    staff_id: int,
) -> list[dict[str, Any]]:
    """Return all date-specific availability overrides for a doctor.

    Args:
        staff_id: Primary key of the doctor's staff record.

    Returns:
        List of dicts with override_date, is_available, start_time, end_time,
        and note, ordered by date.
    """
    sql = """
        SELECT
            doctor_availability_overrides.override_date,
            doctor_availability_overrides.is_available,
            doctor_availability_overrides.start_time,
            doctor_availability_overrides.end_time,
            doctor_availability_overrides.note
        FROM doctor_availability_overrides
        WHERE doctor_availability_overrides.staff_id = %s
        ORDER BY doctor_availability_overrides.override_date
    """
    return fetch_all(connection, sql, (staff_id,))


def get_availability_override(
    connection: Any,
    staff_id: int,
    override_date: date,
) -> dict[str, Any] | None:
    """Fetch the availability override for a doctor on a specific date.

    Args:
        staff_id: Primary key of the doctor's staff record.
        override_date: The calendar date of the override.

    Returns:
        A dict with override_date, is_available, start_time, end_time, and note,
        or None if no override exists for that date.
    """
    sql = """
        SELECT
            doctor_availability_overrides.override_date,
            doctor_availability_overrides.is_available,
            doctor_availability_overrides.start_time,
            doctor_availability_overrides.end_time,
            doctor_availability_overrides.note
        FROM doctor_availability_overrides
        WHERE doctor_availability_overrides.staff_id = %s
            AND doctor_availability_overrides.override_date = %s
    """
    return fetch_one(connection, sql, (staff_id, override_date))


def upsert_availability_override(
    connection: Any,
    staff_id: int,
    override_date: date,
    is_available: bool,
    start_time: time | None,
    end_time: time | None,
    note: str | None,
) -> None:
    """Insert or update a date-specific availability override for a doctor.

    Args:
        staff_id: Primary key of the doctor's staff record.
        override_date: The calendar date being overridden.
        is_available: Whether the doctor is available on this date.
        start_time: Working hours start time, or None to clear.
        end_time: Working hours end time, or None to clear.
        note: Optional human-readable reason for the override.
    """
    sql = """
        INSERT INTO doctor_availability_overrides (
            staff_id,
            override_date,
            is_available,
            start_time,
            end_time,
            note
        )
        VALUES (%s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            is_available = VALUES(is_available),
            start_time = VALUES(start_time),
            end_time = VALUES(end_time),
            note = VALUES(note)
    """
    execute(
        connection,
        sql,
        (staff_id, override_date, is_available, start_time, end_time, note),
    )


def delete_availability_override(
    connection: Any,
    staff_id: int,
    override_date: date,
) -> None:
    """Delete the availability override for a doctor on a specific date.

    Args:
        staff_id: Primary key of the doctor's staff record.
        override_date: The calendar date whose override should be removed.
    """
    sql = """
        DELETE FROM doctor_availability_overrides
        WHERE doctor_availability_overrides.staff_id = %s
            AND doctor_availability_overrides.override_date = %s
    """
    execute(connection, sql, (staff_id, override_date))


def get_appointment_detail(
    connection: Any,
    appointment_id: int,
) -> dict[str, Any] | None:
    """Fetch full appointment details including student, doctor, and certificate info.

    Args:
        appointment_id: Primary key of the appointment.

    Returns:
        A dict with appointment_id, slot_date, start_time, end_time, status,
        student/doctor identifiers and names, reason, diagnosis, remarks,
        certificate_id, and certificate_type, or None if not found.
    """
    sql = """
        SELECT
            v_appointment_details.appointment_id,
            v_appointment_details.slot_date,
            v_appointment_details.start_time,
            v_appointment_details.end_time,
            v_appointment_details.status,
            v_appointment_details.student_id,
            v_appointment_details.student_name,
            v_appointment_details.student_email,
            v_appointment_details.doctor_id,
            v_appointment_details.doctor_name,
            v_appointment_details.reason,
            v_appointment_details.diagnosis,
            v_appointment_details.remarks,
            v_appointment_details.certificate_id,
            v_appointment_details.certificate_type
        FROM v_appointment_details
        WHERE v_appointment_details.appointment_id = %s
    """
    return fetch_one(connection, sql, (appointment_id,))


def list_patient_history(connection: Any, student_id: int) -> list[dict[str, Any]]:
    """Return a student's full appointment history in reverse chronological order.

    Args:
        student_id: Primary key of the student profile.

    Returns:
        List of dicts with appointment_id, slot_date, start/end times, doctor info,
        status, reason, diagnosis, remarks, and certificate details.
    """
    sql = """
        SELECT
            v_appointment_details.appointment_id,
            v_appointment_details.slot_date,
            v_appointment_details.start_time,
            v_appointment_details.end_time,
            v_appointment_details.doctor_id,
            v_appointment_details.doctor_name,
            v_appointment_details.status,
            v_appointment_details.reason,
            v_appointment_details.diagnosis,
            v_appointment_details.remarks,
            v_appointment_details.certificate_id,
            v_appointment_details.certificate_type
        FROM v_appointment_details
        WHERE v_appointment_details.student_id = %s
        ORDER BY
            v_appointment_details.slot_date DESC,
            v_appointment_details.start_time DESC
    """
    return fetch_all(connection, sql, (student_id,))


def search_patients_for_doctor(
    connection: Any,
    search_text: str,
    staff_id: int,
) -> list[dict[str, Any]]:
    """Search for patients that a specific doctor has previously seen.

    Args:
        search_text: Partial name or roll number to match (LIKE pattern).
        staff_id: Primary key of the doctor's staff record.

    Returns:
        Up to 10 dicts each with student_id, student_name, roll_number,
        department, and year_level.
    """
    pattern = f"%{search_text}%"
    sql = """
        SELECT DISTINCT
            students.student_id,
            users.name AS student_name,
            students.roll_number,
            students.department,
            students.year_level
        FROM students
        INNER JOIN users
            ON users.user_id = students.user_id
        INNER JOIN appointments
            ON appointments.student_id = students.student_id
        INNER JOIN appointment_slots
            ON appointment_slots.slot_id = appointments.slot_id
        WHERE appointment_slots.staff_id = %s
            AND (
                users.name LIKE %s
                OR students.roll_number LIKE %s
            )
        ORDER BY users.name, students.roll_number
        LIMIT 10
    """
    return fetch_all(connection, sql, (staff_id, pattern, pattern))


def search_patients(
    connection: Any,
    search_text: str,
) -> list[dict[str, Any]]:
    """Search for patients across the entire student population.

    Args:
        search_text: Partial name or roll number to match (LIKE pattern).

    Returns:
        Up to 10 dicts each with student_id, student_name, roll_number,
        department, and year_level.
    """
    pattern = f"%{search_text}%"
    sql = """
        SELECT
            students.student_id,
            users.name AS student_name,
            students.roll_number,
            students.department,
            students.year_level
        FROM students
        INNER JOIN users
            ON users.user_id = students.user_id
        WHERE users.name LIKE %s
            OR students.roll_number LIKE %s
        ORDER BY users.name, students.roll_number
        LIMIT 10
    """
    return fetch_all(connection, sql, (pattern, pattern))


def has_doctor_seen_student(
    connection: Any,
    staff_id: int,
    student_id: int,
) -> bool:
    """Check whether a doctor has ever had an appointment with a student.

    Args:
        staff_id: Primary key of the doctor's staff record.
        student_id: Primary key of the student profile.

    Returns:
        True if at least one shared appointment exists, False otherwise.
    """
    sql = """
        SELECT appointments.appointment_id
        FROM appointments
        INNER JOIN appointment_slots
            ON appointment_slots.slot_id = appointments.slot_id
        WHERE appointment_slots.staff_id = %s
            AND appointments.student_id = %s
        LIMIT 1
    """
    return fetch_one(connection, sql, (staff_id, student_id)) is not None
