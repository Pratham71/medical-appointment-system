"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getAdminEmergencyAlerts, getStoredUser } from "@/lib/api";
import type { AdminEmergencyAlertSummary } from "@/lib/types";
import DashboardShell from "@/components/layout/DashboardShell";
import StatusBadge from "@/components/ui/StatusBadge";

export default function StaffDashboardPage() {
  const router = useRouter();
  const [alerts, setAlerts] = useState<AdminEmergencyAlertSummary[]>([]);

  useEffect(() => {
    const user = getStoredUser();
    if (!user) { router.replace("/login"); return; }
    const PATIENT_ROLES = ["student", "professor", "college-staff", "hostel-staff"];
    if (PATIENT_ROLES.includes(user.role_name)) { router.replace("/students"); return; }
    if (user.role_name === "doctor") { router.replace("/doctors"); return; }
    if (user.role_name === "admin") { router.replace("/admin"); return; }
    if (user.role_name !== "staff") { router.replace("/login"); return; }

    getAdminEmergencyAlerts(10)
      .then((al) => setAlerts(al.filter((x) => x.status !== "resolved").slice(0, 3)))
      .catch(() => {});
  }, [router]);

  return (
    <DashboardShell role="staff" title="Staff Dashboard">
      <div className="space-y-5">
        {/* Active emergency alerts */}
        {alerts.length > 0 && (
          <div className="bg-white rounded-card border-l-4 border-red-400 border-t border-r border-b border-brand-border shadow-card">
            <div className="flex items-center justify-between px-5 py-3.5 border-b border-brand-border">
              <h2 className="text-sm font-semibold text-brand-text">Emergency Alerts</h2>
              <div className="flex items-center gap-2">
                <span className="text-xs bg-red-500 text-white rounded-full px-2 py-0.5 font-medium">{alerts.length} active</span>
                <button onClick={() => router.push("/staff/emergency-alerts")} className="text-xs text-teal-600 hover:text-teal-700 transition-colors">View all →</button>
              </div>
            </div>
            <div className="divide-y divide-brand-border">
              {alerts.map((a) => (
                <div key={a.alert_id} className="px-5 py-3">
                  <div className="flex items-start justify-between gap-2">
                    <div className="min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="w-2 h-2 rounded-full bg-red-500 flex-shrink-0" />
                        <p className="text-sm font-medium text-brand-text">{a.student_name}</p>
                        <span className="text-xs text-brand-muted font-mono">{a.roll_number}</span>
                      </div>
                      <p className="text-xs text-brand-muted mt-1">{a.reason} · {a.location}</p>
                      {a.message && <p className="text-xs text-brand-text mt-0.5 line-clamp-1">{a.message}</p>}
                    </div>
                    <StatusBadge status={a.status} />
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="rounded-card border border-brand-border bg-white p-6 shadow-card">
          <p className="text-sm font-medium text-brand-text">Staff access is ready.</p>
          <p className="mt-2 text-sm text-brand-muted">
            Staff can sign in and land here while queue, walk-in, and front-desk workflows are finalized.
          </p>
        </div>
      </div>
    </DashboardShell>
  );
}
