"""
One-command setup for the College Infirmary Appointment System.

Usage:
    python setup.py
"""

import getpass
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).parent
FRONTEND = ROOT / "app" / "frontend"
ENV_FILE = ROOT / ".env"

SCHEMA_SQL = ROOT / "app" / "backend" / "app" / "db" / "schema.sql"
SEED_SQL = ROOT / "app" / "backend" / "app" / "db" / "seed.sql"
MIGRATIONS = ROOT / "app" / "backend" / "app" / "db" / "migrations"
DB_NAME = "medical_appointment_system"
NPM_MAX_VERSION = (11, 11, 11)

ENV_TEMPLATE = """\
ENVIRONMENT=development
DATABASE_PROVIDER=mysql
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD={password}
MYSQL_DATABASE=medical_appointment_system
JWT_SECRET_KEY=change-this-dev-secret
RATE_LIMIT_ENABLED=true
"""


def parse_version(version: str) -> tuple[int, ...]:
    try:
        return tuple(int(part) for part in version.strip().split(".")[:3])
    except ValueError:
        return (0,)


def check_npm_version() -> None:
    try:
        raw = subprocess.check_output(["npm", "--version"], text=True).strip()
    except Exception:
        return

    installed = parse_version(raw)
    if installed > NPM_MAX_VERSION:
        max_str = ".".join(str(part) for part in NPM_MAX_VERSION)
        print()
        print(f"  npm {raw} is installed, but this project requires npm <= {max_str}.")
        print(f"  Downgrade with: npm install -g npm@{max_str}")
        print()
        sys.exit(1)

    print(f"  [OK] npm {raw} supported, max {'.'.join(str(x) for x in NPM_MAX_VERSION)}")


def run(cmd: list[str], cwd: Path | None = None) -> bool:
    print(f"  $ {' '.join(cmd)}")
    return subprocess.run(cmd, cwd=cwd).returncode == 0


def check(name: str) -> bool:
    found = shutil.which(name) is not None
    marker = "[OK]" if found else "[MISSING]"
    print(f"  {marker} {name}")
    return found


def _is_escaped_quote(sql: str, index: int, quote: str) -> bool:
    return quote in {"'", '"'} and index + 1 < len(sql) and sql[index + 1] == quote


def _skip_quoted(sql: str, index: int, quote: str) -> int:
    index += 1
    while index < len(sql):
        char = sql[index]
        if char == "\\" and quote != "`":
            index += 2
            continue
        if char == quote:
            if _is_escaped_quote(sql, index, quote):
                index += 2
                continue
            return index + 1
        index += 1
    return index


def _strip_sql_comments(sql: str) -> str:
    """Remove SQL comments without changing quoted string literals."""
    output: list[str] = []
    index = 0

    while index < len(sql):
        char = sql[index]
        next_two = sql[index : index + 2]

        if char in {"'", '"', "`"}:
            end = _skip_quoted(sql, index, char)
            output.append(sql[index:end])
            index = end
            continue

        if next_two == "--" and (index + 2 == len(sql) or sql[index + 2].isspace()):
            while index < len(sql) and sql[index] not in "\r\n":
                index += 1
            continue

        if char == "#":
            while index < len(sql) and sql[index] not in "\r\n":
                index += 1
            continue

        if next_two == "/*":
            index += 2
            while index + 1 < len(sql) and sql[index : index + 2] != "*/":
                index += 1
            index += 2
            continue

        output.append(char)
        index += 1

    return "".join(output)


def _find_delimiter(sql: str, delimiter: str) -> int:
    index = 0

    while index < len(sql):
        char = sql[index]
        next_two = sql[index : index + 2]

        if char in {"'", '"', "`"}:
            index = _skip_quoted(sql, index, char)
            continue

        if next_two == "--" and (index + 2 == len(sql) or sql[index + 2].isspace()):
            while index < len(sql) and sql[index] not in "\r\n":
                index += 1
            continue

        if char == "#":
            while index < len(sql) and sql[index] not in "\r\n":
                index += 1
            continue

        if next_two == "/*":
            index += 2
            while index + 1 < len(sql) and sql[index : index + 2] != "*/":
                index += 1
            index += 2
            continue

        if sql.startswith(delimiter, index):
            return index

        index += 1

    return -1


