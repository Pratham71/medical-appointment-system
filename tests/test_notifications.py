from datetime import date, time
from importlib import import_module

from app.backend.app.core.config import Settings
from app.backend.app.schemas.appointment import (
    AppointmentBookRequest,
    AppointmentCancelRequest,
)
from app.backend.app.schemas.certificate import CertificateCreate
from app.backend.app.schemas.report import MedicalNoteCreate
from app.backend.app.services import (
    appointment_service,
    certificate_service,
    report_service,
)


def _notification_service():
    return import_module("app.backend.app.services.notification_service")


def test_notification_service_noops_when_email_is_disabled(monkeypatch):
    notification_service = _notification_service()
    attempts = []

    monkeypatch.setattr(
        notification_service,
        "get_settings",
        lambda: Settings(email_notifications_enabled=False),
        raising=False,
    )
    monkeypatch.setattr(
        notification_service,
        "_send_smtp",
        lambda message, settings: attempts.append((message, settings)),
        raising=False,
    )

    result = notification_service.dispatch_email(
        to_email="student@college.edu",
        subject="Appointment booked",
        body="Your appointment is booked.",
    )

    assert result.status == "disabled"
    assert attempts == []


def test_notification_service_handles_provider_failure(monkeypatch):
    notification_service = _notification_service()
    monkeypatch.setattr(
        notification_service,
        "get_settings",
        lambda: Settings(
            email_notifications_enabled=True,
            smtp_host="smtp.example.edu",
            smtp_from_email="infirmary@example.edu",
        ),
        raising=False,
    )

    def fail_send(message, settings):
        raise OSError("SMTP unavailable")

    monkeypatch.setattr(notification_service, "_send_smtp", fail_send, raising=False)

    result = notification_service.dispatch_email(
        to_email="student@college.edu",
        subject="Appointment booked",
        body="Your appointment is booked.",
    )

    assert result.status == "failed"
    assert "SMTP unavailable" in result.detail


def test_booking_dispatches_appointment_confirmation(monkeypatch):
    _notification_service()
    sent = []

    monkeypatch.setattr(
        appointment_service.appointment_repo,
        "book_appointment",
        lambda student_id, slot_id, reason: {
            "appointment_id": 55,
            "slot_id": slot_id,
            "status": "booked",
        },
    )
    monkeypatch.setattr(
        appointment_service.notification_service,
        "send_appointment_booked",
        lambda appointment_id: sent.append(appointment_id),
        raising=False,
    )

    result = appointment_service.book_appointment(
        AppointmentBookRequest(slot_id=7, reason="Fever"),
        student_id=1,
    )

    assert result.appointment_id == 55
    assert sent == [55]


def test_cancellation_dispatches_cancellation_notification(monkeypatch):
    _notification_service()
    sent = []

    monkeypatch.setattr(
        appointment_service.appointment_repo,
        "update_status",
        lambda appointment_id, status_name, cancellation_reason=None: {
            "appointment_id": appointment_id,
            "status": status_name,
        },
    )
    monkeypatch.setattr(
        appointment_service.notification_service,
        "send_appointment_cancelled",
        lambda appointment_id: sent.append(appointment_id),
        raising=False,
    )

    result = appointment_service.cancel_appointment(
        55,
        AppointmentCancelRequest(reason_code="no_show", note="Student did not arrive"),
        actor_role="staff",
    )

    assert result.status == "cancelled"
    assert sent == [55]


def test_report_creation_dispatches_report_available_notification(monkeypatch):
    _notification_service()
    sent = []

    monkeypatch.setattr(
        report_service.report_repo,
        "get_appointment_write_context",
        lambda appointment_id: {"appointment_id": appointment_id, "status": "booked"},
        raising=False,
    )
    monkeypatch.setattr(
        report_service.report_repo,
        "add_medical_note",
        lambda appointment_id, payload: {
            "note_id": 1,
            "appointment_id": appointment_id,
            "diagnosis": payload.diagnosis,
            "remarks": payload.remarks,
        },
    )
    monkeypatch.setattr(
        report_service.notification_service,
        "send_report_available",
        lambda appointment_id: sent.append(appointment_id),
        raising=False,
    )

    result = report_service.add_medical_note(
        55,
        MedicalNoteCreate(diagnosis="Seasonal fever", remarks="Rest"),
    )

    assert result.note_id == 1
    assert sent == [55]


def test_certificate_creation_dispatches_certificate_available_notification(monkeypatch):
    _notification_service()
    sent = []

    monkeypatch.setattr(
        certificate_service.certificate_repo,
        "get_appointment_certificate_context",
        lambda appointment_id: {
            "appointment_id": appointment_id,
            "appointment_date": date(2026, 5, 15),
            "status": "booked",
        },
    )
    monkeypatch.setattr(
        certificate_service.certificate_repo,
        "create_certificate",
        lambda appointment_id, payload: {
            "certificate_id": 5,
            "appointment_id": appointment_id,
            "student_id": 1,
            "student_name": "Aarav Sharma",
            "certificate_type_id": payload.certificate_type_id,
            "certificate_type": "Medical Leave",
            "issue_date": date(2026, 5, 17),
            "doctor_id": 1,
            "doctor_name": "Dr. Meera Singh",
            "appointment_date": date(2026, 5, 15),
            "appointment_reason": "Fever",
            "diagnosis": "Seasonal fever",
            "remarks": "Rest",
            "leave_start_date": None,
            "leave_end_date": None,
            "certificate_notes": None,
        },
    )
    monkeypatch.setattr(
        certificate_service.notification_service,
        "send_certificate_available",
        lambda appointment_id, certificate_type: sent.append((appointment_id, certificate_type)),
        raising=False,
    )

    result = certificate_service.create_certificate(
        55,
        CertificateCreate(certificate_type_id=1, issue_date=date(2026, 5, 17)),
    )

    assert result.certificate_id == 5
    assert sent == [(55, "Medical Leave")]


def test_notification_templates_include_appointment_context(monkeypatch):
    notification_service = _notification_service()
    sent = []
    context = {
        "student_email": "student@college.edu",
        "student_name": "Aarav Sharma",
        "doctor_name": "Dr. Meera Singh",
        "slot_date": date(2026, 5, 18),
        "start_time": time(9, 0),
        "end_time": time(9, 30),
        "reason": "Fever",
        "cancellation_reason": None,
    }

    monkeypatch.setattr(
        notification_service.notification_repo,
        "get_appointment_notification_context",
        lambda appointment_id: context,
        raising=False,
    )
    monkeypatch.setattr(
        notification_service,
        "dispatch_email",
        lambda to_email, subject, body: sent.append((to_email, subject, body)),
        raising=False,
    )

    notification_service.send_appointment_booked(55)

    assert sent[0][0] == "student@college.edu"
    assert "Appointment booked" in sent[0][1]
    assert "Dr. Meera Singh" in sent[0][2]
    assert "2026-05-18" in sent[0][2]
