export interface AuthenticatedUser {
  user_id: number;
  name: string;
  email: string;
  role_name: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  user: AuthenticatedUser;
}

export interface StudentNextAppointment {
  appointment_id: number;
  slot_date: string;
  start_time: string;
  end_time: string;
  doctor_id: number;
  doctor_name: string;
  status: string;
}

export interface StudentDashboard {
  student_id: number;
  student_name: string;
  upcoming_appointments: number;
  completed_appointments: number;
  reports_available: number;
  certificates_available: number;
  next_appointment: StudentNextAppointment | null;
}

export interface StudentAppointmentSummary {
  appointment_id: number;
  slot_date: string;
  start_time: string;
  end_time: string;
  doctor_id: number;
  doctor_name: string;
  status: string;
  reason: string | null;
}

export interface StudentReportSummary {
  appointment_id: number;
  appointment_date: string;
  doctor_id: number;
  doctor_name: string;
  diagnosis: string | null;
  remarks: string | null;
  prescription_count: number;
}

export interface StudentCertificateSummary {
  certificate_id: number;
  appointment_id: number;
  certificate_type_id: number;
  certificate_type: string;
  issue_date: string;
  doctor_id: number;
  doctor_name: string;
  appointment_date: string;
  // optional fields added by future backend work (#16, #17)
  leave_start_date?: string;
  leave_end_date?: string;
  certificate_notes?: string;
}

export interface AppointmentSlot {
  slot_id: number;
  doctor_id: number;
  doctor_name: string;
  slot_date: string;
  start_time: string;
  end_time: string;
}

export interface AppointmentBookResponse {
  appointment_id: number | null;
  slot_id: number;
  status: string;
  message: string;
}

export interface AppointmentStatusResponse {
  appointment_id: number;
  status: string;
  message: string;
}

export interface DoctorDashboard {
  doctor_id: number;
  doctor_name: string;
  todays_appointments: number;
  upcoming_appointments: number;
  completed_appointments: number;
  total_patients: number;
}

export interface DoctorAppointmentSummary {
  appointment_id: number;
  slot_date: string;
  start_time: string;
  end_time: string;
  student_id: number;
  student_name: string;
  status: string;
}

export interface DoctorAppointmentDetail {
  appointment_id: number;
  slot_date: string;
  start_time: string;
  end_time: string;
  status: string;
  student_id: number;
  student_name: string;
  student_email: string;
  doctor_id: number;
  doctor_name: string;
  reason: string | null;
  diagnosis: string | null;
  remarks: string | null;
  certificate_id: number | null;
  certificate_type: string | null;
}

export interface PatientHistoryItem {
  appointment_id: number;
  slot_date: string;
  start_time: string;
  end_time: string;
  doctor_id: number;
  doctor_name: string;
  status: string;
  reason: string | null;
  diagnosis: string | null;
  remarks: string | null;
  certificate_id: number | null;
  certificate_type: string | null;
}

export interface PatientSearchResult {
  student_id: number;
  student_name: string;
  roll_number: string;
  department: string;
  year_level: number;
}

export interface MedicalNoteResponse {
  note_id: number;
  appointment_id: number;
  diagnosis: string;
  remarks: string | null;
}

export interface PrescriptionItemResponse {
  item_id: number;
  medicine_name: string;
  dosage: string;
}

export interface PrescriptionResponse {
  prescription_id: number;
  appointment_id: number;
  items: PrescriptionItemResponse[];
}

export interface ReportAppointmentSummary {
  appointment_id: number;
  student_id: number;
  student_name: string;
  doctor_id: number;
  doctor_name: string;
  slot_date: string;
  start_time: string;
  end_time: string;
  status: string;
}

export interface ReportDetail {
  appointment: ReportAppointmentSummary;
  note: MedicalNoteResponse | null;
  prescription: PrescriptionResponse | null;
}

export interface CertificateResponse {
  certificate_id: number;
  appointment_id: number;
  student_id: number;
  student_name: string;
  certificate_type_id: number;
  certificate_type: string;
  issue_date: string;
}
