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
    """Return dashboard statistics and next appointment for a student.

    Args:
        student_id: Primary key of the student profile.

    Returns:
        A StudentDashboard object with counts and the next upcoming appointment.

    Raises:
        NotFoundError: If the student does not exist.
    """
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
    """Return all appointments for a student in reverse chronological order.

    Args:
        student_id: Primary key of the student profile.

    Returns:
        List of StudentAppointmentSummary objects.
    """
    rows = student_repo.list_appointments(student_id)
    return [StudentAppointmentSummary(**row) for row in rows]


def list_reports(student_id: int) -> list[StudentReportSummary]:
    """Return all medical report summaries for a student, newest first.

    Args:
        student_id: Primary key of the student profile.

    Returns:
        List of StudentReportSummary objects.
    """
    rows = student_repo.list_reports(student_id)
    return [StudentReportSummary(**row) for row in rows]


def list_certificates(student_id: int) -> list[StudentCertificateSummary]:
    """Return all certificate summaries for a student, newest first.

    Args:
        student_id: Primary key of the student profile.

    Returns:
        List of StudentCertificateSummary objects.
    """
    rows = student_repo.list_certificates(student_id)
    return [StudentCertificateSummary(**row) for row in rows]


def list_emergency_alerts(student_id: int) -> list[StudentEmergencyAlertSummary]:
    """Return all emergency alerts submitted by a student, newest first.

    Args:
        student_id: Primary key of the student profile.

    Returns:
        List of StudentEmergencyAlertSummary objects.
    """
    rows = student_repo.list_emergency_alerts(student_id)
    return [StudentEmergencyAlertSummary(**row) for row in rows]
