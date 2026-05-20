#!/usr/bin/env bash
# ── setup.sh ──────────────────────────────────────────────────────────────────
# One-command Docker setup for the College Infirmary Appointment System.
# Run once after cloning:  bash setup.sh
#
# What it does:
#   1. Checks that Docker and Docker Compose are installed
#   2. Copies .env.example → .env (if .env doesn't exist yet)
#   3. Generates a secure random JWT_SECRET_KEY and writes it into .env
#   4. Prompts once for a MySQL root password and writes it into .env
#   5. Runs docker compose up --build -d
# ─────────────────────────────────────────────────────────────────────────────

set -euo pipefail

# ── Colours ───────────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
ok()   { echo -e "${GREEN}  ✓  $*${NC}"; }
warn() { echo -e "${YELLOW}  !  $*${NC}"; }
die()  { echo -e "${RED}  ✗  $*${NC}"; exit 1; }

echo ""
echo "=== College Infirmary — Docker Setup ==="
echo ""

# ── 1. Prerequisite checks ────────────────────────────────────────────────────
echo "Checking prerequisites:"

command -v docker  >/dev/null 2>&1 || die "Docker is not installed. Get it at https://docs.docker.com/get-docker/"
ok "docker $(docker --version | awk '{print $3}' | tr -d ',')"

# Support both 'docker compose' (v2 plugin) and 'docker-compose' (v1 standalone)
if docker compose version >/dev/null 2>&1; then
    COMPOSE="docker compose"
elif command -v docker-compose >/dev/null 2>&1; then
    COMPOSE="docker-compose"
else
    die "Docker Compose is not installed. Get it at https://docs.docker.com/compose/install/"
fi
ok "docker compose ($($COMPOSE version --short 2>/dev/null || echo 'v1'))"

echo ""

# ── 2. Create .env from template ──────────────────────────────────────────────
if [ -f ".env" ]; then
    warn ".env already exists — skipping copy from .env.example"
else
    cp .env.example .env
    ok "Created .env from .env.example"
fi

# ── 3. Generate JWT secret ────────────────────────────────────────────────────
# Only generate if the key is currently empty or still the placeholder
current_jwt=$(grep "^JWT_SECRET_KEY=" .env | cut -d'=' -f2 | tr -d ' ')
if [ -z "$current_jwt" ] || [ "$current_jwt" = "change-this-dev-secret" ]; then
    # openssl is available on macOS and most Linux distros
    if command -v openssl >/dev/null 2>&1; then
        jwt_secret=$(openssl rand -hex 32)
    else
        # fallback: /dev/urandom via python (always available if Python is installed)
        jwt_secret=$(python3 -c "import secrets; print(secrets.token_hex(32))")
    fi
    # Replace the JWT_SECRET_KEY line in-place (works on both macOS and Linux)
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "s|^JWT_SECRET_KEY=.*|JWT_SECRET_KEY=${jwt_secret}|" .env
    else
        sed -i "s|^JWT_SECRET_KEY=.*|JWT_SECRET_KEY=${jwt_secret}|" .env
    fi
    ok "Generated JWT_SECRET_KEY"
else
    ok "JWT_SECRET_KEY already set — keeping existing value"
fi

# ── 4. MySQL password ─────────────────────────────────────────────────────────
current_pw=$(grep "^MYSQL_PASSWORD=" .env | cut -d'=' -f2 | tr -d ' ')
if [ -z "$current_pw" ]; then
    echo "  Enter a MySQL root password for the local Docker database."
    echo "  This is only used inside Docker — any value works for local dev."
    read -rsp "  Password: " mysql_password
    echo ""
    if [ -z "$mysql_password" ]; then
        die "MySQL password cannot be empty."
    fi
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "s|^MYSQL_PASSWORD=.*|MYSQL_PASSWORD=${mysql_password}|" .env
    else
        sed -i "s|^MYSQL_PASSWORD=.*|MYSQL_PASSWORD=${mysql_password}|" .env
    fi
    ok "MYSQL_PASSWORD written to .env"
else
    ok "MYSQL_PASSWORD already set — keeping existing value"
fi

echo ""

# ── 5. Start containers ───────────────────────────────────────────────────────
echo "Building and starting containers (this takes a few minutes the first time):"
echo ""
$COMPOSE up --build -d

echo ""
ok "All containers are up"
echo ""
echo "=== Setup complete ==="
echo ""
echo "  Frontend  →  http://localhost:3000"
echo "  Backend   →  http://localhost:8000"
echo "  API docs  →  http://localhost:8000/docs"
echo ""
echo "Seed accounts (password: password123):"
printf "  %-16s %s\n" "Student"        "student@college.edu"
printf "  %-16s %s\n" "Professor"      "professor@college.edu"
printf "  %-16s %s\n" "College Staff"  "college.staff@college.edu"
printf "  %-16s %s\n" "Hostel Staff"   "hostel.staff@college.edu"
printf "  %-16s %s\n" "Doctor"         "doctor@college.edu"
printf "  %-16s %s\n" "Staff"          "staff@college.edu"
printf "  %-16s %s\n" "Admin"          "admin@college.edu"
echo ""
echo "To stop:              docker compose down"
echo "To reset the database: docker compose down -v  (deletes all data)"
echo ""
