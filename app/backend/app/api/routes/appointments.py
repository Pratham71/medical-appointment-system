from datetime import date

from fastapi import APIRouter, Path, Query

from app.backend.app.api.errors import service_error_to_http
from app.backend.app.schemas.appointment import (
    AppointmentBookRequest,
    AppointmentBookResponse,
    AppointmentSlot,
    AppointmentStatusResponse,
)
from app.backend.app.services import appointment_service

router = APIRouter(prefix="/appointments", tags=["Appointments"])


@router.get("/slots", response_model=list[AppointmentSlot])
def get_slots(from_date: date | None = Query(default=None)) -> list[AppointmentSlot]:
    try:
        return appointment_service.list_available_slots(from_date)
    except Exception as exc:
        raise service_error_to_http(exc) from exc


@router.post("/book", response_model=AppointmentBookResponse, status_code=201)
def book_appointment(payload: AppointmentBookRequest) -> AppointmentBookResponse:
    try:
        return appointment_service.book_appointment(payload)
    except Exception as exc:
        raise service_error_to_http(exc) from exc


@router.patch("/{appointment_id}/cancel", response_model=AppointmentStatusResponse)
def cancel_appointment(
    appointment_id: int = Path(..., gt=0),
) -> AppointmentStatusResponse:
    try:
        return appointment_service.cancel_appointment(appointment_id)
    except Exception as exc:
        raise service_error_to_http(exc) from exc


@router.patch("/{appointment_id}/complete", response_model=AppointmentStatusResponse)
def complete_appointment(
    appointment_id: int = Path(..., gt=0),
) -> AppointmentStatusResponse:
    try:
        return appointment_service.complete_appointment(appointment_id)
    except Exception as exc:
        raise service_error_to_http(exc) from exc
