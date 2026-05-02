Project Context

Project Name
Medical Appointment System – College Infirmary

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

Future Scope
- Staff dashboard
- Walk-in management
- Live queue system
- Notifications
- Analytics
- OAuth
- ORM migration

Database Decision
- PostgreSQL or MySQL (to be finalized)
- Schema design should stay compatible with both

ER Diagram
- Not required at this stage
- Will be created after schema finalization

Tech Stack
Backend: FastAPI
Database: PostgreSQL/MySQL
Frontend: Next.js
Package Manager: uv

Architecture
routes → services → repositories → queries → db

Design Philosophy
- Keep simple
- Focus on database design
- Maintain clean separation of concerns
