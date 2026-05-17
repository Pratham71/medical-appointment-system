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
    """Return dashboard statistics for the authenticated doctor.

    Args:
        staff_id: Resolved staff_id of the authenticated doctor.

    Returns:
        A DoctorDashboard with appointment counts and patient totals.

    Raises:
        HTTPException: 404 if the doctor does not exist.
    """
    try:
        return doctor_service.get_dashboard(staff_id)
    except Exception as exc:
        raise service_error_to_http(exc) from exc


@router.get("/appointments", response_model=list[DoctorAppointmentSummary])
def appointments(
    staff_id: int = Depends(require_doctor_staff_id),
) -> list[DoctorAppointmentSummary]:
    """Return all appointments assigned to the authenticated doctor.

    Args:
        staff_id: Resolved staff_id of the authenticated doctor.

    Returns:
        List of DoctorAppointmentSummary objects ordered by date and time.
    """
    try:
        return doctor_service.list_appointments(staff_id)
    except Exception as exc:
        raise service_error_to_http(exc) from exc


@router.get("/availability", response_model=DoctorAvailabilitySettings)
def availability(
    staff_id: int = Depends(require_doctor_staff_id),
) -> DoctorAvailabilitySettings:
    """Return the full availability configuration for the authenticated doctor.

    Args:
        staff_id: Resolved staff_id of the authenticated doctor.

    Returns:
        A DoctorAvailabilitySettings object with weekly rules and date overrides.
    """
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
    """Update the recurring availability rule for a specific weekday.

    Args:
        payload: Availability update including is_available, start_time, and end_time.
        weekday: Day of the week (0 = Monday, 6 = Sunday).
        staff_id: Resolved staff_id of the authenticated doctor.

    Returns:
        A DoctorWeeklyAvailability object with the saved rule.
    """
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
    """Create or update a date-specific availability override.

    Existing booked appointments on the blocked date are automatically cancelled.

    Args:
        payload: Override details including is_available, times, and note.
        override_date: The calendar date to override.
        staff_id: Resolved staff_id of the authenticated doctor.

    Returns:
        A DoctorAvailabilityOverride reflecting the saved override.
    """
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
    """Remove a date-specific availability override.

    Args:
        override_date: The calendar date whose override to remove.
        staff_id: Resolved staff_id of the authenticated doctor.

    Returns:
        A DoctorAvailabilityDeleteResponse with a confirmation message.
    """
    try:
        return doctor_service.delete_availability_override(staff_id, override_date)
    except Exception as exc:
        raise service_error_to_http(exc) from exc


@router.get("/patients/search", response_model=list[PatientSearchResult])
def search_patients(
    q: str = Query(..., min_length=2, max_length=120),
    current_user: AuthenticatedUser = Depends(require_roles("doctor", "admin")),
) -> list[PatientSearchResult]:
    """Search patients by name or roll number.

    Doctors are restricted to patients they have previously seen; admins see all.

    Args:
        q: Search term (minimum 2 characters).
        current_user: An authenticated doctor or admin.

    Returns:
        Up to 10 PatientSearchResult objects.
    """
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
    """Return full appointment detail for a doctor or admin.

    Args:
        appointment_id: Primary key of the appointment.
        current_user: An authenticated doctor (own appointments only) or admin.

    Returns:
        A DoctorAppointmentDetail object.

    Raises:
        HTTPException: 403 if access is denied; 404 if not found.
    """
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
    """Return a patient's appointment history (accessible to treating doctors and admins).

    Args:
        student_id: Primary key of the student profile.
        current_user: An authenticated doctor who has seen the student, or an admin.

    Returns:
        List of PatientHistoryItem objects in reverse chronological order.

    Raises:
        HTTPException: 403 if the doctor has not seen this student.
    """
    try:
        ensure_student_record_access(current_user, student_id)
        return doctor_service.list_patient_history(student_id)
    except Exception as exc:
        raise service_error_to_http(exc) from exc
