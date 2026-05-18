from pydantic import BaseModel, Field, model_validator


class StaffDashboard(BaseModel):
    appointments_today: int = 0
    booked_appointments: int = 0
    cancelled_today: int = 0
    emergency_alerts: int = 0


class StaffPatientSearchResult(BaseModel):
    student_id: int
    student_name: str
    email: str
    roll_number: str
    department: str
    year_level: int
    role_name: str


class StaffWalkInAppointmentRequest(BaseModel):
    student_id: int = Field(..., gt=0)
    slot_id: int = Field(..., gt=0)
    reason: str | None = Field(default=None, max_length=500)

    @model_validator(mode="after")
    def normalize_reason(self) -> "StaffWalkInAppointmentRequest":
        if self.reason is not None:
            self.reason = self.reason.strip() or None
        return self
