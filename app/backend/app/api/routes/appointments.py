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
    try:
        return appointment_service.list_doctors_with_availability(for_date)
    except Exception as exc:
        raise service_error_to_http(exc) from exc


@router.get("/slots", response_model=list[AppointmentSlot])
def get_slots(
    from_date: date | None = Query(default=None),
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> list[AppointmentSlot]:
    try:
        return appointment_service.list_available_slots(from_date)
    except Exception as exc:
        raise service_error_to_http(exc) from exc


@router.post("/book", response_model=AppointmentBookResponse, status_code=201)
def book_appointment(
    payload: AppointmentBookRequest,
    student_id: int = Depends(require_student_id),
) -> AppointmentBookResponse:
    try:
        return appointment_service.book_appointment(payload, student_id)
    except Exception as exc:
        raise service_error_to_http(exc) from exc


@router.patch("/{appointment_id}/cancel", response_model=AppointmentStatusResponse)
def cancel_appointment(
    appointment_id: int = Path(..., gt=0),
    payload: AppointmentCancelRequest | None = None,
    current_user: AuthenticatedUser = Depends(
        require_roles("student", "doctor", "admin"),
    ),
) -> AppointmentStatusResponse:
    try:
        ensure_appointment_access(
            current_user,
            appointment_id,
            allow_student=True,
            allow_doctor=True,
            allow_admin=True,
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
