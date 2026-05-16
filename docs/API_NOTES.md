API Notes

Rules
- Use REST APIs
- Use JSON request/response
- Keep endpoint names consistent
- Validate inputs
- Return proper status codes
- Keep SQL out of routes

Current MVP Notes
- MySQL is selected as the database provider.
- Backend repositories call MySQL query functions.
- Protected API routes require JWT Bearer authentication.
- Role-based access is enforced for student, doctor, staff, and admin-supported routes.
- Staff login and a safe staff landing page are implemented; full staff workflows are still tracked in GitHub issue #12.
- Student endpoints use the authenticated student context instead of `student_id` query parameters.
- Doctor dashboard and appointment list endpoints use the authenticated staff context instead of `staff_id` query parameters.
- Doctor patient search supports name or roll-number lookup and scopes doctor users to their own patients.
- Doctor availability endpoints use the authenticated doctor staff context and support weekly rules plus date-level overrides.
- Write endpoints use idempotency/replay protection where required.
- Login includes brute-force protection.
- Rate limiting is enabled for sensitive and high-traffic routes.

Auth Requirements
- Use `Authorization: Bearer <access_token>` for protected routes.
- Public routes: `POST /auth/login` and `GET /health`.
- Protected routes: student, doctor, appointment, report, certificate, logout, and `/auth/me`.
- Return `401` for missing/invalid tokens.
- Return `403` for valid users without the required role.

Security Headers/Request Rules
- Replay-sensitive write endpoints require an `Idempotency-Key` header.
- Rate-limited requests return `429`.
- Repeated failed login attempts are locked according to backend policy.

Auth
POST /auth/login
POST /auth/logout
GET /auth/me

Students
GET /students/dashboard
GET /students/appointments
GET /students/reports
GET /students/certificates

Doctors
GET /doctors/dashboard
GET /doctors/appointments
GET /doctors/availability
PUT /doctors/availability/weekly/{weekday}
PUT /doctors/availability/overrides/{override_date}
DELETE /doctors/availability/overrides/{override_date}
GET /doctors/appointment/{id}
GET /doctors/patients/search?q={name_or_roll_number}
GET /doctors/patient-history/{student_id}

Doctor availability notes:
- Weekday values use MySQL `WEEKDAY()` numbering: Monday `0` through Sunday `6`.
- Doctors are available Monday-Saturday by default and unavailable on Sunday by default.
- A date override takes priority over the weekly rule for that date.
- Available slot reads hide slots outside the active weekly rule or date override.
- Availability write endpoints require `Idempotency-Key`.

Appointments
GET /appointments/slots
POST /appointments/book
PATCH /appointments/{id}/cancel
PATCH /appointments/{id}/complete

Reports
POST /reports/{appointment_id}/notes
POST /reports/{appointment_id}/prescription
GET /reports/{appointment_id}

Report write notes:
- Completed and cancelled appointments are locked; doctors cannot edit notes or prescriptions after the appointment reaches a terminal status.

Certificates
POST /certificates/{appointment_id}
GET /certificates/student/{student_id}

Certificate request/response notes:
- `POST /certificates/{appointment_id}` accepts `certificate_type_id`, optional `issue_date`, optional `leave_start_date`, optional `leave_end_date`, and optional `certificate_notes`.
- Certificate issue date must not be before the appointment date.
- Certificates cannot be issued for future appointments.
- Completed and cancelled appointments are locked; doctors cannot issue or update certificates after the appointment reaches a terminal status.
- Leave date fields must be provided together and `leave_end_date` must be on or after `leave_start_date`.
- Certificate responses include appointment reference, patient name, issuing doctor, appointment date, appointment reason, diagnosis, remarks, leave dates, and certificate notes where available.

Future APIs
GET /live/queue
POST /walkins
POST /vitals/{appointment_id}
GET /notifications
GET /audit-logs
GET /analytics/admin
GET /analytics/doctor
GET /analytics/staff
