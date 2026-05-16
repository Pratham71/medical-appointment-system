from contextlib import contextmanager
from datetime import date, datetime, time, timedelta
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.backend.app.core.config import Settings
from app.backend.app.api.errors import ConflictError
from app.backend.app.db import session
from app.backend.app.db.queries._helpers import fetch_all
from app.backend.app.repositories import appointment_repo, certificate_repo
from app.backend.app.repositories import doctor_repo
from app.backend.app.schemas.certificate import CertificateCreate, CertificateResponse
from app.backend.app.schemas.report import (
    MedicalNoteCreate,
    PrescriptionCreate,
    PrescriptionItemCreate,
)
from app.backend.app.schemas.student import StudentCertificateSummary
from app.backend.app.schemas.student import StudentAppointmentSummary
from app.backend.app.services import (
    appointment_service,
    certificate_service,
    doctor_service,
    report_service,
)


ROOT = Path(__file__).resolve().parents[1]
DB_DIR = ROOT / "app" / "backend" / "app" / "db"
QUERY_DIR = DB_DIR / "queries"
MIGRATION_DIR = DB_DIR / "migrations"


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
        "doctor_weekly_availability",
        "doctor_availability_overrides",
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
    assert "active_slot_id int generated always as" in schema
    assert "unique (active_slot_id)" in schema
    assert "foreign key" in schema
    assert "idx_appointments_student" in schema
    assert "idx_appointment_slots_staff_date" in schema
    assert "idx_appointment_slots_date_status" in schema
    assert "idx_doctor_weekly_availability_staff_weekday" in schema
    assert "idx_doctor_availability_overrides_staff_date" in schema


def test_schema_defines_doctor_availability_rules():
    schema = (DB_DIR / "schema.sql").read_text(encoding="utf-8").lower()

    assert "create table doctor_weekly_availability" in schema
    assert "weekday tinyint unsigned not null" in schema
    assert "unique (staff_id, weekday)" in schema
    assert "check (weekday between 0 and 6)" in schema
    assert "create table doctor_availability_overrides" in schema
    assert "override_date date not null" in schema
    assert "unique (staff_id, override_date)" in schema


def test_schema_and_migration_include_cancellation_reason():
    schema = (DB_DIR / "schema.sql").read_text(encoding="utf-8").lower()
    migration = (
        MIGRATION_DIR / "2026_05_16_add_cancellation_reason.sql"
    ).read_text(encoding="utf-8").lower()

    assert "cancellation_reason varchar(500) null default null" in schema
    assert "appointments.cancellation_reason" in schema
    assert "alter table appointments" in migration
    assert "add column cancellation_reason varchar(500) null default null" in migration
    assert "create or replace view v_appointment_details" in migration


def test_live_schema_migration_repairs_availability_and_certificate_views():
    migration = (
        MIGRATION_DIR / "2026_05_16_sync_live_schema.sql"
    ).read_text(encoding="utf-8").lower()

    assert "create table if not exists doctor_weekly_availability" in migration
    assert "create table if not exists doctor_availability_overrides" in migration
    assert "from doctor_availability" in migration
    assert "when doctor_availability.day_of_week = 6 then false" in migration
    assert "create or replace view v_available_appointment_slots" in migration
    assert "left join doctor_weekly_availability" in migration
    assert "create or replace view v_student_certificate_summaries" in migration
    assert "appointments.reason as appointment_reason" in migration
    assert "medical_notes.diagnosis" in migration


def test_available_slots_view_respects_doctor_availability_rules():
    schema = (DB_DIR / "schema.sql").read_text(encoding="utf-8").lower()

    assert "left join doctor_availability_overrides" in schema
    assert "left join doctor_weekly_availability" in schema
    assert "weekday(appointment_slots.slot_date)" in schema
    assert "coalesce(doctor_weekly_availability.is_available, weekday(appointment_slots.slot_date) < 6)" in schema
    assert "doctor_availability_overrides.is_available = true" in schema


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


def test_schema_enforces_certificate_issue_date_against_appointment_date():
    schema = (DB_DIR / "schema.sql").read_text(encoding="utf-8").lower()

    assert "trg_medical_certificates_validate_insert" in schema
    assert "trg_medical_certificates_validate_update" in schema
    assert "new.issue_date < appointment_date" in schema
    assert "appointment_date > current_date" in schema
    assert "signal sqlstate '45000'" in schema


