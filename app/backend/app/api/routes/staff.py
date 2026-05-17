from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query

from app.backend.app.api.dependencies import require_roles
from app.backend.app.api.errors import service_error_to_http
from app.backend.app.schemas.admin import (
    AdminAppointmentFilters,
    AdminAppointmentSummary,
)
from app.backend.app.schemas.auth import AuthenticatedUser
from app.backend.app.schemas.staff import StaffDashboard
from app.backend.app.services import staff_service

router = APIRouter(prefix="/staff", tags=["Staff"])


@router.get("/dashboard", response_model=StaffDashboard)
def dashboard(
    current_user: AuthenticatedUser = Depends(require_roles("staff", "admin")),
) -> StaffDashboard:
    try:
        return staff_service.get_dashboard()
    except Exception as exc:
        raise service_error_to_http(exc) from exc


@router.get("/appointments", response_model=list[AdminAppointmentSummary])
def appointments(
    status: str | None = Query(default=None, max_length=50),
    from_date: date | None = Query(default=None),
    to_date: date | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=250),
    current_user: AuthenticatedUser = Depends(require_roles("staff", "admin")),
) -> list[AdminAppointmentSummary]:
    if from_date is not None and to_date is not None and to_date < from_date:
        raise HTTPException(status_code=422, detail="to_date cannot be before from_date")
    try:
        filters = AdminAppointmentFilters(
            status=status,
            from_date=from_date,
            to_date=to_date,
            limit=limit,
        )
        return staff_service.list_appointments(filters)
    except Exception as exc:
        raise service_error_to_http(exc) from exc
