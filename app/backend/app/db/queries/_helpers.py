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
        return cursor.fetchone()
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
        return cursor.fetchall()
    finally:
        cursor.close()


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