def test_certificate_summary_view_includes_medical_context():
    schema = (DB_DIR / "schema.sql").read_text(encoding="utf-8").lower()

    assert "appointments.reason as appointment_reason" in schema
    assert "medical_notes.diagnosis" in schema
    assert "medical_notes.remarks" in schema


def test_certificate_schema_and_view_include_leave_dates():
    schema = (DB_DIR / "schema.sql").read_text(encoding="utf-8").lower()

    assert "leave_start_date date null" in schema
    assert "leave_end_date date null" in schema
    assert "medical_certificates.leave_start_date" in schema
    assert "medical_certificates.leave_end_date" in schema


def test_certificate_schema_and_view_include_certificate_notes():
    schema = (DB_DIR / "schema.sql").read_text(encoding="utf-8").lower()

    assert "certificate_notes text null" in schema
    assert "medical_certificates.certificate_notes" in schema


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
    assert "insert into doctor_weekly_availability" in seed
    assert "(1, 6, false" in seed
    assert "insert into appointment_slots" in seed


def test_schema_and_migration_define_emergency_alerts():
    schema = (DB_DIR / "schema.sql").read_text(encoding="utf-8").lower()
    migration = (
        MIGRATION_DIR / "2026_05_16_add_emergency_alerts.sql"
    ).read_text(encoding="utf-8").lower()

    assert "create table emergency_alerts" in schema
    assert "student_id int not null" in schema
    assert "message varchar(500) not null" in schema
    assert "foreign key (student_id) references students(student_id)" in schema
    assert "create table if not exists emergency_alerts" in migration


def test_emergency_alert_response_schema_accepts_alert_context():
    from app.backend.app.schemas.emergency import EmergencyAlertResponse

    response = EmergencyAlertResponse(
        alert_id=1,
        student_id=1,
        student_name="Aarav Sharma",
        roll_number="CSE-2026-001",
        message="Need urgent medical help",
        created_at=datetime(2026, 5, 16, 12, 0),
    )

    assert response.student_name == "Aarav Sharma"
    assert response.roll_number == "CSE-2026-001"


def test_emergency_service_defaults_blank_alert_message(monkeypatch):
    from app.backend.app.services import emergency_service

    captured = {}

    def fake_create_alert(student_id: int, message: str):
        captured["student_id"] = student_id
        captured["message"] = message
        return {
            "alert_id": 1,
            "student_id": student_id,
            "student_name": "Aarav Sharma",
            "roll_number": "CSE-2026-001",
            "message": message,
            "created_at": datetime(2026, 5, 16, 12, 0),
        }

    monkeypatch.setattr(emergency_service.emergency_repo, "create_alert", fake_create_alert)

    response = emergency_service.create_alert(1, "   ")

    assert response.message == "Student requested emergency assistance"
    assert captured == {
        "student_id": 1,
        "message": "Student requested emergency assistance",
    }


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


def test_appointment_service_filters_today_slots_after_local_time(monkeypatch):
    captured = {}

    def fake_list_available_slots(from_date, current_time=None):
        captured["from_date"] = from_date
        captured["current_time"] = current_time
        return []

    monkeypatch.setattr(
        appointment_service,
        "_get_local_now",
        lambda: datetime(2026, 5, 15, 9, 30),
        raising=False,
    )
    monkeypatch.setattr(
        appointment_service.appointment_repo,
        "ensure_slots_for_date",
        lambda slot_date: captured.setdefault("ensured_date", slot_date),
        raising=False,
    )
    monkeypatch.setattr(
        appointment_service.appointment_repo,
        "list_available_slots",
        fake_list_available_slots,
    )

    result = appointment_service.list_available_slots(date(2026, 5, 15))

    assert result == []
    assert captured == {
        "ensured_date": date(2026, 5, 15),
        "from_date": date(2026, 5, 15),
        "current_time": time(9, 30),
    }


