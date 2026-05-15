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
[x] Fix admin frontend redirect loop crash
[x] Add staff login seed account, routing, and safe staff landing page
[x] Add doctor patient search by name or roll number
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
[x] Add staff login, seed account, routing, and safe staff landing page
[ ] [TOFIX] Build full staff workflow after front-desk requirements are finalized (GitHub issue #12)

Appointment APIs

[ ] Implement get doctors
[x] Implement get slots
[x] Implement book appointment
[x] Implement cancel appointment
[x] Implement mark appointment complete
[ ] [TOFIX] Prevent doctors from completing cancelled appointments and make sure cancelled appointments free their slots (GitHub issue #13)
[ ] [TOFIX] Add doctor availability management with default Monday-Sunday availability (GitHub issue #14)

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
[x] Implement patient search by name or roll number

Certificate APIs

[x] Implement create certificate
[x] Implement list student certificates
[ ] [TOFIX] Make certificates more informative with leave/custom date ranges and stronger certificate details (GitHub issue #15)

Frontend Tasks

[x] Setup Next.js frontend
[x] Add one-command full-stack dev startup
[x] Build login page
[x] Build MVP student pages
[x] Build MVP doctor pages
[x] Connect frontend to backend API

Frontend To Fix

[x] [TOFIX] Upcoming appointments tab shows no appointments
[x] [TOFIX] Add view/download support for student medical reports
[x] [TOFIX] Add view/download support for student prescriptions
[x] [TOFIX] Add view/download support for student certificates
[x] [TOFIX] Preserve doctor report and prescription context on appointment detail
[x] [TOFIX] Fix doctor's today's schedule local-date filtering
[x] [TOFIX] Replace patient history student ID input with name or roll-number lookup
[x] Add root DESIGN.md brief for report, prescription, and certificate templates
[x] [TOFIX] Create printable/downloadable templates for medical reports after templates are supplied
[x] [TOFIX] Create printable/downloadable templates for prescriptions after templates are supplied (embedded in report template)
[x] [TOFIX] Create printable/downloadable templates for medical certificates after templates are supplied
[ ] [TOFIX] Medical Leave Certificate missing leave start/end dates and duration — frontend template pre-wired, needs backend schema (GitHub issue #16)
[ ] [TOFIX] Fitness Certificate missing clearance details and certificate notes — frontend template pre-wired, needs backend schema (GitHub issue #17)
[ ] [TOFIX] Fix certificate issue_date allowed to precede appointment_date — frontend warning added, needs backend validation (GitHub issue #18)
[x] [TOFIX] Fix Reports/Certificates tab state resetting on back navigation from document view (GitHub issue #19)
[ ] [TOFIX] Build full admin dashboard and admin workflows — waiting on backend admin routes (GET /admin/dashboard, /admin/appointments, /admin/students, /admin/doctors) (GitHub issue #11)
[x] [TOFIX] Add staff dashboard or safe staff landing page after staff role decision

Testing and Documentation Tasks

[ ] Add live MySQL API integration tests
[x] Add auth and authorization tests
[x] Add security/rate-limit tests
[x] Add frontend workflow regression tests
[ ] Screenshots for report
[ ] Final documentation

Delivery Tasks

[ ] Open backend API pull request
