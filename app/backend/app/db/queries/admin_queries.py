from datetime import date
from typing import Any

from app.backend.app.db.queries._helpers import execute, fetch_all, fetch_one


def get_dashboard_counts(connection: Any) -> dict[str, Any] | None:
    sql = """
        SELECT
            (
                SELECT COUNT(users.user_id)
                FROM users
                INNER JOIN roles ON roles.role_id = users.role_id
                WHERE roles.role_name = %s
                    AND users.is_active = TRUE
            ) AS total_students,
            (
                SELECT COUNT(users.user_id)
                FROM users
                INNER JOIN roles ON roles.role_id = users.role_id
                WHERE roles.role_name = %s
                    AND users.is_active = TRUE
            ) AS total_professors,
            (
                SELECT COUNT(staff.staff_id)
                FROM staff
                WHERE staff.is_doctor = TRUE
            ) AS total_doctors,
            (
                SELECT COUNT(staff.staff_id)
                FROM staff
                WHERE staff.is_doctor = FALSE
            ) AS total_staff,
            (
                SELECT COUNT(appointments.appointment_id)
                FROM appointments
                INNER JOIN appointment_slots
                    ON appointment_slots.slot_id = appointments.slot_id
                WHERE appointment_slots.slot_date = CURRENT_DATE
            ) AS appointments_today,
            (
                SELECT COUNT(appointments.appointment_id)
                FROM appointments
                INNER JOIN appointment_statuses
                    ON appointment_statuses.status_id = appointments.status_id
                WHERE appointment_statuses.status_name = %s
            ) AS booked_appointments,
            (
                SELECT COUNT(appointments.appointment_id)
                FROM appointments
                INNER JOIN appointment_statuses
                    ON appointment_statuses.status_id = appointments.status_id
                WHERE appointment_statuses.status_name = %s
            ) AS completed_appointments,
            (
                SELECT COUNT(appointments.appointment_id)
                FROM appointments
                INNER JOIN appointment_statuses
                    ON appointment_statuses.status_id = appointments.status_id
                WHERE appointment_statuses.status_name = %s
            ) AS cancelled_appointments,
            (SELECT COUNT(medical_notes.note_id) FROM medical_notes)
                AS reports_available,
            (
                SELECT COUNT(medical_certificates.certificate_id)
                FROM medical_certificates
            ) AS certificates_issued,
            (
                SELECT COUNT(emergency_alerts.alert_id)
                FROM emergency_alerts
            ) AS emergency_alerts
    """
    return fetch_one(
        connection,
        sql,
        ("student", "professor", "booked", "completed", "cancelled"),
    )


def list_users(
    connection: Any,
    *,
    search_text: str | None,
    role_name: str | None,
    limit: int,
) -> list[dict[str, Any]]:
    pattern = f"%{search_text}%" if search_text else None
    sql = """
        SELECT
            users.user_id,
            users.name,
            users.email,
            roles.role_name,
            users.is_active,
            students.student_id,
            staff.staff_id
        FROM users
        INNER JOIN roles
            ON roles.role_id = users.role_id
        LEFT JOIN students
            ON students.user_id = users.user_id
        LEFT JOIN staff
            ON staff.user_id = users.user_id
        WHERE (%s IS NULL OR roles.role_name = %s)
            AND (
                %s IS NULL
                OR users.name LIKE %s
                OR users.email LIKE %s
            )
        ORDER BY users.name, users.email
        LIMIT %s
    """
    params = [role_name, role_name, pattern, pattern, pattern, limit]
    return fetch_all(connection, sql, tuple(params))


def get_role_id(connection: Any, role_name: str) -> dict[str, Any] | None:
    sql = """
        SELECT roles.role_id
        FROM roles
        WHERE roles.role_name = %s
    """
    return fetch_one(connection, sql, (role_name,))