def test_appointment_service_does_not_filter_future_date_by_current_time(monkeypatch):
    captured = {}

    def fake_list_available_slots(from_date, current_time=None):
        captured["from_date"] = from_date
        captured["current_time"] = current_time
        return []

    monkeypatch.setattr(
        appointment_service,
        "_get_local_now",
        lambda: datetime(2026, 5, 15, 9, 30),
        raising=False,
    )
    monkeypatch.setattr(
        appointment_service.appointment_repo,
        "ensure_slots_for_date",
        lambda slot_date: captured.setdefault("ensured_date", slot_date),
        raising=False,
    )
    monkeypatch.setattr(
        appointment_service.appointment_repo,
        "list_available_slots",
        fake_list_available_slots,
    )

    appointment_service.list_available_slots(date(2026, 5, 16))

    assert captured == {
        "ensured_date": date(2026, 5, 16),
        "from_date": date(2026, 5, 16),
        "current_time": None,
    }


def test_appointment_service_lists_doctors_with_availability(monkeypatch):
    captured = []

    def fake_list_doctors(for_date):
        captured.append(for_date)
        return [
            {
                "doctor_id": 1,
                "doctor_name": "Dr. Meera Rao",
                "specialization": "General Medicine",
                "is_available": True,
                "available_slots": 4,
                "unavailability_note": None,
            },
            {
                "doctor_id": 2,
                "doctor_name": "Dr. Nikhil Sen",
                "specialization": "Orthopedics",
                "is_available": False,
                "available_slots": 0,
                "unavailability_note": "Campus camp",
            },
        ]

    monkeypatch.setattr(
        appointment_service.appointment_repo,
        "ensure_slots_for_date",
        lambda slot_date: captured.append(("ensure", slot_date)),
        raising=False,
    )
    monkeypatch.setattr(
        appointment_service.appointment_repo,
        "list_doctors_with_availability",
        lambda for_date: fake_list_doctors(for_date),
        raising=False,
    )

    result = appointment_service.list_doctors_with_availability(date(2026, 5, 18))

    assert captured == [("ensure", date(2026, 5, 18)), date(2026, 5, 18)]
    assert [doctor.doctor_id for doctor in result] == [1, 2]
    assert result[0].available_slots == 4
    assert result[1].is_available is False
    assert result[1].unavailability_note == "Campus camp"


def test_appointment_service_generates_future_weekday_slots_before_listing(monkeypatch):
    calls = []

    monkeypatch.setattr(
        appointment_service,
        "_get_local_now",
        lambda: datetime(2026, 5, 16, 9, 0),
        raising=False,
    )
    monkeypatch.setattr(
        appointment_service.appointment_repo,
        "ensure_slots_for_date",
        lambda slot_date: calls.append(("ensure", slot_date)),
        raising=False,
    )
    monkeypatch.setattr(
        appointment_service.appointment_repo,
        "list_available_slots",
        lambda from_date, current_time=None: calls.append(("list", from_date, current_time)) or [],
    )

    appointment_service.list_available_slots(date(2026, 5, 18))

    assert calls == [
        ("ensure", date(2026, 5, 18)),
        ("list", date(2026, 5, 18), None),
    ]


def test_repository_generates_half_hour_slots_for_available_weekday(monkeypatch):
    inserted = []

    class FakeAppointmentQueries:
        @staticmethod
        def get_slot_status_id(connection, status_name):
            assert status_name == "available"
            return 1

        @staticmethod
        def list_doctor_slot_generation_windows(connection, slot_date):
            assert slot_date == date(2026, 5, 18)
            return [
                {
                    "staff_id": 1,
                    "start_time": time(9, 0),
                    "end_time": time(10, 0),
                }
            ]

        @staticmethod
        def insert_slot_if_missing(
            connection,
            staff_id,
            slot_status_id,
            slot_date,
            start_time,
            end_time,
        ):
            inserted.append(
                (staff_id, slot_status_id, slot_date, start_time, end_time)
            )

    @contextmanager
    def fake_transaction_scope():
        yield {}

    monkeypatch.setattr(appointment_repo, "appointment_queries", FakeAppointmentQueries)
    monkeypatch.setattr(appointment_repo.session, "transaction_scope", fake_transaction_scope)

    appointment_repo.ensure_slots_for_date(date(2026, 5, 18))

    assert inserted == [
        (1, 1, date(2026, 5, 18), time(9, 0), time(9, 30)),
        (1, 1, date(2026, 5, 18), time(9, 30), time(10, 0)),
    ]


