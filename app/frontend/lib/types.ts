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
  cancellation_reason: string | null;
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
  appointment_reason?: string | null;
  diagnosis?: string | null;
  remarks?: string | null;
  // optional fields added by future backend work (#16, #17)
  leave_start_date?: string;
  leave_end_date?: string;
  certificate_notes?: string | null;
}

export type EmergencyAlertStatus = "unread" | "acknowledged" | "resolved";

export interface EmergencyAlertCreatePayload {
  reason: string;
  location: string;
  contact_number?: string | null;
  message?: string | null;
}

export interface EmergencyAlertResponse {
  alert_id: number;
  student_id: number;
  student_name: string;
  roll_number: string;
  reason: string;
  location: string;
  contact_number: string | null;
  message: string;
  status: EmergencyAlertStatus;
  created_at: string;
}

export interface StudentEmergencyAlertSummary {
  alert_id: number;
  reason: string;
  location: string;
  contact_number: string | null;
  message: string;
  status: EmergencyAlertStatus;
  created_at: string;
  acknowledged_at: string | null;
  resolved_at: string | null;
  resolution_note: string | null;
}

export interface AppointmentSlot {
  slot_id: number;
  doctor_id: number;
  doctor_name: string;
  slot_date: string;
  start_time: string;
  end_time: string;
}

export interface AppointmentSlotWithStatus extends AppointmentSlot {
  is_available: boolean;
  appointment_status: "booked" | "completed" | null;
}

export interface DoctorAvailabilityStatus {
  doctor_id: number;
  doctor_name: string;
  specialization: string | null;
  is_available: boolean;
  available_slots: number;
  unavailability_note: string | null;
}

export interface AppointmentBookResponse {
  appointment_id: number | null;
  slot_id: number;
  status: string;
  message: string;
}

export type AppointmentCancelReasonCode =
  | "no_show"
  | "student_request"
  | "doctor_unavailable"
  | "emergency_priority"
  | "duplicate_booking"
  | "other";

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

export interface DoctorWeeklyAvailability {
  weekday: number;
  weekday_name: string;
  is_available: boolean;
  start_time: string | null;
  end_time: string | null;
}

export interface DoctorAvailabilityOverride {
  override_date: string;
  is_available: boolean;
  start_time: string | null;
  end_time: string | null;
  note: string | null;
}

export interface DoctorAvailabilitySettings {
  doctor_id: number;
  weekly_availability: DoctorWeeklyAvailability[];
  date_overrides: DoctorAvailabilityOverride[];
}

export interface DoctorAvailabilityPayload {
  is_available: boolean;
  start_time?: string | null;
  end_time?: string | null;
  note?: string | null;
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
  leave_start_date?: string | null;
  leave_end_date?: string | null;
  certificate_notes?: string | null;
  doctor_id: number;
  doctor_name: string;
  appointment_date: string;
  appointment_reason?: string | null;
  diagnosis?: string | null;
  remarks?: string | null;
}

// ── Admin ─────────────────────────────────────────────────────────────────────

export type AssignableRole =
  | "student"
  | "professor"
  | "college-staff"
  | "hostel-staff"
  | "doctor"
  | "staff"
  | "admin";

export interface AdminDashboard {
  total_students: number;
  total_professors: number;
  total_doctors: number;
  total_staff: number;
  appointments_today: number;
  booked_appointments: number;
  completed_appointments: number;
  cancelled_appointments: number;
  reports_available: number;
  certificates_issued: number;
  emergency_alerts: number;
}

export interface AdminUserSummary {
  user_id: number;
  name: string;
  email: string;
  role_name: string;
  is_active: boolean;
  student_id: number | null;
  staff_id: number | null;
}

export interface AdminRoleAssignmentRequest {
  role_name: AssignableRole;
  roll_number?: string | null;
  department?: string | null;
  year_level?: number | null;
  employee_number?: string | null;
  specialization?: string | null;
}

export interface AdminRoleAssignmentResponse {
  user_id: number;
  name: string;
  email: string;
  role_name: string;
  student_id: number | null;
  staff_id: number | null;
  message: string;
}

export interface AdminUserStatusResponse {
  user_id: number;
  is_active: boolean;
  message: string;
}

export interface AdminAppointmentSummary {
  appointment_id: number;
  slot_date: string;
  start_time: string;
  end_time: string;
  student_id: number;
  student_name: string;
  roll_number: string;
  doctor_id: number;
  doctor_name: string;
  status: string;
  reason: string | null;
  cancellation_reason: string | null;
}

export interface AdminStudentSummary {
  student_id: number;
  student_name: string;
  email: string;
  roll_number: string;
  department: string;
  year_level: number;
  role_name: string;
  total_appointments: number;
  completed_appointments: number;
}

export interface AdminDoctorSummary {
  doctor_id: number;
  doctor_name: string;
  email: string;
  employee_number: string;
  specialization: string | null;
  is_available_today: boolean;
  appointments_today: number;
  upcoming_appointments: number;
}

export interface AdminStaffSummary {
  staff_id: number;
  staff_name: string;
  email: string;
  employee_number: string;
  specialization: string | null;
  is_doctor: boolean;
}

export interface AdminEmergencyAlertSummary {
  alert_id: number;
  student_id: number;
  student_name: string;
  roll_number: string;
  reason: string;
  location: string;
  contact_number: string | null;
  message: string;
  status: EmergencyAlertStatus;
  created_at: string;
  acknowledged_by: number | null;
  acknowledged_at: string | null;
  resolved_by: number | null;
  resolved_at: string | null;
  resolution_note: string | null;
}
