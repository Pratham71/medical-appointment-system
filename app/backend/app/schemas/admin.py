from datetime import date, datetime, time
from typing import Literal

from pydantic import BaseModel, Field, model_validator


AssignableRole = Literal[
    "student",
    "professor",
    "college-staff",
    "hostel-staff",
    "doctor",
    "staff",
    "admin",
]


class AdminDashboard(BaseModel):
    total_students: int = 0
    total_professors: int = 0
    total_doctors: int = 0
    total_staff: int = 0
    appointments_today: int = 0
    booked_appointments: int = 0
    completed_appointments: int = 0
    cancelled_appointments: int = 0
    reports_available: int = 0
    certificates_issued: int = 0
    emergency_alerts: int = 0


class AdminUserSummary(BaseModel):
    user_id: int
    name: str
    email: str
    role_name: str
    is_active: bool
    student_id: int | None = None
    staff_id: int | None = None


class AdminRoleAssignmentRequest(BaseModel):
    role_name: AssignableRole
    roll_number: str | None = Field(default=None, max_length=50)
    department: str | None = Field(default=None, max_length=120)
    year_level: int | None = Field(default=None, ge=1, le=6)
    employee_number: str | None = Field(default=None, max_length=50)
    specialization: str | None = Field(default=None, max_length=120)

    @model_validator(mode="after")
    def validate_required_profile_fields(self) -> "AdminRoleAssignmentRequest":
        if self.role_name in {
            "student",
            "professor",
            "college-staff",
            "hostel-staff",
        }:
            if not self.roll_number or not self.department or self.year_level is None:
                raise ValueError(
                    "roll_number, department, and year_level are required"
                )
        if self.role_name in {"doctor", "staff"} and not self.employee_number:
            raise ValueError("employee_number is required for doctor/staff role")
        return self


class AdminRoleAssignmentResponse(BaseModel):
    user_id: int
    name: str
    email: str
    role_name: str
    student_id: int | None = None
    staff_id: int | None = None
    message: str = "User role updated"


class AdminUserStatusResponse(BaseModel):
    user_id: int
    is_active: bool
    message: str


class AdminAppointmentFilters(BaseModel):
    status: str | None = Field(default=None, max_length=50)
    from_date: date | None = None
    to_date: date | None = None
    doctor_id: int | None = Field(default=None, gt=0)
    student_id: int | None = Field(default=None, gt=0)
    limit: int = Field(default=100, ge=1, le=250)

    @model_validator(mode="after")
    def validate_date_range(self) -> "AdminAppointmentFilters":
        if (
            self.from_date is not None
            and self.to_date is not None
            and self.to_date < self.from_date
        ):
            raise ValueError("to_date cannot be before from_date")
        return self


class AdminAppointmentSummary(BaseModel):
    appointment_id: int
    slot_date: date
    start_time: time
    end_time: time
    student_id: int
    student_name: str
    roll_number: str
    doctor_id: int
    doctor_name: str
    status: str
    reason: str | None = None
    cancellation_reason: str | None = None


class AdminStudentSummary(BaseModel):
    student_id: int
    student_name: str
    email: str
    roll_number: str
    department: str
    year_level: int
    role_name: str
    total_appointments: int = 0
    completed_appointments: int = 0


class AdminDoctorSummary(BaseModel):
    doctor_id: int
    doctor_name: str
    email: str
    employee_number: str
    specialization: str | None = None
    is_available_today: bool
    appointments_today: int = 0
    upcoming_appointments: int = 0


class AdminStaffSummary(BaseModel):
    staff_id: int
    staff_name: str
    email: str
    employee_number: str
    specialization: str | None = None
    is_doctor: bool


class AdminEmergencyAlertSummary(BaseModel):
    alert_id: int
    student_id: int
    student_name: str
    roll_number: str
    reason: str
    location: str
    contact_number: str | None = None
    message: str
    status: Literal["unread", "acknowledged", "resolved"]
    created_at: datetime
    acknowledged_by: int | None = None
    acknowledged_at: datetime | None = None
    resolved_by: int | None = None
    resolved_at: datetime | None = None
    resolution_note: str | None = None


class EmergencyAlertResolveRequest(BaseModel):
    resolution_note: str | None = Field(default=None, max_length=1000)