def get_user_role_context(connection: Any, user_id: int) -> dict[str, Any] | None:
    sql = """
        SELECT
            users.user_id,
            users.name,
            users.email,
            roles.role_name,
            students.student_id,
            staff.staff_id,
            (
                SELECT COUNT(appointments.appointment_id)
                FROM appointments
                WHERE appointments.student_id = students.student_id
            ) AS student_appointment_count,
            (
                SELECT COUNT(appointment_slots.slot_id)
                FROM appointment_slots
                WHERE appointment_slots.staff_id = staff.staff_id
            ) AS staff_slot_count
        FROM users
        INNER JOIN roles
            ON roles.role_id = users.role_id
        LEFT JOIN students
            ON students.user_id = users.user_id
        LEFT JOIN staff
            ON staff.user_id = users.user_id
        WHERE users.user_id = %s
            AND users.is_active = TRUE
    """
    return fetch_one(connection, sql, (user_id,))


def update_user_role(connection: Any, user_id: int, role_id: int) -> None:
    sql = """
        UPDATE users
        SET users.role_id = %s
        WHERE users.user_id = %s
    """
    execute(connection, sql, (role_id, user_id))


def get_student_profile_by_user_id(
    connection: Any,
    user_id: int,
) -> dict[str, Any] | None:
    sql = """
        SELECT students.student_id
        FROM students
        WHERE students.user_id = %s
    """
    return fetch_one(connection, sql, (user_id,))


def insert_student_profile(
    connection: Any,
    *,
    user_id: int,
    roll_number: str,
    department: str,
    year_level: int,
) -> None:
    sql = """
        INSERT INTO students (
            user_id,
            roll_number,
            department,
            year_level
        )
        VALUES (%s, %s, %s, %s)
    """
    execute(connection, sql, (user_id, roll_number, department, year_level))


def upsert_student_profile(
    connection: Any,
    *,
    user_id: int,
    roll_number: str,
    department: str,
    year_level: int,
) -> None:
    sql = """
        UPDATE students
        SET
            students.roll_number = %s,
            students.department = %s,
            students.year_level = %s
        WHERE students.user_id = %s
    """
    execute(connection, sql, (roll_number, department, year_level, user_id))


def get_staff_profile_by_user_id(
    connection: Any,
    user_id: int,
) -> dict[str, Any] | None:
    sql = """
        SELECT staff.staff_id
        FROM staff
        WHERE staff.user_id = %s
    """
    return fetch_one(connection, sql, (user_id,))


def insert_staff_profile(
    connection: Any,
    *,
    user_id: int,
    employee_number: str,
    specialization: str | None,
    is_doctor: bool,
) -> None:
    sql = """
        INSERT INTO staff (
            user_id,
            employee_number,
            specialization,
            is_doctor
        )
        VALUES (%s, %s, %s, %s)
    """
    execute(connection, sql, (user_id, employee_number, specialization, is_doctor))


def upsert_staff_profile(
    connection: Any,
    *,
    user_id: int,
    employee_number: str,
    specialization: str | None,
    is_doctor: bool,
) -> None:
    sql = """
        UPDATE staff
        SET
            staff.employee_number = %s,
            staff.specialization = %s,
            staff.is_doctor = %s
        WHERE staff.user_id = %s
    """
    execute(connection, sql, (employee_number, specialization, is_doctor, user_id))


def delete_student_profile(connection: Any, user_id: int) -> None:
    sql = """
        DELETE FROM students
        WHERE students.user_id = %s
    """
    execute(connection, sql, (user_id,))


def delete_staff_profile(connection: Any, user_id: int) -> None:
    sql = """
        DELETE FROM staff
        WHERE staff.user_id = %s
    """
    execute(connection, sql, (user_id,))


