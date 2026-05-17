from datetime import date
from typing import Any

from app.backend.app.db.queries._helpers import execute, fetch_all, fetch_one


def get_dashboard_counts(connection: Any) -> dict[str, Any] | None:
    """Fetch system-wide aggregate statistics for the admin dashboard.

    Returns:
        A dict with total_students, total_professors, total_doctors, total_staff,
        appointments_today, booked_appointments, completed_appointments,
        cancelled_appointments, reports_available, certificates_issued,
        and emergency_alerts, or None if no rows are returned.
    """
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
    """Return a filtered, paginated list of users for admin user management.

    Args:
        search_text: Optional partial name or email to match (LIKE pattern).
        role_name: Optional role to filter by.
        limit: Maximum number of rows to return.

    Returns:
        List of dicts with user_id, name, email, role_name, is_active,
        student_id, and staff_id, ordered by name and email.
    """
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
    """Look up the numeric role ID for the given role name.

    Args:
        role_name: The textual role name (e.g. "admin", "doctor").

    Returns:
        A dict with role_id, or None if the role does not exist.
    """
    sql = """
        SELECT roles.role_id
        FROM roles
        WHERE roles.role_name = %s
    """
    return fetch_one(connection, sql, (role_name,))


def get_user_role_context(connection: Any, user_id: int) -> dict[str, Any] | None:
    """Fetch a user's current role, linked profile IDs, and activity counters needed for role reassignment.

    Args:
        user_id: Primary key of the user account.

    Returns:
        A dict with user_id, name, email, role_name, student_id, staff_id,
        student_appointment_count, and staff_slot_count, or None if not found.
    """
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
    """Update the role assigned to a user account.

    Args:
        user_id: Primary key of the user account to update.
        role_id: Foreign-key ID of the new role.
    """
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
    """Fetch the student profile linked to a user account.

    Args:
        user_id: Primary key of the user account.

    Returns:
        A dict with student_id, or None if no student profile exists.
    """
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
    """Create a new student profile row for an existing user account.

    Args:
        user_id: Foreign-key ID of the user account.
        roll_number: Unique institutional roll/enrollment number.
        department: Academic department of the student.
        year_level: Current year of study (1-based).
    """
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
    """Update the student profile fields for an existing student user.

    Args:
        user_id: Foreign-key ID of the user account.
        roll_number: New roll/enrollment number.
        department: Updated academic department.
        year_level: Updated year of study (1-based).
    """
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
    """Fetch the staff profile linked to a user account.

    Args:
        user_id: Primary key of the user account.

    Returns:
        A dict with staff_id, or None if no staff profile exists.
    """
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
    """Create a new staff profile row for an existing user account.

    Args:
        user_id: Foreign-key ID of the user account.
        employee_number: Unique institutional employee number.
        specialization: Medical specialization, or None for non-doctor staff.
        is_doctor: True if the staff member is a doctor, False otherwise.
    """
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
    """Update the staff profile fields for an existing staff user.

    Args:
        user_id: Foreign-key ID of the user account.
        employee_number: New employee number.
        specialization: Updated medical specialization, or None to clear.
        is_doctor: Whether the staff member should be flagged as a doctor.
    """
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
    """Remove the student profile row linked to a user account.

    Args:
        user_id: Foreign-key ID of the user account whose student profile to delete.
    """
    sql = """
        DELETE FROM students
        WHERE students.user_id = %s
    """
    execute(connection, sql, (user_id,))


def delete_staff_profile(connection: Any, user_id: int) -> None:
    """Remove the staff profile row linked to a user account.

    Args:
        user_id: Foreign-key ID of the user account whose staff profile to delete.
    """
    sql = """
        DELETE FROM staff
        WHERE staff.user_id = %s
    """
    execute(connection, sql, (user_id,))


