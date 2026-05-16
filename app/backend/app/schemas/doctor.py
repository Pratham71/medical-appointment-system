from datetime import date, time

from pydantic import BaseModel, Field, model_validator


class DoctorDashboard(BaseModel):
    doctor_id: int
    doctor_name: str
    todays_appointments: int = 0
    upcoming_appointments: int = 0
    completed_appointments: int = 0
    total_patients: int = 0


class DoctorAppointmentSummary(BaseModel):
    appointment_id: int
    slot_date: date
    start_time: time
    end_time: time
    student_id: int
    student_name: str
    status: str


class DoctorAppointmentDetail(BaseModel):
    appointment_id: int
    slot_date: date
    start_time: time
    end_time: time
    status: str
    student_id: int
    student_name: str
    student_email: str
    doctor_id: int
    doctor_name: str
    reason: str | None = None
    diagnosis: str | None = None
    remarks: str | None = None
    certificate_id: int | None = None
    certificate_type: str | None = None


class PatientHistoryItem(BaseModel):
    appointment_id: int
    slot_date: date
    start_time: time
    end_time: time
    doctor_id: int
    doctor_name: str
    status: str
    reason: str | None = None
    diagnosis: str | None = None
    remarks: str | None = None
    certificate_id: int | None = None
    certificate_type: str | None = None


class PatientSearchResult(BaseModel):
    student_id: int
    student_name: str
    roll_number: str
    department: str
    year_level: int


class DoctorAvailabilityUpdate(BaseModel):
    is_available: bool
    start_time: time | None = None
    end_time: time | None = None

    @model_validator(mode="after")
    def validate_time_range(self) -> "DoctorAvailabilityUpdate":
        if (self.start_time is None) != (self.end_time is None):
            raise ValueError("Start and end time must be provided together")
        if (
            self.start_time is not None
            and self.end_time is not None
            and self.end_time <= self.start_time
        ):
            raise ValueError("End time must be after start time")
        return self


class DoctorAvailabilityOverrideUpdate(DoctorAvailabilityUpdate):
    note: str | None = Field(default=None, max_length=255)


class DoctorWeeklyAvailability(BaseModel):
    weekday: int = Field(..., ge=0, le=6)
    weekday_name: str
    is_available: bool
    start_time: time | None = None
    end_time: time | None = None


class DoctorAvailabilityOverride(BaseModel):
    override_date: date
    is_available: bool
    start_time: time | None = None
    end_time: time | None = None
    note: str | None = None


class DoctorAvailabilitySettings(BaseModel):
    doctor_id: int
    weekly_availability: list[DoctorWeeklyAvailability]
    date_overrides: list[DoctorAvailabilityOverride]


class DoctorAvailabilityDeleteResponse(BaseModel):
    message: str
