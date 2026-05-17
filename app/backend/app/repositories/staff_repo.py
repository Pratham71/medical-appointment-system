from datetime import date
from typing import Any

from app.backend.app.db import session
from app.backend.app.db.queries import staff_queries


def get_dashboard_counts() -> dict[str, Any] | None:
    """Fetch system-wide appointment statistics for the staff dashboard.

    Returns:
        A dict with appointments_today, booked_appointments, cancelled_today,
        and emergency_alerts, or None if no rows are returned.
    """
    with session.connection_scope() as connection:
        return staff_queries.get_dashboard_counts(connection)


def list_appointments(
    *,
    status: str | None,
    from_date: date | None,
    to_date: date | None,
    limit: int,
) -> list[dict[str, Any]]:
    """Return a filtered, paginated list of appointments for staff review.

    Args:
        status: Optional appointment status to filter by.
        from_date: Optional start of the date range (inclusive).
        to_date: Optional end of the date range (inclusive).
        limit: Maximum number of rows to return.

    Returns:
        List of appointment summary dicts ordered by slot_date descending.
    """
    with session.connection_scope() as connection:
        return staff_queries.list_appointments(
            connection,
            status=status,
            from_date=from_date,
            to_date=to_date,
            limit=limit,
        )
