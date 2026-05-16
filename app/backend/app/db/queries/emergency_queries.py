from typing import Any

from app.backend.app.db.queries._helpers import execute, fetch_one


def insert_alert(
    connection: Any,
    student_id: int,
    message: str,
) -> int:
    sql = """
        INSERT INTO emergency_alerts (
            student_id,
            message
        )
        VALUES (%s, %s)
    """
    return execute(connection, sql, (student_id, message))


def get_alert(connection: Any, alert_id: int) -> dict[str, Any] | None:
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
        WHERE emergency_alerts.alert_id = %s
    """
    return fetch_one(connection, sql, (alert_id,))