def _split_statements(sql: str) -> list[str]:
    """Split MySQL SQL text into executable statements.

    Handles client-side DELIMITER commands so trigger bodies in schema.sql are
    sent to mysql-connector as complete statements.
    """
    statements: list[str] = []
    delimiter = ";"
    pending = ""

    for raw_line in sql.splitlines():
        stripped = raw_line.strip()
        pending_has_sql = bool(_strip_sql_comments(pending).strip())

        if not pending_has_sql and stripped.upper().startswith("DELIMITER "):
            delimiter = stripped.split(None, 1)[1]
            pending = ""
            continue

        pending = f"{pending}\n{raw_line}" if pending else raw_line

        while True:
            delimiter_index = _find_delimiter(pending, delimiter)
            if delimiter_index == -1:
                break

            raw_statement = pending[:delimiter_index]
            statement = _strip_sql_comments(raw_statement).strip()
            if statement:
                statements.append(statement)
            pending = pending[delimiter_index + len(delimiter) :].lstrip("\r\n")

    statement = _strip_sql_comments(pending).strip()
    if statement:
        statements.append(statement)

    return statements


def _is_ignorable_sql_error(error: Exception) -> bool:
    message = str(error).lower()
    return any(
        expected in message
        for expected in [
            "already exists",
            "duplicate",
            "duplicate column",
            "duplicate key",
            "duplicate entry",
        ]
    )


def _execute_sql_file(cursor: object, path: Path) -> None:
    sql = path.read_text(encoding="utf-8")
    for statement in _split_statements(sql):
        try:
            cursor.execute(statement)
            try:
                cursor.fetchall()
            except Exception:
                pass
        except Exception as exc:
            if not _is_ignorable_sql_error(exc):
                raise


def _apply_migrations(cursor: object, connection: object, migrations_dir: Path) -> int:
    applied = 0
    for migration in sorted(migrations_dir.glob("*.sql")):
        try:
            _execute_sql_file(cursor, migration)
            connection.commit()
            applied += 1
        except Exception as exc:
            connection.rollback()
            raise RuntimeError(f"Migration failed: {migration.name}") from exc
    return applied


