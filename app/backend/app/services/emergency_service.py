from app.backend.app.api.errors import NotFoundError
from app.backend.app.repositories import emergency_repo
from app.backend.app.schemas.emergency import EmergencyAlertResponse


_DEFAULT_MESSAGE = "Student requested emergency assistance"


def create_alert(
    student_id: int,
    message: str | None,
) -> EmergencyAlertResponse:
    alert_message = message.strip() if message and message.strip() else _DEFAULT_MESSAGE
    row = emergency_repo.create_alert(
        student_id=student_id,
        message=alert_message,
    )
    if row is None:
        raise NotFoundError("Emergency alert was not created")
    return EmergencyAlertResponse(**row)
