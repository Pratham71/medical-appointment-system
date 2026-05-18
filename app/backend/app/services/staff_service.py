from app.backend.app.api.errors import NotFoundError
from app.backend.app.repositories import staff_repo
from app.backend.app.schemas.admin import (
    AdminAppointmentFilters,
    AdminAppointmentSummary,
)
from app.backend.app.schemas.appointment import (
    AppointmentBookRequest,
    AppointmentBookResponse,
)
from app.backend.app.schemas.staff import (
    StaffDashboard,
    StaffPatientSearchResult,
    StaffWalkInAppointmentRequest,
)
from app.backend.app.services import appointment_service


_DEFAULT_WALK_IN_REASON = "Walk-in consultation"


def get_dashboard() -> StaffDashboard:
    """Return system-wide appointment statistics for the staff dashboard.

    Returns:
        A StaffDashboard object with today's counts and emergency alert totals.
    """
    row = staff_repo.get_dashboard_counts() or {}
    return StaffDashboard(**row)


def list_appointments(
    filters: AdminAppointmentFilters,
) -> list[AdminAppointmentSummary]:
    """Return a filtered list of appointments for staff review.

    Args:
        filters: Filter criteria including status, date range, and pagination limit.

    Returns:
        List of AdminAppointmentSummary objects.
    """
    rows = staff_repo.list_appointments(
        status=filters.status,
        from_date=filters.from_date,
        to_date=filters.to_date,
        limit=filters.limit,
    )
    return [AdminAppointmentSummary(**row) for row in rows]


def list_walk_ins(
    filters: AdminAppointmentFilters,
) -> list[AdminAppointmentSummary]:
    """Return staff-created walk-in bookings.

    Args:
        filters: Filter criteria including status, date range, and pagination limit.

    Returns:
        List of walk-in appointment summaries.
    """
    rows = staff_repo.list_walk_ins(
        status=filters.status,
        from_date=filters.from_date,
        to_date=filters.to_date,
        limit=filters.limit,
    )
    return [AdminAppointmentSummary(**row) for row in rows]


def search_patients(q: str, limit: int) -> list[StaffPatientSearchResult]:
    """Search existing active patients for staff walk-in booking.

    Args:
        q: Partial patient name, email, or roll number.
        limit: Maximum number of rows to return.

    Returns:
        List of matching patient summaries.
    """
    rows = staff_repo.search_patients(q.strip(), limit)
    return [StaffPatientSearchResult(**row) for row in rows]


def book_walk_in(
    payload: StaffWalkInAppointmentRequest,
) -> AppointmentBookResponse:
    """Book a walk-in appointment for an existing patient.

    Args:
        payload: Existing patient ID, slot ID, and optional walk-in reason.

    Returns:
        Appointment booking response.

    Raises:
        NotFoundError: If the selected patient profile does not exist.
    """
    patient = staff_repo.get_patient_by_student_id(payload.student_id)
    if patient is None:
        raise NotFoundError("Patient was not found")

    reason = _format_walk_in_reason(payload.reason)
    response = appointment_service.book_appointment(
        AppointmentBookRequest(slot_id=payload.slot_id, reason=reason),
        payload.student_id,
    )
    response.message = "Walk-in appointment booked"
    return response


def _format_walk_in_reason(reason: str | None) -> str:
    """Return a reason string that clearly marks the appointment as a walk-in."""
    if not reason:
        return _DEFAULT_WALK_IN_REASON
    return f"{_DEFAULT_WALK_IN_REASON}: {reason}"
