"""
One-command setup for College Infirmary Appointment System.
Installs backend (uv) and frontend (npm) dependencies, then
auto-initialises the MySQL database if credentials are correct.

Usage:
    python setup.py
"""

import getpass
import subprocess
import sys
import shutil
from pathlib import Path

ROOT     = Path(__file__).parent
FRONTEND = ROOT / "app" / "frontend"
ENV_FILE = ROOT / ".env"

SCHEMA_SQL    = ROOT / "app" / "backend" / "app" / "db" / "schema.sql"
SEED_SQL      = ROOT / "app" / "backend" / "app" / "db" / "seed.sql"
MIGRATIONS    = ROOT / "app" / "backend" / "app" / "db" / "migrations"
DB_NAME       = "medical_appointment_system"
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


# ── Helpers ────────────────────────────────────────────────────────────────────

def parse_version(v: str) -> tuple[int, ...]:
    try:
        return tuple(int(x) for x in v.strip().split(".")[:3])
    except ValueError:
        return (0,)


def check_npm_version() -> None:
    try:
        raw = subprocess.check_output(["npm", "--version"], text=True).strip()
    except Exception:
        return
    installed = parse_version(raw)
    max_v = NPM_MAX_VERSION
    if installed > max_v:
        max_str = ".".join(str(x) for x in max_v)
        print(
            f"\n  npm {raw} is installed but this project requires npm <= {max_str}.\n"
            f"  Downgrade with:  npm install -g npm@{max_str}\n"
        )
        sys.exit(1)
    print(f"  ✓  npm {raw} (supported — max {'.'.join(str(x) for x in max_v)})")


def run(cmd: list[str], cwd: Path | None = None) -> bool:
    print(f"  $ {' '.join(cmd)}")
    return subprocess.run(cmd, cwd=cwd).returncode == 0


def check(name: str) -> bool:
    found = shutil.which(name) is not None
    print(f"  {'✓' if found else '✗'}  {name}")
    return found


def _strip_inline_comments(sql: str) -> str:
    """Remove -- inline comments from SQL while preserving string literals."""
    import re
    # Remove -- comments that are not inside single-quoted strings
    result = re.sub(r"--[^\n]*", "", sql)
    return result


def _split_statements(sql: str) -> list[str]:
    """Split a SQL file into individual statements, skipping blank ones."""
    sql = _strip_inline_comments(sql)
    stmts = []
    for raw in sql.split(";"):
        stmt = raw.strip()
        if stmt:
            stmts.append(stmt)
    return stmts


# ── Database initialisation ────────────────────────────────────────────────────

def init_database(host: str, port: int, user: str, password: str) -> bool:
    """Connect to MySQL, create the database, apply schema + seed + migrations."""
    try:
        import mysql.connector  # available after uv sync
    except ImportError:
        print("  mysql-connector-python not found — run uv sync first.\n")
        return False

    # ── Connect (no database selected yet) ───────────────────────────────────
    try:
        conn = mysql.connector.connect(
            host=host, port=port, user=user, password=password,
            autocommit=True,
        )
    except mysql.connector.Error as e:
        print(f"\n  MySQL connection failed: {e}")
        print("  Check your host, port, user, and password and try again.\n")
        return False

    cursor = conn.cursor()

    # ── Create database ───────────────────────────────────────────────────────
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
    print(f"  ✓  Database '{DB_NAME}' ready")

    cursor.execute(f"USE `{DB_NAME}`")

    # ── Apply schema (idempotent — CREATE TABLE IF NOT EXISTS) ───────────────
    cursor.execute("SHOW TABLES LIKE 'users'")
    schema_applied = cursor.fetchone() is not None

    if schema_applied:
        print("  ✓  Schema already applied")
    else:
        print("  Applying schema…")
        _execute_sql_file(cursor, SCHEMA_SQL)
        print("  ✓  Schema applied")

    # ── Apply seed (always attempt — duplicates are silently skipped) ─────────
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]

    if user_count >= 7:
        print("  ✓  Seed data already loaded")
    else:
        print("  Seeding data…")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        _execute_sql_file(cursor, SEED_SQL)
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        conn.commit()
        print("  ✓  Seed data loaded")

    # ── Apply any pending migrations ──────────────────────────────────────────
    if MIGRATIONS.exists():
        migration_files = sorted(MIGRATIONS.glob("*.sql"))
        applied = 0
        for mf in migration_files:
            try:
                _execute_sql_file(cursor, mf)
                conn.commit()
                applied += 1
            except Exception:
                conn.rollback()
        if applied:
            print(f"  ✓  {applied} migration(s) applied")

    cursor.close()
    conn.close()
    return True


