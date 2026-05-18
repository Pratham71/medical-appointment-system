"use client";
import { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { getAdminDoctors, getStoredUser } from "@/lib/api";
import type { AdminDoctorSummary } from "@/lib/types";
import DashboardShell from "@/components/layout/DashboardShell";

export default function AdminDoctorsPage() {
  const router = useRouter();
  const [doctors, setDoctors] = useState<AdminDoctorSummary[]>([]);
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const fetchDoctors = useCallback((q: string) => {
    setLoading(true);
    setError("");
    getAdminDoctors(q || undefined)
      .then(setDoctors)
      .catch((e: unknown) => setError(e instanceof Error ? e.message : "Failed to load"))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    const user = getStoredUser();
    if (!user) { router.replace("/login"); return; }
    if (user.role_name !== "admin") { router.replace("/login"); return; }
    fetchDoctors("");
  }, [router, fetchDoctors]);

  return (
    <DashboardShell role="admin" title="Doctors">
      <div className="space-y-4">
        {/* Search */}
        <div className="bg-white rounded-card border border-brand-border shadow-card p-4 flex gap-3">
          <input
            type="text"
            placeholder="Search by name or email…"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && fetchDoctors(query)}
            className="flex-1 border border-brand-border rounded-btn px-3 py-2 text-sm text-brand-text focus:outline-none focus:ring-2 focus:ring-teal-500"
          />
          <button
            onClick={() => fetchDoctors(query)}
            className="px-4 py-2 text-sm bg-teal-600 hover:bg-teal-700 text-white rounded-btn font-medium transition"
          >
            Search
          </button>
        </div>

        {/* Table / Cards */}
        <div className="bg-white rounded-card border border-brand-border shadow-card">
          {error && (
            <div className="px-5 py-4 text-sm text-red-600 bg-red-50 border-b border-brand-border">{error}</div>
          )}

          {loading && (
            <div className="px-5 py-8 text-center text-brand-muted text-sm animate-pulse">Loading…</div>
          )}

          {!loading && doctors.length === 0 && !error && (
            <div className="px-5 py-8 text-center text-brand-muted text-sm">No doctors found</div>
          )}

          {!loading && doctors.length > 0 && (
            <>
              {/* Desktop table */}
              <div className="hidden md:block overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-brand-border bg-brand-bg">
                      <th className="text-left px-5 py-3 text-xs font-medium text-brand-muted">Name</th>
                      <th className="text-left px-5 py-3 text-xs font-medium text-brand-muted">Email</th>
                      <th className="text-left px-5 py-3 text-xs font-medium text-brand-muted">Employee No.</th>
                      <th className="text-left px-5 py-3 text-xs font-medium text-brand-muted">Specialization</th>
                      <th className="text-left px-5 py-3 text-xs font-medium text-brand-muted">Available Today</th>
                      <th className="text-left px-5 py-3 text-xs font-medium text-brand-muted">Today</th>
                      <th className="text-left px-5 py-3 text-xs font-medium text-brand-muted">Upcoming</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-brand-border">
                    {doctors.map((d) => (
                      <tr key={d.doctor_id} className="hover:bg-brand-raised transition-colors">
                        <td className="px-5 py-3 font-medium text-brand-text">{d.doctor_name}</td>
                        <td className="px-5 py-3 text-brand-muted">{d.email}</td>
                        <td className="px-5 py-3 text-brand-muted font-mono text-xs">{d.employee_number}</td>
                        <td className="px-5 py-3 text-brand-muted">{d.specialization ?? "—"}</td>
                        <td className="px-5 py-3">
                          {d.is_available_today ? (
                            <span className="inline-flex items-center gap-1 text-xs text-emerald-600 font-medium">
                              <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>
                              Available
                            </span>
                          ) : (
                            <span className="inline-flex items-center gap-1 text-xs text-red-500 font-medium">
                              <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" /></svg>
                              Unavailable
                            </span>
                          )}
                        </td>
                        <td className="px-5 py-3 text-brand-muted">{d.appointments_today}</td>
                        <td className="px-5 py-3 text-brand-muted">{d.upcoming_appointments}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Mobile cards */}
              <div className="md:hidden divide-y divide-brand-border">
                {doctors.map((d) => (
                  <div key={d.doctor_id} className="p-4">
                    <div className="flex items-start justify-between gap-3">
                      <div className="min-w-0">
                        <p className="font-medium text-brand-text">{d.doctor_name}</p>
                        <p className="text-xs text-brand-muted mt-0.5">{d.email}</p>
                        <p className="text-xs text-brand-muted font-mono mt-0.5">{d.employee_number}</p>
                        {d.specialization && <p className="text-xs text-brand-muted mt-0.5">{d.specialization}</p>}
                      </div>
                      {d.is_available_today ? (
                        <span className="inline-flex items-center gap-1 text-xs text-emerald-600 font-medium flex-shrink-0">
                          <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>
                          Available
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 text-xs text-red-500 font-medium flex-shrink-0">
                          <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" /></svg>
                          Unavailable
                        </span>
                      )}
                    </div>
                    <div className="mt-2 flex gap-4 text-xs text-brand-muted">
                      <span><strong className="text-brand-text">{d.appointments_today}</strong> today</span>
                      <span><strong className="text-brand-text">{d.upcoming_appointments}</strong> upcoming</span>
                    </div>
                  </div>
                ))}
              </div>
            </>
          )}

          {!loading && (
            <div className="px-5 py-3 border-t border-brand-border text-xs text-brand-muted">
              {doctors.length} doctor{doctors.length !== 1 ? "s" : ""}
            </div>
          )}
        </div>
      </div>
    </DashboardShell>
  );
}
