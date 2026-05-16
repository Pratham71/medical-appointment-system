"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getStudentDashboard, getStudentAppointments, getStoredUser } from "@/lib/api";
import { doctorName } from "@/lib/utils";
import type { StudentAppointmentSummary, StudentDashboard } from "@/lib/types";
import DashboardShell from "@/components/layout/DashboardShell";
import StatsCard from "@/components/ui/StatsCard";
import StatusBadge from "@/components/ui/StatusBadge";

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
  const [error, setError] = useState("");

  useEffect(() => {
    const user = getStoredUser();
    if (!user) { router.replace("/login"); return; }
    if (user.role_name === "doctor") { router.replace("/doctors"); return; }
    if (user.role_name === "admin") { router.replace("/admin"); return; }
    if (user.role_name === "staff") { router.replace("/staff"); return; }
    if (user.role_name !== "student") { router.replace("/login"); return; }

    const today = todayKey();
    Promise.all([getStudentDashboard(), getStudentAppointments()])
      .then(([dashboard, appointments]) => {
        setData(dashboard);
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
          {todayCancelled.map((a) => (
            <div
              key={a.appointment_id}
              className="rounded-card border-l-4 border-red-400 border-t border-r border-b border-brand-border bg-red-50 p-4 flex items-center justify-between"
            >
              <div>
                <p className="text-xs text-red-500 uppercase tracking-wide font-medium mb-1">
                  Appointment Cancelled Today
                </p>
                <p className="text-sm font-semibold text-brand-text">
                  {fmt(a.slot_date, a.start_time)}
                </p>
                <p className="text-sm text-brand-muted mt-0.5">
                  Dr. {doctorName(a.doctor_name)}
                </p>
                {a.reason && (
                  <p className="text-xs text-brand-muted mt-0.5">Reason: {a.reason}</p>
                )}
              </div>
              <div className="flex items-center gap-3">
                <StatusBadge status={a.status} />
                <button
                  onClick={() => router.push("/students/book")}
                  className="text-sm text-teal-600 hover:text-teal-700 font-medium transition-colors"
                >
                  Rebook →
                </button>
              </div>
            </div>
          ))}

          {/* Next appointment banner */}
          {data.next_appointment ? (
            <div className="bg-white rounded-card border-l-4 border-teal-600 border-t border-r border-b border-brand-border shadow-card p-4 flex items-center justify-between">
              <div>
                <p className="text-xs text-brand-muted uppercase tracking-wide font-medium mb-1">
                  Next Appointment
                </p>
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
