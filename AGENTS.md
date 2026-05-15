Medical Appointment System - Contributor Instructions

Project Goal
Build a clean DBMS-focused medical appointment system for a college infirmary with a simple UI and strong backend/database design.

Core Rules

- Follow layered architecture strictly:
  routes -> services -> repositories -> queries -> db
- Never write SQL in routes or services.
- All SQL must be inside app/backend/app/db/queries/.
- Repositories must call query functions only.
- Do not over-engineer.
- Prefer simple, working solutions.

Project Structure

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

Coding Guidelines

- Use raw SQL only.
- Use parameterized queries.
- Avoid SELECT *.
- Use one function per query.
- Keep queries reusable.
- Keep routes thin and readable.
- Put business logic in services.
- Keep database access coordination in repositories.
- Protected route identity must come from authenticated JWT context, not from caller-supplied `student_id` or `staff_id` query parameters.
- Keep authorization checks in route dependencies/services; keep SQL in query modules only.
- Use idempotency keys for replay-sensitive write requests where implemented.

Database Rules

- Maintain 3NF normalization.
- Use foreign keys properly.
- Add indexes where needed.
- Prevent double booking using UNIQUE(slot_id).
- Use transactions for appointment booking.
- MySQL is the selected database provider for the MVP.

ERD Rule

- Do not generate ER diagrams yet.
- The final ERD will be created after the database choice and schema finalization.

Workflow

- Check TODO.md before coding.
- Update TODO.md after completing tasks.
- Add an entry to CHANGELOG.md after changes.
- Update docs if structure, setup, database design, or APIs change.
- Keep README.md aligned with the current project status.

Changelog Rules

- Format: [DATE] [TYPE] [AUTHOR] [BRANCH] - Description
- Keep only recent entries, roughly 7 days or 50 entries.
- Move older entries to changelog/archive/.

General

- Keep code simple and readable.
- Avoid unnecessary dependencies.
- Focus on completing the MVP first.
- Do not claim planned features are implemented until the code exists.
