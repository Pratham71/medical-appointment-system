"use client";
import { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { getAdminStudents, getStoredUser } from "@/lib/api";
import type { AdminStudentSummary } from "@/lib/types";
import DashboardShell from "@/components/layout/DashboardShell";

type Tab = "student" | "professor";

export default function AdminStudentsPage() {
  const router = useRouter();
  const [all, setAll] = useState<AdminStudentSummary[]>([]);
  const [query, setQuery] = useState("");
  const [tab, setTab] = useState<Tab>("student");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const fetchAll = useCallback((q: string) => {
    setLoading(true);
    setError("");
    getAdminStudents(q || undefined)
      .then(setAll)
      .catch((e: unknown) => setError(e instanceof Error ? e.message : "Failed to load"))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    const user = getStoredUser();
    if (!user) { router.replace("/login"); return; }
    if (user.role_name !== "admin") { router.replace("/login"); return; }
    fetchAll("");
  }, [router, fetchAll]);

  const rows = all.filter((s) => s.role_name === tab);

  return (
    <DashboardShell role="admin" title="Students & Professors">
      <div className="space-y-4">
        {/* Tabs + search row */}
        <div className="flex flex-wrap items-center gap-3">
          {/* Tab switcher */}
          <div className="flex bg-white rounded-card border border-brand-border shadow-card overflow-hidden">
            {(["student", "professor"] as Tab[]).map((t) => (
              <button
                key={t}
                onClick={() => setTab(t)}
                className={`px-4 py-2 text-sm font-medium transition-colors ${
                  tab === t
                    ? "bg-teal-600 text-white"
                    : "text-brand-muted hover:text-brand-text hover:bg-brand-raised"
                }`}
              >
                {t === "student" ? "Students" : "Professors"}
                {!loading && (
                  <span className={`ml-2 text-xs px-1.5 py-0.5 rounded-full ${
                    tab === t ? "bg-teal-700 text-teal-100" : "bg-brand-raised text-brand-muted"
                  }`}>
                    {all.filter((s) => s.role_name === t).length}
                  </span>
                )}
              </button>
            ))}
          </div>

          {/* Search */}
          <div className="flex gap-2 flex-1 min-w-[240px]">
            <input
              type="text"
              placeholder={`Search ${tab === "student" ? "students" : "professors"}…`}
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && fetchAll(query)}
              className="flex-1 border border-brand-border rounded-btn px-3 py-2 text-sm text-brand-text bg-white shadow-card focus:outline-none focus:ring-2 focus:ring-teal-500"
            />
            <button
              onClick={() => fetchAll(query)}
              className="px-4 py-2 text-sm bg-teal-600 hover:bg-teal-700 text-white rounded-btn font-medium transition"
            >
              Search
            </button>
          </div>
        </div>

        {/* Table */}
        <div className="bg-white rounded-card border border-brand-border shadow-card">
          {error && (
            <div className="px-5 py-4 text-sm text-red-600 bg-red-50 border-b border-brand-border">{error}</div>
          )}
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-brand-border bg-brand-bg">
                  <th className="text-left px-5 py-3 text-xs font-medium text-brand-muted">Name</th>
                  <th className="text-left px-5 py-3 text-xs font-medium text-brand-muted">Email</th>
                  <th className="text-left px-5 py-3 text-xs font-medium text-brand-muted">
                    {tab === "student" ? "Roll No." : "ID"}
                  </th>
                  <th className="text-left px-5 py-3 text-xs font-medium text-brand-muted">Department</th>
                  <th className="text-left px-5 py-3 text-xs font-medium text-brand-muted">Year</th>
                  <th className="text-left px-5 py-3 text-xs font-medium text-brand-muted">Total Appts</th>
                  <th className="text-left px-5 py-3 text-xs font-medium text-brand-muted">Completed</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-brand-border">
                {loading && (
                  <tr>
                    <td colSpan={7} className="px-5 py-8 text-center text-brand-muted text-sm animate-pulse">
                      Loading…
                    </td>
                  </tr>
                )}
                {!loading && rows.map((s) => (
                  <tr key={s.student_id} className="hover:bg-brand-raised transition-colors">
                    <td className="px-5 py-3 font-medium text-brand-text">{s.student_name}</td>
                    <td className="px-5 py-3 text-brand-muted">{s.email}</td>
                    <td className="px-5 py-3 text-brand-muted font-mono text-xs">{s.roll_number}</td>
                    <td className="px-5 py-3 text-brand-muted">{s.department}</td>
                    <td className="px-5 py-3">
                      <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ring-1 ${
                        tab === "professor"
                          ? "bg-purple-50 text-purple-700 ring-purple-200"
                          : "bg-teal-50 text-teal-700 ring-teal-200"
                      }`}>
                        Y{s.year_level}
                      </span>
                    </td>
                    <td className="px-5 py-3 text-brand-muted">{s.total_appointments}</td>
                    <td className="px-5 py-3 text-emerald-600 font-medium">{s.completed_appointments}</td>
                  </tr>
                ))}
                {!loading && rows.length === 0 && !error && (
                  <tr>
                    <td colSpan={7} className="px-5 py-8 text-center text-brand-muted text-sm">
                      No {tab === "student" ? "students" : "professors"} found
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
          {!loading && (
            <div className="px-5 py-3 border-t border-brand-border text-xs text-brand-muted">
              {rows.length} {tab === "student" ? "student" : "professor"}{rows.length !== 1 ? "s" : ""}
            </div>
          )}
        </div>
      </div>
    </DashboardShell>
  );
}
