"use client";
import { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { getAdminStaff, getStoredUser } from "@/lib/api";
import type { AdminStaffSummary } from "@/lib/types";
import DashboardShell from "@/components/layout/DashboardShell";

export default function AdminStaffPage() {
  const router = useRouter();
  const [staff, setStaff] = useState<AdminStaffSummary[]>([]);
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const fetchStaff = useCallback((q: string) => {
    setLoading(true);
    setError("");
    getAdminStaff(q || undefined)
      .then(setStaff)
      .catch((e: unknown) => setError(e instanceof Error ? e.message : "Failed to load"))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    const user = getStoredUser();
    if (!user) { router.replace("/login"); return; }
    if (user.role_name !== "admin") { router.replace("/login"); return; }
    fetchStaff("");
  }, [router, fetchStaff]);

  return (
    <DashboardShell role="admin" title="Staff">
      <div className="space-y-4">
        {/* Search */}
        <div className="bg-white rounded-card border border-brand-border shadow-card p-4 flex gap-3">
          <input
            type="text"
            placeholder="Search by name or email…"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && fetchStaff(query)}
            className="flex-1 border border-brand-border rounded-btn px-3 py-2 text-sm text-brand-text focus:outline-none focus:ring-2 focus:ring-teal-500"
          />
          <button
            onClick={() => fetchStaff(query)}
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

          {!loading && staff.length === 0 && !error && (
            <div className="px-5 py-8 text-center text-brand-muted text-sm">No staff found</div>
          )}

          {!loading && staff.length > 0 && (
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
                      <th className="text-left px-5 py-3 text-xs font-medium text-brand-muted">Type</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-brand-border">
                    {staff.map((s) => (
                      <tr key={s.staff_id} className="hover:bg-brand-raised transition-colors">
                        <td className="px-5 py-3 font-medium text-brand-text">{s.staff_name}</td>
                        <td className="px-5 py-3 text-brand-muted">{s.email}</td>
                        <td className="px-5 py-3 text-brand-muted font-mono text-xs">{s.employee_number}</td>
                        <td className="px-5 py-3 text-brand-muted">{s.specialization ?? "—"}</td>
                        <td className="px-5 py-3">
                          {s.is_doctor ? (
                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-teal-50 text-teal-700 ring-1 ring-teal-200">Doctor</span>
                          ) : (
                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-slate-100 text-slate-600 ring-1 ring-slate-200">Staff</span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Mobile cards */}
              <div className="md:hidden divide-y divide-brand-border">
                {staff.map((s) => (
                  <div key={s.staff_id} className="p-4">
                    <div className="flex items-start justify-between gap-3">
                      <div className="min-w-0">
                        <p className="font-medium text-brand-text">{s.staff_name}</p>
                        <p className="text-xs text-brand-muted mt-0.5">{s.email}</p>
                        <p className="text-xs text-brand-muted font-mono mt-0.5">{s.employee_number}</p>
                        {s.specialization && (
                          <p className="text-xs text-brand-muted mt-0.5">{s.specialization}</p>
                        )}
                      </div>
                      {s.is_doctor ? (
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-teal-50 text-teal-700 ring-1 ring-teal-200 flex-shrink-0">Doctor</span>
                      ) : (
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-slate-100 text-slate-600 ring-1 ring-slate-200 flex-shrink-0">Staff</span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </>
          )}

          {!loading && (
            <div className="px-5 py-3 border-t border-brand-border text-xs text-brand-muted">
              {staff.length} staff member{staff.length !== 1 ? "s" : ""}
            </div>
          )}
        </div>
      </div>
    </DashboardShell>
  );
}