def get_role_assignment_result(connection: Any, user_id: int) -> dict[str, Any] | None:
    sql = """
        SELECT
            users.user_id,
            users.name,
            users.email,
            roles.role_name,
            students.student_id,
            staff.staff_id
        FROM users
        INNER JOIN roles
            ON roles.role_id = users.role_id
        LEFT JOIN students
            ON students.user_id = users.user_id
        LEFT JOIN staff
            ON staff.user_id = users.user_id
        WHERE users.user_id = %s
    """
    return fetch_one(connection, sql, (user_id,))


def list_appointments(
    connection: Any,
    *,
    status: str | None,
    from_date: date | None,
    to_date: date | None,
    doctor_id: int | None,
    student_id: int | None,
    limit: int,
) -> list[dict[str, Any]]:
    sql = """
        SELECT
            appointments.appointment_id,
            appointment_slots.slot_date,
            appointment_slots.start_time,
            appointment_slots.end_time,
            students.student_id,
            student_users.name AS student_name,
            students.roll_number,
            staff.staff_id AS doctor_id,
            doctor_users.name AS doctor_name,
            appointment_statuses.status_name AS status,
            appointments.reason,
            appointments.cancellation_reason
        FROM appointments
        INNER JOIN students
            ON students.student_id = appointments.student_id
        INNER JOIN users AS student_users
            ON student_users.user_id = students.user_id
        INNER JOIN appointment_slots
            ON appointment_slots.slot_id = appointments.slot_id
        INNER JOIN staff
            ON staff.staff_id = appointment_slots.staff_id
        INNER JOIN users AS doctor_users
            ON doctor_users.user_id = staff.user_id
        INNER JOIN appointment_statuses
            ON appointment_statuses.status_id = appointments.status_id
        WHERE (%s IS NULL OR appointment_statuses.status_name = %s)
            AND (%s IS NULL OR appointment_slots.slot_date >= %s)
            AND (%s IS NULL OR appointment_slots.slot_date <= %s)
            AND (%s IS NULL OR staff.staff_id = %s)
            AND (%s IS NULL OR students.student_id = %s)
        ORDER BY
            appointment_slots.slot_date DESC,
            appointment_slots.start_time DESC,
            appointments.appointment_id DESC
        LIMIT %s
    """
    params = [
        status,
        status,
        from_date,
        from_date,
        to_date,
        to_date,
        doctor_id,
        doctor_id,
        student_id,
        student_id,
        limit,
    ]
    return fetch_all(connection, sql, tuple(params))


def list_students(
    connection: Any,
    *,
    search_text: str | None,
    limit: int,
) -> list[dict[str, Any]]:
    pattern = f"%{search_text}%" if search_text else None
    sql = """
        SELECT
            students.student_id,
            users.name AS student_name,
            users.email,
            roles.role_name,
            students.roll_number,
            students.department,
            students.year_level,
            COUNT(appointments.appointment_id) AS total_appointments,
            SUM(
                CASE
                    WHEN appointment_statuses.status_name = 'completed'
                    THEN 1
                    ELSE 0
                END
            ) AS completed_appointments
        FROM students
        INNER JOIN users
            ON users.user_id = students.user_id
        INNER JOIN roles
            ON roles.role_id = users.role_id
        LEFT JOIN appointments
            ON appointments.student_id = students.student_id
        LEFT JOIN appointment_statuses
            ON appointment_statuses.status_id = appointments.status_id
        WHERE roles.role_name IN ('student', 'professor')
            AND (
                %s IS NULL
                OR users.name LIKE %s
                OR users.email LIKE %s
                OR students.roll_number LIKE %s
            )
        GROUP BY
            students.student_id,
            users.name,
            users.email,
            roles.role_name,
            students.roll_number,
            students.department,
            students.year_level
        ORDER BY users.name, students.roll_number
        LIMIT %s
    """
    params = [pattern, pattern, pattern, pattern, limit]
    return fetch_all(connection, sql, tuple(params))


