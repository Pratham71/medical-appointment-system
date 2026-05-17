"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import {
  getAdminDashboard,
  getAdminAppointments,
  getAdminEmergencyAlerts,
  getStoredUser,
} from "@/lib/api";
import type {
  AdminDashboard,
  AdminAppointmentSummary,
  AdminEmergencyAlertSummary,
} from "@/lib/types";
import DashboardShell from "@/components/layout/DashboardShell";
import StatsCard from "@/components/ui/StatsCard";
import StatusBadge from "@/components/ui/StatusBadge";

function fmtDate(date: string, time: string) {
  return `${new Date(date + "T00:00:00").toLocaleDateString("en-IN", { day: "numeric", month: "short" })} · ${time.slice(0, 5)}`;
}

function timeAgo(iso: string): string {
  const h = Math.floor((Date.now() - new Date(iso).getTime()) / 3_600_000);
  if (h < 1) return "< 1h ago";
  if (h < 24) return `${h}h ago`;
  return `${Math.floor(h / 24)}d ago`;
}

const STAT2_COLORS: Record<string, string> = {
  amber: "text-amber-600",
  blue: "text-blue-600",
  emerald: "text-emerald-600",
  red: "text-red-600",
};

export default function AdminDashboardPage() {
  const router = useRouter();
  const [dash, setDash] = useState<AdminDashboard | null>(null);
  const [appts, setAppts] = useState<AdminAppointmentSummary[]>([]);
  const [alerts, setAlerts] = useState<AdminEmergencyAlertSummary[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    const user = getStoredUser();
    if (!user) { router.replace("/login"); return; }
    if (user.role_name !== "admin") { router.replace("/login"); return; }

    Promise.all([
      getAdminDashboard(),
      getAdminAppointments({ limit: 6 }),
      getAdminEmergencyAlerts(3),
    ])
      .then(([d, a, al]) => { setDash(d); setAppts(a); setAlerts(al); })
      .catch((e: unknown) => setError(e instanceof Error ? e.message : "Failed to load"));
  }, [router]);

  return (
    <DashboardShell role="admin" title="Admin Dashboard">
      {error && (
        <div className="bg-red-50 border border-red-100 text-red-600 text-sm rounded-card px-4 py-3 mb-6">
          {error}
        </div>
      )}

      {!dash && !error && (
        <div className="text-brand-muted text-sm animate-pulse">Loading…</div>
      )}

      {dash && (
        <div className="space-y-6">
          {/* Stats row 1 — people counts */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <StatsCard index={0} label="Total Students" value={dash.total_students}
              icon={<svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 14l9-5-9-5-9 5 9 5zm0 0l6.16-3.422a12.083 12.083 0 01.665 6.479A11.952 11.952 0 0012 20.055a11.952 11.952 0 00-6.824-2.998 12.078 12.078 0 01.665-6.479L12 14z" /></svg>}
            />
            <StatsCard index={1} label="Total Professors" value={dash.total_professors}
              icon={<svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" /></svg>}
            />
            <StatsCard index={2} label="Active Doctors" value={dash.total_doctors}
              icon={<svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>}
            />
          </div>

          {/* Stats row 2 — appointment counts */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            {(
              [
                { label: "Appointments Today", value: dash.appointments_today, color: "amber" },
                { label: "Booked", value: dash.booked_appointments, color: "blue" },
                { label: "Completed", value: dash.completed_appointments, color: "emerald" },
                { label: "Cancelled", value: dash.cancelled_appointments, color: "red" },
              ] as const
            ).map(({ label, value, color }, i) => (
              <motion.div
                key={label}
                initial={{ opacity: 0, y: 16 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, delay: (i + 3) * 0.08, ease: "easeOut" }}
                className="bg-white rounded-card border border-brand-border shadow-card p-4"
              >
                <p className="text-2xl font-semibold text-brand-text">{value}</p>
                <p className={`text-xs font-medium mt-1 ${STAT2_COLORS[color]}`}>{label}</p>
              </motion.div>
            ))}
          </div>

          {/* Main two-column layout */}
          <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
            {/* Recent appointments table */}
            <div className="lg:col-span-3 bg-white rounded-card border border-brand-border shadow-card">
              <div className="flex items-center justify-between px-5 py-3.5 border-b border-brand-border">
                <h2 className="text-sm font-semibold text-brand-text">Recent Appointments</h2>
                <button
                  onClick={() => router.push("/admin/appointments")}
                  className="text-xs text-teal-600 hover:text-teal-700 transition-colors"
                >
                  View all →
                </button>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-brand-border bg-brand-bg">
                      <th className="text-left px-5 py-2.5 text-xs font-medium text-brand-muted">Date & Time</th>
                      <th className="text-left px-5 py-2.5 text-xs font-medium text-brand-muted">Student</th>
                      <th className="text-left px-5 py-2.5 text-xs font-medium text-brand-muted">Doctor</th>
                      <th className="text-left px-5 py-2.5 text-xs font-medium text-brand-muted">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-brand-border">
                    {appts.map((a) => (
                      <tr key={a.appointment_id} className="hover:bg-brand-raised transition-colors">
                        <td className="px-5 py-3 text-brand-muted whitespace-nowrap">{fmtDate(a.slot_date, a.start_time)}</td>
                        <td className="px-5 py-3">
                          <p className="font-medium text-brand-text">{a.student_name}</p>
                          <p className="text-xs text-brand-muted">{a.roll_number}</p>
                        </td>
                        <td className="px-5 py-3 text-brand-muted">{a.doctor_name}</td>
                        <td className="px-5 py-3"><StatusBadge status={a.status} /></td>
                      </tr>
                    ))}
                    {appts.length === 0 && (
                      <tr>
                        <td colSpan={4} className="px-5 py-8 text-center text-brand-muted text-sm">
                          No appointments found
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Right column */}
            <div className="lg:col-span-2 space-y-4">
              {/* Emergency alerts */}
              <div className="bg-white rounded-card border-l-4 border-red-400 border-t border-r border-b border-brand-border shadow-card">
                <div className="flex items-center justify-between px-5 py-3.5 border-b border-brand-border">
                  <h2 className="text-sm font-semibold text-brand-text">Emergency Alerts</h2>
                  {dash.emergency_alerts > 0 && (
                    <span className="text-xs bg-red-500 text-white rounded-full px-2 py-0.5 font-medium">
                      {dash.emergency_alerts}
                    </span>
                  )}
                </div>
                <div className="divide-y divide-brand-border">
                  {alerts.map((a) => (
                    <div key={a.alert_id} className="px-5 py-3">
                      <div className="flex items-start justify-between gap-2">
                        <div className="min-w-0">
                          <p className="text-sm font-medium text-brand-text truncate">{a.student_name}</p>
                          <p className="text-xs text-brand-muted">{a.roll_number}</p>
                          <div className="mt-1">
                            <StatusBadge status={a.status} />
                          </div>
                          <p className="text-xs text-brand-muted mt-1">
                            {a.reason} - {a.location}
                          </p>
                          <p className="text-xs text-brand-text mt-1 line-clamp-2">{a.message}</p>
                        </div>
                        <span className="text-xs text-brand-muted whitespace-nowrap flex-shrink-0">
                          {timeAgo(a.created_at)}
                        </span>
                      </div>
                    </div>
                  ))}
                  {alerts.length === 0 && (
                    <p className="px-5 py-4 text-sm text-brand-muted">No recent alerts</p>
                  )}
                </div>
                <div className="px-5 py-3 border-t border-brand-border">
                  <button
                    onClick={() => router.push("/admin/emergency-alerts")}
                    className="text-xs text-teal-600 hover:text-teal-700 transition-colors"
                  >
                    View all alerts →
                  </button>
                </div>
              </div>

              {/* System users role summary */}
              <div className="bg-white rounded-card border border-brand-border shadow-card">
                <div className="px-5 py-3.5 border-b border-brand-border">
                  <h2 className="text-sm font-semibold text-brand-text">System Users</h2>
                </div>
                <div className="divide-y divide-brand-border">
                  {[
                    { label: "Students", value: dash.total_students },
                    { label: "Professors", value: dash.total_professors },
                    { label: "Doctors", value: dash.total_doctors },
                    { label: "Staff", value: dash.total_staff },
                  ].map(({ label, value }) => (
                    <div key={label} className="flex items-center justify-between px-5 py-3">
                      <span className="text-sm text-brand-muted">{label}</span>
                      <span className="text-sm font-semibold text-teal-600">{value}</span>
                    </div>
                  ))}
                </div>
                <div className="px-5 py-3 border-t border-brand-border">
                  <button
                    onClick={() => router.push("/admin/users")}
                    className="text-xs text-teal-600 hover:text-teal-700 transition-colors"
                  >
                    Manage users →
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </DashboardShell>
  );
}
