from fastapi import APIRouter, Depends

from app.backend.app.api.dependencies import require_student_id
from app.backend.app.api.errors import service_error_to_http
from app.backend.app.schemas.student import (
    StudentAppointmentSummary,
    StudentCertificateSummary,
    StudentDashboard,
    StudentEmergencyAlertSummary,
    StudentReportSummary,
)
from app.backend.app.services import student_service

router = APIRouter(prefix="/students", tags=["Students"])


@router.get("/dashboard", response_model=StudentDashboard)
def dashboard(student_id: int = Depends(require_student_id)) -> StudentDashboard:
    """Return dashboard statistics for the authenticated student.

    Args:
        student_id: Resolved student_id of the authenticated user.

    Returns:
        A StudentDashboard with counts and the next upcoming appointment.

    Raises:
        HTTPException: 404 if the student does not exist.
    """
    try:
        return student_service.get_dashboard(student_id)
    except Exception as exc:
        raise service_error_to_http(exc) from exc


@router.get("/appointments", response_model=list[StudentAppointmentSummary])
def appointments(
    student_id: int = Depends(require_student_id),
) -> list[StudentAppointmentSummary]:
    """Return all appointments for the authenticated student.

    Args:
        student_id: Resolved student_id of the authenticated user.

    Returns:
        List of StudentAppointmentSummary objects in reverse chronological order.
    """
    try:
        return student_service.list_appointments(student_id)
    except Exception as exc:
        raise service_error_to_http(exc) from exc


@router.get("/reports", response_model=list[StudentReportSummary])
def reports(
    student_id: int = Depends(require_student_id),
) -> list[StudentReportSummary]:
    """Return all medical report summaries for the authenticated student.

    Args:
        student_id: Resolved student_id of the authenticated user.

    Returns:
        List of StudentReportSummary objects ordered by appointment date descending.
    """
    try:
        return student_service.list_reports(student_id)
    except Exception as exc:
        raise service_error_to_http(exc) from exc


@router.get("/certificates", response_model=list[StudentCertificateSummary])
def certificates(
    student_id: int = Depends(require_student_id),
) -> list[StudentCertificateSummary]:
    """Return all certificate summaries for the authenticated student.

    Args:
        student_id: Resolved student_id of the authenticated user.

    Returns:
        List of StudentCertificateSummary objects ordered by issue_date descending.
    """
    try:
        return student_service.list_certificates(student_id)
    except Exception as exc:
        raise service_error_to_http(exc) from exc


@router.get("/emergency-alerts", response_model=list[StudentEmergencyAlertSummary])
def emergency_alerts(
    student_id: int = Depends(require_student_id),
) -> list[StudentEmergencyAlertSummary]:
    """Return all emergency alerts submitted by the authenticated student.

    Args:
        student_id: Resolved student_id of the authenticated user.

    Returns:
        List of StudentEmergencyAlertSummary objects ordered by created_at descending.
    """
    try:
        return student_service.list_emergency_alerts(student_id)
    except Exception as exc:
        raise service_error_to_http(exc) from exc
