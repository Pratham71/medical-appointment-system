from typing import Any

from app.backend.app.db import session
from app.backend.app.db.queries import notification_queries


def get_appointment_notification_context(
    appointment_id: int,
) -> dict[str, Any] | None:
    """Fetch the data needed to compose an appointment email notification.

    Args:
        appointment_id: Primary key of the appointment.

    Returns:
        A dict with student and doctor contact info, slot details, and reason,
        or None if the appointment does not exist.
    """
    with session.connection_scope() as connection:
        return notification_queries.get_appointment_notification_context(
            connection,
            appointment_id,
        )
