import importlib.util
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SETUP_PY = ROOT / "setup.py"
SCHEMA_SQL = ROOT / "app" / "backend" / "app" / "db" / "schema.sql"


def load_setup_module():
    spec = importlib.util.spec_from_file_location("project_setup", SETUP_PY)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class RecordingConnection:
    def __init__(self) -> None:
        self.commits = 0
        self.rollbacks = 0

    def commit(self) -> None:
        self.commits += 1

    def rollback(self) -> None:
        self.rollbacks += 1


class RecordingCursor:
    def __init__(self, fail_on: str | None = None) -> None:
        self.fail_on = fail_on
        self.executed: list[str] = []

    def execute(self, statement: str) -> None:
        if self.fail_on and self.fail_on in statement:
            raise RuntimeError("forced SQL failure")
        self.executed.append(statement)

    def fetchall(self) -> list[object]:
        return []


def test_split_statements_preserves_inline_comment_markers_inside_strings():
    setup = load_setup_module()

    statements = setup._split_statements(
        "SELECT 'literal -- not a comment; still literal'; -- remove this\n"
        "SELECT 1;"
    )

    assert statements == [
        "SELECT 'literal -- not a comment; still literal'",
        "SELECT 1",
    ]


def test_split_statements_handles_mysql_delimiter_trigger_blocks():
    setup = load_setup_module()

    statements = setup._split_statements(
        "DELIMITER //\n"
        "CREATE TRIGGER trg_example BEFORE INSERT ON example\n"
        "FOR EACH ROW\n"
        "BEGIN\n"
        "    SET NEW.name = 'a; b';\n"
        "    SIGNAL SQLSTATE '45000'\n"
        "        SET MESSAGE_TEXT = 'bad; value';\n"
        "END//\n"
        "DELIMITER ;\n"
        "CREATE VIEW v_example AS SELECT 1;"
    )

    assert len(statements) == 2
    assert statements[0].startswith("CREATE TRIGGER trg_example")
    assert "SET NEW.name = 'a; b';" in statements[0]
    assert "SET MESSAGE_TEXT = 'bad; value';" in statements[0]
    assert statements[0].endswith("END")
    assert statements[1] == "CREATE VIEW v_example AS SELECT 1"
    assert not any("DELIMITER" in statement for statement in statements)


def test_schema_sql_splits_for_setup_with_triggers_and_summary_views():
    setup = load_setup_module()

    statements = setup._split_statements(SCHEMA_SQL.read_text(encoding="utf-8"))

    assert any(
        statement.startswith("CREATE TRIGGER trg_medical_certificates_validate_insert")
        for statement in statements
    )
    assert any(
        statement.startswith("CREATE TRIGGER trg_medical_certificates_validate_update")
        for statement in statements
    )
    assert any(
        "CREATE OR REPLACE VIEW v_doctor_appointment_summaries" in statement
        for statement in statements
    )
    assert any(
        "CREATE OR REPLACE VIEW v_student_report_summaries" in statement
        for statement in statements
    )
    assert not any("DELIMITER" in statement for statement in statements)


def test_apply_migrations_raises_when_a_migration_fails(tmp_path):
    setup = load_setup_module()
    (tmp_path / "001_ok.sql").write_text("SELECT 1;", encoding="utf-8")
    (tmp_path / "002_bad.sql").write_text("SELECT broken;", encoding="utf-8")
    cursor = RecordingCursor(fail_on="broken")
    connection = RecordingConnection()

    with pytest.raises(RuntimeError, match="002_bad.sql"):
        setup._apply_migrations(cursor, connection, tmp_path)

    assert connection.commits == 1
    assert connection.rollbacks == 1
