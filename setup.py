"""
One-command setup for College Infirmary Appointment System.
Installs backend (uv) and frontend (npm) dependencies.

Usage:
    python setup.py
"""

import subprocess
import sys
import shutil
from pathlib import Path

ROOT = Path(__file__).parent
FRONTEND = ROOT / "app" / "frontend"
ENV_FILE = ROOT / ".env"

ENV_TEMPLATE = """\
ENVIRONMENT=development
DATABASE_PROVIDER=mysql
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password
MYSQL_DATABASE=medical_appointment_system
JWT_SECRET_KEY=change-this-dev-secret
RATE_LIMIT_ENABLED=true
"""


NPM_MAX_VERSION = (11, 11, 11)


def parse_version(v: str) -> tuple[int, ...]:
    """Convert a version string like '10.2.3' to a comparable tuple."""
    try:
        return tuple(int(x) for x in v.strip().split(".")[:3])
    except ValueError:
        return (0,)


def check_npm_version() -> None:
    """Warn and exit if the installed npm version exceeds the supported maximum."""
    try:
        raw = subprocess.check_output(["npm", "--version"], text=True).strip()
    except Exception:
        return  # npm not found — already caught by check()
    installed = parse_version(raw)
    max_v = NPM_MAX_VERSION
    if installed > max_v:
        max_str = ".".join(str(x) for x in max_v)
        print(
            f"\n  npm {raw} is installed but this project requires npm <= {max_str}.\n"
            f"  Downgrade with:  npm install -g npm@{max_str}\n"
        )
        sys.exit(1)
    print(f"  ✓  npm {raw} (within supported range <= {'.'.join(str(x) for x in max_v)})")


def run(cmd: list[str], cwd: Path | None = None) -> bool:
    print(f"  $ {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd)
    return result.returncode == 0


def check(name: str) -> bool:
    found = shutil.which(name) is not None
    status = "✓" if found else "✗"
    print(f"  {status}  {name}")
    return found


def main() -> None:
    print("\n=== College Infirmary — Setup ===\n")

    # ── Check prerequisites ───────────────────────────────────────────────────
    print("Checking prerequisites:")
    py_ok   = check("python") or check("python3")
    uv_ok   = check("uv")
    node_ok = check("node")
    npm_ok  = check("npm")

    missing = []
    if not uv_ok:
        missing.append("uv  →  https://docs.astral.sh/uv/getting-started/installation/")
    if not node_ok or not npm_ok:
        missing.append("Node.js + npm  →  https://nodejs.org/")

    if missing:
        print("\n  Some prerequisites are missing:")
        for m in missing:
            print(f"    • {m}")
        print("\nInstall them and re-run setup.py.\n")
        sys.exit(1)

    if npm_ok:
        check_npm_version()

    print()

    # ── Backend dependencies ──────────────────────────────────────────────────
    print("Installing backend dependencies (uv sync):")
    if not run(["uv", "sync"], cwd=ROOT):
        print("\n  Backend install failed. Check your Python/uv setup.\n")
        sys.exit(1)
    print()

    # ── Frontend dependencies ─────────────────────────────────────────────────
    lockfile = FRONTEND / "package-lock.json"
    npm_cmd  = ["npm", "ci"] if lockfile.exists() else ["npm", "install"]
    print(f"Installing frontend dependencies ({' '.join(npm_cmd)}):")
    if not run(npm_cmd, cwd=FRONTEND):
        print("\n  Frontend install failed.\n")
        sys.exit(1)
    print()

    # ── .env scaffold ─────────────────────────────────────────────────────────
    if not ENV_FILE.exists():
        ENV_FILE.write_text(ENV_TEMPLATE)
        print("Created .env  →  edit it and set MYSQL_PASSWORD before starting.\n")
    else:
        print(".env already exists — skipped.\n")

    # ── Done ──────────────────────────────────────────────────────────────────
    print("=== Setup complete ===\n")
    print("Next steps:")
    print("  1. Edit .env  →  set MYSQL_PASSWORD (and JWT_SECRET_KEY for production)")
    print("  2. Create the database:")
    print("       mysql -u root -p -e \"CREATE DATABASE medical_appointment_system;\"")
    print("  3. Load schema + seed data:")
    print("       mysql -u root -p medical_appointment_system < app/backend/app/db/schema.sql")
    print("       mysql -u root -p medical_appointment_system < app/backend/app/db/seed.sql")
    print("  4. Start the app:")
    print("       npm run dev")
    print("\n  Frontend  →  http://localhost:3000")
    print("  Backend   →  http://localhost:8000")
    print("  API docs  →  http://localhost:8000/docs\n")
    print("Seed accounts (password: password123):")
    accounts = [
        ("student@college.edu",       "Student"),
        ("professor@college.edu",     "Professor"),
        ("college.staff@college.edu", "College Staff"),
        ("hostel.staff@college.edu",  "Hostel Staff"),
        ("doctor@college.edu",        "Doctor"),
        ("admin@college.edu",         "Admin"),
        ("staff@college.edu",         "Staff"),
    ]
    for email, role in accounts:
        print(f"  {role:<16} {email}")
    print()


if __name__ == "__main__":
    main()
