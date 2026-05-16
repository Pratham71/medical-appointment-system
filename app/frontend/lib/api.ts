import type {
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
    throw new Error(body.detail ?? `HTTP ${res.status}`);
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

// ── Appointments ─────────────────────────────────────────────────────────────

export async function getSlots(fromDate: string): Promise<AppointmentSlot[]> {
  return request<AppointmentSlot[]>(`/appointments/slots?from_date=${fromDate}`);
}

export async function getDoctorsForDate(forDate: string): Promise<DoctorAvailabilityStatus[]> {
  return request<DoctorAvailabilityStatus[]>(`/appointments/doctors?for_date=${forDate}`);
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
  message?: string
): Promise<{ alert_id: number; created_at: string }> {
  return request<{ alert_id: number; created_at: string }>(
    "/emergency/alert",
    {
      method: "POST",
      body: JSON.stringify({ message: message ?? null }),
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
