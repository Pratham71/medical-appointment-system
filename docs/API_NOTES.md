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
- Role-based access is enforced for student, professor, college-staff, hostel-staff, doctor, staff, and admin-supported routes.
- Professors, college-staff, and hostel-staff use the same appointment/report/certificate workflow as students; the API preserves each distinct `role_name` for frontend labeling.
- New signup accounts are created as student/patient accounts by default; admin-only role assignment can later change them to professor, college-staff, hostel-staff, doctor, staff, or admin.
- Admin backend routes are available for dashboard metrics, user role assignment, user activation/deactivation, appointment oversight, directories, and emergency alert review.
- Emergency alert review includes context fields plus acknowledge/resolve lifecycle actions for admin/staff responders.
- Staff workflow APIs are implemented for dashboard counts and appointment lookup/oversight. Staff can cancel appointments with a structured reason through the shared cancellation endpoint.
- Email notifications are environment-driven and disabled by default; when enabled, SMTP dispatch is best-effort and does not block the appointment/document workflow.
- Student endpoints use the authenticated student context instead of `student_id` query parameters.
- Doctor dashboard and appointment list endpoints use the authenticated staff context instead of `staff_id` query parameters.
- Doctor patient search supports name or roll-number lookup and scopes doctor users to their own patients.
- Doctor availability endpoints use the authenticated doctor staff context and support weekly rules plus date-level overrides.
- Emergency alerts use the authenticated student context and store alert confirmations for staff follow-up.
- Write endpoints use idempotency/replay protection where required.
- Login includes brute-force protection.
- Rate limiting is enabled for sensitive and high-traffic routes.

Auth Requirements
- Use `Authorization: Bearer <access_token>` for protected routes.
- Public routes: `POST /auth/signup`, `POST /auth/login`, and `GET /health`.
- Protected routes: student/professor/college-staff/hostel-staff, staff, doctor, admin, appointment, report, certificate, logout, and `/auth/me`.
- Return `401` for missing/invalid tokens.
- Return `403` for valid users without the required role.

Security Headers/Request Rules
- Replay-sensitive write endpoints require an `Idempotency-Key` header.
- Rate-limited requests return `429`.
- Repeated failed login attempts are locked according to backend policy.

Auth
POST /auth/signup
POST /auth/login
POST /auth/logout
GET /auth/me

Signup notes:
- `POST /auth/signup` accepts name, email, password, roll_number, department, and year_level.
- Signup does not accept a role field.
- Signup always returns an authenticated user with `role_name = student`.
- Professors, college-staff, and hostel-staff must be changed from student by an admin after signup.

Admin
GET /admin/dashboard
GET /admin/users
PATCH /admin/users/{user_id}/role
PATCH /admin/users/{user_id}/deactivate
PATCH /admin/users/{user_id}/activate
DELETE /admin/users/{user_id}
GET /admin/appointments
GET /admin/students
GET /admin/doctors
GET /admin/staff
GET /admin/emergency-alerts
PATCH /admin/emergency-alerts/{alert_id}/acknowledge
PATCH /admin/emergency-alerts/{alert_id}/resolve

Admin notes:
- Admin endpoints require `role_name = admin`, except emergency alert acknowledge/resolve actions also allow `role_name = staff`.
- `GET /admin/dashboard` returns high-level counts for students, professors, doctors, staff, appointment statuses, reports, certificates, and emergency alerts.
- `GET /admin/users` supports `q`, `role_name`, and `limit` query parameters for role management screens.
- `PATCH /admin/users/{user_id}/role` requires `Idempotency-Key` and can assign `student`, `professor`, `college-staff`, `hostel-staff`, `doctor`, `staff`, or `admin`.
- `PATCH /admin/users/{user_id}/deactivate`, `PATCH /admin/users/{user_id}/activate`, and `DELETE /admin/users/{user_id}` require `Idempotency-Key`; delete is a safe soft-deactivate operation and does not hard-delete medical records.
- Student, professor, college-staff, and hostel-staff role assignment uses the existing patient/student profile fields: `roll_number`, `department`, and `year_level`.
- Doctor and staff role assignment uses `employee_number` and optional `specialization`.
- Role changes return `409` when the change would remove a patient/staff profile that already has appointment or slot history.
- Admins cannot deactivate their own account.
- `GET /admin/emergency-alerts` returns reason, location, contact_number, status, acknowledgement fields, resolution fields, and resolution_note.
- `PATCH /admin/emergency-alerts/{alert_id}/acknowledge` requires `Idempotency-Key` and stores the responder user/time.
- `PATCH /admin/emergency-alerts/{alert_id}/resolve` requires `Idempotency-Key` and stores the responder user/time plus optional `resolution_note`.
- Emergency alert acknowledge/resolve endpoints allow `admin` and `staff` roles.

Staff
GET /staff/dashboard
GET /staff/appointments

Staff notes:
- Staff endpoints require `role_name = staff` or `role_name = admin`.
- `GET /staff/dashboard` returns appointment and emergency-alert counts for front-desk triage.
- `GET /staff/appointments` supports `status`, `from_date`, `to_date`, and `limit`.

Students
GET /students/dashboard
GET /students/appointments
GET /students/reports
GET /students/certificates
GET /students/emergency-alerts

Student/professor/patient-equivalent notes:
- `student`, `professor`, `college-staff`, and `hostel-staff` roles can use these endpoints.
- The role name is different for frontend labeling, but backend permissions and patient records are the same.
- `GET /students/emergency-alerts` returns the authenticated user's own emergency alerts with status `unread`, `acknowledged`, or `resolved`.

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

Appointment cancellation notes:
- Students and patient-equivalent roles can cancel their own booked appointments without a request body.
- Doctors, staff, and admins can cancel accessible booked appointments with a request body containing `reason_code` and optional `note`.
- Supported staff/doctor/admin `reason_code` values: `no_show`, `student_request`, `doctor_unavailable`, `emergency_priority`, `duplicate_booking`, `other`.
- Notes are optional for every reason, including `other`.
- Staff/doctor/admin cancellation reasons are stored in `appointments.cancellation_reason`, and cancelling releases the appointment slot.

Reports
POST /reports/{appointment_id}/notes
POST /reports/{appointment_id}/prescription
GET /reports/{appointment_id}

Report write notes:
- Completed and cancelled appointments are locked; doctors cannot edit notes or prescriptions after the appointment reaches a terminal status.

Emergency
POST /emergency/alert

Emergency alert notes:
- Student/patient-equivalent endpoint.
- Requires `Authorization: Bearer <access_token>` and `Idempotency-Key`.
- Request body requires `reason` and `location`, and accepts optional `contact_number` and optional `message`.
- Stores an `emergency_alerts` row with student identity, context fields, message, timestamp, and lifecycle fields.
- New alerts start with status `unread`; acknowledgement changes status to `acknowledged`; resolution changes status to `resolved`.
- Real-time external SMS/push delivery is future scope. Email dispatch is available through environment-driven SMTP settings.

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

Notifications
- Set `EMAIL_NOTIFICATIONS_ENABLED=true` plus SMTP settings to enable email notifications.
- Supported notification events: appointment booked, appointment cancelled with reason, doctor-unavailability auto-cancel, report/prescription updated, and certificate available.
- SMTP provider failures are treated as best-effort notification failures and do not roll back appointment or document writes.

Future APIs
GET /live/queue
POST /walkins
POST /vitals/{appointment_id}
GET /notifications
GET /audit-logs
GET /analytics/admin
GET /analytics/doctor
GET /analytics/staff
