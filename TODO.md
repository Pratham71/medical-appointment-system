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
[x] Add API surface tests
[x] Add project README
[x] Update contributor instructions
[x] Update setup docs for current backend/frontend state
[x] Remove frontend placeholder files
[x] Push feat/backend/api branch

Database Tasks

[ ] Decide database provider: PostgreSQL or MySQL
[ ] Setup selected database provider
[ ] Setup DB connection pooling after provider is chosen
[ ] Create normalized core tables after provider is chosen
[ ] Insert dummy data after schema is finalized
[ ] Add indexes
[ ] Test queries with EXPLAIN ANALYZE

Auth and Security Tasks

[ ] Implement DB-backed login
[ ] Protect API routes with JWT authentication
[ ] Add role-based access for student, doctor, and admin/staff routes
[ ] Replace temporary `student_id` and `staff_id` query parameters with authenticated user context
[ ] Implement security features like idempotency, rate limiting, and replay-safe write requests
[ ] Require production-safe JWT secret configuration
[ ] Add brute-force protection for login

Appointment APIs

[ ] Implement get doctors
[ ] Implement get slots
[ ] Implement book appointment
[ ] Implement cancel appointment
[ ] Implement mark appointment complete

Student APIs

[ ] Implement dashboard
[ ] Implement my appointments
[ ] Implement reports
[ ] Implement certificates

Doctor APIs

[ ] Implement view appointments
[ ] Implement appointment details
[ ] Implement add notes
[ ] Implement add prescriptions
[ ] Implement patient history

Certificate APIs

[ ] Implement create certificate
[ ] Implement list student certificates

Frontend Tasks

[ ] Setup Next.js frontend
[ ] Build login page
[ ] Build student pages
[ ] Build doctor pages
[ ] Connect frontend to backend API

Testing and Documentation Tasks

[ ] Add DB-backed API tests after provider is chosen
[ ] Add auth and authorization tests
[ ] Add security/rate-limit tests
[ ] Screenshots for report
[ ] Final documentation

Delivery Tasks

[ ] Open backend API pull request
