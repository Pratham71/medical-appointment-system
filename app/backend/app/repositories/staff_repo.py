from datetime import date
from typing import Any

from app.backend.app.db import session
from app.backend.app.db.queries import staff_queries


def get_dashboard_counts() -> dict[str, Any] | None:
    with session.connection_scope() as connection:
        return staff_queries.get_dashboard_counts(connection)


def list_appointments(
    *,
    status: str | None,
    from_date: date | None,
    to_date: date | None,
    limit: int,
) -> list[dict[str, Any]]:
    with session.connection_scope() as connection:
        return staff_queries.list_appointments(
            connection,
            status=status,
            from_date=from_date,
            to_date=to_date,
            limit=limit,
        )
