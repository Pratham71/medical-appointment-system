from app.backend.app.api.errors import NotFoundError
from app.backend.app.repositories import emergency_repo
from app.backend.app.schemas.emergency import EmergencyAlertResponse


_DEFAULT_MESSAGE = "Student requested emergency assistance"


def create_alert(
    student_id: int,
    *,
    reason: str,
    location: str,
    contact_number: str | None,
    message: str | None,
) -> EmergencyAlertResponse:
    """Create a new emergency alert for a student.

    Args:
        student_id: Primary key of the student raising the alert.
        reason: Category or short description of the emergency.
        location: Current location of the student.
        contact_number: Optional phone number for follow-up contact.
        message: Optional detailed description; defaults to a standard message if blank.

    Returns:
        An EmergencyAlertResponse with the created alert's data.

    Raises:
        NotFoundError: If the alert cannot be retrieved after creation.
    """
    alert_message = message.strip() if message and message.strip() else _DEFAULT_MESSAGE
    row = emergency_repo.create_alert(
        student_id=student_id,
        reason=reason.strip(),
        location=location.strip(),
        contact_number=contact_number.strip() if contact_number else None,
        message=alert_message,
    )
    if row is None:
        raise NotFoundError("Emergency alert was not created")
    return EmergencyAlertResponse(**row)
