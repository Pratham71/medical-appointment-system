Setup Guide

Prerequisites
- Python 3.12+
- uv installed
- Node.js 18+
- MySQL or PostgreSQL

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
DATABASE_URL=your_database_connection_url
ENV=dev
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

1. Create database
```sql
CREATE DATABASE medapp;
```

2. Run schema after `schema.sql` is completed
```text
app/backend/app/db/schema.sql
```

3. Run seed data if available
```text
app/backend/app/db/seed.sql
```

Use the command-line tool or database client for the selected database engine.

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
- Ensure the database is running before the backend.
- Keep `.env` values correct.
- Do not run frontend package commands until the frontend project has a `package.json`.

