from typing import NoReturn

from app.backend.app.api.errors import DatabaseNotConfiguredError


def database_deferred() -> NoReturn:
    raise DatabaseNotConfiguredError(
        "Database access is deferred until MySQL/PostgreSQL is selected"
    )
