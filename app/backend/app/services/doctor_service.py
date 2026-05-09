from app.backend.app.api.errors import NotFoundError
from app.backend.app.repositories import doctor_repo
from app.backend.app.schemas.doctor import (
    DoctorAppointmentDetail,
    DoctorAppointmentSummary,
    DoctorDashboard,
    PatientHistoryItem,
)


def get_dashboard(staff_id: int) -> DoctorDashboard:
    row = doctor_repo.get_dashboard_counts(staff_id)
    if row is None:
        raise NotFoundError("Doctor was not found")
    return DoctorDashboard(**row)


def list_appointments(staff_id: int) -> list[DoctorAppointmentSummary]:
    rows = doctor_repo.list_appointments(staff_id)
    return [DoctorAppointmentSummary(**row) for row in rows]


def get_appointment_detail(appointment_id: int) -> DoctorAppointmentDetail:
    row = doctor_repo.get_appointment_detail(appointment_id)
    if row is None:
        raise NotFoundError("Appointment was not found")
    return DoctorAppointmentDetail(**row)


def list_patient_history(student_id: int) -> list[PatientHistoryItem]:
    rows = doctor_repo.list_patient_history(student_id)
    return [PatientHistoryItem(**row) for row in rows]
