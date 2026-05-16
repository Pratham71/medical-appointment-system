"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getStudentAppointments, cancelAppointment, getStoredUser } from "@/lib/api";
import { doctorName } from "@/lib/utils";
import type { StudentAppointmentSummary } from "@/lib/types";
import { motion, AnimatePresence } from "framer-motion";
import DashboardShell from "@/components/layout/DashboardShell";
import StatusBadge from "@/components/ui/StatusBadge";
import Modal from "@/components/ui/Modal";
import { SkeletonTableRows } from "@/components/ui/Skeleton";

type Tab = "upcoming" | "past" | "cancelled";

function fmtDate(d: string) {
  return new Date(d).toLocaleDateString("en-IN", { day: "numeric", month: "short", year: "numeric" });
}

export default function MyAppointmentsPage() {
  const router = useRouter();
  const [appointments, setAppointments] = useState<StudentAppointmentSummary[]>([]);
  const [tab, setTab] = useState<Tab>("upcoming");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [cancelId, setCancelId] = useState<number | null>(null);
  const [cancelling, setCancelling] = useState(false);

  useEffect(() => {
    const user = getStoredUser();
    if (!user) { router.replace("/login"); setLoading(false); return; }
    getStudentAppointments()
      .then(setAppointments)
      .catch((e: unknown) => setError(e instanceof Error ? e.message : "Failed to load"))
      .finally(() => setLoading(false));
  }, [router]);

  const filtered = appointments.filter((a) => {
    const s = a.status.toLowerCase();
    if (tab === "upcoming") return s === "booked";
    if (tab === "past") return s === "completed";
    return s === "cancelled";
  });

  const handleCancel = async () => {
    if (!cancelId) return;
    setCancelling(true);
    try {
      await cancelAppointment(cancelId);
      setAppointments((prev) =>
        prev.map((a) => (a.appointment_id === cancelId ? { ...a, status: "cancelled" } : a))
      );
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Cancel failed");
    } finally {
      setCancelling(false);
      setCancelId(null);
    }
  };

  const tabs: { key: Tab; label: string }[] = [
    { key: "upcoming", label: "Upcoming" },
    { key: "past", label: "Past" },
    { key: "cancelled", label: "Cancelled" },
  ];

  return (
    <DashboardShell role="student" title="My Appointments">
      <AnimatePresence>
        {cancelId && (
          <Modal
            title="Cancel Appointment"
            message="Are you sure you want to cancel this appointment? This action cannot be undone."
            confirmLabel={cancelling ? "Cancelling…" : "Cancel Appointment"}
            cancelLabel="Keep Appointment"
            danger
            onConfirm={handleCancel}
            onCancel={() => setCancelId(null)}
          />
        )}
      </AnimatePresence>

      {/* Tabs */}
      <div className="flex border-b border-brand-border mb-5">
        {tabs.map((t) => (
          <button
            key={t.key}
            onClick={() => setTab(t.key)}
            className={`px-4 py-2.5 text-sm font-medium border-b-2 -mb-px transition-colors ${
              tab === t.key
                ? "border-teal-600 text-teal-700"
                : "border-transparent text-brand-muted hover:text-brand-text"
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {error && (
        <div className="bg-red-50 border border-red-100 text-red-600 text-sm rounded-card px-4 py-3 mb-5">
          {error}
        </div>
      )}

      <AnimatePresence mode="wait">
      <motion.div
        key={tab}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        transition={{ duration: 0.15 }}
      >
      <div className="bg-white rounded-card border border-brand-border shadow-card overflow-hidden">
        {loading ? (
          <table className="w-full text-sm">
            <tbody><SkeletonTableRows rows={4} cols={5} /></tbody>
          </table>
        ) : filtered.length === 0 ? (
          <div className="p-8 text-center text-brand-muted text-sm">
            No {tab} appointments.
            {tab === "upcoming" && (
              <button
                onClick={() => router.push("/students/book")}
                className="ml-2 text-teal-600 hover:text-teal-700 transition-colors"
              >
                Book one →
              </button>
            )}
          </div>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-brand-raised border-b border-brand-border">
                <th className="text-left px-4 py-3 text-xs font-semibold text-brand-muted uppercase tracking-wide">Date</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-brand-muted uppercase tracking-wide">Time</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-brand-muted uppercase tracking-wide">Doctor</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-brand-muted uppercase tracking-wide">Status</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-brand-muted uppercase tracking-wide">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-brand-border">
              {filtered.map((a, i) => (
                <motion.tr
                  key={a.appointment_id}
                  initial={{ opacity: 0, y: 4 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.18, delay: Math.min(i * 0.04, 0.3) }}
                  className="hover:bg-brand-raised transition-colors"
                >
                  <td className="px-4 py-3 text-brand-text">{fmtDate(a.slot_date)}</td>
                  <td className="px-4 py-3 text-brand-text font-mono text-xs">
                    {a.start_time.slice(0, 5)}
                  </td>
                  <td className="px-4 py-3 text-brand-text">Dr. {doctorName(a.doctor_name)}</td>
                  <td className="px-4 py-3">
                    <StatusBadge status={a.status} />
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => router.push(`/students/appointments/${a.appointment_id}?from=${tab}`)}
                        className="text-xs text-teal-600 hover:text-teal-700 border border-teal-200 hover:border-teal-300 px-2.5 py-1 rounded-btn transition-colors"
                      >
                        View
                      </button>
                      {a.status.toLowerCase() === "booked" && (
                        <button
                          onClick={() => setCancelId(a.appointment_id)}
                          className="text-xs text-red-500 hover:text-red-600 border border-red-200 hover:border-red-300 px-2.5 py-1 rounded-btn transition-colors"
                        >
                          Cancel
                        </button>
                      )}
                    </div>
                  </td>
                </motion.tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
      </motion.div>
      </AnimatePresence>
    </DashboardShell>
  );
}
