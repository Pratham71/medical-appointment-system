from app.backend.app.api.errors import NotFoundError
from app.backend.app.repositories import report_repo
from app.backend.app.schemas.report import (
    MedicalNoteCreate,
    MedicalNoteResponse,
    PrescriptionCreate,
    PrescriptionResponse,
    ReportDetail,
)


def add_medical_note(
    appointment_id: int, payload: MedicalNoteCreate
) -> MedicalNoteResponse:
    row = report_repo.add_medical_note(appointment_id, payload)
    if row is None:
        raise NotFoundError("Appointment was not found")
    return MedicalNoteResponse(**row)


def add_prescription(
    appointment_id: int, payload: PrescriptionCreate
) -> PrescriptionResponse:
    row = report_repo.add_prescription(appointment_id, payload)
    if row is None:
        raise NotFoundError("Appointment was not found")
    return PrescriptionResponse(**row)


def get_report(appointment_id: int) -> ReportDetail:
    row = report_repo.get_report(appointment_id)
    if row is None:
        raise NotFoundError("Appointment was not found")
    return ReportDetail(**row)
