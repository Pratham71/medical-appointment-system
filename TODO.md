Project Tasks

Rules
- Keep this file updated
- Mark completed tasks with [x]
- Add owner initials if needed
- Example: [ ] [PR] Setup DB schema

Completed Tasks

[x] Setup FastAPI project
[x] Setup uv environment
[x] Register MVP API route skeletons
[x] Add API schema, service, and repository skeletons
[x] Add health endpoint
[x] Add stateless logout endpoint
[x] Add API surface tests
[x] Add MySQL database layer tests
[x] Run live MySQL route smoke test locally
[x] Run live JWT/RBAC/idempotency smoke test locally
[x] Add project README
[x] Update contributor instructions
[x] Update setup docs for current backend/frontend state
[x] Remove frontend placeholder files
[x] Push feat/backend/api branch

Database Tasks

[x] Decide database provider: MySQL
[x] Setup MySQL provider configuration
[x] Setup MySQL connection pooling
[x] Create normalized MySQL core tables
[x] Insert MySQL dummy seed data
[x] Add MySQL indexes
[x] Add MySQL raw SQL query modules
[x] Add MySQL views for dashboard and report queries
[x] Run MySQL EXPLAIN query analysis on a live database

Auth and Security Tasks

[x] Implement DB-backed login
[x] Protect API routes with JWT authentication
[x] Add role-based access for student, doctor, and admin/staff routes
[x] Replace temporary `student_id` and `staff_id` query parameters with authenticated user context
[x] Implement security features like idempotency, rate limiting, and replay-safe write requests
[x] Require production-safe JWT secret configuration
[x] Add brute-force protection for login

Appointment APIs

[ ] Implement get doctors
[x] Implement get slots
[x] Implement book appointment
[x] Implement cancel appointment
[x] Implement mark appointment complete

Student APIs

[x] Implement dashboard
[x] Implement my appointments
[x] Implement reports
[x] Implement certificates

Doctor APIs

[x] Implement view appointments
[x] Implement appointment details
[x] Implement add notes
[x] Implement add prescriptions
[x] Implement patient history

Certificate APIs

[x] Implement create certificate
[x] Implement list student certificates

Frontend Tasks

[x] Setup Next.js frontend
[x] Add one-command full-stack dev startup
[x] Build login page
[ ] Build student pages
[ ] Build doctor pages
[x] Connect frontend to backend API

Frontend To Fix

[ ] [TOFIX] Upcoming appointments tab shows no appointments
[ ] [TOFIX] Add view/download support for student medical reports
[ ] [TOFIX] Add view/download support for student prescriptions
[ ] [TOFIX] Add view/download support for student certificates
[ ] [TOFIX] Create printable/downloadable templates for medical reports
[ ] [TOFIX] Create printable/downloadable templates for prescriptions
[ ] [TOFIX] Create printable/downloadable templates for medical certificates

Testing and Documentation Tasks

[ ] Add live MySQL API integration tests
[x] Add auth and authorization tests
[x] Add security/rate-limit tests
[ ] Screenshots for report
[ ] Final documentation

Delivery Tasks

[ ] Open backend API pull request
