# Medical Appointment System

A web-based medical appointment system for a college infirmary. It helps students book appointments, doctors manage consultations, and the infirmary maintain medical records, prescriptions, and certificates in an organized way.

## Overview

The project is built as a DBMS-focused application with a simple frontend and a structured backend. The main focus is clean database design, normalized tables, proper relationships, and a maintainable API layer.

## Features

- Student appointment booking
- Appointment slot management
- Student appointment history
- Doctor appointment dashboard
- Medical consultation notes
- Prescription records
- Medical certificate records
- Basic login flow
- REST API backend
- Simple web interface

## Tech Stack

- Backend: FastAPI
- Frontend: Next.js
- Database: MySQL/PostgreSQL
- Package Manager: uv
- Query Style: Raw SQL

## Project Structure

```text
medical-appointment-system/
├── app/
│   ├── backend/
│   │   └── app/
│   │       ├── api/
│   │       │   ├── routes/
│   │       │   │   ├── appointments.py
│   │       │   │   ├── auth.py
│   │       │   │   ├── certificates.py
│   │       │   │   ├── doctors.py
│   │       │   │   ├── reports.py
│   │       │   │   └── students.py
│   │       │   └── api_router.py
│   │       ├── core/
│   │       │   ├── config.py
│   │       │   └── security.py
│   │       ├── db/
│   │       │   ├── queries/
│   │       │   │   ├── appointment_queries.py
│   │       │   │   ├── auth_queries.py
│   │       │   │   ├── certificate_queries.py
│   │       │   │   ├── doctor_queries.py
│   │       │   │   ├── report_queries.py
│   │       │   │   └── student_queries.py
│   │       │   ├── schema.sql
│   │       │   ├── seed.sql
│   │       │   └── session.py
│   │       ├── repositories/
│   │       │   ├── appointment_repo.py
│   │       │   ├── certificate_repo.py
│   │       │   ├── doctor_repo.py
│   │       │   ├── report_repo.py
│   │       │   ├── student_repo.py
│   │       │   └── user_repo.py
│   │       ├── schemas/
│   │       │   ├── appointment.py
│   │       │   ├── auth.py
│   │       │   ├── certificate.py
│   │       │   ├── doctor.py
│   │       │   ├── report.py
│   │       │   └── student.py
│   │       ├── services/
│   │       │   ├── appointment_service.py
│   │       │   ├── auth_service.py
│   │       │   ├── certificate_service.py
│   │       │   ├── doctor_service.py
│   │       │   ├── report_service.py
│   │       │   └── student_service.py
│   │       └── main.py
│   └── frontend/
│       ├── app/
│       │   ├── doctors/
│       │   ├── login/
│       │   └── students/
│       ├── components/
│       │   ├── cards/
│       │   ├── forms/
│       │   ├── layout/
│       │   └── tables/
│       └── lib/
├── docs/
│   ├── API_NOTES.md
│   ├── DB_NOTES.md
│   ├── ERD_NOTES.md
│   ├── PROJECT_CONTEXT.md
│   ├── REPORT_NOTES.md
│   └── SETUP.md
├── changelog/
│   ├── archive/
│   └── branches/
├── AGENTS.md
├── CHANGELOG.md
├── README.md
├── TODO.md
├── pyproject.toml
└── uv.lock
```

## Backend Architecture

The backend follows a layered structure:

```text
routes -> services -> repositories -> queries -> db
```

- Routes handle HTTP requests and responses.
- Services contain business logic.
- Repositories coordinate database access.
- Query files contain raw SQL.
- Database files handle schema, seed data, and connection setup.

## Database Design

The database is planned around normalized tables for users, students, staff, appointments, slots, notes, prescriptions, and certificates.

Key database concepts covered:

- Primary keys
- Foreign keys
- Unique constraints
- Normalization
- Joins
- Indexing
- Transactions

The final database engine will be either MySQL or PostgreSQL.

## Planned API Routes

### Auth

- `POST /auth/login`
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

Follow these steps to set up the project locally.

### Prerequisites

- Python 3.12+
- uv
- Node.js 18+
- MySQL or PostgreSQL

### Install uv

Install `uv` using the official installer.

Windows PowerShell:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

macOS/Linux:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Check that it installed correctly:

```bash
uv --version
```

Official uv installation docs: https://docs.astral.sh/uv/getting-started/installation/

### 1. Clone the Repository

```bash
git clone <repository-url>
cd medical-appointment-system
```

### 2. Backend Setup

Create the Python virtual environment:

```bash
uv venv
```

Install backend dependencies:

```bash
uv sync
```

Create a `.env` file in the project root:

```env
DATABASE_URL=your_database_connection_url
ENV=dev
```

### 3. Database Setup

Create a database named `medapp` in either MySQL or PostgreSQL.

After the schema file is completed, execute this file in the selected database:

```text
app/backend/app/db/schema.sql
```

If seed data is available, execute:

```text
app/backend/app/db/seed.sql
```

Use the command-line tool or database client for whichever database engine is selected.

### 4. Run the Backend

```bash
uv run uvicorn app.backend.app.main:app --reload
```

Backend URL:

```text
http://127.0.0.1:8000
```

API docs:

```text
http://127.0.0.1:8000/docs
```

### 5. Frontend Setup

Go to the frontend directory:

```bash
cd app/frontend
```

Install frontend dependencies:

```bash
npm install
```

Run the frontend:

```bash
npm run dev
```

Frontend URL:

```text
http://localhost:3000
```

### 6. Development Flow

- Start the database server.
- Run the backend from the project root.
- Run the frontend from `app/frontend`.
- Open the frontend at `http://localhost:3000`.
- Use the API docs at `http://127.0.0.1:8000/docs` while testing backend routes.

## Documentation

Additional project notes are available in the `docs/` directory:

- `PROJECT_CONTEXT.md`
- `DB_NOTES.md`
- `API_NOTES.md`
- `SETUP.md`
- `REPORT_NOTES.md`
- `ERD_NOTES.md`

## Current Status

The project structure and documentation are currently set up. Backend APIs, database schema, and frontend pages are under development.
