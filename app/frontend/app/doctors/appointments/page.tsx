"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getDoctorAppointments, getStoredUser } from "@/lib/api";
import type { DoctorAppointmentSummary } from "@/lib/types";
import DashboardShell from "@/components/layout/DashboardShell";
import StatusBadge from "@/components/ui/StatusBadge";

type Tab = "today" | "all";

function getLocalDateKey() {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
}

function fmtDate(d: string) {
  return new Date(d).toLocaleDateString("en-IN", { day: "numeric", month: "short", year: "numeric" });
}

export default function DoctorAppointmentsPage() {
  const router = useRouter();
  const [appointments, setAppointments] = useState<DoctorAppointmentSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [tab, setTab] = useState<Tab>("today");

  useEffect(() => {
    const user = getStoredUser();
    if (!user) { router.replace("/login"); setLoading(false); return; }
    getDoctorAppointments()
      .then(setAppointments)
      .catch((e: unknown) => setError(e instanceof Error ? e.message : "Failed to load"))
      .finally(() => setLoading(false));
  }, [router]);

  const today = getLocalDateKey();
  const filtered = tab === "today"
    ? appointments.filter((a) => a.slot_date === today)
    : appointments;

  const tabs: { key: Tab; label: string }[] = [
    { key: "today", label: "Today" },
    { key: "all", label: "All Appointments" },
  ];

  return (
    <DashboardShell role="doctor" title="Appointments">
      {error && (
        <div className="bg-red-50 border border-red-100 text-red-600 text-sm rounded-card px-4 py-3 mb-5">{error}</div>
      )}

      <div className="mb-5 flex border-b border-brand-border">
        {tabs.map((t) => (
          <button
            key={t.key}
            onClick={() => setTab(t.key)}
            className={`-mb-px border-b-2 px-4 py-2.5 text-sm font-medium transition-colors ${
              tab === t.key
                ? "border-teal-600 text-teal-700"
                : "border-transparent text-brand-muted hover:text-brand-text"
            }`}
          >
            {t.label}
            {t.key === "today" && !loading && (
              <span className={`ml-2 rounded-full px-1.5 py-0.5 text-xs ${
                tab === "today" ? "bg-teal-100 text-teal-700" : "bg-brand-raised text-brand-muted"
              }`}>
                {appointments.filter((a) => a.slot_date === today).length}
              </span>
            )}
          </button>
        ))}
      </div>

      <div className="bg-white rounded-card border border-brand-border shadow-card overflow-hidden">
        {loading ? (
          <div className="p-6 text-brand-muted text-sm animate-pulse">Loading…</div>
        ) : filtered.length === 0 ? (
          <div className="p-8 text-center text-brand-muted text-sm">
            {tab === "today" ? "No appointments scheduled for today." : "No appointments found."}
          </div>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-brand-raised border-b border-brand-border">
                {tab === "all" && <th className="text-left px-4 py-3 text-xs font-semibold text-brand-muted uppercase tracking-wide">Date</th>}
                <th className="text-left px-4 py-3 text-xs font-semibold text-brand-muted uppercase tracking-wide">Time</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-brand-muted uppercase tracking-wide">Patient</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-brand-muted uppercase tracking-wide">Student ID</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-brand-muted uppercase tracking-wide">Status</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-brand-muted uppercase tracking-wide">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-brand-border">
              {filtered.map((a) => (
                <tr key={a.appointment_id} className="hover:bg-brand-raised transition-colors">
                  {tab === "all" && <td className="px-4 py-3 text-brand-text">{fmtDate(a.slot_date)}</td>}
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
