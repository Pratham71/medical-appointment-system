import type {
  AdminAppointmentSummary,
  AdminDashboard,
  AdminDoctorSummary,
  AdminEmergencyAlertSummary,
  AdminRoleAssignmentRequest,
  AdminRoleAssignmentResponse,
  AdminStaffSummary,
  AdminStudentSummary,
  AdminUserStatusResponse,
  AdminUserSummary,
  AppointmentBookResponse,
  AppointmentCancelReasonCode,
  AppointmentSlot,
  AppointmentStatusResponse,
  AuthenticatedUser,
  CertificateResponse,
  DoctorAvailabilityStatus,
  DoctorAvailabilityOverride,
  DoctorAvailabilityPayload,
  DoctorAvailabilitySettings,
  DoctorWeeklyAvailability,
  EmergencyAlertCreatePayload,
  EmergencyAlertResponse,
  DoctorAppointmentDetail,
  DoctorAppointmentSummary,
  DoctorDashboard,
  MedicalNoteResponse,
  PatientHistoryItem,
  PatientSearchResult,
  PrescriptionResponse,
  ReportDetail,
  StudentAppointmentSummary,
  StudentCertificateSummary,
  StudentDashboard,
  StudentEmergencyAlertSummary,
  StudentReportSummary,
  TokenResponse,
} from "./types";

const BASE = "/api";

function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("mas_token");
}

export function setSession(token: string, user: AuthenticatedUser) {
  localStorage.setItem("mas_token", token);
  localStorage.setItem("mas_user", JSON.stringify(user));
}

export function clearSession() {
  localStorage.removeItem("mas_token");
  localStorage.removeItem("mas_user");
}

export function getStoredUser(): AuthenticatedUser | null {
  if (typeof window === "undefined") return null;
  const raw = localStorage.getItem("mas_user");
  if (!raw) return null;
  try {
    return JSON.parse(raw) as AuthenticatedUser;
  } catch {
    clearSession();
    return null;
  }
}

function idempotencyKey(): string {
  return crypto.randomUUID();
}

async function request<T>(
  path: string,
  options: RequestInit = {},
  isWrite = false
): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };
  if (token) headers["Authorization"] = `Bearer ${token}`;
  if (isWrite) headers["Idempotency-Key"] = idempotencyKey();

  const res = await fetch(`${BASE}${path}`, { ...options, headers });

  if (!res.ok) {
    if (res.status === 401 && typeof window !== "undefined") {
      clearSession();
      window.location.href = "/login";
      return new Promise<never>(() => {}) as unknown as T;
    }
    const body = await res.json().catch(() => ({ detail: res.statusText }));
    const detail = body.detail;
    const message =
      typeof detail === "string"
        ? detail
        : Array.isArray(detail)
        ? detail.map((e: { msg?: string }) => e.msg ?? JSON.stringify(e)).join("; ")
        : `HTTP ${res.status}`;
    throw new Error(message);
  }

  const text = await res.text();
  return text ? (JSON.parse(text) as T) : ({} as T);
}

