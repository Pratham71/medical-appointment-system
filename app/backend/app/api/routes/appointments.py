from datetime import date

from fastapi import APIRouter, Depends, Path, Query

from app.backend.app.api.dependencies import (
    ensure_appointment_access,
    get_current_user,
    require_roles,
    require_student_id,
)
from app.backend.app.api.errors import service_error_to_http
from app.backend.app.schemas.appointment import (
    AppointmentBookRequest,
    AppointmentBookResponse,
    AppointmentCancelRequest,
    AppointmentSlot,
    AppointmentSlotWithStatus,
    AppointmentStatusResponse,
    DoctorAvailabilityStatus,
)
from app.backend.app.schemas.auth import AuthenticatedUser
from app.backend.app.services import appointment_service

router = APIRouter(prefix="/appointments", tags=["Appointments"])


@router.get("/doctors", response_model=list[DoctorAvailabilityStatus])
def get_doctors(
    for_date: date | None = Query(default=None),
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> list[DoctorAvailabilityStatus]:
    """Return all doctors with computed availability status for a date.

    Args:
        for_date: Calendar date to evaluate; defaults to today.
        current_user: Any authenticated user.

    Returns:
        List of DoctorAvailabilityStatus objects.
    """
    try:
        return appointment_service.list_doctors_with_availability(for_date)
    except Exception as exc:
        raise service_error_to_http(exc) from exc


@router.get("/slots/all", response_model=list[AppointmentSlotWithStatus])
def get_all_slots_for_doctor(
    doctor_id: int = Query(..., gt=0),
    slot_date: date = Query(...),
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> list[AppointmentSlotWithStatus]:
    """Return all slots for a doctor on a date, including booked ones.

    Args:
        doctor_id: Primary key of the doctor's staff record.
        slot_date: Calendar date to query.
        current_user: Any authenticated user.

    Returns:
        List of AppointmentSlotWithStatus objects.
    """
    try:
        return appointment_service.list_all_slots_for_doctor(doctor_id, slot_date)
    except Exception as exc:
        raise service_error_to_http(exc) from exc


@router.get("/slots", response_model=list[AppointmentSlot])
def get_slots(
    from_date: date | None = Query(default=None),
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> list[AppointmentSlot]:
    """Return available appointment slots for a date.

    Args:
        from_date: Calendar date to query; defaults to today.
        current_user: Any authenticated user.

    Returns:
        List of bookable AppointmentSlot objects.
    """
    try:
        return appointment_service.list_available_slots(from_date)
    except Exception as exc:
        raise service_error_to_http(exc) from exc


@router.post("/book", response_model=AppointmentBookResponse, status_code=201)
def book_appointment(
    payload: AppointmentBookRequest,
    student_id: int = Depends(require_student_id),
) -> AppointmentBookResponse:
    """Book an appointment slot for the authenticated student.

    Args:
        payload: Booking request with slot_id and optional reason.
        student_id: Resolved student_id of the authenticated user.

    Returns:
        An AppointmentBookResponse with appointment_id and status.

    Raises:
        HTTPException: 404 if the slot is not found; 409 if already booked or elapsed.
    """
    try:
        return appointment_service.book_appointment(payload, student_id)
    except Exception as exc:
        raise service_error_to_http(exc) from exc


@router.patch("/{appointment_id}/cancel", response_model=AppointmentStatusResponse)
def cancel_appointment(
    appointment_id: int = Path(..., gt=0),
    payload: AppointmentCancelRequest | None = None,
    current_user: AuthenticatedUser = Depends(
        require_roles(
            "student",
            "professor",
            "college-staff",
            "hostel-staff",
            "doctor",
            "staff",
            "admin",
        ),
    ),
) -> AppointmentStatusResponse:
    """Cancel an appointment; doctor/staff/admin callers must supply a reason.

    Args:
        appointment_id: Primary key of the appointment to cancel.
        payload: Cancellation reason; required for doctor, staff, and admin roles.
        current_user: The authenticated user; any role may cancel their own appointment.

    Returns:
        An AppointmentStatusResponse confirming cancellation.

    Raises:
        HTTPException: 403 if access is denied; 404 if not found; 409 if the
            status transition is not permitted.
    """
    try:
        ensure_appointment_access(
            current_user,
            appointment_id,
            allow_student=True,
            allow_doctor=True,
            allow_admin=True,
            allow_staff=True,
        )
        return appointment_service.cancel_appointment(
            appointment_id,
            payload,
            actor_role=current_user.role_name,
        )
    except Exception as exc:
        raise service_error_to_http(exc) from exc


@router.patch("/{appointment_id}/complete", response_model=AppointmentStatusResponse)
def complete_appointment(
    appointment_id: int = Path(..., gt=0),
    current_user: AuthenticatedUser = Depends(require_roles("doctor", "admin")),
) -> AppointmentStatusResponse:
    """Mark an appointment as completed (doctors and admins only).

    Args:
        appointment_id: Primary key of the appointment to complete.
        current_user: An authenticated doctor or admin.

    Returns:
        An AppointmentStatusResponse confirming completion.

    Raises:
        HTTPException: 403 if access is denied; 404 if not found; 409 if the
            status transition is not permitted.
    """
    try:
        ensure_appointment_access(
            current_user,
            appointment_id,
            allow_student=False,
            allow_doctor=True,
            allow_admin=True,
        )
        return appointment_service.complete_appointment(appointment_id)
    except Exception as exc:
        raise service_error_to_http(exc) from exc
