"use client";
import { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import {
  getStudentAppointments,
  getStudentDashboard,
  getStudentEmergencyAlerts,
  getStoredUser,
} from "@/lib/api";
import { doctorName } from "@/lib/utils";
import type {
  StudentAppointmentSummary,
  StudentDashboard,
  StudentEmergencyAlertSummary,
} from "@/lib/types";
import { motion, AnimatePresence } from "framer-motion";
import DashboardShell from "@/components/layout/DashboardShell";
import StatsCard from "@/components/ui/StatsCard";
import StatusBadge from "@/components/ui/StatusBadge";

const PATIENT_ROLES = ["student", "professor", "college-staff", "hostel-staff"];

function isPatientRole(roleName: string) {
  return PATIENT_ROLES.includes(roleName);
}

function fmt(date: string, time: string) {
  return `${new Date(date).toLocaleDateString("en-IN", { day: "numeric", month: "short", year: "numeric" })} · ${time.slice(0, 5)}`;
}

function todayKey() {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
}

export default function StudentDashboardPage() {
  const router = useRouter();
  const [data, setData] = useState<StudentDashboard | null>(null);
  const [todayCancelled, setTodayCancelled] = useState<StudentAppointmentSummary[]>([]);
  const [emergencyAlerts, setEmergencyAlerts] = useState<StudentEmergencyAlertSummary[]>([]);
  const [error, setError] = useState("");
  const [cancelledOpen, setCancelledOpen] = useState(true);
  const [nextOpen, setNextOpen] = useState(true);

  useEffect(() => {
    const user = getStoredUser();
    if (!user) { router.replace("/login"); return; }
    if (user.role_name === "doctor") { router.replace("/doctors"); return; }
    if (user.role_name === "admin") { router.replace("/admin"); return; }
    if (user.role_name === "staff") { router.replace("/staff"); return; }
    if (!isPatientRole(user.role_name)) { router.replace("/login"); return; }

    const today = todayKey();
    Promise.all([
      getStudentDashboard(),
      getStudentAppointments(),
      getStudentEmergencyAlerts(),
    ])
      .then(([dashboard, appointments, alerts]) => {
        setData(dashboard);
        setEmergencyAlerts(alerts.filter((a) => a.status !== "resolved").slice(0, 3));
        const cancelled = appointments.filter(
          (a) => a.slot_date === today && a.status.toLowerCase() === "cancelled"
        );
        setTodayCancelled(cancelled);
      })
      .catch((e: unknown) => setError(e instanceof Error ? e.message : "Failed to load"));
  }, [router]);

  return (
    <DashboardShell role="student" title="Dashboard">
      {error && (
        <div className="bg-red-50 border border-red-100 text-red-600 text-sm rounded-card px-4 py-3 mb-6">
          {error}
        </div>
      )}

      {!data && !error && (
        <div className="text-brand-muted text-sm animate-pulse">Loading…</div>
      )}

      {data && (
        <div className="space-y-6">
          {/* Stats */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <StatsCard
              index={0}
              label="Upcoming Appointments"
              value={data.upcoming_appointments}
              icon={
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
              }
            />
            <StatsCard
              index={1}
              label="Completed Visits"
              value={data.completed_appointments}
              icon={
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              }
            />
            <StatsCard
              index={2}
              label="Certificates Available"
              value={data.certificates_available}
              icon={
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              }
            />
          </div>

          {/* Same-day cancelled appointments */}
          {todayCancelled.length > 0 && (
            <div className="rounded-card border-l-4 border-red-400 border-t border-r border-b border-brand-border bg-red-50 overflow-hidden">
              <button
                onClick={() => setCancelledOpen((v) => !v)}
                className="w-full flex items-center justify-between px-4 py-3 hover:bg-red-100/50 transition-colors"
              >
                <div className="flex items-center gap-2">
                  <span className="text-xs text-red-500 uppercase tracking-wide font-medium">
                    Appointment{todayCancelled.length > 1 ? "s" : ""} Cancelled Today
                  </span>
                  {todayCancelled.length > 1 && (
                    <span className="text-xs bg-red-100 text-red-600 rounded-full px-1.5 py-0.5 font-medium">{todayCancelled.length}</span>
                  )}
                </div>
                <div className="flex items-center gap-3">
                  {!cancelledOpen && (
                    <span className="text-xs text-brand-muted">
                      {fmt(todayCancelled[0].slot_date, todayCancelled[0].start_time)} · Dr. {doctorName(todayCancelled[0].doctor_name)}
                    </span>
                  )}
                  <motion.svg
                    animate={{ rotate: cancelledOpen ? 180 : 0 }}
                    transition={{ duration: 0.2 }}
                    className="w-4 h-4 text-red-400 flex-shrink-0"
                    fill="none" stroke="currentColor" viewBox="0 0 24 24"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </motion.svg>
                </div>
              </button>
              <AnimatePresence initial={false}>
                {cancelledOpen && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: "auto", opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.22, ease: "easeInOut" }}
                    className="overflow-hidden"
                  >
                    <div className="border-t border-red-200 divide-y divide-red-100">
                      {todayCancelled.map((a) => (
                        <div key={a.appointment_id} className="px-4 py-3">
                          <div className="flex items-start justify-between gap-4">
                            <div className="min-w-0">
                              <p className="text-sm font-semibold text-brand-text">{fmt(a.slot_date, a.start_time)}</p>
                              <p className="text-sm text-brand-muted mt-0.5">Dr. {doctorName(a.doctor_name)}</p>
                              {a.reason && (
                                <p className="text-xs text-brand-muted mt-0.5">
                                  <span className="font-medium">Booked for:</span> {a.reason}
                                </p>
                              )}
                              {a.cancellation_reason && (
                                <p className="text-xs text-red-600 mt-1">
                                  <span className="font-medium">Cancelled:</span> {a.cancellation_reason}
                                </p>
                              )}
                            </div>
                            <div className="flex flex-col items-end gap-2 flex-shrink-0">
                              <StatusBadge status={a.status} />
                              <div className="flex items-center gap-2">
                                <button
                                  onClick={() => router.push(`/students/appointments/${a.appointment_id}?from=cancelled`)}
                                  className="text-xs text-brand-muted hover:text-brand-text border border-brand-border px-2.5 py-1 rounded-btn transition-colors"
                                >
                                  View
                                </button>
                                <button
                                  onClick={() => router.push("/students/book")}
                                  className="text-xs text-teal-600 hover:text-teal-700 border border-teal-200 hover:border-teal-300 px-2.5 py-1 rounded-btn font-medium transition-colors"
                                >
                                  Rebook →
                                </button>
                              </div>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          )}

          {/* Next appointment banner */}
          {data.next_appointment ? (
            <div className="bg-white rounded-card border-l-4 border-teal-600 border-t border-r border-b border-brand-border shadow-card overflow-hidden">
              <button
                onClick={() => setNextOpen((v) => !v)}
                className="w-full flex items-center justify-between px-4 py-3 hover:bg-brand-raised transition-colors"
              >
                <div className="flex items-center gap-3">
                  <p className="text-xs text-brand-muted uppercase tracking-wide font-medium">Next Appointment</p>
                  {!nextOpen && (
                    <span className="text-sm font-semibold text-brand-text">
                      {fmt(data.next_appointment.slot_date, data.next_appointment.start_time)} · Dr. {doctorName(data.next_appointment.doctor_name)}
                    </span>
                  )}
                </div>
                <motion.svg
                  animate={{ rotate: nextOpen ? 180 : 0 }}
                  transition={{ duration: 0.2 }}
                  className="w-4 h-4 text-brand-muted flex-shrink-0"
                  fill="none" stroke="currentColor" viewBox="0 0 24 24"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </motion.svg>
              </button>
              <AnimatePresence initial={false}>
                {nextOpen && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: "auto", opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.22, ease: "easeInOut" }}
                    className="overflow-hidden"
                  >
                    <div className="border-t border-brand-border px-4 py-3 flex items-center justify-between">
                      <div>
                        <p className="text-sm font-semibold text-brand-text">
                          {fmt(data.next_appointment.slot_date, data.next_appointment.start_time)}
                        </p>
                        <p className="text-sm text-brand-muted mt-0.5">
                          Dr. {doctorName(data.next_appointment.doctor_name)}
                        </p>
                      </div>
                      <div className="flex items-center gap-3">
                        <StatusBadge status={data.next_appointment.status} />
                        <button
                          onClick={() => router.push("/students/appointments")}
                          className="text-sm text-teal-600 hover:text-teal-700 font-medium transition-colors"
                        >
                          View Details →
                        </button>
                      </div>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          ) : (
            <div className="bg-white rounded-card border border-brand-border shadow-card p-6 text-center">
              <p className="text-brand-muted text-sm">No upcoming appointments.</p>
              <button
                onClick={() => router.push("/students/book")}
                className="mt-3 text-sm bg-teal-600 hover:bg-teal-700 text-white px-4 py-2 rounded-btn font-medium transition-colors"
              >
                Book Appointment
              </button>
            </div>
          )}

          {/* Emergency alert status */}
          {emergencyAlerts.length > 0 && (
            <div className="bg-white rounded-card border border-brand-border shadow-card p-4">
              <div className="mb-3 flex items-center justify-between">
                <h2 className="text-sm font-semibold text-brand-text">Emergency Alert Status</h2>
                <span className="text-xs text-brand-muted">{emergencyAlerts.length} recent</span>
              </div>
              <div className="space-y-2">
                {emergencyAlerts.map((alert) => (
                  <div
                    key={alert.alert_id}
                    className="rounded-btn border border-brand-border bg-brand-bg px-3 py-2"
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div className="min-w-0">
                        <p className="text-sm font-medium text-brand-text">{alert.reason}</p>
                        <p className="text-xs text-brand-muted">{alert.location}</p>
                        {alert.resolution_note && (
                          <p className="mt-1 text-xs text-emerald-700">
                            {alert.resolution_note}
                          </p>
                        )}
                      </div>
                      <StatusBadge status={alert.status} />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Reports summary */}
          <div className="bg-white rounded-card border border-brand-border shadow-card p-4">
            <div className="flex items-center justify-between mb-3">
              <h2 className="text-sm font-semibold text-brand-text">Reports & Certificates</h2>
              <button
                onClick={() => router.push("/students/reports")}
                className="text-xs text-teal-600 hover:text-teal-700 transition-colors"
              >
                View all →
              </button>
            </div>
            <div className="flex gap-6 text-sm text-brand-muted">
              <span><strong className="text-brand-text">{data.reports_available}</strong> reports</span>
              <span><strong className="text-brand-text">{data.certificates_available}</strong> certificates</span>
            </div>
          </div>
        </div>
      )}
    </DashboardShell>
  );
}
