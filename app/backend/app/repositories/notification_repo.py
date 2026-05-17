from typing import Any

from app.backend.app.db import session
from app.backend.app.db.queries import notification_queries


def get_appointment_notification_context(
    appointment_id: int,
) -> dict[str, Any] | None:
    with session.connection_scope() as connection:
        return notification_queries.get_appointment_notification_context(
            connection,
            appointment_id,
        )
