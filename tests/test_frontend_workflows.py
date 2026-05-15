from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FRONTEND = ROOT / "app" / "frontend"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_student_upcoming_appointments_accept_backend_booked_status() -> None:
    page = read(FRONTEND / "app" / "students" / "appointments" / "page.tsx")

    assert 's === "booked"' in page
    assert 'a.status.toLowerCase() === "booked"' in page


def test_student_records_page_can_view_and_download_records() -> None:
    page = read(FRONTEND / "app" / "students" / "reports" / "page.tsx")

    assert "getReportDetail" in page
    assert "selectedReport" in page
    assert "downloadReport" in page
    assert "downloadCertificate" in page
    assert "URL.createObjectURL" in page


def test_doctor_detail_loads_existing_report_prescription_context() -> None:
    page = read(
        FRONTEND / "app" / "doctors" / "appointments" / "[id]" / "page.tsx"
    )

    assert "getReportDetail" in page
    assert "report.prescription?.items" in page
    assert "setPrescRows" in page


def test_doctor_today_schedule_uses_local_date_key() -> None:
    page = read(FRONTEND / "app" / "doctors" / "page.tsx")

    assert "getLocalDateKey" in page
    assert 'new Date().toISOString().split("T")[0]' not in page


def test_patient_history_uses_name_or_roll_number_lookup() -> None:
    page = read(FRONTEND / "app" / "doctors" / "patients" / "page.tsx")

    assert "searchPatients" in page
    assert "Name or roll number" in page
    assert 'type="number"' not in page
