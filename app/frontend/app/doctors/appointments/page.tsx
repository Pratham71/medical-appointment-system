"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getDoctorAppointments, getStoredUser } from "@/lib/api";
import type { DoctorAppointmentSummary } from "@/lib/types";
import DashboardShell from "@/components/layout/DashboardShell";
import StatusBadge from "@/components/ui/StatusBadge";

function fmtDate(d: string) {
  return new Date(d).toLocaleDateString("en-IN", { day: "numeric", month: "short", year: "numeric" });
}

export default function DoctorAppointmentsPage() {
  const router = useRouter();
  const [appointments, setAppointments] = useState<DoctorAppointmentSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const user = getStoredUser();
    if (!user) { router.replace("/login"); return; }
    getDoctorAppointments()
      .then(setAppointments)
      .catch((e: unknown) => setError(e instanceof Error ? e.message : "Failed to load"))
      .finally(() => setLoading(false));
  }, [router]);

  return (
    <DashboardShell role="doctor" title="Appointments">
      {error && (
        <div className="bg-red-50 border border-red-100 text-red-600 text-sm rounded-card px-4 py-3 mb-5">{error}</div>
      )}

      <div className="bg-white rounded-card border border-brand-border shadow-card overflow-hidden">
        {loading ? (
          <div className="p-6 text-brand-muted text-sm animate-pulse">Loading…</div>
        ) : appointments.length === 0 ? (
          <div className="p-8 text-center text-brand-muted text-sm">No appointments found.</div>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-brand-raised border-b border-brand-border">
                <th className="text-left px-4 py-3 text-xs font-semibold text-brand-muted uppercase tracking-wide">Date</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-brand-muted uppercase tracking-wide">Time</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-brand-muted uppercase tracking-wide">Patient</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-brand-muted uppercase tracking-wide">Student ID</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-brand-muted uppercase tracking-wide">Status</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-brand-muted uppercase tracking-wide">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-brand-border">
              {appointments.map((a) => (
                <tr key={a.appointment_id} className="hover:bg-brand-raised transition-colors">
                  <td className="px-4 py-3 text-brand-text">{fmtDate(a.slot_date)}</td>
                  <td className="px-4 py-3 font-mono text-xs text-brand-text">{a.start_time.slice(0, 5)}</td>
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
    </DashboardShell>
  );
}
