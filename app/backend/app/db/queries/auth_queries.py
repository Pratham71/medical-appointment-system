from typing import Any

from app.backend.app.db.queries._helpers import execute, fetch_one


def get_user_by_email(connection: Any, email: str) -> dict[str, Any] | None:
    """Fetch an active user record along with their role by email address.

    Args:
        email: Email address to look up.

    Returns:
        A dict with user_id, name, email, password_hash, role_name, or None if not found.
    """
    sql = """
        SELECT
            users.user_id,
            users.name,
            users.email,
            users.password_hash,
            roles.role_name
        FROM users
        INNER JOIN roles ON roles.role_id = users.role_id
        WHERE users.email = %s
            AND users.is_active = TRUE
    """
    return fetch_one(connection, sql, (email,))


def get_role_id_by_name(connection: Any, role_name: str) -> dict[str, Any] | None:
    """Look up the numeric role ID for the given role name.

    Args:
        role_name: The textual role name (e.g. "student", "doctor").

    Returns:
        A dict with role_id, or None if the role does not exist.
    """
    sql = """
        SELECT roles.role_id
        FROM roles
        WHERE roles.role_name = %s
    """
    return fetch_one(connection, sql, (role_name,))


def insert_user(
    connection: Any,
    *,
    role_id: int,
    name: str,
    email: str,
    password_hash: str,
) -> int:
    """Insert a new user row and return the generated user ID.

    Args:
        role_id: Foreign-key ID of the role to assign.
        name: Display name of the new user.
        email: Unique email address.
        password_hash: Bcrypt-hashed password string.

    Returns:
        The auto-generated user_id of the newly inserted row.
    """
    sql = """
        INSERT INTO users (
            role_id,
            name,
            email,
            password_hash
        )
        VALUES (%s, %s, %s, %s)
    """
    return execute(connection, sql, (role_id, name, email, password_hash))


def insert_student_profile(
    connection: Any,
    *,
    user_id: int,
    roll_number: str,
    department: str,
    year_level: int,
) -> int:
    """Create the student profile row linked to an existing user account.

    Args:
        user_id: Foreign-key ID of the user account.
        roll_number: Unique institutional roll/enrollment number.
        department: Academic department of the student.
        year_level: Current year of study (1-based).

    Returns:
        The auto-generated student_id of the new row.
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
    return execute(connection, sql, (user_id, roll_number, department, year_level))


def get_user_by_id(connection: Any, user_id: int) -> dict[str, Any] | None:
    """Fetch an active user record along with their role by user ID.

    Args:
        user_id: Primary key of the user to retrieve.

    Returns:
        A dict with user_id, name, email, role_name, or None if not found.
    """
    sql = """
        SELECT
            users.user_id,
            users.name,
            users.email,
            roles.role_name
        FROM users
        INNER JOIN roles ON roles.role_id = users.role_id
        WHERE users.user_id = %s
            AND users.is_active = TRUE
    """
    return fetch_one(connection, sql, (user_id,))


def get_student_id_by_user_id(connection: Any, user_id: int) -> dict[str, Any] | None:
    """Retrieve the student_id that belongs to the given user account.

    Args:
        user_id: Primary key of the user account.

    Returns:
        A dict with student_id, or None if the user has no student profile.
    """
    sql = """
        SELECT students.student_id
        FROM students
        WHERE students.user_id = %s
    """
    return fetch_one(connection, sql, (user_id,))


def get_staff_id_by_user_id(connection: Any, user_id: int) -> dict[str, Any] | None:
    """Retrieve the staff_id of the doctor profile linked to the given user account.

    Args:
        user_id: Primary key of the user account.

    Returns:
        A dict with staff_id, or None if the user has no doctor staff profile.
    """
    sql = """
        SELECT staff.staff_id
        FROM staff
        WHERE staff.user_id = %s
            AND staff.is_doctor = TRUE
    """
    return fetch_one(connection, sql, (user_id,))
