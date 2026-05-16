Changelog

Purpose
Track who changed what so the team stays updated.

Entry Format
[YYYY-MM-DD] [TYPE] [AUTHOR/INITIALS] [BRANCH] - Description

Types
[INIT]    Initial setup
[ADD]     Added new feature/file
[UPDATE]  Updated existing code/docs
[FIX]     Bug fix
[DB]      Database/schema/query change
[API]     API change
[UI]      Frontend/UI change
[DOCS]    Documentation change
[TEST]    Testing change
[REFACTOR] Code cleanup/restructure

Examples
[2026-05-02] [INIT] [PR] [main] - Created initial project structure
[2026-05-02] [DB] [AK] [db-schema] - Added appointments and slots schema
[2026-05-02] [API] [RS] [backend-auth] - Added basic login endpoint
[2026-05-02] [UI] [SM] [frontend-student] - Added student dashboard page

Changelog Size Rule
- Keep only recent/current sprint changes in this file
- If this file gets too long, move older entries into archive files
- Recommended limit: keep max 7 days OR max 50 entries here
- Archive older entries under changelog/archive/

Archive Format
changelog/archive/YYYY-MM-DD_to_YYYY-MM-DD.md

Branch-Based Option
If the team wants branch-specific changelogs, use:
changelog/branches/main.md
changelog/branches/backend.md
changelog/branches/frontend.md
changelog/branches/db.md

Current Entries

[2026-05-16] [API] [TEAM] [fix/issues-26-30-31] - Added GET /appointments/doctors?for_date= for issue #31, returning every doctor with specialization, availability status, slot count, and override unavailability note for the selected date
[2026-05-16] [FIX] [TEAM] [fix/issues-26-30-31] - Fixed future booking dates after seeded slots by lazily generating 30-minute appointment slots from doctor weekly availability; future weekdays now stay bookable and Sundays remain unavailable by default
[2026-05-16] [DB] [TEAM] [fix/issues-26-30-31] - Added cancellation_reason to appointments with a non-destructive MySQL migration and refreshed appointment detail view for issue #30
[2026-05-16] [API] [TEAM] [fix/issues-26-30-31] - Auto-cancel booked appointments when a doctor saves an unavailable date override, releasing affected slots and storing an infirmary cancellation reason
[2026-05-16] [UI] [TEAM] [fix/issues-26-30-31] - Student appointment detail now shows doctor-cancelled appointments with the cancellation reason, Reschedule action, and walk-in guidance
[2026-05-16] [UI] [TEAM] [fix/issues-26-30-31] - Updated student booking page for issue #31 to fetch all doctors for the selected date and render unavailable doctors as disabled grey cards with amber reason badges instead of hiding them
[2026-05-16] [TEST] [TEAM] [fix/issues-26-30-31] - Added regression coverage for the doctor availability status API route, service/query contract, OpenAPI surface, and booking-page frontend wiring

[2026-05-16] [FIX] [TEAM] [fix/backend-appointment-certificates] - Fixed doctor cards disappearing on booking page when unavailable — now shows all doctors with 0 slots as greyed-out cards with strikethrough slot count and amber "Unavailable today" badge
[2026-05-16] [UI] [TEAM] [fix/backend-appointment-certificates] - Add emergency quick-dial button — floating pulsing red button in student shell, modal with tel: links for infirmary, hostel warden, campus security; shows 999 as last resort
[2026-05-16] [FIX] [TEAM] [fix/backend-appointment-certificates] - Doctor appointment detail and patient history now always show booking reason with "Not provided" fallback instead of hiding when null

[2026-05-16] [FIX] [TEAM] [fix/backend-appointment-certificates] - Added non-destructive MySQL sync migration to repair older local databases where doctor availability tables and certificate summary view columns were missing, causing availability/certificate API 500s
[2026-05-16] [DOCS] [TEAM] [fix/backend-appointment-certificates] - Documented the live schema sync migration command in setup and DB notes
[2026-05-16] [TEST] [TEAM] [fix/backend-appointment-certificates] - Added regression coverage for the live schema migration contents

