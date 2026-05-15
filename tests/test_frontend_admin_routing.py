from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FRONTEND = ROOT / "app" / "frontend" / "app"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_admin_role_routes_to_admin_page_instead_of_student_doctor_loop() -> None:
    root_page = read(FRONTEND / "page.tsx")
    login_page = read(FRONTEND / "login" / "page.tsx")
    student_page = read(FRONTEND / "students" / "page.tsx")
    doctor_page = read(FRONTEND / "doctors" / "page.tsx")

    assert 'router.replace("/admin")' in root_page
    assert 'router.replace("/admin")' in login_page
    assert 'router.replace("/admin")' in student_page
    assert 'router.replace("/admin")' in doctor_page
    assert 'if (user.role_name !== "student") { router.replace("/doctors"); return; }' not in student_page
    assert 'if (user.role_name !== "doctor") { router.replace("/students"); return; }' not in doctor_page


def test_admin_dashboard_page_exists_without_backend_dashboard_call() -> None:
    admin_page = FRONTEND / "admin" / "page.tsx"

    assert admin_page.exists()
    content = read(admin_page)
    assert '<DashboardShell role="admin" title="Admin Dashboard">' in content
    assert "getStudentDashboard" not in content
    assert "getDoctorDashboard" not in content


def test_staff_role_routes_to_staff_landing_page() -> None:
    root_page = read(FRONTEND / "page.tsx")
    login_page = read(FRONTEND / "login" / "page.tsx")
    sidebar = read(ROOT / "app" / "frontend" / "components" / "layout" / "Sidebar.tsx")
    shell = read(
        ROOT / "app" / "frontend" / "components" / "layout" / "DashboardShell.tsx"
    )
    staff_page = FRONTEND / "staff" / "page.tsx"

    assert staff_page.exists()
    assert 'router.replace("/staff")' in root_page
    assert 'router.replace("/staff")' in login_page
    assert 'role: "student" | "doctor" | "admin" | "staff"' in shell
    assert 'role: "student" | "doctor" | "admin" | "staff"' in sidebar
