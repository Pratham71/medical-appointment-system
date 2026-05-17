"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getDoctorDashboard, getDoctorAppointments, getAdminEmergencyAlerts, getStoredUser } from "@/lib/api";
import { motion, AnimatePresence } from "framer-motion";
import type { DoctorDashboard, DoctorAppointmentSummary, AdminEmergencyAlertSummary } from "@/lib/types";
import StatusBadge from "@/components/ui/StatusBadge";
import DashboardShell from "@/components/layout/DashboardShell";
import StatsCard from "@/components/ui/StatsCard";

function fmtTime(t: string) {
  return t.slice(0, 5);
}

function getLocalDateKey(date = new Date()) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

export default function DoctorDashboardPage() {
  const router = useRouter();
  const [dashboard, setDashboard] = useState<DoctorDashboard | null>(null);
  const [appointments, setAppointments] = useState<DoctorAppointmentSummary[]>([]);
  const [alerts, setAlerts] = useState<AdminEmergencyAlertSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [scheduleOpen, setScheduleOpen] = useState(true);

  useEffect(() => {
    const user = getStoredUser();
    if (!user) { router.replace("/login"); setLoading(false); return; }
    if (user.role_name === "student") { router.replace("/students"); setLoading(false); return; }
    if (user.role_name === "admin") { router.replace("/admin"); setLoading(false); return; }
    if (user.role_name === "staff") { router.replace("/staff"); setLoading(false); return; }
    if (user.role_name !== "doctor") { router.replace("/login"); setLoading(false); return; }

    Promise.all([getDoctorDashboard(), getDoctorAppointments(), getAdminEmergencyAlerts(10)])
      .then(([d, a, al]) => {
        setDashboard(d);
        setAppointments(a);
        setAlerts(al.filter((x) => x.status !== "resolved").slice(0, 3));
      })
      .catch((e: unknown) => setError(e instanceof Error ? e.message : "Failed to load"))
      .finally(() => setLoading(false));
  }, [router]);

  // Show today's appointments only
  const today = getLocalDateKey();
  const todaysAppts = appointments.filter((a) => a.slot_date === today);

  return (
    <DashboardShell role="doctor" title="Dashboard">
      {error && (
        <div className="bg-red-50 border border-red-100 text-red-600 text-sm rounded-card px-4 py-3 mb-6">{error}</div>
      )}

      {loading && <div className="text-brand-muted text-sm animate-pulse">Loading…</div>}

      {dashboard && (
        <div className="space-y-6">
          {/* Stats */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <StatsCard
              index={0}
              label="Completed Today"
              value={dashboard.todays_appointments}
              icon={
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              }
            />
            <StatsCard
              index={1}
              label="Upcoming"
              value={dashboard.upcoming_appointments}
              icon={
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              }
            />
            <StatsCard
              index={2}
              label="Total Patients"
              value={dashboard.total_patients}
              icon={
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
              }
            />
          </div>

          {/* Active emergency alerts */}
          {alerts.length > 0 && (
            <div className="bg-white rounded-card border-l-4 border-red-400 border-t border-r border-b border-brand-border shadow-card">
              <div className="flex items-center justify-between px-5 py-3.5 border-b border-brand-border">
                <h2 className="text-sm font-semibold text-brand-text">Emergency Alerts</h2>
                <div className="flex items-center gap-2">
                  <span className="text-xs bg-red-500 text-white rounded-full px-2 py-0.5 font-medium">{alerts.length} active</span>
                  <button onClick={() => router.push("/doctors/emergency-alerts")} className="text-xs text-teal-600 hover:text-teal-700 transition-colors">View all →</button>
                </div>
              </div>
              <div className="divide-y divide-brand-border">
                {alerts.map((a) => (
                  <div key={a.alert_id} className="px-5 py-3">
                    <div className="flex items-start justify-between gap-2">
                      <div className="min-w-0">
                        <div className="flex items-center gap-2">
                          <span className="w-2 h-2 rounded-full bg-red-500 flex-shrink-0" />
                          <p className="text-sm font-medium text-brand-text">{a.student_name}</p>
                          <span className="text-xs text-brand-muted font-mono">{a.roll_number}</span>
                        </div>
                        <p className="text-xs text-brand-muted mt-1">{a.reason} · {a.location}</p>
                        {a.message && <p className="text-xs text-brand-text mt-0.5 line-clamp-1">{a.message}</p>}
                      </div>
                      <StatusBadge status={a.status} />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Today's Schedule */}
          <div className="bg-white rounded-card border border-brand-border shadow-card overflow-hidden">
            <button
              onClick={() => setScheduleOpen((v) => !v)}
              className="w-full px-5 py-3.5 flex items-center justify-between hover:bg-brand-raised transition-colors"
            >
              <div className="flex items-center gap-3">
                <h2 className="text-sm font-semibold text-brand-text">Today&apos;s Schedule</h2>
                {!loading && (
                  <span className={`text-xs rounded-full px-1.5 py-0.5 font-medium ${
                    todaysAppts.length > 0 ? "bg-teal-100 text-teal-700" : "bg-brand-raised text-brand-muted"
                  }`}>
                    {todaysAppts.length}
                  </span>
                )}
                {!scheduleOpen && todaysAppts.length > 0 && (
                  <span className="text-xs text-brand-muted">
                    Latest: {fmtTime(todaysAppts[0].start_time)} · {todaysAppts[0].student_name}
                  </span>
                )}
              </div>
              <div className="flex items-center gap-3">
                <span
                  onClick={(e) => { e.stopPropagation(); router.push("/doctors/appointments"); }}
                  className="text-xs text-teal-600 hover:text-teal-700 transition-colors"
                >
                  View all →
                </span>
                <motion.svg
                  animate={{ rotate: scheduleOpen ? 180 : 0 }}
                  transition={{ duration: 0.2 }}
                  className="w-4 h-4 text-brand-muted flex-shrink-0"
                  fill="none" stroke="currentColor" viewBox="0 0 24 24"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </motion.svg>
              </div>
            </button>
            <AnimatePresence initial={false}>
              {scheduleOpen && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: "auto", opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  transition={{ duration: 0.22, ease: "easeInOut" }}
                  className="overflow-hidden"
                >
                  {todaysAppts.length === 0 ? (
                    <div className="border-t border-brand-border p-6 text-center text-brand-muted text-sm">
                      No appointments scheduled for today.
                    </div>
                  ) : (
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="bg-brand-raised border-y border-brand-border">
                          <th className="text-left px-4 py-3 text-xs font-semibold text-brand-muted uppercase tracking-wide">Time</th>
                          <th className="text-left px-4 py-3 text-xs font-semibold text-brand-muted uppercase tracking-wide">Patient</th>
                          <th className="text-left px-4 py-3 text-xs font-semibold text-brand-muted uppercase tracking-wide">ID</th>
                          <th className="text-left px-4 py-3 text-xs font-semibold text-brand-muted uppercase tracking-wide">Status</th>
                          <th className="text-left px-4 py-3 text-xs font-semibold text-brand-muted uppercase tracking-wide">Action</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-brand-border">
                        {todaysAppts.map((a) => (
                          <tr key={a.appointment_id} className="hover:bg-brand-raised transition-colors">
                            <td className="px-4 py-3 font-mono text-xs text-brand-text">{fmtTime(a.start_time)}</td>
                            <td className="px-4 py-3 text-brand-text">{a.student_name}</td>
                            <td className="px-4 py-3 font-mono text-xs text-brand-muted">{a.student_id}</td>
                            <td className="px-4 py-3"><StatusBadge status={a.status} /></td>
                            <td className="px-4 py-3">
                              <button
                                onClick={() => router.push(`/doctors/appointments/${a.appointment_id}`)}
                                className="text-xs text-teal-600 hover:text-teal-700 font-medium transition-colors"
                              >
                                View Details →
                              </button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  )}
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      )}
    </DashboardShell>
  );
}
