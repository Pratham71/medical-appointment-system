Project Context

Project Name
Medical Appointment System - College Infirmary

Objective
Build a DBMS-focused system for managing appointments, medical records, prescriptions, and certificates.

MVP Scope
- Student booking system
- Appointment history
- Doctor appointment management
- Medical notes
- Prescriptions
- Certificates
- Basic dashboard stats
- Staff login safe landing and backend appointment oversight
- Admin role and user-status management
- Emergency alert context, acknowledgement, resolution, and student-visible status
- Email notifications for appointment/document updates

Future Scope
- Active user presence tracking
- Walk-in management
- Live queue system
- SMS/push notification providers
- Analytics
- OAuth
- ORM migration

Database Decision
- MySQL is selected for the MVP database.
- Schema and seed files are stored under `app/backend/app/db/`.

Current Role Notes
- Staff login, seed account, dashboard API, appointment lookup API, and cancellation with reason are implemented.
- Professor, college-staff, and hostel-staff users reuse the student/patient workflow with distinct role names for labeling.
- Admin delete/remove is implemented as soft-deactivation through `users.is_active`.
- Emergency alerts now capture reason, location, optional contact number, and move through unread, acknowledged, and resolved states.

ER Diagram
- Not required at this stage
- Will be created after the MySQL schema is reviewed

Tech Stack
Backend: FastAPI
Database: MySQL
Frontend: Next.js
Package Manager: uv

Architecture
routes -> services -> repositories -> queries -> db

Design Philosophy
- Keep simple
- Focus on database design
- Maintain clean separation of concerns
