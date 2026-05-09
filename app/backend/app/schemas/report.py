from datetime import date, time

from pydantic import BaseModel, Field


class MedicalNoteCreate(BaseModel):
    diagnosis: str = Field(..., min_length=1, max_length=255)
    remarks: str | None = Field(default=None, max_length=1000)


class MedicalNoteResponse(BaseModel):
    note_id: int
    appointment_id: int
    diagnosis: str
    remarks: str | None = None


class PrescriptionItemCreate(BaseModel):
    medicine_name: str = Field(..., min_length=1, max_length=255)
    dosage: str = Field(..., min_length=1, max_length=255)


class PrescriptionCreate(BaseModel):
    items: list[PrescriptionItemCreate] = Field(..., min_length=1)


class PrescriptionItemResponse(BaseModel):
    item_id: int
    medicine_name: str
    dosage: str


class PrescriptionResponse(BaseModel):
    prescription_id: int
    appointment_id: int
    items: list[PrescriptionItemResponse] = Field(default_factory=list)


class ReportAppointmentSummary(BaseModel):
    appointment_id: int
    student_id: int
    student_name: str
    doctor_id: int
    doctor_name: str
    slot_date: date
    start_time: time
    end_time: time
    status: str


class ReportDetail(BaseModel):
    appointment: ReportAppointmentSummary
    note: MedicalNoteResponse | None = None
    prescription: PrescriptionResponse | None = None
