from collections.abc import Generator
from contextlib import contextmanager
from typing import Any

from app.backend.app.api.errors import DatabaseNotConfiguredError


def _database_deferred() -> None:
    raise DatabaseNotConfiguredError(
        "Database access is deferred until MySQL/PostgreSQL is selected"
    )


@contextmanager
def connection_scope() -> Generator[Any]:
    _database_deferred()
    yield


@contextmanager
def transaction_scope() -> Generator[Any]:
    _database_deferred()
    yield