[2026-05-16] [DB] [TEAM] [fix/backend-appointment-certificates] - Added doctor availability schema (#14/#28): weekly availability rules, date-level overrides, indexes, seeded Monday-Saturday availability, and Sunday unavailable by default
[2026-05-16] [API] [TEAM] [fix/backend-appointment-certificates] - Added doctor availability APIs (#14/#28): GET /doctors/availability, PUT weekly rules, PUT date overrides, and DELETE date overrides using authenticated doctor context
[2026-05-16] [UI] [TEAM] [fix/backend-appointment-certificates] - Added doctor Availability page and sidebar tab (#29) for weekly toggles and date-level override management
[2026-05-16] [DOCS] [TEAM] [fix/backend-appointment-certificates] - Marked forgot password/password reset as future scope and updated README/API/DB/ERD notes for doctor availability
[2026-05-16] [TEST] [TEAM] [fix/backend-appointment-certificates] - Added regression coverage for doctor availability defaults, available-slot filtering, API route surface, authenticated doctor context, and frontend availability wiring

[2026-05-16] [DOCS] [TEAM] [fix/backend-appointment-certificates] - Added GitHub issue #29 and TODO tracking for a doctor availability tab with Sunday unavailable by default and manual override workflow
[2026-05-16] [FIX] [TEAM] [fix/backend-appointment-certificates] - Locked completed/cancelled appointments from further doctor edits across medical notes, prescriptions, and certificates; doctor detail form now renders read-only/disabled for locked appointments
[2026-05-16] [FIX] [TEAM] [fix/backend-appointment-certificates] - Filtered available appointment slots by exact selected date and local current time so elapsed same-day slots are not shown or bookable
[2026-05-16] [FIX] [TEAM] [fix/backend-appointment-certificates] - Fixed cancelled appointment lifecycle (#13): backend rejects cancelled-to-completed transitions, cancelling releases the slot, and schema now uses generated active_slot_id uniqueness so cancelled slots can be rebooked without double-booking active appointments
[2026-05-16] [DB] [TEAM] [fix/backend-appointment-certificates] - Added certificate issue-date integrity enforcement (#18): service validation plus MySQL insert/update triggers reject certificates before appointment date and future appointment certificate issuance
[2026-05-16] [API] [TEAM] [fix/backend-appointment-certificates] - Expanded certificate responses (#15): certificate APIs now return doctor, appointment date, appointment reason, diagnosis, and remarks for richer certificate templates
[2026-05-16] [API] [TEAM] [fix/backend-appointment-certificates] - Added medical leave certificate date range support (#16): POST /certificates accepts leave_start_date and leave_end_date, stores them, validates range order, and returns them in certificate summaries
[2026-05-16] [API] [TEAM] [fix/backend-appointment-certificates] - Added fitness certificate clearance notes (#17): POST /certificates accepts certificate_notes, persists them, and returns them for student certificate templates
[2026-05-16] [UI] [TEAM] [fix/backend-appointment-certificates] - Wired doctor certificate form to send leave date ranges and fitness clearance notes, with certificate type IDs aligned to MySQL seed data
[2026-05-16] [TEST] [TEAM] [fix/backend-appointment-certificates] - Added regression coverage for appointment status transitions, certificate date integrity, leave dates, certificate notes, and doctor certificate form payload wiring

[2026-05-15] [FIX] [TEAM] [feat/student-appointment-view] - Fixed booking showing 108 slots — filter to selected date only instead of all slots from that date onwards
[2026-05-15] [API] [TEAM] [feat/student-appointment-view] - Added reason field to student list_appointments query and StudentAppointmentSummary type
[2026-05-15] [UI] [TEAM] [feat/student-appointment-view] - Show booking reason on student appointment detail page when present
[2026-05-15] [UI] [TEAM] [feat/student-appointment-view] - Doctor appointments page: Today tab with count badge showing only today's appointments, All tab for full list
[2026-05-15] [UI] [TEAM] [feat/student-appointment-view] - Add View button on all student appointments, dedicated detail page /students/appointments/[id] with reference number, date/time/doctor, Cancel button for booked, View Report link for completed (closes #25)
[2026-05-15] [UI] [TEAM] [feat/login-improvements] - Login page: entrance animations (panels slide in from sides, form/features stagger in), spinner on submit button, rate limit countdown with 30s timer, auto-focus on email field
[2026-05-15] [DOCS] [TEAM] [feat/login-improvements] - Opened GitHub issue #23 for forgot password / password reset flow
[2026-05-15] [UI] [TEAM] [feat/framer-motion] - Add Framer Motion animations — page transitions in DashboardShell, staggered StatsCard entrance + hover lift, Modal scale-in/out with AnimatePresence, smooth accordion height animation in patient history, step slide transitions in book appointment flow, fade-in entrance on 404 error page
[2026-05-15] [FIX] [TEAM] [feat/error-pages-autologout] - Auto-logout on 401 invalid bearer token — clearSession() + redirect to /login in api.ts request handler
[2026-05-15] [UI] [TEAM] [feat/error-pages-autologout] - Add custom 404 page — Newsreader teal "404", Go to Dashboard + Go Back buttons, matches design system
[2026-05-15] [UI] [TEAM] [feat/error-pages-autologout] - Add custom 500 error page — detects network/service errors and shows 503 Service Unavailable design instead, collapsible error details in JetBrains Mono
[2026-05-15] [UI] [TEAM] [feat/error-pages-autologout] - Add global-error.tsx fallback for root-level crashes

[2026-05-15] [FIX] [TEAM] [feat/backend/api] - Fixed raw ISO slot_date displaying in book appointment step 2 and confirmation — now formatted consistently
[2026-05-15] [FIX] [TEAM] [feat/backend/api] - Fixed certificate type dropdown having wrong labels — now matches DB types (Consultation Proof, Medical Leave Certificate, Fitness Certificate)
[2026-05-15] [FIX] [TEAM] [feat/backend/api] - Hidden Mark Complete button for cancelled appointments on doctor appointment detail (frontend guard for #13)
[2026-05-15] [FIX] [TEAM] [feat/backend/api] - Fixed missing setLoading(false) on auth redirects in doctor dashboard and appointment detail pages
[2026-05-15] [DOCS] [TEAM] [feat/backend/api] - Opened GitHub issue #21 for Google OAuth (future scope); admin dashboard #11 and role assignment remain active scope
[2026-05-15] [FIX] [TEAM] [feat/backend/api] - Fixed "Dr. Dr. Name" double prefix bug — seed data stores names with "Dr." prefix, frontend was prepending another; added doctorName() util to strip it before display
[2026-05-15] [FIX] [TEAM] [feat/backend/api] - Fixed patient history accordion — only one entry open at a time, opening a new one closes the previous (#20)
[2026-05-15] [FIX] [TEAM] [feat/backend/api] - Fixed patient search showing "No student found" before any search is performed — now only shows after a search (#20)
[2026-05-15] [FIX] [TEAM] [feat/backend/api] - Patient history profile card now shows student name, roll number, and correct initials passed from search results
[2026-05-15] [FIX] [TEAM] [feat/backend/api] - Fixed missing setLoading(false) on auth redirect in doctor appointments, student appointments, and patient history pages
[2026-05-15] [DOCS] [TEAM] [feat/backend/api] - Opened GitHub issue #20 — doctor patient history search feedback and accordion expansion
[2026-05-15] [FIX] [TEAM] [feat/backend/api] - Closed GitHub issue #19 — Reports/Certificates tab state fix verified and merged
[2026-05-15] [FIX] [TEAM] [feat/backend/api] - Fixed report issue date using today instead of appointment date — now uses slot_date for reproducible printed documents
[2026-05-15] [FIX] [TEAM] [feat/backend/api] - Fixed empty-string diagnosis and remarks rendering blank instead of "Not recorded" on report template
[2026-05-15] [FIX] [TEAM] [feat/backend/api] - Fixed report footer mt-auto not anchoring in non-flex container
[2026-05-15] [FIX] [TEAM] [feat/backend/api] - Added back button to error states on both report and certificate document pages
[2026-05-15] [UI] [TEAM] [feat/backend/api] - Added on-screen warning when certificate issue_date precedes appointment_date (#18)
[2026-05-15] [UI] [TEAM] [feat/backend/api] - Pre-wired Medical Leave Certificate template with leave period block (from/until/duration) and Fitness Certificate with clearance details block — shows data when backend adds fields (#16, #17)
[2026-05-15] [UI] [TEAM] [feat/backend/api] - Made certificate document template type-aware with distinct formal statements for Medical Leave, Fitness, and generic certificate types
[2026-05-15] [UI] [TEAM] [feat/backend/api] - Added optional leave_start_date, leave_end_date, certificate_notes fields to StudentCertificateSummary type for future backend compatibility
[2026-05-15] [UI] [TEAM] [feat/backend/api] - Replaced report and certificate modal/download pattern with dedicated A4 print-ready document template routes
[2026-05-15] [UI] [TEAM] [feat/backend/api] - Added auto-print trigger via ?print=1 query param and Back + Print controls on document pages
[2026-05-15] [FIX] [TEAM] [feat/backend/api] - Fixed Reports/Certificates tab state resetting on back navigation — active tab now encoded in URL as ?tab= (#19)
[2026-05-15] [DOCS] [TEAM] [feat/backend/api] - Added root DESIGN.md brief for Stitch report, prescription, and certificate templates
[2026-05-15] [DOCS] [TEAM] [feat/backend/api] - Updated TODO with appointment lifecycle, doctor availability, and richer certificate tracking issues
[2026-05-02] [INIT] [TEAM] [main] - Project initialized
[2026-05-02] [INIT] [TEAM] [main] - Base directory structure defined
[2026-05-02] [DOCS] [TEAM] [main] - Added agent instructions, TODO, API notes, DB notes, and project context
[2026-05-02] [DOCS] [TEAM] [main] - Added project README and updated contributor instructions
[2026-05-02] [DOCS] [TEAM] [main] - Updated README database wording before final database selection
[2026-05-02] [DOCS] [TEAM] [main] - Reworked README for public repository presentation
[2026-05-02] [DOCS] [TEAM] [main] - Improved README setup steps and project tree formatting
[2026-05-02] [DOCS] [TEAM] [main] - Added uv installation instructions to README
[2026-05-02] [ADD] [TEAM] [main] - Added frontend placeholder files so scaffold directories are tracked
[2026-05-02] [DOCS] [TEAM] [main] - Updated setup guide for current frontend scaffold state
[2026-05-02] [UPDATE] [TEAM] [main] - Removed frontend placeholder files
[2026-05-09] [API] [TEAM] [feat/backend/api] - Added MVP FastAPI route, schema, service, and repository skeletons
[2026-05-09] [TEST] [TEAM] [feat/backend/api] - Added API surface tests for health and MVP route registration
[2026-05-09] [API] [TEAM] [feat/backend/api] - Added stateless auth logout endpoint
[2026-05-09] [DOCS] [TEAM] [feat/backend/api] - Deferred database setup instructions until database selection
[2026-05-10] [DOCS] [TEAM] [feat/backend/api] - Updated TODO with completed API skeleton work, database provider decision task, and security hardening tasks
[2026-05-14] [DB] [TEAM] [feat/backend/api] - Selected MySQL and added schema, seed data, connection pooling, raw SQL queries, and repository integration
[2026-05-14] [TEST] [TEAM] [feat/backend/api] - Added MySQL database layer tests and bcrypt verification coverage
[2026-05-14] [DOCS] [TEAM] [feat/backend/api] - Updated setup, database, API, ERD notes, README, AGENTS, and TODO for MySQL
[2026-05-14] [FIX] [TEAM] [feat/backend/api] - Normalized MySQL TIME values for API responses and kept cancelled unique slots from being relisted as available
[2026-05-14] [TEST] [TEAM] [feat/backend/api] - Ran live MySQL schema, seed, API route smoke test, and EXPLAIN checks
[2026-05-14] [DB] [TEAM] [feat/backend/api] - Added MySQL views for available slots, appointment details, doctor appointments, student reports, and student certificates
[2026-05-14] [API] [TEAM] [feat/backend/api] - Protected API routes with JWT authentication and role-based access
[2026-05-14] [API] [TEAM] [feat/backend/api] - Replaced temporary student_id and staff_id query parameters with authenticated user context
[2026-05-14] [UPDATE] [TEAM] [feat/backend/api] - Added idempotency, rate limiting, replay-safe write handling, and login brute-force protection
[2026-05-14] [TEST] [TEAM] [feat/backend/api] - Added auth, authorization, idempotency, and rate-limit test coverage
[2026-05-14] [TEST] [TEAM] [feat/backend/api] - Ran live MySQL JWT, role access, idempotency, and protected route smoke checks
[2026-05-14] [DOCS] [TEAM] [feat/backend/api] - Updated API, setup, database, README, AGENTS, and TODO notes for security hardening
[2026-05-14] [ADD] [TEAM] [feat/backend/api] - Added root npm dev command to start backend and frontend together
[2026-05-14] [UI] [TEAM] [feat/backend/api] - Added login password visibility toggle and routed frontend API calls through the Next.js local proxy
[2026-05-14] [TEST] [TEAM] [feat/backend/api] - Added frontend login/proxy regression checks and fixed the patient history TypeScript error
[2026-05-14] [FIX] [TEAM] [feat/backend/api] - Fixed Windows root dev launcher spawn handling for npm and uv
[2026-05-14] [DOCS] [TEAM] [feat/backend/api] - Added frontend to-fix items for upcoming appointments and report, prescription, and certificate downloads
[2026-05-14] [DOCS] [TEAM] [feat/backend/api] - Added template tasks for reports, prescriptions, and medical certificates
[2026-05-14] [FIX] [TEAM] [feat/backend/api] - Fixed admin login redirect loop by routing admin users to a safe admin dashboard landing page
[2026-05-14] [TEST] [TEAM] [feat/backend/api] - Added regression coverage for admin frontend routing
[2026-05-14] [DOCS] [TEAM] [feat/backend/api] - Added staff login and staff workflow gap to TODO, README, and project context with GitHub issue tracking
[2026-05-15] [API] [TEAM] [feat/backend/api] - Added doctor patient search by name or roll number with doctor-scoped results
[2026-05-15] [UPDATE] [TEAM] [feat/backend/api] - Added staff seed login, frontend staff routing, and safe staff landing page
[2026-05-15] [FIX] [TEAM] [feat/backend/api] - Fixed student upcoming appointment filtering for backend booked status
[2026-05-15] [FIX] [TEAM] [feat/backend/api] - Added student report, prescription, and certificate view/download actions without printable templates
[2026-05-15] [FIX] [TEAM] [feat/backend/api] - Preserved existing prescription context on doctor appointment details and fixed local-date schedule filtering
[2026-05-15] [TEST] [TEAM] [feat/backend/api] - Added frontend workflow and patient-search regression tests
[2026-05-15] [DOCS] [TEAM] [feat/backend/api] - Updated README, setup, API notes, project context, report notes, and TODO for staff login and UI integration fixes
