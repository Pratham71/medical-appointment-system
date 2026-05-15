from typing import Any

from app.backend.app.db.queries._helpers import fetch_one


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
