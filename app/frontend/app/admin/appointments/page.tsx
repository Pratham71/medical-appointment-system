"use client";
import { useEffect, useState, Fragment } from "react";
import { useRouter } from "next/navigation";
import { getAdminAppointments, getStoredUser } from "@/lib/api";
import type { AdminAppointmentSummary } from "@/lib/types";
import DashboardShell from "@/components/layout/DashboardShell";
import StatusBadge from "@/components/ui/StatusBadge";

function groupByMonth<T extends { slot_date: string }>(items: T[]) {
  const map = new Map<string, T[]>();
  for (const item of items) {
    const [year, month] = item.slot_date.split("-");
    const key = `${year}-${month}`;
    if (!map.has(key)) map.set(key, []);
    map.get(key)!.push(item);
  }
  return Array.from(map.entries())
    .sort((a, b) => b[0].localeCompare(a[0]))
    .map(([key, rows]) => ({
      key,
      label: new Date(`${key}-01`).toLocaleDateString("en-IN", { month: "long", year: "numeric" }),
      rows,
    }));
}

function fmtDate(date: string) {
  return new Date(date + "T00:00:00").toLocaleDateString("en-IN", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });
}

export default function AdminAppointmentsPage() {
  const router = useRouter();
  const [appts, setAppts] = useState<AdminAppointmentSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [status, setStatus] = useState("");
  const [fromDate, setFromDate] = useState("");
  const [toDate, setToDate] = useState("");
  const [collapsedMonths, setCollapsedMonths] = useState<Set<string>>(new Set());

  function toggleMonth(key: string) {
    setCollapsedMonths((prev) => {
      const next = new Set(prev);
      next.has(key) ? next.delete(key) : next.add(key);
      return next;
    });
  }

  useEffect(() => {
    const user = getStoredUser();
    if (!user) { router.replace("/login"); return; }
    if (user.role_name !== "admin") { router.replace("/login"); return; }
    fetchAppts({});
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [router]);

  function fetchAppts(params: {
    status?: string;
    from_date?: string;
    to_date?: string;
  }) {
    setLoading(true);
    setError("");
    getAdminAppointments({ ...params, limit: 250 })
      .then(setAppts)
      .catch((e: unknown) => setError(e instanceof Error ? e.message : "Failed to load"))
      .finally(() => setLoading(false));
  }

  function handleApply() {
    fetchAppts({
      status: status || undefined,
      from_date: fromDate || undefined,
      to_date: toDate || undefined,
    });
  }

  function handleClear() {
    setStatus("");
    setFromDate("");
    setToDate("");
    fetchAppts({});
  }

  return (
    <DashboardShell role="admin" title="Appointments">
      <div className="space-y-4">
        {/* Filter bar */}
        <div className="bg-white rounded-card border border-brand-border shadow-card p-4 flex flex-wrap gap-3 items-end">
          <div>
            <label className="block text-xs font-medium text-brand-muted mb-1">Status</label>
            <select
              value={status}
              onChange={(e) => setStatus(e.target.value)}
              className="border border-brand-border rounded-btn px-3 py-2 text-sm text-brand-text bg-white focus:outline-none focus:ring-2 focus:ring-teal-500"
            >
              <option value="">All statuses</option>
              <option value="booked">Booked</option>
              <option value="completed">Completed</option>
              <option value="cancelled">Cancelled</option>
            </select>
          </div>
          <div>
            <label className="block text-xs font-medium text-brand-muted mb-1">From date</label>
            <input
              type="date"
              value={fromDate}
              onChange={(e) => setFromDate(e.target.value)}
              className="border border-brand-border rounded-btn px-3 py-2 text-sm text-brand-text focus:outline-none focus:ring-2 focus:ring-teal-500"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-brand-muted mb-1">To date</label>
            <input
              type="date"
              value={toDate}
              onChange={(e) => setToDate(e.target.value)}
              className="border border-brand-border rounded-btn px-3 py-2 text-sm text-brand-text focus:outline-none focus:ring-2 focus:ring-teal-500"
            />
          </div>
          <div className="flex gap-2">
            <button
              onClick={handleApply}
              className="px-4 py-2 text-sm bg-teal-600 hover:bg-teal-700 text-white rounded-btn font-medium transition"
            >
              Apply
            </button>
            <button
              onClick={handleClear}
              className="px-4 py-2 text-sm border border-brand-border text-brand-muted hover:bg-brand-raised rounded-btn transition"
            >
              Clear
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
                  <th className="text-left px-5 py-3 text-xs font-medium text-brand-muted">#</th>
                  <th className="text-left px-5 py-3 text-xs font-medium text-brand-muted">Date</th>
                  <th className="text-left px-5 py-3 text-xs font-medium text-brand-muted">Time</th>
                  <th className="text-left px-5 py-3 text-xs font-medium text-brand-muted">Student</th>
                  <th className="text-left px-5 py-3 text-xs font-medium text-brand-muted">Doctor</th>
                  <th className="text-left px-5 py-3 text-xs font-medium text-brand-muted">Status</th>
                  <th className="text-left px-5 py-3 text-xs font-medium text-brand-muted">Reason</th>
                  <th className="text-left px-5 py-3 text-xs font-medium text-brand-muted">Cancellation</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-brand-border">
                {loading && (
                  <tr>
                    <td colSpan={8} className="px-5 py-8 text-center text-brand-muted text-sm animate-pulse">
                      Loading…
                    </td>
                  </tr>
                )}
                {!loading && appts.length === 0 && !error && (
                  <tr>
                    <td colSpan={8} className="px-5 py-8 text-center text-brand-muted text-sm">
                      No appointments found
                    </td>
                  </tr>
                )}
                {!loading && groupByMonth(appts).map((group) => {
                  const collapsed = collapsedMonths.has(group.key);
                  return (
                    <Fragment key={group.key}>
                      <tr
                        className="bg-brand-raised/70 cursor-pointer hover:bg-brand-raised border-y border-brand-border select-none"
                        onClick={() => toggleMonth(group.key)}
                      >
                        <td colSpan={8} className="px-5 py-2">
                          <div className="flex items-center gap-2">
                            <svg
                              className={`w-3 h-3 text-brand-muted transition-transform duration-150 ${collapsed ? "" : "rotate-90"}`}
                              fill="none" stroke="currentColor" viewBox="0 0 24 24"
                            >
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M9 5l7 7-7 7" />
                            </svg>
                            <span className="text-xs font-semibold text-brand-text">{group.label}</span>
                            <span className="text-xs text-brand-muted">·</span>
                            <span className="text-xs text-brand-muted">
                              {group.rows.length} appointment{group.rows.length !== 1 ? "s" : ""}
                            </span>
                          </div>
                        </td>
                      </tr>
                      {!collapsed && group.rows.map((a) => (
                        <tr key={a.appointment_id} className="hover:bg-brand-raised transition-colors">
                          <td className="px-5 py-3 text-brand-muted text-xs">{a.appointment_id}</td>
                          <td className="px-5 py-3 text-brand-muted whitespace-nowrap">{fmtDate(a.slot_date)}</td>
                          <td className="px-5 py-3 text-brand-muted whitespace-nowrap">{a.start_time.slice(0, 5)}</td>
                          <td className="px-5 py-3">
                            <p className="font-medium text-brand-text">{a.student_name}</p>
                            <p className="text-xs text-brand-muted">{a.roll_number}</p>
                          </td>
                          <td className="px-5 py-3 text-brand-muted">{a.doctor_name}</td>
                          <td className="px-5 py-3"><StatusBadge status={a.status} /></td>
                          <td className="px-5 py-3 text-brand-muted max-w-[160px] truncate">{a.reason ?? "—"}</td>
                          <td className="px-5 py-3 text-brand-muted max-w-[160px] truncate">{a.cancellation_reason ?? "—"}</td>
                        </tr>
                      ))}
                    </Fragment>
                  );
                })}
              </tbody>
            </table>
          </div>
          {!loading && (
            <div className="px-5 py-3 border-t border-brand-border text-xs text-brand-muted">
              {appts.length} appointment{appts.length !== 1 ? "s" : ""}
            </div>
          )}
        </div>
      </div>
    </DashboardShell>
  );
}
