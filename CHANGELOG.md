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
