from datetime import date, time

from pydantic import BaseModel


class StudentNextAppointment(BaseModel):
    appointment_id: int
    slot_date: date
    start_time: time
    end_time: time
    doctor_id: int
    doctor_name: str
    status: str


class StudentDashboard(BaseModel):
    student_id: int
    student_name: str
    upcoming_appointments: int = 0
    completed_appointments: int = 0
    reports_available: int = 0
    certificates_available: int = 0
    next_appointment: StudentNextAppointment | None = None


class StudentAppointmentSummary(BaseModel):
    appointment_id: int
    slot_date: date
    start_time: time
    end_time: time
    doctor_id: int
    doctor_name: str
    status: str
    reason: str | None = None


class StudentReportSummary(BaseModel):
    appointment_id: int
    appointment_date: date
    doctor_id: int
    doctor_name: str
    diagnosis: str | None = None
    remarks: str | None = None
    prescription_count: int = 0


class StudentCertificateSummary(BaseModel):
    certificate_id: int
    appointment_id: int
    certificate_type_id: int
    certificate_type: str
    issue_date: date
    doctor_id: int
    doctor_name: str
    appointment_date: date
    appointment_reason: str | None = None
    diagnosis: str | None = None
    remarks: str | None = None
    leave_start_date: date | None = None
    leave_end_date: date | None = None
    certificate_notes: str | None = None
