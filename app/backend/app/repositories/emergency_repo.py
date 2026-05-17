from typing import Any

from app.backend.app.db import session
from app.backend.app.db.queries import emergency_queries


def create_alert(
    *,
    student_id: int,
    reason: str,
    location: str,
    contact_number: str | None,
    message: str,
) -> dict[str, Any] | None:
    """Create a new emergency alert and return its data.

    Args:
        student_id: Primary key of the student raising the alert.
        reason: Category or short description of the emergency.
        location: Current location of the student.
        contact_number: Optional phone number for follow-up.
        message: Detailed description of the situation.

    Returns:
        The newly created alert dict, or None if retrieval fails.
    """
    with session.transaction_scope() as connection:
        alert_id = emergency_queries.insert_alert(
            connection,
            student_id=student_id,
            reason=reason,
            location=location,
            contact_number=contact_number,
            message=message,
        )
        return emergency_queries.get_alert(connection, alert_id)
