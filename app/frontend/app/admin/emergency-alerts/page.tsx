"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import {
  acknowledgeEmergencyAlert,
  getAdminEmergencyAlerts,
  getStoredUser,
  resolveEmergencyAlert,
} from "@/lib/api";
import type { AdminEmergencyAlertSummary } from "@/lib/types";
import DashboardShell from "@/components/layout/DashboardShell";
import StatusBadge from "@/components/ui/StatusBadge";

function timeAgo(iso: string): string {
  const h = Math.floor((Date.now() - new Date(iso).getTime()) / 3_600_000);
  if (h < 1) return "< 1h ago";
  if (h < 24) return `${h}h ago`;
  const d = Math.floor(h / 24);
  return `${d}d ago`;
}

function fmtFull(iso: string): string {
  return new Date(iso).toLocaleString("en-IN", {
    day: "numeric",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export default function AdminEmergencyAlertsPage() {
  const router = useRouter();
  const [alerts, setAlerts] = useState<AdminEmergencyAlertSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [actionBusy, setActionBusy] = useState<number | null>(null);
  const [resolutionNote, setResolutionNote] = useState<Record<number, string>>({});

  useEffect(() => {
    const user = getStoredUser();
    if (!user) { router.replace("/login"); return; }
    if (user.role_name !== "admin") { router.replace("/login"); return; }

    getAdminEmergencyAlerts(100)
      .then(setAlerts)
      .catch((e: unknown) => setError(e instanceof Error ? e.message : "Failed to load"))
      .finally(() => setLoading(false));
  }, [router]);

  const replaceAlert = (updated: AdminEmergencyAlertSummary) => {
    setAlerts((current) =>
      current.map((alert) => (alert.alert_id === updated.alert_id ? updated : alert))
    );
  };

  const handleAcknowledge = async (alertId: number) => {
    setActionBusy(alertId);
    setError("");
    try {
      replaceAlert(await acknowledgeEmergencyAlert(alertId));
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to acknowledge alert");
    } finally {
      setActionBusy(null);
    }
  };

  const handleResolve = async (alertId: number) => {
    setActionBusy(alertId);
    setError("");
    try {
      replaceAlert(await resolveEmergencyAlert(alertId, resolutionNote[alertId]));
      setResolutionNote((current) => ({ ...current, [alertId]: "" }));
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to resolve alert");
    } finally {
      setActionBusy(null);
    }
  };

  return (
    <DashboardShell role="admin" title="Emergency Alerts">
      <div className="space-y-4">
        {/* Header summary */}
        <div className="flex items-center gap-3">
          <h2 className="text-sm font-semibold text-brand-text">
            {loading ? "Loading…" : `${alerts.length} alert${alerts.length !== 1 ? "s" : ""} total`}
          </h2>
          {!loading && alerts.length > 0 && (
            <span className="text-xs bg-red-500 text-white rounded-full px-2.5 py-0.5 font-medium">
              {alerts.length} recorded
            </span>
          )}
        </div>

        {error && (
          <div className="bg-red-50 border border-red-100 text-red-600 text-sm rounded-card px-4 py-3">
            {error}
          </div>
        )}

        {loading && (
          <div className="text-brand-muted text-sm animate-pulse">Loading…</div>
        )}

        {/* Alert cards */}
        <div className="space-y-3">
          {alerts.map((a, i) => (
            <motion.div
              key={a.alert_id}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.25, delay: i * 0.04, ease: "easeOut" }}
              className="bg-white rounded-card border-l-4 border-red-400 border-t border-r border-b border-brand-border shadow-card p-4"
            >
              <div className="flex items-start justify-between gap-4">
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="w-2 h-2 rounded-full bg-red-500 flex-shrink-0" />
                    <p className="text-sm font-semibold text-brand-text">{a.student_name}</p>
                    <span className="text-xs text-brand-muted font-mono">{a.roll_number}</span>
                    <StatusBadge status={a.status} />
                  </div>
                  <div className="grid gap-2 py-2 text-xs sm:grid-cols-3">
                    <div className="rounded-btn bg-brand-bg px-3 py-2">
                      <span className="block text-brand-muted">Reason</span>
                      <span className="font-medium text-brand-text">{a.reason}</span>
                    </div>
                    <div className="rounded-btn bg-brand-bg px-3 py-2">
                      <span className="block text-brand-muted">Location</span>
                      <span className="font-medium text-brand-text">{a.location}</span>
                    </div>
                    <div className="rounded-btn bg-brand-bg px-3 py-2">
                      <span className="block text-brand-muted">Contact</span>
                      <span className="font-medium text-brand-text">
                        {a.contact_number || "Not provided"}
                      </span>
                    </div>
                  </div>
                  <p className="text-sm text-brand-text leading-relaxed">{a.message}</p>
                  {a.resolution_note && (
                    <p className="mt-2 text-xs text-emerald-700">
                      <span className="font-medium">Resolution:</span> {a.resolution_note}
                    </p>
                  )}
                  <p className="text-xs text-brand-muted mt-2">{fmtFull(a.created_at)}</p>
                </div>
                <div className="flex w-48 flex-shrink-0 flex-col items-end gap-2 text-right">
                  <span className="text-xs text-brand-muted">{timeAgo(a.created_at)}</span>
                  {a.status !== "resolved" && (
                    <>
                      {a.status === "unread" && (
                        <button
                          onClick={() => handleAcknowledge(a.alert_id)}
                          disabled={actionBusy === a.alert_id}
                          className="rounded-btn border border-amber-200 px-3 py-1 text-xs font-medium text-amber-700 hover:bg-amber-50 disabled:opacity-60"
                        >
                          Acknowledge
                        </button>
                      )}
                      <input
                        value={resolutionNote[a.alert_id] ?? ""}
                        onChange={(e) =>
                          setResolutionNote((current) => ({
                            ...current,
                            [a.alert_id]: e.target.value,
                          }))
                        }
                        placeholder="Resolution note"
                        className="w-full rounded-btn border border-brand-border px-2 py-1 text-xs text-brand-text outline-none focus:border-emerald-300"
                      />
                      <button
                        onClick={() => handleResolve(a.alert_id)}
                        disabled={actionBusy === a.alert_id}
                        className="rounded-btn border border-emerald-200 px-3 py-1 text-xs font-medium text-emerald-700 hover:bg-emerald-50 disabled:opacity-60"
                      >
                        Resolve
                      </button>
                    </>
                  )}
                </div>
              </div>
            </motion.div>
          ))}

          {!loading && alerts.length === 0 && !error && (
            <div className="bg-white rounded-card border border-brand-border shadow-card p-8 text-center">
              <p className="text-brand-muted text-sm">No emergency alerts recorded</p>
            </div>
          )}
        </div>
      </div>
    </DashboardShell>
  );
}
