from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class EmergencyAlertRequest(BaseModel):
    reason: str = Field(min_length=1, max_length=120)
    location: str = Field(min_length=1, max_length=255)
    contact_number: str | None = Field(default=None, max_length=30)
    message: str | None = Field(default=None, max_length=500)


class EmergencyAlertResponse(BaseModel):
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
