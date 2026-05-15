"use client";
import { Suspense } from "react";
import { useEffect, useState } from "react";
import { useParams, useRouter, useSearchParams } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { getPatientHistory, getStoredUser } from "@/lib/api";
import { doctorName } from "@/lib/utils";
import type { PatientHistoryItem } from "@/lib/types";
import DashboardShell from "@/components/layout/DashboardShell";
import StatusBadge from "@/components/ui/StatusBadge";

function fmtDate(d: string) {
  return new Date(d).toLocaleDateString("en-IN", { day: "numeric", month: "short", year: "numeric" });
}

function initials(name: string): string {
  return name
    .split(" ")
    .filter(Boolean)
    .slice(0, 2)
    .map((w) => w[0].toUpperCase())
    .join("");
}

function PatientHistoryPageInner() {
  const params = useParams();
  const router = useRouter();
  const searchParams = useSearchParams();
  const studentId = Number(params.student_id);

  const patientName = searchParams.get("name") ?? "";
  const patientRoll = searchParams.get("roll") ?? "";

  const [history, setHistory] = useState<PatientHistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [expanded, setExpanded] = useState<number | null>(null);

  useEffect(() => {
    const user = getStoredUser();
    if (!user) {
      router.replace("/login");
      setLoading(false);
      return;
    }
    getPatientHistory(studentId)
      .then(setHistory)
      .catch((e: unknown) => setError(e instanceof Error ? e.message : "Failed to load"))
      .finally(() => setLoading(false));
  }, [studentId, router]);

  function toggle(id: number) {
    setExpanded((prev) => (prev === id ? null : id));
  }

  return (
    <DashboardShell role="doctor" title="Patient History">
      <div className="mb-4">
        <button
          onClick={() => router.back()}
          className="text-sm text-brand-muted hover:text-brand-text flex items-center gap-1 transition-colors"
        >
          ← Back
        </button>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-100 text-red-600 text-sm rounded-card px-4 py-3 mb-5">{error}</div>
      )}

      {/* Patient profile card */}
      <div className="bg-white rounded-card border border-brand-border shadow-card p-5 mb-5 flex items-center gap-4">
        <div className="w-14 h-14 rounded-full bg-teal-600 flex items-center justify-center text-white text-lg font-semibold flex-shrink-0">
          {patientName ? initials(patientName) : "?"}
        </div>
        <div className="flex-1">
          <h2 className="text-base font-semibold text-brand-text">
            {patientName || `Patient #${studentId}`}
          </h2>
          {patientRoll && (
            <p className="text-xs font-mono text-brand-muted mt-0.5">{patientRoll}</p>
          )}
          <p className="text-xs font-mono text-brand-muted mt-0.5">Student ID: {studentId}</p>
          {!loading && (
            <p className="text-sm text-brand-muted mt-1">
              {history.length} visit{history.length !== 1 ? "s" : ""} recorded
            </p>
          )}
        </div>
      </div>

      {loading && <p className="text-brand-muted text-sm animate-pulse">Loading…</p>}

      {!loading && history.length === 0 && (
        <p className="text-brand-muted text-sm">No visit history found for this patient.</p>
      )}

      <div className="space-y-3">
        {history.map((item, i) => (
          <div key={item.appointment_id} className="relative flex gap-4">
            {/* Timeline line */}
            <div className="flex flex-col items-center">
              <div className="w-3 h-3 rounded-full bg-teal-600 mt-5 flex-shrink-0 z-10" />
              {i < history.length - 1 && (
                <div className="w-px flex-1 bg-brand-border mt-1" />
              )}
            </div>

            {/* Card */}
            <div className="flex-1 bg-white rounded-card border border-brand-border shadow-card mb-2 overflow-hidden">
              <button
                onClick={() => toggle(item.appointment_id)}
                className="w-full text-left px-4 py-3 flex items-center justify-between hover:bg-brand-raised transition-colors"
              >
                <div className="flex items-center gap-4 flex-wrap">
                  <span className="text-sm font-medium text-brand-text">{fmtDate(item.slot_date)}</span>
                  <span className="text-sm text-brand-muted">Dr. {doctorName(item.doctor_name)}</span>
                  <StatusBadge status={item.status} />
                  {item.certificate_id && (
                    <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs bg-purple-50 text-purple-700 ring-1 ring-purple-200">
                      Certificate
                    </span>
                  )}
                </div>
                <svg
                  className={`w-4 h-4 text-brand-muted transition-transform flex-shrink-0 ml-2 ${expanded === item.appointment_id ? "rotate-180" : ""}`}
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>

              <AnimatePresence initial={false}>
              {expanded === item.appointment_id && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: "auto", opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  transition={{ duration: 0.22, ease: "easeInOut" }}
                  className="overflow-hidden"
                >
                <div className="px-4 pb-4 border-t border-brand-border text-sm space-y-2 pt-3">
                  <div className="flex gap-2">
                    <span className="text-brand-muted w-24 flex-shrink-0">Time</span>
                    <span className="text-brand-text font-mono text-xs">
                      {item.start_time.slice(0, 5)} – {item.end_time.slice(0, 5)}
                    </span>
                  </div>
                  {item.reason && (
                    <div className="flex gap-2">
                      <span className="text-brand-muted w-24 flex-shrink-0">Reason</span>
                      <span className="text-brand-text">{item.reason}</span>
                    </div>
                  )}
                  {item.diagnosis && (
                    <div className="flex gap-2">
                      <span className="text-brand-muted w-24 flex-shrink-0">Diagnosis</span>
                      <span className="text-brand-text">{item.diagnosis}</span>
                    </div>
                  )}
                  {item.remarks && (
                    <div className="flex gap-2">
                      <span className="text-brand-muted w-24 flex-shrink-0">Remarks</span>
                      <span className="text-brand-text">{item.remarks}</span>
                    </div>
                  )}
                  {item.certificate_type && (
                    <div className="flex gap-2">
                      <span className="text-brand-muted w-24 flex-shrink-0">Certificate</span>
                      <span className="text-brand-text">{item.certificate_type}</span>
                    </div>
                  )}
                  <div className="pt-1">
                    <button
                      onClick={() => router.push(`/doctors/appointments/${item.appointment_id}`)}
                      className="text-xs text-teal-600 hover:text-teal-700 font-medium transition-colors"
                    >
                      View Appointment →
                    </button>
                  </div>
                </div>
                </motion.div>
              )}
              </AnimatePresence>
            </div>
          </div>
        ))}
      </div>
    </DashboardShell>
  );
}

export default function PatientHistoryPage() {
  return (
    <Suspense fallback={
      <DashboardShell role="doctor" title="Patient History">
        <p className="animate-pulse text-sm text-brand-muted">Loading…</p>
      </DashboardShell>
    }>
      <PatientHistoryPageInner />
    </Suspense>
  );
}
