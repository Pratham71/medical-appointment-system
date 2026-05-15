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
GET /doctors/appointment/{id}
GET /doctors/patients/search?q={name_or_roll_number}
GET /doctors/patient-history/{student_id}

Appointments
GET /appointments/slots
POST /appointments/book
PATCH /appointments/{id}/cancel
PATCH /appointments/{id}/complete

Reports
POST /reports/{appointment_id}/notes
POST /reports/{appointment_id}/prescription
GET /reports/{appointment_id}

Certificates
POST /certificates/{appointment_id}
GET /certificates/student/{student_id}

Future APIs
GET /live/queue
POST /walkins
POST /vitals/{appointment_id}
GET /notifications
GET /audit-logs
GET /analytics/admin
GET /analytics/doctor
GET /analytics/staff