def test_repository_generates_slots_from_mysql_time_strings(monkeypatch):
    inserted = []

    class FakeAppointmentQueries:
        @staticmethod
        def get_slot_status_id(connection, status_name):
            assert status_name == "available"
            return 1

        @staticmethod
        def list_doctor_slot_generation_windows(connection, slot_date):
            return [
                {
                    "staff_id": 1,
                    "start_time": "09:00:00",
                    "end_time": "10:00:00",
                }
            ]

        @staticmethod
        def insert_slot_if_missing(
            connection,
            staff_id,
            slot_status_id,
            slot_date,
            start_time,
            end_time,
        ):
            inserted.append((start_time, end_time))

    @contextmanager
    def fake_transaction_scope():
        yield {}

    monkeypatch.setattr(appointment_repo, "appointment_queries", FakeAppointmentQueries)
    monkeypatch.setattr(appointment_repo.session, "transaction_scope", fake_transaction_scope)

    appointment_repo.ensure_slots_for_date(date(2026, 5, 18))

    assert inserted == [
        (time(9, 0), time(9, 30)),
        (time(9, 30), time(10, 0)),
    ]


def test_book_appointment_rejects_elapsed_slot(monkeypatch):
    monkeypatch.setattr(
        appointment_service.appointment_repo,
        "book_appointment",
        lambda student_id, slot_id, reason: {
            "expired": True,
            "slot_id": slot_id,
            "status": "available",
        },
    )

    with pytest.raises(ConflictError, match="Appointment slot is no longer available"):
        appointment_service.book_appointment(
            payload=type("Payload", (), {"slot_id": 7, "reason": "Fever"})(),
            student_id=1,
        )


def test_repository_rejects_elapsed_slot_before_insert(monkeypatch):
    inserts = []

    class FakeAppointmentQueries:
        @staticmethod
        def get_available_slot_for_update(connection, slot_id):
            return {
                "slot_id": slot_id,
                "staff_id": 1,
                "slot_date": date(2026, 5, 15),
                "start_time": time(8, 30),
            }

        @staticmethod
        def get_appointment_status_id(connection, status_name):
            return 1

        @staticmethod
        def get_slot_status_id(connection, status_name):
            return 2

        @staticmethod
        def insert_appointment(connection, student_id, slot_id, status_id, reason):
            inserts.append((student_id, slot_id, status_id, reason))
            return 99

    @contextmanager
    def fake_transaction_scope():
        yield {}

    monkeypatch.setattr(appointment_repo, "_get_local_now", lambda: datetime(2026, 5, 15, 9, 30), raising=False)
    monkeypatch.setattr(appointment_repo, "appointment_queries", FakeAppointmentQueries)
    monkeypatch.setattr(appointment_repo.session, "transaction_scope", fake_transaction_scope)

    result = appointment_repo.book_appointment(1, 7, "Fever")

    assert result == {"expired": True, "slot_id": 7, "status": "available"}
    assert inserts == []


def test_available_slot_query_filters_exact_date_and_elapsed_today_slots():
    source = (QUERY_DIR / "appointment_queries.py").read_text(encoding="utf-8").lower()

    assert "slot_date = %s" in source
    assert "start_time > %s" in source
    assert "slot_date >= %s" not in source


def test_doctor_status_query_lists_all_doctors_with_availability_rules():
    source = (QUERY_DIR / "appointment_queries.py").read_text(encoding="utf-8").lower()

    assert "def list_doctors_with_availability" in source
    assert "from staff" in source
    assert "where staff.is_doctor = true" in source
    assert "left join doctor_availability_overrides" in source
    assert "left join doctor_weekly_availability" in source
    assert "as available_slots" in source


def test_auto_cancel_query_functions_exist():
    source = (QUERY_DIR / "appointment_queries.py").read_text(encoding="utf-8").lower()

    assert "def list_appointments_to_cancel" in source
    assert "appointment_statuses.status_name = %s" in source
    assert "appointment_slots.slot_date = %s" in source
    assert "def cancel_appointment_with_reason" in source
    assert "cancellation_reason = %s" in source
    assert "update appointment_slots" in source


