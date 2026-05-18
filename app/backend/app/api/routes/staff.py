from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.backend.app.api.dependencies import require_roles
from app.backend.app.api.errors import service_error_to_http
from app.backend.app.schemas.admin import (
    AdminAppointmentFilters,
    AdminAppointmentSummary,
)
from app.backend.app.schemas.auth import AuthenticatedUser
from app.backend.app.schemas.appointment import AppointmentBookResponse
from app.backend.app.schemas.staff import (
    StaffDashboard,
    StaffPatientSearchResult,
    StaffWalkInAppointmentRequest,
)
from app.backend.app.services import staff_service

router = APIRouter(prefix="/staff", tags=["Staff"])


@router.get("/dashboard", response_model=StaffDashboard)
def dashboard(
    current_user: AuthenticatedUser = Depends(require_roles("staff", "admin")),
) -> StaffDashboard:
    """Return system-wide appointment statistics for the staff dashboard.

    Args:
        current_user: An authenticated staff or admin user.

    Returns:
        A StaffDashboard with today's appointment and emergency alert counts.
    """
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
    """Return a filtered list of appointments for staff review.

    Args:
        status: Optional appointment status to filter by.
        from_date: Optional start of the date range (inclusive).
        to_date: Optional end of the date range (inclusive).
        limit: Maximum number of results (1-250, default 100).
        current_user: An authenticated staff or admin user.

    Returns:
        List of AdminAppointmentSummary objects.

    Raises:
        HTTPException: 422 if to_date is before from_date.
    """
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


@router.get("/patients/search", response_model=list[StaffPatientSearchResult])
def search_patients(
    q: str = Query(..., min_length=2, max_length=100),
    limit: int = Query(default=10, ge=1, le=50),
    current_user: AuthenticatedUser = Depends(require_roles("staff", "admin")),
) -> list[StaffPatientSearchResult]:
    """Search existing patient profiles for staff walk-in booking.

    Args:
        q: Partial patient name, email, or roll number.
        limit: Maximum number of matches to return.
        current_user: An authenticated staff or admin user.

    Returns:
        Matching active patient profiles.
    """
    try:
        return staff_service.search_patients(q, limit)
    except Exception as exc:
        raise service_error_to_http(exc) from exc


@router.get("/walk-ins", response_model=list[AdminAppointmentSummary])
def walk_ins(
    status: str | None = Query(default=None, max_length=50),
    from_date: date | None = Query(default=None),
    to_date: date | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=250),
    current_user: AuthenticatedUser = Depends(require_roles("staff", "admin")),
) -> list[AdminAppointmentSummary]:
    """Return staff-created walk-in appointment bookings.

    Args:
        status: Optional appointment status to filter by.
        from_date: Optional start of the date range (inclusive).
        to_date: Optional end of the date range (inclusive).
        limit: Maximum number of results (1-250, default 100).
        current_user: An authenticated staff or admin user.

    Returns:
        List of walk-in appointment summary objects.

    Raises:
        HTTPException: 422 if to_date is before from_date.
    """
    if from_date is not None and to_date is not None and to_date < from_date:
        raise HTTPException(status_code=422, detail="to_date cannot be before from_date")
    try:
        filters = AdminAppointmentFilters(
            status=status,
            from_date=from_date,
            to_date=to_date,
            limit=limit,
        )
        return staff_service.list_walk_ins(filters)
    except Exception as exc:
        raise service_error_to_http(exc) from exc


@router.post(
    "/walk-ins/book",
    response_model=AppointmentBookResponse,
    status_code=status.HTTP_201_CREATED,
)
def book_walk_in(
    payload: StaffWalkInAppointmentRequest,
    current_user: AuthenticatedUser = Depends(require_roles("staff", "admin")),
) -> AppointmentBookResponse:
    """Book an existing patient into a slot as a staff-created walk-in.

    Args:
        payload: Existing patient ID, slot ID, and optional reason.
        current_user: An authenticated staff or admin user.

    Returns:
        Booking confirmation response.
    """
    try:
        return staff_service.book_walk_in(payload)
    except Exception as exc:
        raise service_error_to_http(exc) from exc