def _execute_sql_file(cursor: object, path: Path) -> None:
    """Read and execute every statement in a SQL file."""
    sql = path.read_text(encoding="utf-8")
    for stmt in _split_statements(sql):
        try:
            cursor.execute(stmt)
            # drain any unread results (e.g. from CREATE TABLE)
            try:
                cursor.fetchall()
            except Exception:
                pass
        except Exception as e:
            # ignore "already exists" type errors (safe re-runs)
            msg = str(e).lower()
            if "already exists" in msg or "duplicate" in msg:
                pass
            else:
                raise


# ── Main ───────────────────────────────────────────────────────────────────────

def main() -> None:
    print("\n=== College Infirmary — Setup ===\n")

    # ── Prerequisites ─────────────────────────────────────────────────────────
    print("Checking prerequisites:")
    check("python") or check("python3")
    uv_ok   = check("uv")
    node_ok = check("node")
    npm_ok  = check("npm")

    missing = []
    if not uv_ok:
        missing.append("uv  →  https://docs.astral.sh/uv/getting-started/installation/")
    if not node_ok or not npm_ok:
        missing.append("Node.js + npm  →  https://nodejs.org/")

    if missing:
        print("\n  Missing:")
        for m in missing:
            print(f"    • {m}")
        print()
        sys.exit(1)

    if npm_ok:
        check_npm_version()

    print()

    # ── Backend deps ──────────────────────────────────────────────────────────
    print("Installing backend dependencies:")
    if not run(["uv", "sync"], cwd=ROOT):
        print("\n  Backend install failed.\n")
        sys.exit(1)
    print()

    # ── Frontend deps ─────────────────────────────────────────────────────────
    lockfile = FRONTEND / "package-lock.json"
    npm_cmd  = ["npm", "ci"] if lockfile.exists() else ["npm", "install"]
    print(f"Installing frontend dependencies ({' '.join(npm_cmd)}):")
    if not run(npm_cmd, cwd=FRONTEND):
        print("\n  Frontend install failed.\n")
        sys.exit(1)
    print()

    # ── MySQL credentials ─────────────────────────────────────────────────────
    print("Database setup:")

    # Read existing .env values if present
    env_vals: dict[str, str] = {}
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text().splitlines():
            if "=" in line and not line.startswith("#"):
                k, _, v = line.partition("=")
                env_vals[k.strip()] = v.strip()

    host     = env_vals.get("MYSQL_HOST", "127.0.0.1")
    port     = int(env_vals.get("MYSQL_PORT", "3306"))
    db_user  = env_vals.get("MYSQL_USER", "root")
    password = env_vals.get("MYSQL_PASSWORD", "")

    # If password is still the placeholder, prompt
    if not password or password == "your_mysql_password":
        print(f"  Enter MySQL password for user '{db_user}' on {host}:{port}")
        password = getpass.getpass("  Password: ")

    db_ok = init_database(host, port, db_user, password)
    print()

    # ── Write / update .env ───────────────────────────────────────────────────
    if not ENV_FILE.exists():
        ENV_FILE.write_text(ENV_TEMPLATE.format(password=password))
        print("Created .env\n")
    elif db_ok and env_vals.get("MYSQL_PASSWORD", "") in ("", "your_mysql_password"):
        # Patch just the password line
        updated = "\n".join(
            f"MYSQL_PASSWORD={password}" if line.startswith("MYSQL_PASSWORD=") else line
            for line in ENV_FILE.read_text().splitlines()
        )
        ENV_FILE.write_text(updated + "\n")
        print("Updated MYSQL_PASSWORD in .env\n")

    if not db_ok:
        print("Database initialisation failed — fix the connection and re-run setup.py.\n")
        sys.exit(1)

    # ── Done ──────────────────────────────────────────────────────────────────
    print("=== Setup complete ===\n")
    print("Start the app:")
    print("  npm run dev\n")
    print("  Frontend  →  http://localhost:3000")
    print("  Backend   →  http://localhost:8000")
    print("  API docs  →  http://localhost:8000/docs\n")
    print("Seed accounts (password: password123):")
    for email, role in [
        ("student@college.edu",       "Student"),
        ("professor@college.edu",     "Professor"),
        ("college.staff@college.edu", "College Staff"),
        ("hostel.staff@college.edu",  "Hostel Staff"),
        ("doctor@college.edu",        "Doctor"),
        ("admin@college.edu",         "Admin"),
        ("staff@college.edu",         "Staff"),
    ]:
        print(f"  {role:<16} {email}")
    print()


if __name__ == "__main__":
    main()