def test_unavailable_override_cancels_booked_appointments(monkeypatch):
    calls = []

    class FakeDoctorQueries:
        @staticmethod
        def upsert_availability_override(
            connection,
            staff_id,
            override_date,
            is_available,
            start_time,
            end_time,
            note,
        ):
            calls.append(("upsert_override", staff_id, override_date, is_available, note))

        @staticmethod
        def get_availability_override(connection, staff_id, override_date):
            return {
                "override_date": override_date,
                "is_available": False,
                "start_time": None,
                "end_time": None,
                "note": "Conference duty",
            }

    class FakeAppointmentQueries:
        @staticmethod
        def get_appointment_status_id(connection, status_name):
            assert status_name == "cancelled"
            return 2

        @staticmethod
        def get_slot_status_id(connection, status_name):
            assert status_name == "available"
            return 1

        @staticmethod
        def list_appointments_to_cancel(
            connection,
            staff_id,
            override_date,
            start_time,
            end_time,
        ):
            calls.append(("list_to_cancel", staff_id, override_date, start_time, end_time))
            return [{"appointment_id": 10, "slot_id": 50}]

        @staticmethod
        def cancel_appointment_with_reason(
            connection,
            appointment_id,
            cancelled_status_id,
            available_slot_status_id,
            slot_id,
            cancellation_reason,
        ):
            calls.append(
                (
                    "cancel",
                    appointment_id,
                    cancelled_status_id,
                    available_slot_status_id,
                    slot_id,
                    cancellation_reason,
                )
            )

    @contextmanager
    def fake_transaction_scope():
        yield {}

    monkeypatch.setattr(doctor_repo, "doctor_queries", FakeDoctorQueries)
    monkeypatch.setattr(doctor_repo, "appointment_queries", FakeAppointmentQueries, raising=False)
    monkeypatch.setattr(doctor_repo.session, "transaction_scope", fake_transaction_scope)

    result = doctor_repo.upsert_availability_override(
        staff_id=1,
        override_date=date(2026, 5, 18),
        is_available=False,
        start_time=None,
        end_time=None,
        note="Conference duty",
    )

    assert result["is_available"] is False
    assert calls == [
        ("upsert_override", 1, date(2026, 5, 18), False, "Conference duty"),
        ("list_to_cancel", 1, date(2026, 5, 18), None, None),
        ("cancel", 10, 2, 1, 50, "Doctor unavailable: Conference duty"),
    ]


def test_student_appointment_summary_includes_cancellation_reason():
    summary = StudentAppointmentSummary(
        appointment_id=1,
        slot_date=date(2026, 5, 18),
        start_time=time(9, 0),
        end_time=time(9, 30),
        doctor_id=1,
        doctor_name="Dr. Meera Singh",
        status="cancelled",
        reason="Fever",
        cancellation_reason="Doctor unavailable: Conference duty",
    )

    assert summary.cancellation_reason == "Doctor unavailable: Conference duty"


def test_doctor_service_returns_default_weekly_availability_when_rows_missing(monkeypatch):
    monkeypatch.setattr(
        doctor_service.doctor_repo,
        "get_availability",
        lambda staff_id: {"weekly_availability": [], "date_overrides": []},
    )

    result = doctor_service.get_availability(1)

    assert result.doctor_id == 1
    assert [rule.weekday for rule in result.weekly_availability] == list(range(7))
    assert result.weekly_availability[0].is_available is True
    assert result.weekly_availability[5].is_available is True
    assert result.weekly_availability[6].is_available is False
    assert result.date_overrides == []


def test_doctor_availability_update_rejects_invalid_time_range():
    from app.backend.app.schemas.doctor import DoctorAvailabilityUpdate

    with pytest.raises(ValidationError):
        DoctorAvailabilityUpdate(
            is_available=True,
            start_time=time(10, 0),
            end_time=time(9, 0),
        )


