from typing import Any

from app.backend.app.db import session
from app.backend.app.db.queries import emergency_queries


def create_alert(student_id: int, message: str) -> dict[str, Any] | None:
    with session.transaction_scope() as connection:
        alert_id = emergency_queries.insert_alert(
            connection,
            student_id=student_id,
            message=message,
        )
        return emergency_queries.get_alert(connection, alert_id)
