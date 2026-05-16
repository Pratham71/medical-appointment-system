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

    assert "`/students/reports/${report.appointment_id}`" in page
    assert "`/students/reports/${report.appointment_id}?print=1`" in page
    assert "`/students/certificates/${certificate.certificate_id}`" in page
    assert "`/students/certificates/${certificate.certificate_id}?print=1`" in page
    assert "View" in page
    assert "Download" in page


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


def test_doctor_availability_page_is_wired_into_sidebar_and_api() -> None:
    sidebar = read(FRONTEND / "components" / "layout" / "sidebar.tsx")
    api = read(FRONTEND / "lib" / "api.ts")
    availability_page = FRONTEND / "app" / "doctors" / "availability" / "page.tsx"

    assert 'href: "/doctors/availability"' in sidebar
    assert availability_page.exists()
    page = read(availability_page)
    assert "getDoctorAvailability" in page
    assert "updateDoctorWeeklyAvailability" in page
    assert "updateDoctorAvailabilityOverride" in page
    assert "weekday_name" in page
    assert "getDoctorAvailability" in api
    assert "updateDoctorWeeklyAvailability" in api
    assert "updateDoctorAvailabilityOverride" in api


def test_patient_history_uses_name_or_roll_number_lookup() -> None:
    page = read(FRONTEND / "app" / "doctors" / "patients" / "page.tsx")

    assert "searchPatients" in page
    assert "Name or roll number" in page
    assert 'type="number"' not in page


def test_doctor_certificate_form_sends_leave_dates_and_notes() -> None:
    page = read(
        FRONTEND / "app" / "doctors" / "appointments" / "[id]" / "page.tsx"
    )
    api = read(FRONTEND / "lib" / "api.ts")

    assert "leaveStartDate" in page
    assert "leaveEndDate" in page
    assert "certificateNotes" in page
    assert "leave_start_date" in page
    assert "leave_end_date" in page
    assert "certificate_notes" in page
    assert "issueCertificate(id, Number(certTypeId), certificatePayload)" in page
    assert "certificatePayload" in api


def test_doctor_completed_appointment_detail_locks_editing() -> None:
    page = read(
        FRONTEND / "app" / "doctors" / "appointments" / "[id]" / "page.tsx"
    )

    assert "isAppointmentLocked" in page
    assert 'detail?.status.toLowerCase() === "completed"' in page
    assert "Completed appointments cannot be edited" in page
    assert "readOnly={isAppointmentLocked}" in page
    assert "disabled={saving || !diagnosis.trim() || isAppointmentLocked}" in page
    assert "disabled={saving || isAppointmentLocked}" in page


def test_student_booking_uses_local_date_and_hides_elapsed_slots() -> None:
    page = read(FRONTEND / "app" / "students" / "book" / "page.tsx")

    assert "getLocalDateKey" in page
    assert "isFutureSlot" in page
    assert "new Date().toISOString().split" not in page
    assert "s.slot_date === fromDate && isFutureSlot(s, fromDate)" in page