def test_cancel_status_marks_slot_available(monkeypatch):
    slot_updates = []

    class FakeAppointmentQueries:
        @staticmethod
        def get_appointment_for_update(connection, appointment_id):
            return {"appointment_id": appointment_id, "slot_id": 10, "status": "booked"}

        @staticmethod
        def get_appointment_status_id(connection, status_name):
            return {"cancelled": 2, "available": 1}[status_name]

        @staticmethod
        def get_slot_status_id(connection, status_name):
            assert status_name == "available"
            return 1

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
    assert slot_updates == [(10, 1)]


def test_repository_rejects_completing_cancelled_appointment(monkeypatch):
    status_updates = []
    slot_updates = []

    class FakeAppointmentQueries:
        @staticmethod
        def get_appointment_for_update(connection, appointment_id):
            return {"appointment_id": appointment_id, "slot_id": 10, "status": "cancelled"}

        @staticmethod
        def get_appointment_status_id(connection, status_name):
            assert status_name == "completed"
            return 3

        @staticmethod
        def update_appointment_status(connection, appointment_id, status_id):
            status_updates.append((appointment_id, status_id))

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

    result = appointment_repo.update_status(5, "completed")

    assert result == {
        "appointment_id": 5,
        "status": "cancelled",
        "invalid_transition": True,
    }
    assert status_updates == []
    assert slot_updates == []


def test_complete_cancelled_appointment_raises_conflict(monkeypatch):
    monkeypatch.setattr(
        appointment_service.appointment_repo,
        "update_status",
        lambda appointment_id, status_name: {
            "appointment_id": appointment_id,
            "status": "cancelled",
            "invalid_transition": True,
        },
    )

    with pytest.raises(ConflictError, match="Cannot change appointment from cancelled"):
        appointment_service.complete_appointment(5)


def test_certificate_service_rejects_issue_date_before_appointment_date(monkeypatch):
    created = []

    monkeypatch.setattr(
        certificate_service.certificate_repo,
        "get_appointment_certificate_context",
        lambda appointment_id: {"appointment_id": appointment_id, "appointment_date": date(2026, 5, 15)},
        raising=False,
    )
    monkeypatch.setattr(
        certificate_service.certificate_repo,
        "create_certificate",
        lambda appointment_id, payload: created.append((appointment_id, payload)),
    )

    payload = CertificateCreate(certificate_type_id=1, issue_date=date(2026, 5, 14))

    with pytest.raises(
        ConflictError,
        match="Certificate issue date cannot be before appointment date",
    ):
        certificate_service.create_certificate(5, payload)

    assert created == []


def test_certificate_service_rejects_future_appointment(monkeypatch):
    future_date = date.today() + timedelta(days=1)
    created = []

    monkeypatch.setattr(
        certificate_service.certificate_repo,
        "get_appointment_certificate_context",
        lambda appointment_id: {"appointment_id": appointment_id, "appointment_date": future_date},
        raising=False,
    )
    monkeypatch.setattr(
        certificate_service.certificate_repo,
        "create_certificate",
        lambda appointment_id, payload: created.append((appointment_id, payload)),
    )

    payload = CertificateCreate(certificate_type_id=1)

    with pytest.raises(
        ConflictError,
        match="Cannot issue certificate for a future appointment",
    ):
        certificate_service.create_certificate(5, payload)

    assert created == []


def test_report_service_rejects_notes_for_completed_appointment(monkeypatch):
    writes = []

    monkeypatch.setattr(
        report_service.report_repo,
        "get_appointment_write_context",
        lambda appointment_id: {"appointment_id": appointment_id, "status": "completed"},
        raising=False,
    )
    monkeypatch.setattr(
        report_service.report_repo,
        "add_medical_note",
        lambda appointment_id, payload: writes.append((appointment_id, payload)),
    )

    with pytest.raises(ConflictError, match="Completed appointments cannot be edited"):
        report_service.add_medical_note(
            5,
            MedicalNoteCreate(diagnosis="Fever", remarks="Rest"),
        )

    assert writes == []


def test_report_service_rejects_prescription_for_completed_appointment(monkeypatch):
    writes = []

    monkeypatch.setattr(
        report_service.report_repo,
        "get_appointment_write_context",
        lambda appointment_id: {"appointment_id": appointment_id, "status": "completed"},
        raising=False,
    )
    monkeypatch.setattr(
        report_service.report_repo,
        "add_prescription",
        lambda appointment_id, payload: writes.append((appointment_id, payload)),
    )

    with pytest.raises(ConflictError, match="Completed appointments cannot be edited"):
        report_service.add_prescription(
            5,
            PrescriptionCreate(
                items=[
                    PrescriptionItemCreate(
                        medicine_name="Paracetamol",
                        dosage="500mg",
                    )
                ],
            ),
        )

    assert writes == []


