from typing import Any

from app.backend.app.db.queries._helpers import execute, fetch_one


def get_user_by_email(connection: Any, email: str) -> dict[str, Any] | None:
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
    sql = """
        SELECT students.student_id
        FROM students
        WHERE students.user_id = %s
    """
    return fetch_one(connection, sql, (user_id,))


def get_staff_id_by_user_id(connection: Any, user_id: int) -> dict[str, Any] | None:
    sql = """
        SELECT staff.staff_id
        FROM staff
        WHERE staff.user_id = %s
            AND staff.is_doctor = TRUE
    """
    return fetch_one(connection, sql, (user_id,))
