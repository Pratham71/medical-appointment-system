# Medical Appointment System

A web-based medical appointment system for a college infirmary. It helps students book appointments, doctors manage consultations, and infirmary staff maintain medical records, prescriptions, and certificates.

## Overview

This is a DBMS-focused project with a FastAPI backend, MySQL database, raw SQL query layer, JWT authentication, role-based access, and a Next.js frontend for the MVP workflows.

## Features

- Student appointment booking
- Appointment slot listing and booking
- Student appointment history
- Doctor appointment dashboard
- Medical consultation notes
- Prescription records
- Medical certificate records
- Student report and certificate view/download actions
- Staff login landing page
- JWT-based login flow
- Role-based access for student, doctor, staff, and admin users
- Rate limiting and login brute-force protection
- Idempotent write requests
- REST API backend

## Tech Stack

- Backend: FastAPI
- Frontend: Next.js
- Database: MySQL
- Package manager: uv
- Query style: Raw SQL

## Project Structure

```text
medical-appointment-system/
|-- app/
|   |-- backend/
|   |   `-- app/
|   |       |-- api/
|   |       |   |-- routes/
|   |       |   |   |-- appointments.py
|   |       |   |   |-- auth.py
|   |       |   |   |-- certificates.py
|   |       |   |   |-- doctors.py
|   |       |   |   |-- reports.py
|   |       |   |   `-- students.py
|   |       |   |-- api_router.py
|   |       |   |-- dependencies.py
|   |       |   `-- errors.py
|   |       |-- core/
|   |       |   |-- config.py
|   |       |   |-- security.py
|   |       |   `-- security_controls.py
|   |       |-- db/
|   |       |   |-- queries/
|   |       |   |-- schema.sql
|   |       |   |-- seed.sql
|   |       |   `-- session.py
|   |       |-- repositories/
|   |       |-- schemas/
|   |       |-- services/
|   |       `-- main.py
|   `-- frontend/
|       |-- app/
|       |   |-- admin/
|       |   |-- doctors/
|       |   |-- login/
|       |   |-- staff/
|       |   `-- students/
|       |-- components/
|       |-- lib/
|       |-- next.config.mjs
|       `-- package.json
|-- docs/
|-- scripts/
|-- tests/
|-- AGENTS.md
|-- CHANGELOG.md
|-- README.md
|-- TODO.md
|-- package.json
|-- pyproject.toml
`-- uv.lock
```

## Backend Architecture

```text
routes -> services -> repositories -> queries -> db
```

- Routes handle HTTP requests and responses.
- Services contain business logic.
- Repositories coordinate database access.
- Query files contain raw SQL.
- Database files handle schema, seed data, and connection setup.

## Database Design

The database is normalized around users, roles, students, staff, appointment slots, appointments, medical notes, prescriptions, prescription items, certificate types, and medical certificates.

Key database concepts covered:

- Primary keys
- Foreign keys
- Unique constraints
- Normalization
- Joins
- Views
- Indexing
- Transactions

The selected database engine is MySQL.

## API Routes

### Auth

- `POST /auth/login`
- `POST /auth/logout`
- `GET /auth/me`

### Students

- `GET /students/dashboard`
- `GET /students/appointments`
- `GET /students/reports`
- `GET /students/certificates`

### Doctors

- `GET /doctors/dashboard`
- `GET /doctors/appointments`
- `GET /doctors/appointment/{id}`
- `GET /doctors/patients/search?q={name_or_roll_number}`
- `GET /doctors/patient-history/{student_id}`

### Appointments

- `GET /appointments/slots`
- `POST /appointments/book`
- `PATCH /appointments/{id}/cancel`
- `PATCH /appointments/{id}/complete`

### Reports

- `POST /reports/{appointment_id}/notes`
- `POST /reports/{appointment_id}/prescription`
- `GET /reports/{appointment_id}`

### Certificates

- `POST /certificates/{appointment_id}`
- `GET /certificates/student/{student_id}`

## Setup and Run

### Prerequisites

- Python 3.12+
- uv
- Node.js 18+
- MySQL 8+

### Install uv

Windows PowerShell:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

macOS/Linux:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Verify installation:

```bash
uv --version
```

### Backend Setup

```bash
uv venv
uv sync
```

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

Create and seed the database:

```sql
CREATE DATABASE medical_appointment_system;
```

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

### Run

Run backend only:

```bash
uv run uvicorn app.backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

Run backend and frontend together:

```bash
npm run dev
```

If frontend dependencies are missing on a clean checkout, install from the lockfile:

```bash
npm --prefix app/frontend ci
```

Local URLs:

```text
Backend:  http://127.0.0.1:8000
Docs:     http://127.0.0.1:8000/docs
Frontend: http://localhost:3000
```

Protected routes use:

```text
Authorization: Bearer <access_token>
```

Replay-sensitive write routes also use:

```text
Idempotency-Key: <unique-request-key>
```

## Seed Login Accounts

All seeded accounts use `password123`.

```text
student@college.edu
doctor@college.edu
admin@college.edu
staff@college.edu
```

## Current Status

The backend has FastAPI routes, MySQL schema/seed files, MySQL connection pooling, raw SQL query modules, reporting views, JWT route protection, role-based access, authenticated user context, rate limiting, idempotency, login brute-force protection, and doctor patient search.

The frontend supports login, student appointment lists, student report/certificate view and text downloads, doctor appointment details with existing prescription context, local-date doctor schedule filtering, patient lookup by name or roll number, admin safe landing, and staff safe landing.

Current known gaps include the full admin workflow, full staff workflow, printable/downloadable templates for reports, prescriptions, and certificates, and live MySQL API integration tests.
