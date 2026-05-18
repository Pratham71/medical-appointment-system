"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { getAdminEmergencyAlerts, getStoredUser } from "@/lib/api";
import type { AdminEmergencyAlertSummary } from "@/lib/types";
import DashboardShell from "@/components/layout/DashboardShell";
import StatusBadge from "@/components/ui/StatusBadge";

const item = { hidden: { opacity: 0, y: 12 }, show: { opacity: 1, y: 0 } };
const container = {
  hidden: {},
  show: { transition: { staggerChildren: 0.07 } },
};

export default function StaffDashboardPage() {
  const router = useRouter();
  const [alerts, setAlerts] = useState<AdminEmergencyAlertSummary[]>([]);
  const [userName, setUserName] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const user = getStoredUser();
    if (!user) { router.replace("/login"); return; }
    const PATIENT_ROLES = ["student", "professor", "college-staff", "hostel-staff"];
    if (PATIENT_ROLES.includes(user.role_name)) { router.replace("/students"); return; }
    if (user.role_name === "doctor") { router.replace("/doctors"); return; }
    if (user.role_name === "admin") { router.replace("/admin"); return; }
    if (user.role_name !== "staff") { router.replace("/login"); return; }
    setUserName(user.name.split(" ")[0]);

    getAdminEmergencyAlerts(10)
      .then((al) => setAlerts(al.filter((x) => x.status !== "resolved").slice(0, 3)))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [router]);

  const activeCount = alerts.length;

  return (
    <DashboardShell role="staff" title="Dashboard">
      <motion.div
        variants={container}
        initial="hidden"
        animate="show"
        className="space-y-5"
      >
        {/* Greeting */}
        <motion.div variants={item}>
          <h2 className="text-lg font-semibold text-brand-text">
            {userName ? `Good to see you, ${userName}.` : "Staff Dashboard"}
          </h2>
          <p className="text-sm text-brand-muted mt-0.5">
            Manage walk-ins and respond to emergency alerts from here.
          </p>
        </motion.div>

        {/* Active alerts banner */}
        {!loading && activeCount > 0 && (
          <motion.div
            variants={item}
            className="bg-white rounded-card border-l-4 border-red-400 border-t border-r border-b border-brand-border shadow-card overflow-hidden"
          >
            <div className="flex items-center justify-between px-4 py-3 border-b border-brand-border">
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />
                <h3 className="text-sm font-semibold text-brand-text">Active Alerts</h3>
                <span className="text-xs bg-red-500 text-white rounded-full px-2 py-0.5 font-medium">
                  {activeCount}
                </span>
              </div>
              <button
                onClick={() => router.push("/staff/emergency-alerts")}
                className="text-xs text-teal-600 hover:text-teal-700 font-medium transition-colors"
              >
                View all →
              </button>
            </div>
            <div className="divide-y divide-brand-border">
              {alerts.map((a) => (
                <div key={a.alert_id} className="px-4 py-3">
                  <div className="flex items-start justify-between gap-3">
                    <div className="min-w-0">
                      <div className="flex items-center gap-2 flex-wrap">
                        <p className="text-sm font-medium text-brand-text">{a.student_name}</p>
                        <span className="text-xs text-brand-muted font-mono">{a.roll_number}</span>
                      </div>
                      <p className="text-xs text-brand-muted mt-0.5">{a.reason} · {a.location}</p>
                      {a.message && (
                        <p className="text-xs text-brand-text mt-0.5 line-clamp-1">{a.message}</p>
                      )}
                    </div>
                    <StatusBadge status={a.status} />
                  </div>
                </div>
              ))}
            </div>
          </motion.div>
        )}

        {/* Quick actions */}
        <motion.div variants={item} className="grid gap-4 sm:grid-cols-2">
          <motion.button
            whileHover={{ y: -2 }}
            whileTap={{ scale: 0.98 }}
            transition={{ duration: 0.15 }}
            onClick={() => router.push("/staff/walk-ins")}
            className="rounded-card border border-brand-border bg-white p-5 text-left shadow-card transition-colors hover:border-teal-300 hover:shadow-md"
          >
            <span className="inline-flex h-10 w-10 items-center justify-center rounded-lg bg-teal-50 text-teal-700 ring-1 ring-teal-100">
              <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            </span>
            <p className="mt-3 text-sm font-semibold text-brand-text">Book Walk-in</p>
            <p className="mt-1 text-sm text-brand-muted leading-relaxed">
              Find an existing patient and assign an available slot.
            </p>
            <span className="mt-3 inline-flex items-center gap-1 text-xs text-teal-600 font-medium">
              Open →
            </span>
          </motion.button>

          <motion.button
            whileHover={{ y: -2 }}
            whileTap={{ scale: 0.98 }}
            transition={{ duration: 0.15 }}
            onClick={() => router.push("/staff/emergency-alerts")}
            className="rounded-card border border-brand-border bg-white p-5 text-left shadow-card transition-colors hover:border-red-200 hover:shadow-md relative overflow-hidden"
          >
            {activeCount > 0 && (
              <span className="absolute top-3 right-3 h-2 w-2 rounded-full bg-red-500 ring-2 ring-white" />
            )}
            <span className="inline-flex h-10 w-10 items-center justify-center rounded-lg bg-red-50 text-red-600 ring-1 ring-red-100">
              <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" />
              </svg>
            </span>
            <p className="mt-3 text-sm font-semibold text-brand-text">Emergency Alerts</p>
            <p className="mt-1 text-sm text-brand-muted leading-relaxed">
              Acknowledge and resolve active infirmary alerts.
            </p>
            <span className="mt-3 inline-flex items-center gap-1 text-xs text-red-600 font-medium">
              {activeCount > 0 ? `${activeCount} active` : "No active alerts"} →
            </span>
          </motion.button>
        </motion.div>
      </motion.div>
    </DashboardShell>
  );
}
