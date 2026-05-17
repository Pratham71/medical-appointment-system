from dataclasses import dataclass
from email.message import EmailMessage
import smtplib
from typing import Any

from app.backend.app.core.config import Settings, get_settings
from app.backend.app.repositories import notification_repo


@dataclass(frozen=True)
class NotificationDispatchResult:
    status: str
    detail: str | None = None


@dataclass(frozen=True)
class NotificationEmail:
    to_email: str
    subject: str
    body: str


def dispatch_email(
    *,
    to_email: str,
    subject: str,
    body: str,
) -> NotificationDispatchResult:
    """Send a plain-text email via SMTP, returning a result indicating success or failure.

    Args:
        to_email: Recipient email address.
        subject: Email subject line.
        body: Plain-text email body.

    Returns:
        A NotificationDispatchResult with status "sent", "failed", or "disabled".
    """
    settings = get_settings()
    if (
        not settings.email_notifications_enabled
        or not settings.smtp_host
        or not settings.smtp_from_email
    ):
        return NotificationDispatchResult(status="disabled")

    message = NotificationEmail(to_email=to_email, subject=subject, body=body)
    try:
        _send_smtp(message, settings)
    except Exception as exc:
        return NotificationDispatchResult(status="failed", detail=str(exc))
    return NotificationDispatchResult(status="sent")


def send_appointment_booked(appointment_id: int) -> NotificationDispatchResult:
    """Send an appointment booking confirmation email to the student.

    Args:
        appointment_id: Primary key of the booked appointment.

    Returns:
        A NotificationDispatchResult indicating dispatch status.
    """
    return _send_appointment_email(
        appointment_id,
        subject="Appointment booked",
        intro="Your infirmary appointment has been booked.",
    )


def send_appointment_cancelled(appointment_id: int) -> NotificationDispatchResult:
    """Send an appointment cancellation email to the student with the cancellation reason.

    Args:
        appointment_id: Primary key of the cancelled appointment.

    Returns:
        A NotificationDispatchResult indicating dispatch status, or "skipped" if
        the appointment context cannot be found.
    """
    context = notification_repo.get_appointment_notification_context(appointment_id)
    if context is None:
        return NotificationDispatchResult(status="skipped", detail="Appointment not found")

    reason = context.get("cancellation_reason") or "No reason provided"
    body = "\n".join(
        [
            f"Hello {context['student_name']},",
            "Your infirmary appointment has been cancelled.",
            f"Doctor: {context['doctor_name']}",
            f"Date: {context['slot_date']}",
            f"Time: {_time_range(context)}",
            f"Reason: {reason}",
        ]
    )
    return dispatch_email(
        to_email=context["student_email"],
        subject="Appointment cancelled",
        body=body,
    )


def send_report_available(appointment_id: int) -> NotificationDispatchResult:
    """Notify the student that a medical report or prescription has been updated.

    Args:
        appointment_id: Primary key of the appointment whose report was updated.

    Returns:
        A NotificationDispatchResult indicating dispatch status.
    """
    return _send_appointment_email(
        appointment_id,
        subject="Medical report available",
        intro="Your medical report or prescription has been updated.",
    )


def send_certificate_available(
    appointment_id: int,
    certificate_type: str,
) -> NotificationDispatchResult:
    """Notify the student that a medical certificate is available.

    Args:
        appointment_id: Primary key of the appointment the certificate belongs to.
        certificate_type: Human-readable certificate type name (e.g. "Medical Leave").

    Returns:
        A NotificationDispatchResult indicating dispatch status.
    """
    return _send_appointment_email(
        appointment_id,
        subject=f"{certificate_type} available",
        intro=f"Your {certificate_type} is available in the infirmary portal.",
    )


def _send_appointment_email(
    appointment_id: int,
    *,
    subject: str,
    intro: str,
) -> NotificationDispatchResult:
    """Build and dispatch a standard appointment email to the student.

    Args:
        appointment_id: Primary key of the appointment to look up.
        subject: Email subject line.
        intro: Opening sentence that appears after the greeting.

    Returns:
        A NotificationDispatchResult indicating dispatch status, or "skipped" if
        the appointment context cannot be found.
    """
    context = notification_repo.get_appointment_notification_context(appointment_id)
    if context is None:
        return NotificationDispatchResult(status="skipped", detail="Appointment not found")

    body = "\n".join(
        [
            f"Hello {context['student_name']},",
            intro,
            f"Doctor: {context['doctor_name']}",
            f"Date: {context['slot_date']}",
            f"Time: {_time_range(context)}",
            f"Reason: {context.get('reason') or 'Not provided'}",
        ]
    )
    return dispatch_email(
        to_email=context["student_email"],
        subject=subject,
        body=body,
    )


def _time_range(context: dict[str, Any]) -> str:
    """Format the start and end times from a context dict as a "HH:MM-HH:MM" string.

    Args:
        context: A notification context dict containing start_time and end_time fields.

    Returns:
        A formatted time range string such as "09:00-09:30".
    """
    start_time = str(context["start_time"])[:5]
    end_time = str(context["end_time"])[:5]
    return f"{start_time}-{end_time}"


def _send_smtp(message: NotificationEmail, settings: Settings) -> None:
    """Deliver an email message via SMTP using the application settings.

    Args:
        message: The NotificationEmail dataclass with recipient, subject, and body.
        settings: Application settings providing SMTP host, port, credentials, and TLS flag.

    Raises:
        Exception: Propagates any SMTP or network error to the caller.
    """
    email = EmailMessage()
    email["From"] = settings.smtp_from_email or ""
    email["To"] = message.to_email
    email["Subject"] = message.subject
    email.set_content(message.body)

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as smtp:
        if settings.smtp_use_tls:
            smtp.starttls()
        if settings.smtp_username and settings.smtp_password:
            smtp.login(settings.smtp_username, settings.smtp_password)
        smtp.send_message(email)
