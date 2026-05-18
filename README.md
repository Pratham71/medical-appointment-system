# Medical Appointment System

A web-based medical appointment system for a college infirmary. It helps students and professors book appointments, doctors manage consultations, and infirmary staff maintain medical records, prescriptions, and certificates.

## Overview

This is a DBMS-focused project with a FastAPI backend, MySQL database, raw SQL query layer, JWT authentication, role-based access, and a Next.js frontend for the MVP workflows.

## Features

- Student appointment booking
- Professor appointment access using the same patient workflow as students
- Appointment slot listing and booking
- Student appointment history
- Admin backend APIs for dashboard metrics, user role assignment, user activation/deactivation, directories, appointments, and emergency alerts
- Doctor appointment dashboard
- Doctor weekly availability and date override management
- Medical consultation notes
- Prescription records
- Medical certificate records
- Student report and certificate view/download actions
- Structured emergency alerts with reason, location, optional contact number, acknowledgement, resolution, and student-visible status
- Staff dashboard workflow for emergency alerts and existing-patient walk-in booking
- College-staff and hostel-staff patient access using the student workflow
- Best-effort SMTP email notifications for appointment and document updates
- JWT-based login flow
- Role-based access for student, professor, college-staff, hostel-staff, doctor, staff, and admin users
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
|   |       |   |   |-- admin.py
|   |       |   |   |-- appointments.py
|   |       |   |   |-- auth.py
|   |       |   |   |-- certificates.py
|   |       |   |   |-- doctors.py
|   |       |   |   |-- reports.py
|   |       |   |   |-- staff.py
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

The database is normalized around users, roles, students, staff, doctor availability rules, appointment slots, appointments, medical notes, prescriptions, prescription items, certificate types, and medical certificates.

Key database concepts covered:

- Primary keys
- Foreign keys
- Unique constraints
- Normalization
- Joins
- Views
- Indexing
- Transactions
- Triggers

The selected database engine is MySQL.

## API Routes

### Auth

- `POST /auth/signup`
- `POST /auth/login`
- `POST /auth/logout`
- `GET /auth/me`

### Admin

- `GET /admin/dashboard`
- `GET /admin/users`
- `PATCH /admin/users/{user_id}/role`
- `PATCH /admin/users/{user_id}/deactivate`
- `PATCH /admin/users/{user_id}/activate`
- `DELETE /admin/users/{user_id}`
- `GET /admin/appointments`
- `GET /admin/students`
- `GET /admin/doctors`
- `GET /admin/staff`
- `GET /admin/emergency-alerts`
- `PATCH /admin/emergency-alerts/{alert_id}/acknowledge`
- `PATCH /admin/emergency-alerts/{alert_id}/resolve`

### Staff

- `GET /staff/dashboard`
- `GET /staff/appointments`
- `GET /staff/patients/search`
- `GET /staff/walk-ins`
- `POST /staff/walk-ins/book`

### Students

- `GET /students/dashboard`
- `GET /students/appointments`
- `GET /students/reports`
- `GET /students/certificates`
- `GET /students/emergency-alerts`

### Doctors

- `GET /doctors/dashboard`
- `GET /doctors/appointments`
- `GET /doctors/availability`
- `PUT /doctors/availability/weekly/{weekday}`
- `PUT /doctors/availability/overrides/{override_date}`
- `DELETE /doctors/availability/overrides/{override_date}`
- `GET /doctors/appointment/{id}`
- `GET /doctors/patients/search?q={name_or_roll_number}`
- `GET /doctors/patient-history/{student_id}`

### Appointments

- `GET /appointments/slots`
- `POST /appointments/book`
- `PATCH /appointments/{id}/cancel`
- `PATCH /appointments/{id}/complete`

### Emergency

- `POST /emergency/alert`

### Reports

- `POST /reports/{appointment_id}/notes`
- `POST /reports/{appointment_id}/prescription`
- `GET /reports/{appointment_id}`

### Certificates

- `POST /certificates/{appointment_id}`
- `GET /certificates/student/{student_id}`

Certificates include issuing doctor, appointment reference, appointment date,
medical context, optional leave date range, and optional fitness clearance notes.

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
EMAIL_NOTIFICATIONS_ENABLED=false
SMTP_HOST=
SMTP_PORT=587
SMTP_FROM_EMAIL=
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

If your local database existed before emergency alert context/lifecycle support, apply:

```powershell
Get-Content app\backend\app\db\migrations\2026_05_17_update_emergency_alerts_context_lifecycle.sql | mysql -u root -p medical_appointment_system
```

```bash
mysql -u root -p medical_appointment_system < app/backend/app/db/migrations/2026_05_17_update_emergency_alerts_context_lifecycle.sql
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
professor@college.edu
college.staff@college.edu
hostel.staff@college.edu
doctor@college.edu
admin@college.edu
staff@college.edu
```

## Current Status

The backend has FastAPI routes, MySQL schema/seed files, MySQL connection pooling, raw SQL query modules, reporting views, JWT route protection, role-based access, authenticated user context, signup defaulting to student/patient accounts, professor/college-staff/hostel-staff patient-equivalent role support, admin role assignment and user status management, staff appointment oversight, staff existing-patient walk-in booking, structured emergency alert lifecycle management, best-effort email notifications, rate limiting, idempotency, login brute-force protection, doctor patient search, and doctor availability management.

The frontend supports login, student appointment lists, student report/certificate view and text downloads, emergency alert submission/status review, doctor appointment details with existing prescription context, local-date doctor schedule filtering, patient lookup by name or roll number, doctor availability management, admin user role/status actions, admin emergency alert acknowledgement/resolution, admin safe landing, staff emergency alert review, and staff existing-patient walk-in booking.

Current known gaps include forgot password/password reset as future scope, active user presence tracking, printable/downloadable templates for reports, prescriptions, and certificates, and live MySQL API integration tests.
