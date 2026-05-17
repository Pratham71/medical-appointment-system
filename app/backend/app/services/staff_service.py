from app.backend.app.repositories import staff_repo
from app.backend.app.schemas.admin import (
    AdminAppointmentFilters,
    AdminAppointmentSummary,
)
from app.backend.app.schemas.staff import StaffDashboard


def get_dashboard() -> StaffDashboard:
    row = staff_repo.get_dashboard_counts() or {}
    return StaffDashboard(**row)


def list_appointments(
    filters: AdminAppointmentFilters,
) -> list[AdminAppointmentSummary]:
    rows = staff_repo.list_appointments(
        status=filters.status,
        from_date=filters.from_date,
        to_date=filters.to_date,
        limit=filters.limit,
    )
    return [AdminAppointmentSummary(**row) for row in rows]
