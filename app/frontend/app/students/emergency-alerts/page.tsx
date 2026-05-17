"use client";
import { useEffect, useState, Fragment } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { getStudentEmergencyAlerts, getStoredUser } from "@/lib/api";
import type { StudentEmergencyAlertSummary } from "@/lib/types";
import DashboardShell from "@/components/layout/DashboardShell";

const PATIENT_ROLES = ["student", "professor", "college-staff", "hostel-staff"];

function groupByMonth<T extends { created_at: string }>(items: T[]) {
  const map = new Map<string, T[]>();
  for (const item of items) {
    const d = new Date(item.created_at);
    const key = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}`;
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

function fmtFull(iso: string) {
  return new Date(iso).toLocaleString("en-IN", {
    day: "numeric", month: "short", year: "numeric",
    hour: "2-digit", minute: "2-digit",
  });
}

function timeAgo(iso: string) {
  const h = Math.floor((Date.now() - new Date(iso).getTime()) / 3_600_000);
  if (h < 1) return "< 1h ago";
  if (h < 24) return `${h}h ago`;
  return `${Math.floor(h / 24)}d ago`;
}

const STATUS_STYLES = {
  unread: "bg-red-50 text-red-700 ring-1 ring-red-200",
  acknowledged: "bg-amber-50 text-amber-700 ring-1 ring-amber-200",
  resolved: "bg-emerald-50 text-emerald-700 ring-1 ring-emerald-200",
};
const STATUS_LABELS = { unread: "Unread", acknowledged: "Acknowledged", resolved: "Resolved" };

export default function StudentEmergencyAlertsPage() {
  const router = useRouter();
  const [alerts, setAlerts] = useState<StudentEmergencyAlertSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [collapsedMonths, setCollapsedMonths] = useState<Set<string>>(new Set());

  function toggleMonth(key: string) {
    setCollapsedMonths((prev) => {
      const n = new Set(prev);
      n.has(key) ? n.delete(key) : n.add(key);
      return n;
    });
  }

  useEffect(() => {
    const user = getStoredUser();
    if (!user) { router.replace("/login"); return; }
    if (!PATIENT_ROLES.includes(user.role_name)) { router.replace("/login"); return; }
    getStudentEmergencyAlerts()
      .then(setAlerts)
      .catch((e: unknown) => setError(e instanceof Error ? e.message : "Failed to load"))
      .finally(() => setLoading(false));
  }, [router]);

  return (
    <DashboardShell role="student" title="My Emergency Alerts">
      <div className="space-y-4">
        <div className="flex items-center gap-3">
          <h2 className="text-sm font-semibold text-brand-text">
            {loading ? "Loading…" : `${alerts.length} alert${alerts.length !== 1 ? "s" : ""} sent`}
          </h2>
          {!loading && alerts.filter((a) => a.status === "unread").length > 0 && (
            <span className="text-xs bg-red-500 text-white rounded-full px-2.5 py-0.5 font-medium">
              {alerts.filter((a) => a.status === "unread").length} pending
            </span>
          )}
        </div>

        {error && (
          <div className="bg-red-50 border border-red-100 text-red-600 text-sm rounded-card px-4 py-3">{error}</div>
        )}

        {!loading && alerts.length === 0 && !error && (
          <div className="bg-white rounded-card border border-brand-border shadow-card p-8 text-center">
            <p className="text-brand-muted text-sm">No emergency alerts sent yet.</p>
            <p className="text-xs text-brand-muted mt-1">Use the emergency button to alert infirmary staff.</p>
          </div>
        )}

        <div className="space-y-1">
          {groupByMonth(alerts).map((group) => {
            const collapsed = collapsedMonths.has(group.key);
            return (
              <Fragment key={group.key}>
                <button
                  onClick={() => toggleMonth(group.key)}
                  className="flex items-center gap-2 w-full text-left py-2 px-1 rounded hover:bg-brand-raised transition-colors select-none"
                >
                  <svg className={`w-3 h-3 text-brand-muted transition-transform duration-150 ${collapsed ? "" : "rotate-90"}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M9 5l7 7-7 7" />
                  </svg>
                  <span className="text-xs font-semibold text-brand-text">{group.label}</span>
                  <span className="text-xs text-brand-muted">·</span>
                  <span className="text-xs text-brand-muted">{group.rows.length} alert{group.rows.length !== 1 ? "s" : ""}</span>
                </button>

                {!collapsed && (
                  <div className="space-y-3 mb-4 mt-1">
                    {group.rows.map((a, i) => (
                      <motion.div
                        key={a.alert_id}
                        initial={{ opacity: 0, y: 8 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.18, delay: Math.min(i * 0.04, 0.25) }}
                        className={`bg-white rounded-card border-l-4 border-t border-r border-b border-brand-border shadow-card p-4 ${
                          a.status === "resolved" ? "border-l-emerald-400 opacity-75" : "border-l-red-400"
                        }`}
                      >
                        <div className="flex items-start justify-between gap-4">
                          <div className="min-w-0 flex-1 space-y-2">
                            <div className="flex items-center gap-2 flex-wrap">
                              <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${STATUS_STYLES[a.status]}`}>
                                {STATUS_LABELS[a.status]}
                              </span>
                              <span className="text-xs text-brand-muted">{timeAgo(a.created_at)}</span>
                            </div>
                            <div className="grid gap-2 sm:grid-cols-3 text-xs">
                              <div className="rounded-btn bg-brand-bg px-3 py-2">
                                <span className="block text-brand-muted mb-0.5">Reason</span>
                                <span className="font-medium text-brand-text">{a.reason}</span>
                              </div>
                              <div className="rounded-btn bg-brand-bg px-3 py-2">
                                <span className="block text-brand-muted mb-0.5">Location</span>
                                <span className="font-medium text-brand-text">{a.location}</span>
                              </div>
                              <div className="rounded-btn bg-brand-bg px-3 py-2">
                                <span className="block text-brand-muted mb-0.5">Contact</span>
                                <span className="font-medium text-brand-text">{a.contact_number || "Not provided"}</span>
                              </div>
                            </div>
                            {a.message && <p className="text-sm text-brand-text">{a.message}</p>}
                            {a.resolution_note && (
                              <div className="rounded-btn bg-emerald-50 border border-emerald-100 px-3 py-2 text-xs">
                                <span className="text-emerald-600 font-medium">Staff note: </span>
                                <span className="text-emerald-700">{a.resolution_note}</span>
                              </div>
                            )}
                            <p className="text-xs text-brand-muted">{fmtFull(a.created_at)}</p>
                          </div>
                        </div>
                      </motion.div>
                    ))}
                  </div>
                )}
              </Fragment>
            );
          })}
        </div>
      </div>
    </DashboardShell>
  );
}
