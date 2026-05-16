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


def test_doctor_appointment_detail_can_cancel_with_reason() -> None:
    page = read(
        FRONTEND / "app" / "doctors" / "appointments" / "[id]" / "page.tsx"
    )
    api = read(FRONTEND / "lib" / "api.ts")
    types = read(FRONTEND / "lib" / "types.ts")

    assert "AppointmentCancelReasonCode" in types
    assert "cancelAppointment(id, cancelReasonCode, cancelReasonNote.trim())" in page
    assert 'value="no_show"' in page
    assert 'value="other"' in page
    assert "Cancellation reason" in page
    assert "handleCancelAppointment" in page
    assert "reason_code" in api
    assert 'cancelReasonCode === "other" && !cancelReasonNote.trim()' not in page


def test_student_booking_uses_local_date_and_hides_elapsed_slots() -> None:
    page = read(FRONTEND / "app" / "students" / "book" / "page.tsx")

    assert "getLocalDateKey" in page
    assert "isFutureSlot" in page
    assert "new Date().toISOString().split" not in page
    assert "s.slot_date === fromDate && isFutureSlot(s, fromDate)" in page


def test_student_booking_fetches_all_doctors_for_selected_date() -> None:
    page = read(FRONTEND / "app" / "students" / "book" / "page.tsx")
    api = read(FRONTEND / "lib" / "api.ts")
    types = read(FRONTEND / "lib" / "types.ts")

    assert "DoctorAvailabilityStatus" in types
    assert "getDoctorsForDate" in api
    assert "`/appointments/doctors?for_date=${forDate}`" in api
    assert "getDoctorsForDate(fromDate)" in page
    assert "const [doctors, setDoctors]" in page
    assert "doc.available_slots" in page
    assert "doc.unavailability_note" in page


def test_student_cancelled_appointment_shows_reschedule_options() -> None:
    detail_page = read(
        FRONTEND / "app" / "students" / "appointments" / "[id]" / "page.tsx"
    )
    types = read(FRONTEND / "lib" / "types.ts")

    assert "cancellation_reason" in types
    assert "appointment.cancellation_reason" in detail_page
    assert "Cancelled by infirmary" in detail_page
    assert "Reschedule" in detail_page
    assert "walk-in" in detail_page


def test_emergency_button_sends_backend_alert() -> None:
    button = read(FRONTEND / "components" / "ui" / "EmergencyButton.tsx")
    api = read(FRONTEND / "lib" / "api.ts")

    assert "sendEmergencyAlert" in api
    assert '"/emergency/alert"' in api
    assert "sendEmergencyAlert" in button
    assert "handleSendAlert" in button
    assert "Send Alert to Infirmary" in button
    assert "Alert sent to infirmary" in button
