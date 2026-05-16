from datetime import date, time

from pydantic import BaseModel, Field


class AppointmentSlot(BaseModel):
    slot_id: int
    doctor_id: int
    doctor_name: str
    slot_date: date
    start_time: time
    end_time: time


class DoctorAvailabilityStatus(BaseModel):
    doctor_id: int
    doctor_name: str
    specialization: str | None = None
    is_available: bool
    available_slots: int = 0
    unavailability_note: str | None = None


class AppointmentBookRequest(BaseModel):
    slot_id: int = Field(..., gt=0)
    reason: str | None = Field(default=None, max_length=500)


class AppointmentBookResponse(BaseModel):
    appointment_id: int | None = None
    slot_id: int
    status: str
    message: str


class AppointmentStatusResponse(BaseModel):
    appointment_id: int
    status: str
    message: str
