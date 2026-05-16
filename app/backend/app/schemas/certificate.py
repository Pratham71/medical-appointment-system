from datetime import date

from pydantic import BaseModel, Field


class CertificateCreate(BaseModel):
    certificate_type_id: int = Field(..., gt=0)
    issue_date: date | None = None
    leave_start_date: date | None = None
    leave_end_date: date | None = None
    certificate_notes: str | None = Field(default=None, max_length=1000)


class CertificateResponse(BaseModel):
    certificate_id: int
    appointment_id: int
    student_id: int
    student_name: str
    certificate_type_id: int
    certificate_type: str
    issue_date: date
    doctor_id: int
    doctor_name: str
    appointment_date: date
    appointment_reason: str | None = None
    diagnosis: str | None = None
    remarks: str | None = None
    leave_start_date: date | None = None
    leave_end_date: date | None = None
    certificate_notes: str | None = None
