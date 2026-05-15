from typing import Any

from app.backend.app.db import session
from app.backend.app.db.queries import auth_queries


def get_user_by_email(email: str) -> dict[str, Any] | None:
    with session.connection_scope() as connection:
        return auth_queries.get_user_by_email(connection, email)


def get_user_by_id(user_id: int) -> dict[str, Any] | None:
    with session.connection_scope() as connection:
        return auth_queries.get_user_by_id(connection, user_id)


def get_student_id_by_user_id(user_id: int) -> int | None:
    with session.connection_scope() as connection:
        row = auth_queries.get_student_id_by_user_id(connection, user_id)
    return int(row["student_id"]) if row else None


def get_staff_id_by_user_id(user_id: int) -> int | None:
    with session.connection_scope() as connection:
        row = auth_queries.get_staff_id_by_user_id(connection, user_id)
    return int(row["staff_id"]) if row else None
