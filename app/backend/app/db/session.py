from collections.abc import Generator
from contextlib import contextmanager
from typing import Any

from mysql.connector.pooling import MySQLConnectionPool

from app.backend.app.api.errors import DatabaseNotConfiguredError
from app.backend.app.core.config import get_settings


_connection_pool: MySQLConnectionPool | None = None


def reset_connection_pool() -> None:
    global _connection_pool
    _connection_pool = None


def get_connection_pool() -> MySQLConnectionPool:
    global _connection_pool

    if _connection_pool is None:
        settings = get_settings()
        if settings.database_provider.lower() != "mysql":
            raise DatabaseNotConfiguredError("Only MySQL is configured for this project")

        _connection_pool = MySQLConnectionPool(
            pool_name=settings.mysql_pool_name,
            pool_size=settings.mysql_pool_size,
            host=settings.mysql_host,
            port=settings.mysql_port,
            user=settings.mysql_user,
            password=settings.mysql_password,
            database=settings.mysql_database,
            autocommit=False,
        )

    return _connection_pool


@contextmanager
def connection_scope() -> Generator[Any]:
    connection = get_connection_pool().get_connection()
    try:
        yield connection
    finally:
        connection.close()


@contextmanager
def transaction_scope() -> Generator[Any]:
    connection = get_connection_pool().get_connection()
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()