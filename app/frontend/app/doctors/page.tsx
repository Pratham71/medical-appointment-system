"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getDoctorDashboard, getDoctorAppointments, getStoredUser } from "@/lib/api";
import type { DoctorDashboard, DoctorAppointmentSummary } from "@/lib/types";
import DashboardShell from "@/components/layout/DashboardShell";
import StatsCard from "@/components/ui/StatsCard";
import StatusBadge from "@/components/ui/StatusBadge";

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
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const user = getStoredUser();
    if (!user) { router.replace("/login"); return; }
    if (user.role_name === "student") { router.replace("/students"); return; }
    if (user.role_name === "admin") { router.replace("/admin"); return; }
    if (user.role_name === "staff") { router.replace("/staff"); return; }
    if (user.role_name !== "doctor") { router.replace("/login"); return; }

    Promise.all([getDoctorDashboard(), getDoctorAppointments()])
      .then(([d, a]) => { setDashboard(d); setAppointments(a); })
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
              label="Completed Today"
              value={dashboard.todays_appointments}
              icon={
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              }
            />
            <StatsCard
              label="Upcoming"
              value={dashboard.upcoming_appointments}
              icon={
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              }
            />
            <StatsCard
              label="Total Patients"
              value={dashboard.total_patients}
              icon={
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
              }
            />
          </div>

          {/* Today's Schedule */}
          <div className="bg-white rounded-card border border-brand-border shadow-card overflow-hidden">
            <div className="px-5 py-3.5 border-b border-brand-border flex items-center justify-between">
              <h2 className="text-sm font-semibold text-brand-text">Today&apos;s Schedule</h2>
              <button
                onClick={() => router.push("/doctors/appointments")}
                className="text-xs text-teal-600 hover:text-teal-700 transition-colors"
              >
                View all →
              </button>
            </div>

            {todaysAppts.length === 0 ? (
              <div className="p-6 text-center text-brand-muted text-sm">
                No appointments scheduled for today.
              </div>
            ) : (
              <table className="w-full text-sm">
                <thead>
                  <tr className="bg-brand-raised border-b border-brand-border">
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
                      <td className="px-4 py-3 font-mono text-xs text-brand-text">
                        {fmtTime(a.start_time)}
                      </td>
                      <td className="px-4 py-3 text-brand-text">{a.student_name}</td>
                      <td className="px-4 py-3 font-mono text-xs text-brand-muted">{a.student_id}</td>
                      <td className="px-4 py-3">
                        <StatusBadge status={a.status} />
                      </td>
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
          </div>
        </div>
      )}
    </DashboardShell>
  );
}
