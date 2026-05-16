from datetime import datetime

from pydantic import BaseModel, Field


class EmergencyAlertRequest(BaseModel):
    message: str | None = Field(default=None, max_length=500)


class EmergencyAlertResponse(BaseModel):
    alert_id: int
    student_id: int
    student_name: str
    roll_number: str
    message: str
    created_at: datetime
