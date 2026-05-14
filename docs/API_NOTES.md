API Notes

Rules
- Use REST APIs
- Use JSON request/response
- Keep endpoint names consistent
- Validate inputs
- Return proper status codes
- Keep SQL out of routes

Current MVP Notes
- Student endpoints use a `student_id` query parameter until authenticated student context is wired.
- Doctor dashboard and appointment list endpoints use a `staff_id` query parameter until authenticated doctor context is wired.
- MySQL is selected as the database provider.
- Backend repositories now call MySQL query functions.
- Routes still need authenticated user context and role-based access before production use.

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
