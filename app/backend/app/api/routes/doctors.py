from datetime import date

from fastapi import APIRouter, Depends, Path, Query

from app.backend.app.api.dependencies import (
    ensure_appointment_access,
    ensure_student_record_access,
    require_doctor_staff_id,
    require_roles,
)
from app.backend.app.api.errors import service_error_to_http
from app.backend.app.schemas.auth import AuthenticatedUser
from app.backend.app.schemas.doctor import (
    DoctorAvailabilityDeleteResponse,
    DoctorAvailabilityOverride,
    DoctorAvailabilityOverrideUpdate,
    DoctorAvailabilitySettings,
    DoctorAvailabilityUpdate,
    DoctorWeeklyAvailability,
    DoctorAppointmentDetail,
    DoctorAppointmentSummary,
    DoctorDashboard,
    PatientHistoryItem,
    PatientSearchResult,
)
from app.backend.app.services import auth_service, doctor_service

router = APIRouter(prefix="/doctors", tags=["Doctors"])


@router.get("/dashboard", response_model=DoctorDashboard)
def dashboard(staff_id: int = Depends(require_doctor_staff_id)) -> DoctorDashboard:
    try:
        return doctor_service.get_dashboard(staff_id)
    except Exception as exc:
        raise service_error_to_http(exc) from exc


@router.get("/appointments", response_model=list[DoctorAppointmentSummary])
def appointments(
    staff_id: int = Depends(require_doctor_staff_id),
) -> list[DoctorAppointmentSummary]:
    try:
        return doctor_service.list_appointments(staff_id)
    except Exception as exc:
        raise service_error_to_http(exc) from exc


@router.get("/availability", response_model=DoctorAvailabilitySettings)
def availability(
    staff_id: int = Depends(require_doctor_staff_id),
) -> DoctorAvailabilitySettings:
    try:
        return doctor_service.get_availability(staff_id)
    except Exception as exc:
        raise service_error_to_http(exc) from exc


@router.put(
    "/availability/weekly/{weekday}",
    response_model=DoctorWeeklyAvailability,
)
def update_weekly_availability(
    payload: DoctorAvailabilityUpdate,
    weekday: int = Path(..., ge=0, le=6),
    staff_id: int = Depends(require_doctor_staff_id),
) -> DoctorWeeklyAvailability:
    try:
        return doctor_service.upsert_weekly_availability(staff_id, weekday, payload)
    except Exception as exc:
        raise service_error_to_http(exc) from exc


@router.put(
    "/availability/overrides/{override_date}",
    response_model=DoctorAvailabilityOverride,
)
def update_availability_override(
    payload: DoctorAvailabilityOverrideUpdate,
    override_date: date = Path(...),
    staff_id: int = Depends(require_doctor_staff_id),
) -> DoctorAvailabilityOverride:
    try:
        return doctor_service.upsert_availability_override(
            staff_id,
            override_date,
            payload,
        )
    except Exception as exc:
        raise service_error_to_http(exc) from exc


@router.delete(
    "/availability/overrides/{override_date}",
    response_model=DoctorAvailabilityDeleteResponse,
)
def delete_availability_override(
    override_date: date = Path(...),
    staff_id: int = Depends(require_doctor_staff_id),
) -> DoctorAvailabilityDeleteResponse:
    try:
        return doctor_service.delete_availability_override(staff_id, override_date)
    except Exception as exc:
        raise service_error_to_http(exc) from exc


@router.get("/patients/search", response_model=list[PatientSearchResult])
def search_patients(
    q: str = Query(..., min_length=2, max_length=120),
    current_user: AuthenticatedUser = Depends(require_roles("doctor", "admin")),
) -> list[PatientSearchResult]:
    try:
        staff_id = None
        if current_user.role_name.lower() == "doctor":
            staff_id = auth_service.get_staff_id_for_user(current_user.user_id)
        return doctor_service.search_patients(q, staff_id)
    except Exception as exc:
        raise service_error_to_http(exc) from exc


@router.get("/appointment/{appointment_id}", response_model=DoctorAppointmentDetail)
def appointment_detail(
    appointment_id: int = Path(..., gt=0),
    current_user: AuthenticatedUser = Depends(require_roles("doctor", "admin")),
) -> DoctorAppointmentDetail:
    try:
        ensure_appointment_access(
            current_user,
            appointment_id,
            allow_student=False,
            allow_doctor=True,
            allow_admin=True,
        )
        return doctor_service.get_appointment_detail(appointment_id)
    except Exception as exc:
        raise service_error_to_http(exc) from exc


@router.get("/patient-history/{student_id}", response_model=list[PatientHistoryItem])
def patient_history(
    student_id: int = Path(..., gt=0),
    current_user: AuthenticatedUser = Depends(require_roles("doctor", "admin")),
) -> list[PatientHistoryItem]:
    try:
        ensure_student_record_access(current_user, student_id)
        return doctor_service.list_patient_history(student_id)
    except Exception as exc:
        raise service_error_to_http(exc) from exc
