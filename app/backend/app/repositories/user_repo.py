from typing import Any

from app.backend.app.repositories._deferred import database_deferred


def get_user_by_email(email: str) -> dict[str, Any] | None:
    database_deferred()


def get_user_by_id(user_id: int) -> dict[str, Any] | None:
    database_deferred()
