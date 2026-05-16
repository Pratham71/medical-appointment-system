from datetime import date, time
from typing import Literal

from pydantic import BaseModel, Field, model_validator


AppointmentCancelReasonCode = Literal[
    "no_show",
    "student_request",
    "doctor_unavailable",
    "emergency_priority",
    "duplicate_booking",
    "other",
]


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


class AppointmentSlotWithStatus(BaseModel):
    slot_id: int
    doctor_id: int
    doctor_name: str
    slot_date: date
    start_time: time
    end_time: time
    is_available: bool
    appointment_status: str | None = None  # 'booked' | 'completed' | None


class AppointmentBookRequest(BaseModel):
    slot_id: int = Field(..., gt=0)
    reason: str | None = Field(default=None, max_length=500)


class AppointmentCancelRequest(BaseModel):
    reason_code: AppointmentCancelReasonCode
    note: str | None = Field(default=None, max_length=500)

    @model_validator(mode="after")
    def normalize_note(self) -> "AppointmentCancelRequest":
        if self.note is not None:
            self.note = self.note.strip() or None
        return self


class AppointmentBookResponse(BaseModel):
    appointment_id: int | None = None
    slot_id: int
    status: str
    message: str


class AppointmentStatusResponse(BaseModel):
    appointment_id: int
    status: str
    message: str
