# College Infirmary Appointment System

A full-stack web application for managing a college medical infirmary. Students and patient-equivalent staff book appointments with doctors, doctors manage availability and maintain consultation records, infirmary staff handle walk-ins and emergency responses, and administrators oversee the entire system.

**Version:** beta-1.1.0 &nbsp;|&nbsp; **Stack:** FastAPI · MySQL · Next.js 14 · TypeScript

---

## Overview

This project is a database-systems focused implementation of a real-world medical appointment platform. The backend uses raw SQL throughout no ORM with a structured four-layer architecture (routes, services, repositories, queries). The database schema is in Third Normal Form with triggers, views, and indexes applied where appropriate.

---

## System Roles

| Role          | Profile  | Capabilities                                                |
| ------------- | -------- | ----------------------------------------------------------- |
| student       | students | Book appointments, view records, submit emergency alerts    |
| professor     | students | Patient-equivalent role with identical access to student    |
| college-staff | students | Patient-equivalent, non-teaching staff                      |
| hostel-staff  | students | Patient-equivalent, resident hostel staff                   |
| doctor        | staff    | Manage availability, write notes/prescriptions/certificates |
| staff         | staff    | Walk-in booking, emergency alert management                 |
| admin         | —       | Full system oversight, user and role management             |

---

## Technology Stack

| Component          | Technology                |
| ------------------ | ------------------------- |
| Backend framework  | FastAPI (Python 3.12)     |
| Database           | MySQL 8 (InnoDB, raw SQL) |
| Package manager    | uv                        |
| Authentication     | JWT (HS256), bcrypt       |
| Frontend framework | Next.js 14 App Router     |
| Frontend language  | TypeScript                |
| Styling            | Tailwind CSS              |
| Animations         | Framer Motion             |

---

## Database Design

The schema comprises 15 tables, 5 views, 2 triggers, and 16 indexes. It is normalised to Third Normal Form throughout.

**Tables:** roles, users, students, staff, doctor_weekly_availability, doctor_availability_overrides, appointment_statuses, slot_statuses, appointment_slots, appointments, medical_notes, emergency_alerts, prescriptions, prescription_items, certificate_types, medical_certificates

**Views:** v_available_appointment_slots, v_appointment_details, v_doctor_appointment_summaries, v_student_report_summaries, v_student_certificate_summaries

**Triggers:** trg_medical_certificates_validate_insert and trg_medical_certificates_validate_update enforce that certificate issue dates cannot precede the appointment date and cannot be issued for future appointments.

**Notable constraint:** The appointments table uses a generated stored column (active_slot_id) defined as CASE WHEN status_id = 2 THEN NULL ELSE slot_id END, with a UNIQUE constraint applied to it. This prevents two active appointments from referencing the same slot while allowing multiple cancelled appointments to do so — without requiring a trigger.

---

## Backend Architecture

```
routes  ->  services  ->  repositories  ->  queries  ->  MySQL
```

- **Routes** handle HTTP request parsing, response serialisation, and RBAC enforcement via FastAPI dependencies.
- **Services** contain all business logic and raise typed domain exceptions.
- **Repositories** choose between read-only and transactional connection scopes.
- **Queries** contain all SQL as explicit parameterised strings. No ORM, no query builder.

### Security

- JWT tokens (HS256, 60-minute expiry)
- bcrypt password hashing (cost factor 12)
- Fixed-window rate limiting: 120 requests per minute per user
- Login brute-force protection: lockout after 5 failures for 300 seconds
- Idempotency enforcement on all authenticated mutating requests via SHA-256 keyed in-memory store

---

## Project Structure

```
medical-appointment-system/
├── app/
│   ├── backend/
│   │   └── app/
│   │       ├── api/
│   │       │   ├── routes/          auth, admin, appointments, doctors,
│   │       │   │                    students, staff, reports, certificates,
│   │       │   │                    emergencies
│   │       │   ├── dependencies.py
│   │       │   └── errors.py
│   │       ├── core/
│   │       │   ├── config.py
│   │       │   ├── security.py
│   │       │   └── security_controls.py
│   │       ├── db/
│   │       │   ├── queries/
│   │       │   ├── migrations/
│   │       │   ├── schema.sql
│   │       │   ├── seed.sql
│   │       │   └── session.py
│   │       ├── repositories/
│   │       ├── schemas/
│   │       ├── services/
│   │       └── main.py
│   └── frontend/
│       ├── app/
│       │   ├── admin/
│       │   ├── doctors/
│       │   ├── login/
│       │   ├── signup/
│       │   ├── staff/
│       │   └── students/
│       ├── components/
│       │   ├── layout/
│       │   └── ui/
│       └── lib/
├── tests/
├── setup.py
├── pyproject.toml
└── README.md
```

---

## API Routes

### Authentication

