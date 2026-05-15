Database Notes

Database Choice
- MySQL is selected for the MVP database.
- Schema and setup instructions now target MySQL 8+.

Current Focus
- Table design
- Relationships
- Constraints
- Queries
- Views for common dashboard and report reads
- Authenticated user context for student and staff access
- Staff login seed account and non-doctor staff row
- Login brute-force protection
- Idempotency/replay-safe write request support
- Rate limiting support

ERD
- Do NOT create ER diagram yet
- Will be created after the MySQL schema is reviewed

Design Rules
- Follow 3NF normalization
- Avoid redundancy
- Use proper primary keys
- Use proper foreign keys
- Keep schema clean and minimal for MVP

Core Tables (MVP)
- roles
- users
- students
- staff
- appointment_statuses
- slot_statuses
- appointment_slots
- appointments
- medical_notes
- prescriptions
- prescription_items
- certificate_types
- medical_certificates

Future Tables
- appointment_events
- notifications
- audit_logs
- vitals
- staff_schedule
- slot_exceptions

Query Organization (IMPORTANT)

All SQL queries must be stored in:
app/backend/app/db/queries/

Rules:
- No SQL in routes
- No SQL in services
- Repositories must call query functions
- Use parameterized queries only
- One function per query
- Group queries by feature (appointments, users, etc.)

Example Flow:
Route → Service → Repository → Query → DB

Constraints
- Unique email in users
- Unique slot_id in appointments (prevents double booking)
- Foreign keys across all related tables
- Add CHECK constraints where needed

Indexes
- users(role_id)
- students(user_id)
- staff(user_id)
- appointments(student_id)
- appointments(status_id)
- appointment_slots(staff_id, slot_date)
- appointment_slots(slot_date, status_id)
- medical_notes(appointment_id)
- prescriptions(appointment_id)
- prescription_items(prescription_id)
- medical_certificates(certificate_type_id)

Views
- v_available_appointment_slots
- v_appointment_details
- v_doctor_appointment_summaries
- v_student_report_summaries
- v_student_certificate_summaries

Triggers
- Not required for the MVP right now.
- Double booking is handled with UNIQUE(slot_id) and appointment booking transactions.
- Add triggers later only if the project needs audit logging or automatic history tables.

Transactions
- Use transaction when booking appointment:
  1. Check slot availability
  2. Update slot status
  3. Insert appointment
  4. Commit

DBMS Concepts to Demonstrate
- Normalization (3NF)
- Primary keys
- Foreign keys
- Unique constraints
- Indexing
- Joins
- Views
- Transactions
- MySQL EXPLAIN query analysis
- Auth-backed access control
- Idempotent transaction handling

Notes
- Avoid SELECT *
- Fetch only required columns
- Keep queries efficient and readable
- Final optimization will be done after testing against the live MySQL database