def test_certificate_service_rejects_completed_appointment_edit(monkeypatch):
    writes = []

    monkeypatch.setattr(
        certificate_service.certificate_repo,
        "get_appointment_certificate_context",
        lambda appointment_id: {
            "appointment_id": appointment_id,
            "appointment_date": date(2026, 5, 15),
            "status": "completed",
        },
    )
    monkeypatch.setattr(
        certificate_service.certificate_repo,
        "create_certificate",
        lambda appointment_id, payload: writes.append((appointment_id, payload)),
    )

    with pytest.raises(ConflictError, match="Completed appointments cannot be edited"):
        certificate_service.create_certificate(
            5,
            CertificateCreate(
                certificate_type_id=2,
                issue_date=date(2026, 5, 16),
            ),
        )

    assert writes == []


def test_certificate_response_models_include_medical_context_fields():
    row = {
        "certificate_id": 1,
        "appointment_id": 2,
        "student_id": 1,
        "student_name": "Asha Kumar",
        "certificate_type_id": 1,
        "certificate_type": "Consultation Proof",
        "issue_date": date(2026, 5, 16),
        "doctor_id": 1,
        "doctor_name": "Dr. Meera Rao",
        "appointment_date": date(2026, 5, 15),
        "appointment_reason": "Fever and headache",
        "diagnosis": "Seasonal fever",
        "remarks": "Rest advised",
    }

    response = CertificateResponse(**row)
    summary = StudentCertificateSummary(**row)

    assert response.doctor_name == "Dr. Meera Rao"
    assert response.appointment_date == date(2026, 5, 15)
    assert response.appointment_reason == "Fever and headache"
    assert response.diagnosis == "Seasonal fever"
    assert response.remarks == "Rest advised"
    assert summary.appointment_reason == "Fever and headache"
    assert summary.diagnosis == "Seasonal fever"
    assert summary.remarks == "Rest advised"


def test_certificate_create_accepts_leave_date_range():
    payload = CertificateCreate(
        certificate_type_id=1,
        leave_start_date=date(2026, 5, 15),
        leave_end_date=date(2026, 5, 17),
    )

    assert payload.leave_start_date == date(2026, 5, 15)
    assert payload.leave_end_date == date(2026, 5, 17)


def test_certificate_repository_persists_leave_dates(monkeypatch):
    captured = {}

    class FakeCertificateQueries:
        @staticmethod
        def get_appointment_certificate_context(connection, appointment_id):
            return {
                "appointment_id": appointment_id,
                "appointment_date": date(2026, 5, 15),
                "status": "booked",
            }

        @staticmethod
        def upsert_certificate(
            connection,
            appointment_id,
            certificate_type_id,
            issue_date,
            leave_start_date,
            leave_end_date,
            certificate_notes=None,
        ):
            captured["payload"] = {
                "appointment_id": appointment_id,
                "certificate_type_id": certificate_type_id,
                "issue_date": issue_date,
                "leave_start_date": leave_start_date,
                "leave_end_date": leave_end_date,
                "certificate_notes": certificate_notes,
            }

        @staticmethod
        def get_certificate_by_appointment_type(connection, appointment_id, certificate_type_id):
            return {
                "certificate_id": 1,
                "appointment_id": appointment_id,
                "student_id": 1,
                "student_name": "Asha Kumar",
                "certificate_type_id": certificate_type_id,
                "certificate_type": "Medical Leave",
                "issue_date": date(2026, 5, 16),
                "doctor_id": 1,
                "doctor_name": "Dr. Meera Rao",
                "appointment_date": date(2026, 5, 15),
                "appointment_reason": "Fever",
                "diagnosis": "Seasonal fever",
                "remarks": "Rest advised",
                "leave_start_date": date(2026, 5, 15),
                "leave_end_date": date(2026, 5, 17),
            }

    @contextmanager
    def fake_transaction_scope():
        yield {}

    monkeypatch.setattr(certificate_repo, "certificate_queries", FakeCertificateQueries)
    monkeypatch.setattr(certificate_repo.session, "transaction_scope", fake_transaction_scope)

    payload = CertificateCreate(
        certificate_type_id=1,
        issue_date=date(2026, 5, 16),
        leave_start_date=date(2026, 5, 15),
        leave_end_date=date(2026, 5, 17),
    )

    result = certificate_repo.create_certificate(5, payload)

    assert captured["payload"]["leave_start_date"] == date(2026, 5, 15)
    assert captured["payload"]["leave_end_date"] == date(2026, 5, 17)
    assert result["leave_start_date"] == date(2026, 5, 15)
    assert result["leave_end_date"] == date(2026, 5, 17)


