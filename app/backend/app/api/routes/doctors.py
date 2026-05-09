from fastapi import APIRouter, Path, Query

from app.backend.app.api.errors import service_error_to_http
from app.backend.app.schemas.doctor import (
    DoctorAppointmentDetail,
    DoctorAppointmentSummary,
    DoctorDashboard,
    PatientHistoryItem,
)
from app.backend.app.services import doctor_service

router = APIRouter(prefix="/doctors", tags=["Doctors"])


@router.get("/dashboard", response_model=DoctorDashboard)
def dashboard(staff_id: int = Query(..., gt=0)) -> DoctorDashboard:
    try:
        return doctor_service.get_dashboard(staff_id)
    except Exception as exc:
        raise service_error_to_http(exc) from exc


@router.get("/appointments", response_model=list[DoctorAppointmentSummary])
def appointments(
    staff_id: int = Query(..., gt=0),
) -> list[DoctorAppointmentSummary]:
    try:
        return doctor_service.list_appointments(staff_id)
    except Exception as exc:
        raise service_error_to_http(exc) from exc


@router.get("/appointment/{appointment_id}", response_model=DoctorAppointmentDetail)
def appointment_detail(
    appointment_id: int = Path(..., gt=0),
) -> DoctorAppointmentDetail:
    try:
        return doctor_service.get_appointment_detail(appointment_id)
    except Exception as exc:
        raise service_error_to_http(exc) from exc


@router.get("/patient-history/{student_id}", response_model=list[PatientHistoryItem])
def patient_history(
    student_id: int = Path(..., gt=0),
) -> list[PatientHistoryItem]:
    try:
        return doctor_service.list_patient_history(student_id)
    except Exception as exc:
        raise service_error_to_http(exc) from exc
