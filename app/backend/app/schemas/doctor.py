from datetime import date, time

from pydantic import BaseModel


class DoctorDashboard(BaseModel):
    doctor_id: int
    doctor_name: str
    todays_appointments: int = 0
    upcoming_appointments: int = 0
    completed_appointments: int = 0
    total_patients: int = 0


class DoctorAppointmentSummary(BaseModel):
    appointment_id: int
    slot_date: date
    start_time: time
    end_time: time
    student_id: int
    student_name: str
    status: str


class DoctorAppointmentDetail(BaseModel):
    appointment_id: int
    slot_date: date
    start_time: time
    end_time: time
    status: str
    student_id: int
    student_name: str
    student_email: str
    doctor_id: int
    doctor_name: str
    diagnosis: str | None = None
    remarks: str | None = None
    certificate_id: int | None = None
    certificate_type: str | None = None


class PatientHistoryItem(BaseModel):
    appointment_id: int
    slot_date: date
    start_time: time
    end_time: time
    doctor_id: int
    doctor_name: str
    status: str
    diagnosis: str | None = None
    remarks: str | None = None
    certificate_id: int | None = None
    certificate_type: str | None = None


class PatientSearchResult(BaseModel):
    student_id: int
    student_name: str
    roll_number: str
    department: str
    year_level: int
