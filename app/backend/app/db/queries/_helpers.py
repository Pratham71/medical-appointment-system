from datetime import time, timedelta
from typing import Any


QueryParams = tuple[Any, ...] | list[Any]


def fetch_one(
    connection: Any,
    sql: str,
    params: QueryParams = (),
) -> dict[str, Any] | None:
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
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(sql, params)
        return [_normalize_row(row) for row in cursor.fetchall()]
    finally:
        cursor.close()


def _normalize_row(row: dict[str, Any]) -> dict[str, Any]:
    return {key: _normalize_value(value) for key, value in row.items()}


def _normalize_value(value: Any) -> Any:
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
    cursor = connection.cursor()
    try:
        cursor.execute(sql, params)
        return int(cursor.lastrowid or 0)
    finally:
        cursor.close()
