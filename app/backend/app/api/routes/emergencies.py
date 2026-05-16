from fastapi import APIRouter, Depends

from app.backend.app.api.dependencies import require_student_id
from app.backend.app.api.errors import service_error_to_http
from app.backend.app.schemas.emergency import (
    EmergencyAlertRequest,
    EmergencyAlertResponse,
)
from app.backend.app.services import emergency_service


router = APIRouter(prefix="/emergency", tags=["Emergency"])


@router.post("/alert", response_model=EmergencyAlertResponse, status_code=201)
def send_alert(
    payload: EmergencyAlertRequest,
    student_id: int = Depends(require_student_id),
) -> EmergencyAlertResponse:
    try:
        return emergency_service.create_alert(
            student_id=student_id,
            message=payload.message,
        )
    except Exception as exc:
        raise service_error_to_http(exc) from exc
