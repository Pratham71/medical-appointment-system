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
- Staff login and staff role workflow
- Staff dashboard
- Walk-in management
- Live queue system
- Notifications
- Analytics
- OAuth
- ORM migration

Database Decision
- MySQL is selected for the MVP database.
- Schema and seed files are stored under `app/backend/app/db/`.

Current Open Role Gap
- Staff login is not implemented yet.
- Staff login and staff workflow planning are tracked in GitHub issue #12.

ER Diagram
- Not required at this stage
- Will be created after the MySQL schema is reviewed

Tech Stack
Backend: FastAPI
Database: MySQL
Frontend: Next.js
Package Manager: uv

Architecture
routes → services → repositories → queries → db

Design Philosophy
- Keep simple
- Focus on database design
- Maintain clean separation of concerns
