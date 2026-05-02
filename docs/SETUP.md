Setup Guide

Prerequisites
- Python 3.12+
- Node.js (18+)
- PostgreSQL installed and running
- uv installed (for Python package management)

Backend Setup

1. Create virtual environment
uv venv

2. Install dependencies
uv add fastapi uvicorn asyncpg python-dotenv

3. Setup environment variables
Create .env file in root:

DATABASE_URL=postgresql://user:password@localhost:5432/medapp
ENV=dev

4. Run backend server
uvicorn app.backend.app.main:app --reload

Backend will run on:
http://127.0.0.1:8000

Swagger docs:
http://127.0.0.1:8000/docs

Database Setup

1. Create database in PostgreSQL
CREATE DATABASE medapp;

2. Run schema.sql
psql -U user -d medapp -f app/backend/app/db/schema.sql

3. (Optional) Run seed.sql
psql -U user -d medapp -f app/backend/app/db/seed.sql

Frontend Setup

1. Navigate to frontend
cd app/frontend

2. Install dependencies
npm install

3. Run frontend
npm run dev

Frontend runs on:
http://localhost:3000

Notes
- Use raw SQL only
- Ensure DB is running before backend
- Keep .env values correct