def list_doctors(
    connection: Any,
    *,
    search_text: str | None,
    limit: int,
) -> list[dict[str, Any]]:
    pattern = f"%{search_text}%" if search_text else None
    sql = """
        SELECT
            staff.staff_id AS doctor_id,
            users.name AS doctor_name,
            users.email,
            staff.employee_number,
            staff.specialization,
            CASE
                WHEN doctor_availability_overrides.override_id IS NOT NULL
                THEN doctor_availability_overrides.is_available
                ELSE COALESCE(
                    doctor_weekly_availability.is_available,
                    WEEKDAY(CURRENT_DATE) < 6
                )
            END AS is_available_today,
            COUNT(
                CASE
                    WHEN appointment_slots.slot_date = CURRENT_DATE
                    THEN appointments.appointment_id
                    ELSE NULL
                END
            ) AS appointments_today,
            COUNT(
                CASE
                    WHEN appointment_slots.slot_date >= CURRENT_DATE
                        AND appointment_statuses.status_name = 'booked'
                    THEN appointments.appointment_id
                    ELSE NULL
                END
            ) AS upcoming_appointments
        FROM staff
        INNER JOIN users
            ON users.user_id = staff.user_id
        LEFT JOIN doctor_weekly_availability
            ON doctor_weekly_availability.staff_id = staff.staff_id
            AND doctor_weekly_availability.weekday = WEEKDAY(CURRENT_DATE)
        LEFT JOIN doctor_availability_overrides
            ON doctor_availability_overrides.staff_id = staff.staff_id
            AND doctor_availability_overrides.override_date = CURRENT_DATE
        LEFT JOIN appointment_slots
            ON appointment_slots.staff_id = staff.staff_id
        LEFT JOIN appointments
            ON appointments.slot_id = appointment_slots.slot_id
        LEFT JOIN appointment_statuses
            ON appointment_statuses.status_id = appointments.status_id
        WHERE staff.is_doctor = TRUE
            AND (
                %s IS NULL
                OR users.name LIKE %s
                OR users.email LIKE %s
                OR staff.employee_number LIKE %s
                OR staff.specialization LIKE %s
            )
        GROUP BY
            staff.staff_id,
            users.name,
            users.email,
            staff.employee_number,
            staff.specialization,
            doctor_availability_overrides.override_id,
            doctor_availability_overrides.is_available,
            doctor_weekly_availability.is_available
        ORDER BY users.name, staff.employee_number
        LIMIT %s
    """
    params = [pattern, pattern, pattern, pattern, pattern, limit]
    return fetch_all(connection, sql, tuple(params))


def list_staff(
    connection: Any,
    *,
    search_text: str | None,
    limit: int,
) -> list[dict[str, Any]]:
    pattern = f"%{search_text}%" if search_text else None
    sql = """
        SELECT
            staff.staff_id,
            users.name AS staff_name,
            users.email,
            staff.employee_number,
            staff.specialization,
            staff.is_doctor
        FROM staff
        INNER JOIN users
            ON users.user_id = staff.user_id
        WHERE staff.is_doctor = FALSE
            AND (
                %s IS NULL
                OR users.name LIKE %s
                OR users.email LIKE %s
                OR staff.employee_number LIKE %s
            )
        ORDER BY users.name, staff.employee_number
        LIMIT %s
    """
    params = [pattern, pattern, pattern, pattern, limit]
    return fetch_all(connection, sql, tuple(params))


def list_emergency_alerts(
    connection: Any,
    *,
    limit: int,
) -> list[dict[str, Any]]:
    sql = """
        SELECT
            emergency_alerts.alert_id,
            emergency_alerts.student_id,
            users.name AS student_name,
            students.roll_number,
            emergency_alerts.message,
            emergency_alerts.created_at
        FROM emergency_alerts
        INNER JOIN students
            ON students.student_id = emergency_alerts.student_id
        INNER JOIN users
            ON users.user_id = students.user_id
        ORDER BY emergency_alerts.created_at DESC, emergency_alerts.alert_id DESC
        LIMIT %s
    """
    params = [limit]
    return fetch_all(connection, sql, tuple(params))