def init_database(host: str, port: int, user: str, password: str) -> bool:
    """Connect to MySQL, create the database, apply schema, seed, and migrations."""
    try:
        import mysql.connector
    except ImportError:
        print("  mysql-connector-python not found. Run uv sync first.")
        return False

    try:
        connection = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            autocommit=False,
        )
    except mysql.connector.Error as exc:
        print()
        print(f"  MySQL connection failed: {exc}")
        print("  Check your host, port, user, and password and try again.")
        print()
        return False

    cursor = connection.cursor()

    try:
        cursor.execute(
            f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` "
            "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
        )
        cursor.execute(f"USE `{DB_NAME}`")
        print(f"  [OK] Database '{DB_NAME}' ready")

        cursor.execute("SHOW TABLES LIKE 'users'")
        schema_applied = cursor.fetchone() is not None

        if schema_applied:
            print("  [OK] Base schema already present")
        else:
            print("  Applying base schema...")
            _execute_sql_file(cursor, SCHEMA_SQL)
            connection.commit()
            print("  [OK] Base schema applied")

        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]

        if user_count >= 7:
            print("  [OK] Seed data already loaded")
        else:
            print("  Seeding data...")
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
            _execute_sql_file(cursor, SEED_SQL)
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
            connection.commit()
            print("  [OK] Seed data loaded")

        if MIGRATIONS.exists():
            applied = _apply_migrations(cursor, connection, MIGRATIONS)
            print(f"  [OK] {applied} migration(s) checked/applied")

        return True
    except Exception as exc:
        connection.rollback()
        print()
        print(f"  Database setup failed: {exc}")
        print()
        return False
    finally:
        cursor.close()
        connection.close()


def read_env_file() -> dict[str, str]:
    env_values: dict[str, str] = {}
    if not ENV_FILE.exists():
        return env_values

    for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.lstrip().startswith("#"):
            key, _, value = line.partition("=")
            env_values[key.strip()] = value.strip()

    return env_values


def write_env_password(password: str, env_values: dict[str, str]) -> None:
    if not ENV_FILE.exists():
        ENV_FILE.write_text(ENV_TEMPLATE.format(password=password), encoding="utf-8")
        print("Created .env")
        return

    if env_values.get("MYSQL_PASSWORD", "") not in {"", "your_mysql_password"}:
        return

    updated = "\n".join(
        f"MYSQL_PASSWORD={password}" if line.startswith("MYSQL_PASSWORD=") else line
        for line in ENV_FILE.read_text(encoding="utf-8").splitlines()
    )
    ENV_FILE.write_text(updated + "\n", encoding="utf-8")
    print("Updated MYSQL_PASSWORD in .env")


def main() -> None:
    print()
    print("=== College Infirmary - Setup ===")
    print()

    print("Checking prerequisites:")
    check("python") or check("python3")
    uv_ok = check("uv")
    node_ok = check("node")
    npm_ok = check("npm")

    missing: list[str] = []
    if not uv_ok:
        missing.append("uv - https://docs.astral.sh/uv/getting-started/installation/")
    if not node_ok or not npm_ok:
        missing.append("Node.js + npm - https://nodejs.org/")

    if missing:
        print()
        print("  Missing:")
        for item in missing:
            print(f"    - {item}")
        print()
        sys.exit(1)

    check_npm_version()
    print()

    print("Installing backend dependencies:")
    if not run(["uv", "sync"], cwd=ROOT):
        print()
        print("  Backend install failed.")
        print()
        sys.exit(1)
    print()

    print("Installing frontend dependencies:")
    lockfile = FRONTEND / "package-lock.json"
    if not lockfile.exists():
        print("  package-lock.json is missing. Refusing to run npm install from setup.py.")
        print("  Restore the lockfile or create it intentionally before running setup again.")
        sys.exit(1)

    if not run(["npm", "ci"], cwd=FRONTEND):
        print()
        print("  Frontend install failed.")
        print()
        sys.exit(1)
    print()

    print("Database setup:")
    env_values = read_env_file()

    host = env_values.get("MYSQL_HOST", "127.0.0.1")
    port = int(env_values.get("MYSQL_PORT", "3306"))
    db_user = env_values.get("MYSQL_USER", "root")
    password = env_values.get("MYSQL_PASSWORD", "")

    if not password or password == "your_mysql_password":
        print(f"  Enter MySQL password for user '{db_user}' on {host}:{port}")
        password = getpass.getpass("  Password: ")

    db_ok = init_database(host, port, db_user, password)
    print()

    if not db_ok:
        print("Database initialisation failed. Fix the connection/schema issue and rerun setup.py.")
        sys.exit(1)

    write_env_password(password, env_values)
    print()

    print("=== Setup complete ===")
    print()
    print("Start the app:")
    print("  npm run dev")
    print()
    print("  Frontend  -> http://localhost:3000")
    print("  Backend   -> http://localhost:8000")
    print("  API docs  -> http://localhost:8000/docs")
    print()
    print("Seed accounts (password: password123):")
    for email, role in [
        ("student@college.edu", "Student"),
        ("professor@college.edu", "Professor"),
        ("college.staff@college.edu", "College Staff"),
        ("hostel.staff@college.edu", "Hostel Staff"),
        ("doctor@college.edu", "Doctor"),
        ("admin@college.edu", "Admin"),
        ("staff@college.edu", "Staff"),
    ]:
        print(f"  {role:<16} {email}")
    print()


if __name__ == "__main__":
    main()
