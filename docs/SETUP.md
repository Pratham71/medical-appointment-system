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

4. Run backend server
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

Frontend Setup

The frontend directory is currently a scaffold. After the Next.js app is initialized, run it from:
```bash
cd app/frontend
```

Then start the frontend using the command defined in its `package.json`.

Frontend will run on:
```text
http://localhost:3000
```

Notes
- Use raw SQL only.
- Keep `.env` values correct.
- Do not run frontend package commands until the frontend project has a `package.json`.

Security Configuration Notes
- `JWT_SECRET_KEY` must be changed for production.
- Production must use a strong random JWT secret.
- Protected routes require `Authorization: Bearer <access_token>`.
- Replay-sensitive write endpoints require an `Idempotency-Key` header.
- Login and sensitive routes are rate limited.
