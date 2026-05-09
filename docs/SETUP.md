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

Database setup is deferred until the final engine is selected.

The project will use either MySQL or PostgreSQL. Do not run schema or seed files yet.

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
