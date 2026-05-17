from datetime import time, timedelta
from typing import Any


QueryParams = tuple[Any, ...] | list[Any]


def fetch_one(
    connection: Any,
    sql: str,
    params: QueryParams = (),
) -> dict[str, Any] | None:
    """Execute a SELECT and return the first row as a normalised dict, or None."""
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(sql, params)
        row = cursor.fetchone()
        return _normalize_row(row) if row else None
    finally:
        cursor.close()


def fetch_all(
    connection: Any,
    sql: str,
    params: QueryParams = (),
) -> list[dict[str, Any]]:
    """Execute a SELECT and return all rows as a list of normalised dicts."""
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(sql, params)
        return [_normalize_row(row) for row in cursor.fetchall()]
    finally:
        cursor.close()


def _normalize_row(row: dict[str, Any]) -> dict[str, Any]:
    """Apply value normalisation to every field in a database row dict."""
    return {key: _normalize_value(value) for key, value in row.items()}


def _normalize_value(value: Any) -> Any:
    """Convert MySQL TIME-as-timedelta values to Python time objects; pass other values through."""
    if isinstance(value, timedelta): 
        total_seconds = int(value.total_seconds())
        if 0 <= total_seconds < 24 * 60 * 60:
            hours, remainder = divmod(total_seconds, 60 * 60)
            minutes, seconds = divmod(remainder, 60)
            return time(hours, minutes, seconds, value.microseconds)
    return value


def execute(
    connection: Any,
    sql: str,
    params: QueryParams = (),
) -> int:
    """Execute an INSERT/UPDATE/DELETE and return the last inserted row ID (0 if none)."""
    cursor = connection.cursor()
    try:
        cursor.execute(sql, params)
        return int(cursor.lastrowid or 0)
    finally:
        cursor.close()
