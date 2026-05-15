from contextlib import contextmanager
from datetime import time, timedelta
from pathlib import Path

import pytest

from app.backend.app.core.config import Settings
from app.backend.app.db import session
from app.backend.app.db.queries._helpers import fetch_all
from app.backend.app.repositories import appointment_repo


ROOT = Path(__file__).resolve().parents[1]
DB_DIR = ROOT / "app" / "backend" / "app" / "db"
QUERY_DIR = DB_DIR / "queries"


class FakeConnection:
    def __init__(self) -> None:
        self.committed = False
        self.rolled_back = False
        self.closed = False

    def commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        self.rolled_back = True

    def close(self) -> None:
        self.closed = True


class FakePool:
    created_with = None

    def __init__(self, **kwargs) -> None:
        FakePool.created_with = kwargs
        self.connection = FakeConnection()

    def get_connection(self) -> FakeConnection:
        return self.connection


class FakeCursor:
    def __init__(self) -> None:
        self.executed = None
        self.closed = False

    def execute(self, sql, params) -> None:
        self.executed = (sql, params)

    def fetchall(self):
        return [
            {
                "start_time": timedelta(hours=9, minutes=30),
                "end_time": timedelta(hours=10),
            }
        ]

    def close(self) -> None:
        self.closed = True


class FakeDictionaryConnection:
    def __init__(self) -> None:
        self.cursor_instance = FakeCursor()

    def cursor(self, dictionary=False):
        assert dictionary is True
        return self.cursor_instance


class FakeSettings:
    database_provider = "mysql"
    mysql_pool_name = "medical_appointment_pool"
    mysql_pool_size = 5
    mysql_host = "127.0.0.1"
    mysql_port = 3306
    mysql_user = "root"
    mysql_password = ""
    mysql_database = "medical_appointment_system"


@pytest.fixture(autouse=True)
def reset_db_pool():
    session.reset_connection_pool()
    FakePool.created_with = None
    yield
    session.reset_connection_pool()


def test_settings_default_to_mysql_provider():
    settings = Settings()

    assert settings.database_provider == "mysql"
    assert settings.mysql_host == "127.0.0.1"
    assert settings.mysql_port == 3306
    assert settings.mysql_database == "medical_appointment_system"
    assert settings.mysql_pool_size >= 1


def test_connection_pool_uses_mysql_settings(monkeypatch):
    monkeypatch.setattr(session, "MySQLConnectionPool", FakePool)
    monkeypatch.setattr(session, "get_settings", lambda: FakeSettings())

    pool = session.get_connection_pool()

    assert isinstance(pool, FakePool)
    assert FakePool.created_with == {
        "pool_name": "medical_appointment_pool",
        "pool_size": 5,
        "host": "127.0.0.1",
        "port": 3306,
        "user": "root",
        "password": "",
        "database": "medical_appointment_system",
        "autocommit": False,
    }


def test_transaction_scope_commits_and_closes(monkeypatch):
    monkeypatch.setattr(session, "MySQLConnectionPool", FakePool)

    with session.transaction_scope() as connection:
        assert isinstance(connection, FakeConnection)

    assert connection.committed is True
    assert connection.rolled_back is False
    assert connection.closed is True


def test_transaction_scope_rolls_back_and_closes(monkeypatch):
    monkeypatch.setattr(session, "MySQLConnectionPool", FakePool)

    with pytest.raises(RuntimeError, match="boom"):
        with session.transaction_scope() as connection:
            raise RuntimeError("boom")

    assert connection.committed is False
    assert connection.rolled_back is True
    assert connection.closed is True


def test_schema_defines_mysql_tables_constraints_and_indexes():
    schema = (DB_DIR / "schema.sql").read_text(encoding="utf-8").lower()

    expected_tables = [
        "roles",
        "users",
        "students",
        "staff",
        "appointment_statuses",
        "slot_statuses",
        "appointment_slots",
        "appointments",
        "medical_notes",
        "prescriptions",
        "prescription_items",
        "certificate_types",
        "medical_certificates",
    ]

    for table_name in expected_tables:
        assert f"create table {table_name}" in schema

    assert "engine=innodb" in schema
    assert "unique (slot_id)" in schema
    assert "foreign key" in schema
    assert "idx_appointments_student" in schema
    assert "idx_appointment_slots_staff_date" in schema
    assert "idx_appointment_slots_date_status" in schema


def test_schema_defines_reporting_views():
    schema = (DB_DIR / "schema.sql").read_text(encoding="utf-8").lower()

    expected_views = [
        "v_available_appointment_slots",
        "v_appointment_details",
        "v_doctor_appointment_summaries",
        "v_student_report_summaries",
        "v_student_certificate_summaries",
    ]

    for view_name in expected_views:
        assert f"create view {view_name}" in schema

    assert "drop view if exists v_appointment_details" in schema
    assert "select *" not in schema


def test_seed_inserts_mvp_lookup_and_sample_data():
    seed = (DB_DIR / "seed.sql").read_text(encoding="utf-8").lower()

    assert "insert into roles" in seed
    assert "insert into appointment_statuses" in seed
    assert "insert into slot_statuses" in seed
    assert "insert into certificate_types" in seed
    assert "insert into users" in seed
    assert "insert into students" in seed
    assert "insert into staff" in seed
    assert "'staff'" in seed
    assert "staff@college.edu" in seed
    assert "false" in seed
    assert "insert into appointment_slots" in seed


def test_query_files_keep_sql_parameterized_and_explicit():
    query_files = [
        path
        for path in QUERY_DIR.glob("*_queries.py")
        if path.name != "__init__.py"
    ]

    assert query_files

    for path in query_files:
        source = path.read_text(encoding="utf-8")
        lowered = source.lower()

        assert "select *" not in lowered
        if "select " in lowered or "insert " in lowered or "update " in lowered:
            assert "%s" in source


def test_query_helpers_convert_mysql_time_deltas_to_time_values():
    connection = FakeDictionaryConnection()

    rows = fetch_all(connection, "SELECT start_time, end_time FROM appointment_slots")

    assert rows == [
        {
            "start_time": time(9, 30),
            "end_time": time(10, 0),
        }
    ]


def test_cancel_status_does_not_mark_unique_slot_available(monkeypatch):
    slot_updates = []

    class FakeAppointmentQueries:
        @staticmethod
        def get_appointment_for_update(connection, appointment_id):
            return {"appointment_id": appointment_id, "slot_id": 10}

        @staticmethod
        def get_appointment_status_id(connection, status_name):
            assert status_name == "cancelled"
            return 2

        @staticmethod
        def update_appointment_status(connection, appointment_id, status_id):
            connection["appointment_status"] = (appointment_id, status_id)

        @staticmethod
        def update_slot_status(connection, slot_id, slot_status_id):
            slot_updates.append((slot_id, slot_status_id))

        @staticmethod
        def get_status_result(connection, appointment_id):
            return {"appointment_id": appointment_id, "status": "cancelled"}

    @contextmanager
    def fake_transaction_scope():
        yield {}

    monkeypatch.setattr(appointment_repo, "appointment_queries", FakeAppointmentQueries)
    monkeypatch.setattr(appointment_repo.session, "transaction_scope", fake_transaction_scope)

    result = appointment_repo.update_status(5, "cancelled")

    assert result == {"appointment_id": 5, "status": "cancelled"}
    assert slot_updates == []
