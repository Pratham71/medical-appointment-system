# Emergency Alert Context and Lifecycle Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Complete GitHub issues #46 and #43 by adding structured emergency alert context, admin acknowledge/resolve workflow, and student alert status visibility.

**Architecture:** Keep the existing backend layering: routes call services, services call repositories, repositories call query modules, and all SQL stays under `app/backend/app/db/queries/`. Frontend changes stay in the existing Next.js API helper/type/page pattern.

**Tech Stack:** FastAPI, Pydantic, raw MySQL SQL, pytest, Next.js App Router, TypeScript.

---

### Task 1: Backend Alert Context Fields

**Files:**
- Modify: `tests/test_auth_security.py`
- Modify: `tests/test_mysql_database.py`
- Modify: `app/backend/app/schemas/emergency.py`
- Modify: `app/backend/app/services/emergency_service.py`
- Modify: `app/backend/app/repositories/emergency_repo.py`
- Modify: `app/backend/app/db/queries/emergency_queries.py`
- Modify: `app/backend/app/db/schema.sql`
- Create: `app/backend/app/db/migrations/2026_05_17_update_emergency_alerts_context_lifecycle.sql`

- [ ] **Step 1: Write failing tests**

Add tests asserting `POST /emergency/alert` accepts `reason`, `location`, and optional `contact_number`, and response schemas include the same fields.

- [ ] **Step 2: Run focused tests to verify RED**

Run: `uv run --group dev pytest tests/test_auth_security.py::test_student_emergency_alert_uses_authenticated_student_context tests/test_mysql_database.py::test_emergency_alert_response_schema_accepts_alert_context -q -p no:cacheprovider`

Expected: FAIL because the service signature, schema fields, and SQL do not include the new context fields yet.

- [ ] **Step 3: Implement minimal backend context support**

Add Pydantic fields, service validation/default message handling, repository parameters, query insert/select columns, schema columns, and migration columns.

- [ ] **Step 4: Run focused tests to verify GREEN**

Run: `uv run --group dev pytest tests/test_auth_security.py::test_student_emergency_alert_uses_authenticated_student_context tests/test_mysql_database.py::test_emergency_alert_response_schema_accepts_alert_context -q -p no:cacheprovider`

Expected: PASS.

### Task 2: Admin Alert Lifecycle

**Files:**
- Modify: `tests/test_admin_api.py`
- Modify: `tests/test_api_surface.py`
- Modify: `app/backend/app/api/routes/admin.py`
- Modify: `app/backend/app/schemas/admin.py`
- Modify: `app/backend/app/services/admin_service.py`
- Modify: `app/backend/app/repositories/admin_repo.py`
- Modify: `app/backend/app/db/queries/admin_queries.py`

- [ ] **Step 1: Write failing tests**

Add tests for `PATCH /admin/emergency-alerts/{alert_id}/acknowledge`, `PATCH /admin/emergency-alerts/{alert_id}/resolve`, status values in admin listings, and OpenAPI exposure.

- [ ] **Step 2: Run focused tests to verify RED**

Run: `uv run --group dev pytest tests/test_admin_api.py::test_admin_can_acknowledge_emergency_alert tests/test_admin_api.py::test_admin_can_resolve_emergency_alert tests/test_api_surface.py::test_openapi_includes_mvp_routes -q -p no:cacheprovider`

Expected: FAIL because the routes and service methods do not exist yet.

- [ ] **Step 3: Implement minimal admin lifecycle support**

Add request/response schemas, admin routes, service methods, repository transaction methods, and query functions for status context, acknowledge, resolve, and status-rich listing.

- [ ] **Step 4: Run focused tests to verify GREEN**

Run: `uv run --group dev pytest tests/test_admin_api.py::test_admin_can_acknowledge_emergency_alert tests/test_admin_api.py::test_admin_can_resolve_emergency_alert tests/test_api_surface.py::test_openapi_includes_mvp_routes -q -p no:cacheprovider`

Expected: PASS.

### Task 3: Student Alert Status Endpoint

**Files:**
- Modify: `tests/test_auth_security.py`
- Modify: `tests/test_api_surface.py`
- Modify: `app/backend/app/api/routes/students.py`
- Modify: `app/backend/app/schemas/student.py`
- Modify: `app/backend/app/services/student_service.py`
- Modify: `app/backend/app/repositories/student_repo.py`
- Modify: `app/backend/app/db/queries/student_queries.py`

- [ ] **Step 1: Write failing tests**

Add tests for `GET /students/emergency-alerts` using authenticated student context and returning only that student's alerts with status fields.

- [ ] **Step 2: Run focused tests to verify RED**

Run: `uv run --group dev pytest tests/test_auth_security.py::test_student_can_list_own_emergency_alert_statuses tests/test_api_surface.py::test_openapi_includes_mvp_routes -q -p no:cacheprovider`

Expected: FAIL because the student endpoint and service method do not exist yet.

- [ ] **Step 3: Implement minimal student status support**

Add schema, route, service, repository, and query list function.

- [ ] **Step 4: Run focused tests to verify GREEN**

Run: `uv run --group dev pytest tests/test_auth_security.py::test_student_can_list_own_emergency_alert_statuses tests/test_api_surface.py::test_openapi_includes_mvp_routes -q -p no:cacheprovider`

Expected: PASS.

### Task 4: Frontend Wiring

**Files:**
- Modify: `tests/test_frontend_workflows.py`
- Modify: `app/frontend/lib/types.ts`
- Modify: `app/frontend/lib/api.ts`
- Modify: `app/frontend/components/ui/EmergencyButton.tsx`
- Modify: `app/frontend/app/admin/emergency-alerts/page.tsx`
- Modify: `app/frontend/app/admin/page.tsx`
- Modify: `app/frontend/app/students/page.tsx`

- [ ] **Step 1: Write failing string-level tests**

Add tests that require the structured emergency form, admin acknowledge/resolve helpers, status badges, and student alert status loading.

- [ ] **Step 2: Run frontend workflow tests to verify RED**

Run: `uv run --group dev pytest tests/test_frontend_workflows.py -q -p no:cacheprovider`

Expected: FAIL because the UI and API helpers do not expose the new workflow yet.

- [ ] **Step 3: Implement frontend wiring**

Update API helpers/types, replace the alert button with structured form fields, add admin page actions, and show recent student alert statuses on the student dashboard.

- [ ] **Step 4: Run frontend workflow tests to verify GREEN**

Run: `uv run --group dev pytest tests/test_frontend_workflows.py -q -p no:cacheprovider`

Expected: PASS.

### Task 5: Docs and Final Verification

**Files:**
- Modify: `TODO.md`
- Modify: `CHANGELOG.md`
- Modify: `README.md`
- Modify: `docs/API_NOTES.md`
- Modify: `docs/DB_NOTES.md`
- Modify: `docs/SETUP.md`
- Modify: `AGENTS.md`

- [ ] **Step 1: Update tracking and docs**

Mark #46 and #43 complete in `TODO.md`, add API/DB/setup notes, and add a dated changelog entry.

- [ ] **Step 2: Run full verification**

Run:
- `uv run --group dev pytest -q -p no:cacheprovider`
- `uv run --group dev ruff check .`
- `npm --prefix app/frontend run build`

Expected: all pass.