export async function login(email: string, password: string): Promise<TokenResponse> {
  return request<TokenResponse>("/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

export async function logout(): Promise<void> {
  await request("/auth/logout", { method: "POST" }, true).catch(() => {});
  clearSession();
}

export async function getMe(): Promise<AuthenticatedUser> {
  return request<AuthenticatedUser>("/auth/me");
}

// ── Student ───────────────────────────────────────────────────────────────────

export async function getStudentDashboard(): Promise<StudentDashboard> {
  return request<StudentDashboard>("/students/dashboard");
}

export async function getStudentAppointments(): Promise<StudentAppointmentSummary[]> {
  return request<StudentAppointmentSummary[]>("/students/appointments");
}

export async function getStudentReports(): Promise<StudentReportSummary[]> {
  return request<StudentReportSummary[]>("/students/reports");
}

export async function getStudentCertificates(): Promise<StudentCertificateSummary[]> {
  return request<StudentCertificateSummary[]>("/students/certificates");
}

export async function getStudentEmergencyAlerts(): Promise<StudentEmergencyAlertSummary[]> {
  return request<StudentEmergencyAlertSummary[]>("/students/emergency-alerts");
}

// ── Appointments ─────────────────────────────────────────────────────────────

export async function getSlots(fromDate: string): Promise<AppointmentSlot[]> {
  return request<AppointmentSlot[]>(`/appointments/slots?from_date=${fromDate}`);
}

export async function getDoctorsForDate(forDate: string): Promise<DoctorAvailabilityStatus[]> {
  return request<DoctorAvailabilityStatus[]>(`/appointments/doctors?for_date=${forDate}`);
}

export async function getAllSlotsForDoctor(doctorId: number, slotDate: string): Promise<import("./types").AppointmentSlotWithStatus[]> {
  return request<import("./types").AppointmentSlotWithStatus[]>(`/appointments/slots/all?doctor_id=${doctorId}&slot_date=${slotDate}`);
}

export async function bookAppointment(
  slotId: number,
  reason?: string
): Promise<AppointmentBookResponse> {
  return request<AppointmentBookResponse>(
    "/appointments/book",
    { method: "POST", body: JSON.stringify({ slot_id: slotId, reason: reason ?? null }) },
    true
  );
}

export async function cancelAppointment(
  id: number,
  reasonCode?: AppointmentCancelReasonCode,
  note?: string
): Promise<AppointmentStatusResponse> {
  const body = reasonCode
    ? JSON.stringify({
        reason_code: reasonCode,
        note: note?.trim() || null,
      })
    : undefined;

  return request<AppointmentStatusResponse>(
    `/appointments/${id}/cancel`,
    { method: "PATCH", body },
    true
  );
}

export async function completeAppointment(id: number): Promise<AppointmentStatusResponse> {
  return request<AppointmentStatusResponse>(
    `/appointments/${id}/complete`,
    { method: "PATCH" },
    true
  );
}

// ── Doctor ────────────────────────────────────────────────────────────────────

export async function getDoctorDashboard(): Promise<DoctorDashboard> {
  return request<DoctorDashboard>("/doctors/dashboard");
}

export async function getDoctorAppointments(): Promise<DoctorAppointmentSummary[]> {
  return request<DoctorAppointmentSummary[]>("/doctors/appointments");
}

export async function getDoctorAppointmentDetail(id: number): Promise<DoctorAppointmentDetail> {
  return request<DoctorAppointmentDetail>(`/doctors/appointment/${id}`);
}

export async function getDoctorAvailability(): Promise<DoctorAvailabilitySettings> {
  return request<DoctorAvailabilitySettings>("/doctors/availability");
}

export async function updateDoctorWeeklyAvailability(
  weekday: number,
  payload: DoctorAvailabilityPayload
): Promise<DoctorWeeklyAvailability> {
  return request<DoctorWeeklyAvailability>(
    `/doctors/availability/weekly/${weekday}`,
    { method: "PUT", body: JSON.stringify(payload) },
    true
  );
}

export async function updateDoctorAvailabilityOverride(
  overrideDate: string,
  payload: DoctorAvailabilityPayload
): Promise<DoctorAvailabilityOverride> {
  return request<DoctorAvailabilityOverride>(
    `/doctors/availability/overrides/${overrideDate}`,
    { method: "PUT", body: JSON.stringify(payload) },
    true
  );
}

export async function deleteDoctorAvailabilityOverride(
  overrideDate: string
): Promise<void> {
  await request(
    `/doctors/availability/overrides/${overrideDate}`,
    { method: "DELETE" },
    true
  );
}

export async function getPatientHistory(studentId: number): Promise<PatientHistoryItem[]> {
  return request<PatientHistoryItem[]>(`/doctors/patient-history/${studentId}`);
}

export async function searchPatients(query: string): Promise<PatientSearchResult[]> {
  return request<PatientSearchResult[]>(
    `/doctors/patients/search?q=${encodeURIComponent(query)}`
  );
}

export async function getReportDetail(appointmentId: number): Promise<ReportDetail> {
  return request<ReportDetail>(`/reports/${appointmentId}`);
}

export async function sendEmergencyAlert(
  payload: EmergencyAlertCreatePayload
): Promise<EmergencyAlertResponse> {
  return request<EmergencyAlertResponse>(
    "/emergency/alert",
    {
      method: "POST",
      body: JSON.stringify(payload),
    },
    true
  );
}

// ── Reports ───────────────────────────────────────────────────────────────────

export async function saveNotes(
  appointmentId: number,
  diagnosis: string,
  remarks: string
): Promise<MedicalNoteResponse> {
  return request<MedicalNoteResponse>(
    `/reports/${appointmentId}/notes`,
    { method: "POST", body: JSON.stringify({ diagnosis, remarks }) },
    true
  );
}

export async function savePrescription(
  appointmentId: number,
  items: { medicine_name: string; dosage: string }[]
): Promise<PrescriptionResponse> {
  return request<PrescriptionResponse>(
    `/reports/${appointmentId}/prescription`,
    { method: "POST", body: JSON.stringify({ items }) },
    true
  );
}

// ── Certificates ──────────────────────────────────────────────────────────────

type CertificatePayload = {
  leave_start_date?: string;
  leave_end_date?: string;
  certificate_notes?: string;
};

export async function issueCertificate(
  appointmentId: number,
  certificateTypeId: number,
  certificatePayload: CertificatePayload = {}
): Promise<CertificateResponse> {
  return request<CertificateResponse>(
    `/certificates/${appointmentId}`,
    {
      method: "POST",
      body: JSON.stringify({
        certificate_type_id: certificateTypeId,
        ...certificatePayload,
      }),
    },
    true
  );
}

// ── Admin ─────────────────────────────────────────────────────────────────────

export async function getAdminDashboard(): Promise<AdminDashboard> {
  return request<AdminDashboard>("/admin/dashboard");
}

export async function getAdminUsers(
  q?: string,
  roleName?: string,
  limit = 100
): Promise<AdminUserSummary[]> {
  const p = new URLSearchParams();
  if (q && q.length >= 2) p.set("q", q);
  if (roleName) p.set("role_name", roleName);
  p.set("limit", String(limit));
  return request<AdminUserSummary[]>(`/admin/users?${p}`);
}

export async function assignUserRole(
  userId: number,
  payload: AdminRoleAssignmentRequest
): Promise<AdminRoleAssignmentResponse> {
  return request<AdminRoleAssignmentResponse>(
    `/admin/users/${userId}/role`,
    { method: "PATCH", body: JSON.stringify(payload) },
    true
  );
}

export async function deactivateUser(userId: number): Promise<AdminUserStatusResponse> {
  return request<AdminUserStatusResponse>(
    `/admin/users/${userId}/deactivate`,
    { method: "PATCH" },
    true
  );
}

export async function activateUser(userId: number): Promise<AdminUserStatusResponse> {
  return request<AdminUserStatusResponse>(
    `/admin/users/${userId}/activate`,
    { method: "PATCH" },
    true
  );
}

export async function getAdminAppointments(params?: {
  status?: string;
  from_date?: string;
  to_date?: string;
  doctor_id?: number;
  student_id?: number;
  limit?: number;
}): Promise<AdminAppointmentSummary[]> {
  const p = new URLSearchParams();
  if (params?.status) p.set("status", params.status);
  if (params?.from_date) p.set("from_date", params.from_date);
  if (params?.to_date) p.set("to_date", params.to_date);
  if (params?.doctor_id) p.set("doctor_id", String(params.doctor_id));
  if (params?.student_id) p.set("student_id", String(params.student_id));
  if (params?.limit) p.set("limit", String(params.limit));
  return request<AdminAppointmentSummary[]>(`/admin/appointments?${p}`);
}

export async function getAdminStudents(q?: string, limit = 100): Promise<AdminStudentSummary[]> {
  const p = new URLSearchParams();
  if (q && q.length >= 2) p.set("q", q);
  p.set("limit", String(limit));
  return request<AdminStudentSummary[]>(`/admin/students?${p}`);
}

export async function getAdminDoctors(q?: string, limit = 100): Promise<AdminDoctorSummary[]> {
  const p = new URLSearchParams();
  if (q && q.length >= 2) p.set("q", q);
  p.set("limit", String(limit));
  return request<AdminDoctorSummary[]>(`/admin/doctors?${p}`);
}

export async function getAdminStaff(q?: string, limit = 100): Promise<AdminStaffSummary[]> {
  const p = new URLSearchParams();
  if (q && q.length >= 2) p.set("q", q);
  p.set("limit", String(limit));
  return request<AdminStaffSummary[]>(`/admin/staff?${p}`);
}

export async function getAdminEmergencyAlerts(limit = 50): Promise<AdminEmergencyAlertSummary[]> {
  return request<AdminEmergencyAlertSummary[]>(`/admin/emergency-alerts?limit=${limit}`);
}

export async function acknowledgeEmergencyAlert(
  alertId: number
): Promise<AdminEmergencyAlertSummary> {
  return request<AdminEmergencyAlertSummary>(
    `/admin/emergency-alerts/${alertId}/acknowledge`,
    { method: "PATCH" },
    true
  );
}

export async function resolveEmergencyAlert(
  alertId: number,
  resolutionNote?: string
): Promise<AdminEmergencyAlertSummary> {
  return request<AdminEmergencyAlertSummary>(
    `/admin/emergency-alerts/${alertId}/resolve`,
    {
      method: "PATCH",
      body: JSON.stringify({ resolution_note: resolutionNote?.trim() || null }),
    },
    true
  );
}