def test_certificate_create_accepts_certificate_notes():
    payload = CertificateCreate(
        certificate_type_id=2,
        certificate_notes="Cleared to resume academic attendance",
    )

    assert payload.certificate_notes == "Cleared to resume academic attendance"


def test_certificate_repository_persists_certificate_notes(monkeypatch):
    captured = {}

    class FakeCertificateQueries:
        @staticmethod
        def get_appointment_certificate_context(connection, appointment_id):
            return {
                "appointment_id": appointment_id,
                "appointment_date": date(2026, 5, 15),
                "status": "booked",
            }

        @staticmethod
        def upsert_certificate(
            connection,
            appointment_id,
            certificate_type_id,
            issue_date,
            leave_start_date,
            leave_end_date,
            certificate_notes,
        ):
            captured["payload"] = {
                "appointment_id": appointment_id,
                "certificate_type_id": certificate_type_id,
                "issue_date": issue_date,
                "leave_start_date": leave_start_date,
                "leave_end_date": leave_end_date,
                "certificate_notes": certificate_notes,
            }

        @staticmethod
        def get_certificate_by_appointment_type(connection, appointment_id, certificate_type_id):
            return {
                "certificate_id": 1,
                "appointment_id": appointment_id,
                "student_id": 1,
                "student_name": "Asha Kumar",
                "certificate_type_id": certificate_type_id,
                "certificate_type": "Fitness Certificate",
                "issue_date": date(2026, 5, 16),
                "doctor_id": 1,
                "doctor_name": "Dr. Meera Rao",
                "appointment_date": date(2026, 5, 15),
                "appointment_reason": "Fitness clearance",
                "diagnosis": "Fit",
                "remarks": "No restrictions",
                "leave_start_date": None,
                "leave_end_date": None,
                "certificate_notes": "Cleared to resume academic attendance",
            }

    @contextmanager
    def fake_transaction_scope():
        yield {}

    monkeypatch.setattr(certificate_repo, "certificate_queries", FakeCertificateQueries)
    monkeypatch.setattr(certificate_repo.session, "transaction_scope", fake_transaction_scope)

    payload = CertificateCreate(
        certificate_type_id=2,
        issue_date=date(2026, 5, 16),
        certificate_notes="Cleared to resume academic attendance",
    )

    result = certificate_repo.create_certificate(5, payload)

    assert captured["payload"]["certificate_notes"] == "Cleared to resume academic attendance"
    assert result["certificate_notes"] == "Cleared to resume academic attendance"


def test_certificate_service_rejects_invalid_leave_date_range(monkeypatch):
    created = []

    monkeypatch.setattr(
        certificate_service.certificate_repo,
        "get_appointment_certificate_context",
        lambda appointment_id: {"appointment_id": appointment_id, "appointment_date": date(2026, 5, 15)},
    )
    monkeypatch.setattr(
        certificate_service.certificate_repo,
        "create_certificate",
        lambda appointment_id, payload: created.append((appointment_id, payload)),
    )

    payload = CertificateCreate(
        certificate_type_id=1,
        issue_date=date(2026, 5, 16),
        leave_start_date=date(2026, 5, 18),
        leave_end_date=date(2026, 5, 17),
    )

    with pytest.raises(
        ConflictError,
        match="Leave end date cannot be before leave start date",
    ):
        certificate_service.create_certificate(5, payload)

    assert created == []