def get_role_assignment_result(connection: Any, user_id: int) -> dict[str, Any] | None:
    """Fetch the post-assignment snapshot of a user for the role-assignment response.

    Args:
        user_id: Primary key of the user account.

    Returns:
        A dict with user_id, name, email, role_name, student_id, and staff_id,
        or None if the user does not exist.
    """
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


def get_user_status_context(connection: Any, user_id: int) -> dict[str, Any] | None:
    """Fetch the current active/inactive status for a user account.

    Args:
        user_id: Primary key of the user account.

    Returns:
        A dict with user_id and is_active, or None if not found.
    """
    sql = """
        SELECT
            users.user_id,
            users.is_active
        FROM users
        WHERE users.user_id = %s
    """
    return fetch_one(connection, sql, (user_id,))


def update_user_active_status(
    connection: Any,
    *,
    user_id: int,
    is_active: bool,
) -> None:
    """Set the is_active flag on a user account to activate or deactivate it.

    Args:
        user_id: Primary key of the user account to update.
        is_active: True to activate the account, False to deactivate.
    """
    sql = """
        UPDATE users
        SET users.is_active = %s
        WHERE users.user_id = %s
    """
    execute(connection, sql, (is_active, user_id))


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
    """Return a filtered, paginated list of appointments for admin review.

    Args:
        status: Optional appointment status to filter by.
        from_date: Optional start of the date range (inclusive).
        to_date: Optional end of the date range (inclusive).
        doctor_id: Optional staff_id to restrict results to a single doctor.
        student_id: Optional student_id to restrict results to a single student.
        limit: Maximum number of rows to return.

    Returns:
        List of appointment summary dicts ordered by slot_date and time descending.
    """
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
    """Return a filtered, paginated list of student/patient users for admin review.

    Args:
        search_text: Optional partial name, email, or roll number to match.
        limit: Maximum number of rows to return.

    Returns:
        List of dicts with student_id, student_name, email, role_name,
        roll_number, department, year_level, total_appointments,
        and completed_appointments.
    """
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
        WHERE roles.role_name IN (
            'student',
            'professor',
            'college-staff',
            'hostel-staff'
        )
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
    """Return a filtered, paginated list of doctors for admin review.

    Args:
        search_text: Optional partial name, email, employee number, or specialization to match.
        limit: Maximum number of rows to return.

    Returns:
        List of dicts with doctor_id, doctor_name, email, employee_number,
        specialization, is_available_today, appointments_today,
        and upcoming_appointments.
    """
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
    """Return a filtered, paginated list of non-doctor staff for admin review.

    Args:
        search_text: Optional partial name, email, or employee number to match.
        limit: Maximum number of rows to return.

    Returns:
        List of dicts with staff_id, staff_name, email, employee_number,
        specialization, and is_doctor.
    """
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
    """Return the most recent emergency alerts across all students.

    Args:
        limit: Maximum number of rows to return.

    Returns:
        List of dicts with alert_id, student info, reason, location,
        contact_number, message, status, timestamps, and resolution details.
    """
    sql = """
        SELECT
            emergency_alerts.alert_id,
            emergency_alerts.student_id,
            users.name AS student_name,
            students.roll_number,
            emergency_alerts.reason,
            emergency_alerts.location,
            emergency_alerts.contact_number,
            emergency_alerts.message,
            CASE
                WHEN emergency_alerts.resolved_at IS NOT NULL THEN 'resolved'
                WHEN emergency_alerts.acknowledged_at IS NOT NULL THEN 'acknowledged'
                ELSE 'unread'
            END AS status,
            emergency_alerts.created_at,
            emergency_alerts.acknowledged_by,
            emergency_alerts.acknowledged_at,
            emergency_alerts.resolved_by,
            emergency_alerts.resolved_at,
            emergency_alerts.resolution_note
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


def get_emergency_alert_for_update(
    connection: Any,
    alert_id: int,
) -> dict[str, Any] | None:
    """Lock an emergency alert row for the duration of an acknowledge/resolve transaction.

    Args:
        alert_id: Primary key of the emergency alert.

    Returns:
        A dict with alert_id, acknowledged_at, and resolved_at,
        or None if the alert does not exist.
    """
    sql = """
        SELECT
            emergency_alerts.alert_id,
            emergency_alerts.acknowledged_at,
            emergency_alerts.resolved_at
        FROM emergency_alerts
        WHERE emergency_alerts.alert_id = %s
        FOR UPDATE
    """
    return fetch_one(connection, sql, (alert_id,))


def acknowledge_emergency_alert(
    connection: Any,
    *,
    alert_id: int,
    actor_user_id: int,
) -> None:
    """Mark an emergency alert as acknowledged by a staff or admin user.

    Args:
        alert_id: Primary key of the emergency alert.
        actor_user_id: user_id of the staff/admin performing the acknowledgement.
    """
    sql = """
        UPDATE emergency_alerts
        SET
            emergency_alerts.acknowledged_by = COALESCE(
                emergency_alerts.acknowledged_by,
                %s
            ),
            emergency_alerts.acknowledged_at = COALESCE(
                emergency_alerts.acknowledged_at,
                CURRENT_TIMESTAMP
            )
        WHERE emergency_alerts.alert_id = %s
    """
    execute(connection, sql, (actor_user_id, alert_id))


def resolve_emergency_alert(
    connection: Any,
    *,
    alert_id: int,
    actor_user_id: int,
    resolution_note: str | None,
) -> None:
    """Mark an emergency alert as resolved, also setting acknowledgement if not already set.

    Args:
        alert_id: Primary key of the emergency alert.
        actor_user_id: user_id of the staff/admin performing the resolution.
        resolution_note: Optional human-readable note describing the resolution.
    """
    sql = """
        UPDATE emergency_alerts
        SET
            emergency_alerts.acknowledged_by = COALESCE(
                emergency_alerts.acknowledged_by,
                %s
            ),
            emergency_alerts.acknowledged_at = COALESCE(
                emergency_alerts.acknowledged_at,
                CURRENT_TIMESTAMP
            ),
            emergency_alerts.resolved_by = %s,
            emergency_alerts.resolved_at = COALESCE(
                emergency_alerts.resolved_at,
                CURRENT_TIMESTAMP
            ),
            emergency_alerts.resolution_note = %s
        WHERE emergency_alerts.alert_id = %s
    """
    execute(
        connection,
        sql,
        (actor_user_id, actor_user_id, resolution_note, alert_id),
    )


def get_emergency_alert_summary(
    connection: Any,
    alert_id: int,
) -> dict[str, Any] | None:
    """Fetch the full alert summary with student info after an acknowledge/resolve action.

    Args:
        alert_id: Primary key of the emergency alert.

    Returns:
        A dict with alert_id, student info, reason, location, contact_number,
        message, status, timestamps, and resolution details, or None if not found.
    """
    sql = """
        SELECT
            emergency_alerts.alert_id,
            emergency_alerts.student_id,
            users.name AS student_name,
            students.roll_number,
            emergency_alerts.reason,
            emergency_alerts.location,
            emergency_alerts.contact_number,
            emergency_alerts.message,
            CASE
                WHEN emergency_alerts.resolved_at IS NOT NULL THEN 'resolved'
                WHEN emergency_alerts.acknowledged_at IS NOT NULL THEN 'acknowledged'
                ELSE 'unread'
            END AS status,
            emergency_alerts.created_at,
            emergency_alerts.acknowledged_by,
            emergency_alerts.acknowledged_at,
            emergency_alerts.resolved_by,
            emergency_alerts.resolved_at,
            emergency_alerts.resolution_note
        FROM emergency_alerts
        INNER JOIN students
            ON students.student_id = emergency_alerts.student_id
        INNER JOIN users
            ON users.user_id = students.user_id
        WHERE emergency_alerts.alert_id = %s
    """
    return fetch_one(connection, sql, (alert_id,))
