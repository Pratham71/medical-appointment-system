from typing import Any

from app.backend.app.db.queries._helpers import execute, fetch_one


def insert_alert(
    connection: Any,
    *,
    student_id: int,
    reason: str,
    location: str,
    contact_number: str | None,
    message: str,
) -> int:
    """Insert a new emergency alert and return the generated alert ID.

    Args:
        student_id: Foreign-key ID of the student raising the alert.
        reason: Category or short description of the emergency.
        location: Current location of the student.
        contact_number: Optional phone number for follow-up contact.
        message: Detailed description of the emergency situation.

    Returns:
        The auto-generated alert_id of the new row.
    """
    sql = """
        INSERT INTO emergency_alerts (
            student_id,
            reason,
            location,
            contact_number,
            message
        )
        VALUES (%s, %s, %s, %s, %s)
    """
    return execute(connection, sql, (student_id, reason, location, contact_number, message))


def get_alert(connection: Any, alert_id: int) -> dict[str, Any] | None:
    """Fetch an emergency alert with basic student info and computed status.

    Args:
        alert_id: Primary key of the emergency alert.

    Returns:
        A dict with alert_id, student_id, student_name, roll_number, reason,
        location, contact_number, message, status, and created_at,
        or None if not found.
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
            emergency_alerts.created_at
        FROM emergency_alerts
        INNER JOIN students
            ON students.student_id = emergency_alerts.student_id
        INNER JOIN users
            ON users.user_id = students.user_id
        WHERE emergency_alerts.alert_id = %s
    """
    return fetch_one(connection, sql, (alert_id,))