| Method | Path         |
| ------ | ------------ |
| POST   | /auth/signup |
| POST   | /auth/login  |
| POST   | /auth/logout |
| GET    | /auth/me     |

### Appointments

| Method | Path                        |
| ------ | --------------------------- |
| GET    | /appointments/doctors       |
| GET    | /appointments/slots         |
| GET    | /appointments/slots/all     |
| POST   | /appointments/book          |
| PATCH  | /appointments/{id}/cancel   |
| PATCH  | /appointments/{id}/complete |

### Students

| Method | Path                       |
| ------ | -------------------------- |
| GET    | /students/dashboard        |
| GET    | /students/appointments     |
| GET    | /students/reports          |
| GET    | /students/certificates     |
| GET    | /students/emergency-alerts |

### Doctors

| Method | Path                                   |
| ------ | -------------------------------------- |
| GET    | /doctors/dashboard                     |
| GET    | /doctors/appointments                  |
| GET    | /doctors/appointment/{id}              |
| GET    | /doctors/availability                  |
| PUT    | /doctors/availability/weekly/{weekday} |
| PUT    | /doctors/availability/overrides/{date} |
| DELETE | /doctors/availability/overrides/{date} |
| GET    | /doctors/patients/search               |
| GET    | /doctors/patient-history/{student_id}  |

### Reports

| Method | Path                                   |
| ------ | -------------------------------------- |
| POST   | /reports/{appointment_id}/notes        |
| POST   | /reports/{appointment_id}/prescription |
| GET    | /reports/{appointment_id}              |

### Certificates

| Method | Path                               |
| ------ | ---------------------------------- |
| POST   | /certificates/{appointment_id}     |
| GET    | /certificates/student/{student_id} |

### Emergency

| Method | Path             |
| ------ | ---------------- |
| POST   | /emergency/alert |

### Staff

| Method | Path                   |
| ------ | ---------------------- |
| GET    | /staff/dashboard       |
| GET    | /staff/appointments    |
| GET    | /staff/patients/search |
| GET    | /staff/walk-ins        |
| POST   | /staff/walk-ins/book   |

### Admin

| Method | Path                                     |
| ------ | ---------------------------------------- |
| GET    | /admin/dashboard                         |
| GET    | /admin/users                             |
| PATCH  | /admin/users/{id}/role                   |
| PATCH  | /admin/users/{id}/activate               |
| PATCH  | /admin/users/{id}/deactivate             |
| DELETE | /admin/users/{id}                        |
| GET    | /admin/appointments                      |
| GET    | /admin/students                          |
| GET    | /admin/doctors                           |
| GET    | /admin/staff                             |
| GET    | /admin/emergency-alerts                  |
| PATCH  | /admin/emergency-alerts/{id}/acknowledge |
| PATCH  | /admin/emergency-alerts/{id}/resolve     |

---

## Setup

### Prerequisites

- Python 3.12+
- uv  [installation guide](https://docs.astral.sh/uv/getting-started/installation/)
- Node.js 18+ (npm <= 11.11.1)
- MySQL 8+

### One-command setup

```bash
python setup.py
```

This installs all backend and frontend dependencies, creates the database, applies the schema, seeds initial data, and writes the `.env` file. MySQL credentials are prompted interactively.

### Manual setup (if preferred)

Install backend dependencies:

```bash
uv sync
```

Install frontend dependencies:

```bash
cd app/frontend && npm ci
```

Create a `.env` file in the project root:

```
ENVIRONMENT=development
DATABASE_PROVIDER=mysql
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=medical_appointment_system
JWT_SECRET_KEY=change-this-dev-secret
RATE_LIMIT_ENABLED=true
```

Apply schema and seed:

```bash
mysql -u root -p medical_appointment_system < app/backend/app/db/schema.sql
mysql -u root -p medical_appointment_system < app/backend/app/db/seed.sql
```

### Running the application

```bash
# Backend
uv run uvicorn app.backend.app.main:app --host 0.0.0.0 --port 8000

# Frontend (separate terminal)
cd app/frontend && npm run dev -- -H 0.0.0.0
```

| Service  | URL                        |
| -------- | -------------------------- |
| Frontend | http://localhost:3000      |
| Backend  | http://localhost:8000      |
| API Docs | http://localhost:8000/docs |

### Remote access via Tailscale

```bash
tailscale serve --bg http://localhost:3000
```

Exposes the application at `https://<machine>.<tailnet>.ts.net` with a valid TLS certificate.

---

## Seed Accounts

All accounts use the password `password123`.

| Role          | Email                     |
| ------------- | ------------------------- |
| Student       | student@college.edu       |
| Professor     | professor@college.edu     |
| College Staff | college.staff@college.edu |
| Hostel Staff  | hostel.staff@college.edu  |
| Doctor        | doctor@college.edu        |
| Staff         | staff@college.edu         |
| Admin         | admin@college.edu         |

---

## Tests

```bash
uv run pytest tests/
```
