from fastapi import APIRouter, Depends

from app.backend.app.api.dependencies import require_student_id
from app.backend.app.api.errors import service_error_to_http
from app.backend.app.schemas.student import (
    StudentAppointmentSummary,
    StudentCertificateSummary,
    StudentDashboard,
    StudentReportSummary,
)
from app.backend.app.services import student_service

router = APIRouter(prefix="/students", tags=["Students"])


@router.get("/dashboard", response_model=StudentDashboard)
def dashboard(student_id: int = Depends(require_student_id)) -> StudentDashboard:
    try:
        return student_service.get_dashboard(student_id)
    except Exception as exc:
        raise service_error_to_http(exc) from exc


@router.get("/appointments", response_model=list[StudentAppointmentSummary])
def appointments(
    student_id: int = Depends(require_student_id),
) -> list[StudentAppointmentSummary]:
    try:
        return student_service.list_appointments(student_id)
    except Exception as exc:
        raise service_error_to_http(exc) from exc


@router.get("/reports", response_model=list[StudentReportSummary])
def reports(
    student_id: int = Depends(require_student_id),
) -> list[StudentReportSummary]:
    try:
        return student_service.list_reports(student_id)
    except Exception as exc:
        raise service_error_to_http(exc) from exc


@router.get("/certificates", response_model=list[StudentCertificateSummary])
def certificates(
    student_id: int = Depends(require_student_id),
) -> list[StudentCertificateSummary]:
    try:
        return student_service.list_certificates(student_id)
    except Exception as exc:
        raise service_error_to_http(exc) from exc
