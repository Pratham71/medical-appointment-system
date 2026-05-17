from app.backend.app.api.errors import NotFoundError
from app.backend.app.repositories import student_repo
from app.backend.app.schemas.student import (
    StudentAppointmentSummary,
    StudentCertificateSummary,
    StudentDashboard,
    StudentEmergencyAlertSummary,
    StudentNextAppointment,
    StudentReportSummary,
)


def get_dashboard(student_id: int) -> StudentDashboard:
    counts = student_repo.get_dashboard_counts(student_id)
    if counts is None:
        raise NotFoundError("Student was not found")

    next_appointment = student_repo.get_next_appointment(student_id)
    return StudentDashboard(
        **counts,
        next_appointment=(
            StudentNextAppointment(**next_appointment) if next_appointment else None
        ),
    )


def list_appointments(student_id: int) -> list[StudentAppointmentSummary]:
    rows = student_repo.list_appointments(student_id)
    return [StudentAppointmentSummary(**row) for row in rows]


def list_reports(student_id: int) -> list[StudentReportSummary]:
    rows = student_repo.list_reports(student_id)
    return [StudentReportSummary(**row) for row in rows]


def list_certificates(student_id: int) -> list[StudentCertificateSummary]:
    rows = student_repo.list_certificates(student_id)
    return [StudentCertificateSummary(**row) for row in rows]


def list_emergency_alerts(student_id: int) -> list[StudentEmergencyAlertSummary]:
    rows = student_repo.list_emergency_alerts(student_id)
    return [StudentEmergencyAlertSummary(**row) for row in rows]
