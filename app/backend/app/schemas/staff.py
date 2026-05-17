from pydantic import BaseModel


class StaffDashboard(BaseModel):
    appointments_today: int = 0
    booked_appointments: int = 0
    cancelled_today: int = 0
    emergency_alerts: int = 0
