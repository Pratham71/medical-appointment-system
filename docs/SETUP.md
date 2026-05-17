Setup Guide

Prerequisites
- Python 3.12+
- uv installed
- Node.js 18+
- MySQL 8+

Install uv

Windows PowerShell:
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

macOS/Linux:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Check installation:
```bash
uv --version
```

Backend Setup

1. Create virtual environment
```bash
uv venv
```

2. Install dependencies
```bash
uv sync
```

3. Setup environment variables

Create a `.env` file in the project root:
```env
ENVIRONMENT=development
DATABASE_PROVIDER=mysql
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password
MYSQL_DATABASE=medical_appointment_system
JWT_SECRET_KEY=change-this-dev-secret
RATE_LIMIT_ENABLED=true
```

4. Run the full stack

From the project root:
```bash
npm run dev
```

This starts both services:
```text
Backend:  http://127.0.0.1:8000
Frontend: http://localhost:3000
```

The frontend sends local API requests through its Next.js `/api` proxy, so keep
the backend running on `http://127.0.0.1:8000` while using the app.

To run only the backend:
```bash
uv run uvicorn app.backend.app.main:app --reload
```

Backend will run on:
```text
http://127.0.0.1:8000
```

Swagger docs:
```text
http://127.0.0.1:8000/docs
```

Database Setup

Create the MySQL database:

```sql
CREATE DATABASE medical_appointment_system;
```

Apply the schema and seed data.

Windows PowerShell:
```powershell
Get-Content app\backend\app\db\schema.sql | mysql -u root -p medical_appointment_system
Get-Content app\backend\app\db\seed.sql | mysql -u root -p medical_appointment_system
```

macOS/Linux:
```bash
mysql -u root -p medical_appointment_system < app/backend/app/db/schema.sql
mysql -u root -p medical_appointment_system < app/backend/app/db/seed.sql
```

If your local database already existed before the doctor availability,
certificate context, or cancelled-slot rebooking changes, apply the
non-destructive sync migrations:

Windows PowerShell:
```powershell
Get-Content app\backend\app\db\migrations\2026_05_16_sync_live_schema.sql | mysql -u root -p medical_appointment_system
Get-Content app\backend\app\db\migrations\2026_05_17_repair_cancelled_slot_rebooking.sql | mysql -u root -p medical_appointment_system
```

macOS/Linux:
```bash
mysql -u root -p medical_appointment_system < app/backend/app/db/migrations/2026_05_16_sync_live_schema.sql
mysql -u root -p medical_appointment_system < app/backend/app/db/migrations/2026_05_17_repair_cancelled_slot_rebooking.sql
```

Frontend Setup

If frontend dependencies are missing on a clean checkout, install from the frontend lockfile:
```bash
npm --prefix app/frontend ci
```

Then use the root command:
```bash
npm run dev
```

Frontend will run on:
```text
http://localhost:3000
```

Notes
- Use raw SQL only.
- Keep `.env` values correct.
- Run `npm run dev` from the project root to start backend and frontend together.
- Frontend API calls use the local `/api` proxy to avoid browser CORS issues.
- Seed login accounts use `password123`: `student@college.edu`, `doctor@college.edu`, `admin@college.edu`, and `staff@college.edu`.

Security Configuration Notes
- `JWT_SECRET_KEY` must be changed for production.
- Production must use a strong random JWT secret.
- Protected routes require `Authorization: Bearer <access_token>`.
- Replay-sensitive write endpoints require an `Idempotency-Key` header.
- Login and sensitive routes are rate limited.
