from datetime import date

from pydantic import BaseModel, Field


class CertificateCreate(BaseModel):
    certificate_type_id: int = Field(..., gt=0)
    issue_date: date | None = None


class CertificateResponse(BaseModel):
    certificate_id: int
    appointment_id: int
    student_id: int
    student_name: str
    certificate_type_id: int
    certificate_type: str
    issue_date: date
