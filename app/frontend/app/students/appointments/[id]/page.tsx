"use client";
import { Suspense } from "react";
import { useEffect, useState } from "react";
import { useParams, useRouter, useSearchParams } from "next/navigation";
import { motion } from "framer-motion";
import { getStudentAppointments, cancelAppointment, getStoredUser } from "@/lib/api";
import { doctorName } from "@/lib/utils";
import type { StudentAppointmentSummary } from "@/lib/types";
import DashboardShell from "@/components/layout/DashboardShell";
import StatusBadge from "@/components/ui/StatusBadge";
import Modal from "@/components/ui/Modal";
import { AnimatePresence } from "framer-motion";

function fmtDate(d: string) {
  return new Date(d).toLocaleDateString("en-IN", {
    weekday: "long",
    day: "numeric",
    month: "long",
    year: "numeric",
  });
}

function fmtTime(t: string) {
  return t.slice(0, 5);
}

function AppointmentDetailPageInner() {
  const params = useParams();
  const router = useRouter();
  const searchParams = useSearchParams();
  const rawId = Array.isArray(params.id) ? params.id[0] : params.id;
  const id = rawId ? Number(rawId) : NaN;
  const fromTab = searchParams.get("from") ?? "upcoming";

  const [appointment, setAppointment] = useState<StudentAppointmentSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [confirmCancel, setConfirmCancel] = useState(false);
  const [cancelling, setCancelling] = useState(false);

  useEffect(() => {
    const user = getStoredUser();
    if (!user) {
      router.replace("/login");
      setLoading(false);
      return;
    }
    if (isNaN(id) || id <= 0) {
      setError("Invalid appointment ID");
      setLoading(false);
      return;
    }
    getStudentAppointments()
      .then((appts) => {
        const found = appts.find((a) => a.appointment_id === id) ?? null;
        if (!found) {
          setError("Appointment not found");
          return;
        }
        setAppointment(found);
      })
      .catch((e: unknown) =>
        setError(e instanceof Error ? e.message : "Failed to load appointment")
      )
      .finally(() => setLoading(false));
  }, [id, router]);

  const handleCancel = async () => {
    if (!appointment) return;
    setCancelling(true);
    try {
      await cancelAppointment(appointment.appointment_id);
      setAppointment((prev) => prev ? { ...prev, status: "cancelled" } : prev);
      setConfirmCancel(false);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Cancel failed");
    } finally {
      setCancelling(false);
    }
  };

  const backUrl = `/students/appointments?tab=${fromTab}`;
  const isBooked = appointment?.status.toLowerCase() === "booked";
  const isCompleted = appointment?.status.toLowerCase() === "completed";

  if (loading) {
    return (
      <DashboardShell role="student" title="Appointment">
        <p className="animate-pulse text-sm text-brand-muted">Loading…</p>
      </DashboardShell>
    );
  }

  if (error || !appointment) {
    return (
      <DashboardShell role="student" title="Appointment">
        <button onClick={() => router.back()} className="mb-4 text-sm text-brand-muted hover:text-brand-text flex items-center gap-1 transition-colors">
          ← Back
        </button>
        <p className="text-sm text-red-600">{error || "Appointment not found"}</p>
      </DashboardShell>
    );
  }

  return (
    <DashboardShell role="student" title="Appointment Details">
      <AnimatePresence>
        {confirmCancel && (
          <Modal
            title="Cancel Appointment"
            message="Are you sure you want to cancel this appointment? This action cannot be undone."
            confirmLabel={cancelling ? "Cancelling…" : "Cancel Appointment"}
            cancelLabel="Keep Appointment"
            danger
            onConfirm={handleCancel}
            onCancel={() => setConfirmCancel(false)}
          />
        )}
      </AnimatePresence>

      <button
        onClick={() => router.push(backUrl)}
        className="mb-5 text-sm text-brand-muted hover:text-brand-text flex items-center gap-1 transition-colors"
      >
        ← My Appointments
      </button>

      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.25, ease: "easeOut" }}
        className="space-y-4 max-w-lg"
      >
        {/* Status banner */}
        <div className="bg-white rounded-card border-l-4 border-teal-600 border-t border-r border-b border-brand-border shadow-card p-5">
          <div className="flex items-center justify-between gap-4">
            <div>
              <p className="text-xs text-brand-muted uppercase tracking-wide font-medium mb-1">
                Reference
              </p>
              <p className="font-mono text-sm text-brand-text font-medium">
                APT-{String(appointment.appointment_id).padStart(5, "0")}
              </p>
            </div>
            <StatusBadge status={appointment.status} />
          </div>
        </div>

        {/* Details card */}
        <div className="bg-white rounded-card border border-brand-border shadow-card divide-y divide-brand-border">
          <div className="px-5 py-4 grid grid-cols-2 gap-4">
            <div>
              <p className="text-xs text-brand-muted mb-1">Date</p>
              <p className="text-sm font-medium text-brand-text">{fmtDate(appointment.slot_date)}</p>
            </div>
            <div>
              <p className="text-xs text-brand-muted mb-1">Time</p>
              <p className="text-sm font-medium text-brand-text font-mono">
                {fmtTime(appointment.start_time)} – {fmtTime(appointment.end_time)}
              </p>
            </div>
          </div>
          <div className="px-5 py-4">
            <p className="text-xs text-brand-muted mb-1">Doctor</p>
            <p className="text-sm font-medium text-brand-text">
              Dr. {doctorName(appointment.doctor_name)}
            </p>
            <p className="text-xs text-brand-muted mt-0.5">College Infirmary</p>
          </div>
          <div className="px-5 py-4">
            <p className="text-xs text-brand-muted mb-1">Reason for visit</p>
            <p className="text-sm text-brand-text">
              {appointment.reason ?? <span className="text-brand-muted italic">Not provided</span>}
            </p>
          </div>
        </div>

        {/* Actions */}
        <div className="flex gap-3">
          {isBooked && (
            <button
              onClick={() => setConfirmCancel(true)}
              className="rounded-btn border border-red-200 px-4 py-2 text-sm text-red-500 hover:bg-red-50 hover:border-red-300 transition-colors"
            >
              Cancel Appointment
            </button>
          )}
          {isCompleted && (
            <button
              onClick={() => router.push(`/students/reports/${appointment.appointment_id}`)}
              className="rounded-btn bg-teal-600 px-4 py-2 text-sm font-medium text-white hover:bg-teal-700 transition-colors"
            >
              View Report
            </button>
          )}
        </div>
      </motion.div>
    </DashboardShell>
  );
}

export default function AppointmentDetailPage() {
  return (
    <Suspense
      fallback={
        <DashboardShell role="student" title="Appointment">
          <p className="animate-pulse text-sm text-brand-muted">Loading…</p>
        </DashboardShell>
      }
    >
      <AppointmentDetailPageInner />
    </Suspense>
  );
}
