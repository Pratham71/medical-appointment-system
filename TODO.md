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
[x] Add non-destructive MySQL sync migration for older local databases after availability/certificate schema changes
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
[ ] [FUTURE] Forgot password / password reset flow — frontend button exists but non-functional, needs backend reset token API (GitHub issue #23)
[ ] [FUTURE] Revisit completed-appointment edit override only if approved — current MVP intentionally locks completed appointments from doctor edits; any future override needs admin approval + audit trail (GitHub issue #24)

Google OAuth Tasks — Future Scope (GitHub issue #21)

[ ] [FUTURE] [BACKEND] Add Google OAuth2 provider — verify @dubai.bits-pilani.ac.in domain, reject all others
[ ] [FUTURE] [BACKEND] Extract college ID from email prefix (f20xx0XXX format) and auto-register student on first login
[ ] [FUTURE] [BACKEND] Update users/students table schema and seed data to use college email format
[ ] [FUTURE] [BACKEND] Issue JWT on successful OAuth callback, link existing accounts by email
[ ] [FUTURE] [FRONTEND] Replace login form with Sign in with Google button
[ ] [FUTURE] [FRONTEND] Handle OAuth redirect and callback route, store JWT same as current login
[ ] [FUTURE] [FRONTEND] Show error for non-college Google accounts

Appointment APIs

[x] Implement get doctors
[x] Implement get slots
[x] Implement book appointment
[x] Implement cancel appointment
[x] Implement mark appointment complete
[x] [TOFIX] Prevent doctors from completing cancelled appointments and make sure cancelled appointments free their slots (GitHub issue #13)
[x] [TOFIX] Prevent editing notes, prescriptions, or certificates after an appointment is completed or cancelled
[x] [TOFIX] Hide elapsed same-day appointment slots using local time and reject direct booking attempts for elapsed slots
[x] [TOFIX] Add doctor availability management with default Monday-Saturday availability and Sunday unavailable by default (GitHub issue #14)
[x] [TOFIX] Doctor unavailable on Sundays by default with manual override — weekly day toggles + date-level override table, doctor settings page; slot generation respects availability rules (GitHub issue #28)
[x] [TOFIX] Add a separate doctor availability tab/page where doctors can manage weekly availability and date-level overrides (GitHub issue #29)
[x] [TOFIX] Generate future weekday appointment slots from doctor availability rules so doctors keep showing as bookable after seeded dates, except Sundays by default
[x] [TOFIX] [BACKEND] Auto-cancel bookings when doctor sets unavailability override — on override save, cancel booked appointments, free their slots, store cancellation_reason, and show reschedule/walk-in options to students (GitHub issue #30)
[x] [TOFIX] Show doctor unavailability reason on booking page when selected date is blocked — greyed card with amber "Unavailable — <reason>" badge, disabled Select button (GitHub issue #31)
[x] [TOFIX] [BACKEND] Add GET /appointments/doctors?for_date= endpoint returning all doctors with availability status and override reason for a given date — required for frontend to show unavailable doctors on booking page instead of them disappearing (the v_available_appointment_slots view filters them out at DB level)
[x] [TOFIX] Show doctor specialization (e.g. General Physician) on booking doctor cards — already in staff table, now exposed in API response and rendered in frontend (GitHub issue #31)
[x] [TOFIX] When a doctor becomes unavailable for a date with existing booked appointments, cancel those appointments for that day and provide a normal-checkup or reschedule path

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
[x] [TOFIX] Make certificates more informative with leave/custom date ranges and stronger certificate details (GitHub issue #15)

Frontend Tasks

[x] Setup Next.js frontend
[x] Add custom error pages — 404, 500, 503 (service unavailable), global error fallback
[x] Auto-logout on invalid/expired bearer token (401)
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
[x] [TOFIX] Medical Leave Certificate missing leave start/end dates and duration — frontend template pre-wired, needs backend schema (GitHub issue #16)
[x] [TOFIX] Fitness Certificate missing clearance details and certificate notes — frontend template pre-wired, needs backend schema (GitHub issue #17)
[x] [TOFIX] Fix certificate issue_date allowed to precede appointment_date — frontend warning added, needs backend validation (GitHub issue #18)
[x] [TOFIX] Fix Reports/Certificates tab state resetting on back navigation from document view (GitHub issue #19)
[x] [TOFIX] Doctor patient history — show search result name or "No student found", accordion-style history expansion (GitHub issue #20)
[x] [TOFIX] Add View button on booked appointments + student appointment detail page /students/appointments/[id] (GitHub issue #25)
[x] [TOFIX] Booking reason not showing on doctor appointment detail and patient history pages — now always shown with "Not provided" fallback
[ ] [FUTURE] User profile + onboarding flow — hosteler status, room number, hostel block, local + international contact numbers, emergency contact; multi-step onboarding on first login, profile page in sidebar; backend needs student_profiles table (GitHub issue #27)
[x] [TOFIX] Emergency button — quick-dial infirmary/hostel/security via tel: links plus automated alert POST /emergency/alert stored in MySQL for staff follow-up (GitHub issue #26)
[ ] [FUTURE] Add external emergency notification provider for email/SMS/push delivery after provider choice is finalized
[ ] [TOFIX] Build full admin dashboard and admin workflows — blocked on backend admin routes (GET /admin/dashboard, /admin/appointments, /admin/students, /admin/doctors) (GitHub issue #11)
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
