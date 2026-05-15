"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { getSlots, bookAppointment, getStoredUser } from "@/lib/api";
import { doctorName } from "@/lib/utils";
import type { AppointmentSlot } from "@/lib/types";
import DashboardShell from "@/components/layout/DashboardShell";

type Step = 1 | 2 | 3;

function todayISO() {
  return new Date().toISOString().split("T")[0];
}

function fmtDate(d: string) {
  return new Date(d).toLocaleDateString("en-IN", { day: "numeric", month: "short", year: "numeric" });
}

export default function BookAppointmentPage() {
  const router = useRouter();
  const [step, setStep] = useState<Step>(1);
  const [slots, setSlots] = useState<AppointmentSlot[]>([]);
  const [fromDate, setFromDate] = useState(todayISO());
  const [selectedSlot, setSelectedSlot] = useState<AppointmentSlot | null>(null);
  const [reason, setReason] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    const user = getStoredUser();
    if (!user) { router.replace("/login"); return; }
  }, [router]);

  useEffect(() => {
    setLoading(true);
    getSlots(fromDate)
      .then(setSlots)
      .catch(() => setSlots([]))
      .finally(() => setLoading(false));
  }, [fromDate]);

  // Group slots by doctor — only show slots for the selected date
  const byDoctor = slots.filter((s) => s.slot_date === fromDate).reduce<Record<string, AppointmentSlot[]>>((acc, s) => {
    const key = `${s.doctor_id}:${s.doctor_name}`;
    if (!acc[key]) acc[key] = [];
    acc[key].push(s);
    return acc;
  }, {});

  const handleBook = async () => {
    if (!selectedSlot) return;
    setLoading(true);
    setError("");
    try {
      await bookAppointment(selectedSlot.slot_id, reason || undefined);
      setSuccess(true);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Booking failed");
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <DashboardShell role="student" title="Book Appointment">
        <div className="bg-white rounded-card border border-brand-border shadow-card p-8 text-center max-w-md mx-auto">
          <div className="w-14 h-14 bg-emerald-50 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-7 h-7 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h2 className="text-lg font-semibold text-brand-text mb-2">Appointment Booked!</h2>
          <p className="text-brand-muted text-sm mb-6">
            Your appointment with Dr. {doctorName(selectedSlot?.doctor_name ?? "")} on{" "}
            {fmtDate(selectedSlot?.slot_date ?? "")} at {selectedSlot?.start_time.slice(0, 5)} has been confirmed.
          </p>
          <button
            onClick={() => router.push("/students/appointments")}
            className="bg-teal-600 hover:bg-teal-700 text-white px-5 py-2.5 rounded-btn text-sm font-medium transition-colors"
          >
            View My Appointments
          </button>
        </div>
      </DashboardShell>
    );
  }

  const steps = [
    { n: 1 as Step, label: "Select Doctor" },
    { n: 2 as Step, label: "Pick Date" },
    { n: 3 as Step, label: "Confirm" },
  ];

  return (
    <DashboardShell role="student" title="Book Appointment">
      {/* Step indicator */}
      <div className="flex items-center gap-0 mb-8">
        {steps.map((s, i) => (
          <div key={s.n} className="flex items-center">
            <div className="flex items-center gap-2">
              <div className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-semibold border-2 transition-colors ${
                step === s.n
                  ? "bg-teal-600 border-teal-600 text-white"
                  : step > s.n
                  ? "bg-teal-50 border-teal-600 text-teal-600"
                  : "bg-white border-brand-border text-brand-muted"
              }`}>
                {step > s.n ? (
                  <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                  </svg>
                ) : s.n}
              </div>
              <span className={`text-sm hidden sm:block ${step === s.n ? "text-brand-text font-medium" : "text-brand-muted"}`}>
                {s.label}
              </span>
            </div>
            {i < steps.length - 1 && (
              <div className={`w-12 h-px mx-3 ${step > s.n ? "bg-teal-600" : "bg-brand-border"}`} />
            )}
          </div>
        ))}
      </div>

      <div className="bg-white rounded-card border border-brand-border shadow-card p-6 overflow-hidden">
        <AnimatePresence mode="wait">
        <motion.div
          key={step}
          initial={{ opacity: 0, x: 16 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -16 }}
          transition={{ duration: 0.2, ease: "easeOut" }}
        >
        {/* Step 1 — Select doctor */}
        {step === 1 && (
          <div>
            <div className="flex items-center justify-between mb-5">
              <h2 className="text-base font-semibold text-brand-text">Select a Doctor</h2>
              <div className="flex items-center gap-2">
                <label className="text-xs text-brand-muted">Date</label>
                <input
                  type="date"
                  value={fromDate}
                  min={todayISO()}
                  onChange={(e) => setFromDate(e.target.value)}
                  className="text-xs border border-brand-border rounded px-2 py-1"
                />
              </div>
            </div>

            {loading && <p className="text-brand-muted text-sm animate-pulse">Loading slots…</p>}

            {!loading && Object.keys(byDoctor).length === 0 && (
              <p className="text-brand-muted text-sm">No available slots from this date. Try another date.</p>
            )}

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {Object.entries(byDoctor).map(([key, doctorSlots]) => {
                const [, name] = key.split(":");
                return (
                  <div key={key} className="border border-brand-border rounded-card p-4 hover:border-teal-300 transition-colors">
                    <div className="w-10 h-10 rounded-full bg-teal-600 flex items-center justify-center text-white text-sm font-semibold mb-3">
                      {doctorName(name).split(" ").slice(0, 2).map((w) => w[0]).join("")}
                    </div>
                    <p className="text-sm font-semibold text-brand-text">Dr. {doctorName(name)}</p>
                    <p className="text-xs text-brand-muted mt-0.5 mb-3">
                      {doctorSlots.length} slot{doctorSlots.length !== 1 ? "s" : ""} available
                    </p>
                    <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs bg-teal-50 text-teal-700 ring-1 ring-teal-200 mb-3">
                      Available
                    </span>
                    <button
                      onClick={() => {
                        setSelectedSlot(doctorSlots[0]);
                        setStep(2);
                      }}
                      className="w-full border border-teal-600 text-teal-600 hover:bg-teal-50 text-xs font-medium py-1.5 rounded-btn transition-colors"
                    >
                      Select
                    </button>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Step 2 — Pick slot */}
        {step === 2 && selectedSlot && (
          <div>
            <button
              onClick={() => setStep(1)}
              className="text-sm text-brand-muted hover:text-brand-text mb-4 flex items-center gap-1 transition-colors"
            >
              ← Back
            </button>
            <h2 className="text-base font-semibold text-brand-text mb-1">
              Dr. {doctorName(selectedSlot.doctor_name)}
            </h2>
            <p className="text-sm text-brand-muted mb-5">Choose an available time slot</p>

            <div className="flex flex-wrap gap-2">
              {byDoctor[`${selectedSlot.doctor_id}:${selectedSlot.doctor_name}`]?.map((s) => (
                <button
                  key={s.slot_id}
                  onClick={() => { setSelectedSlot(s); setStep(3); }}
                  className="px-3 py-2 border border-teal-600 text-teal-700 bg-teal-50 hover:bg-teal-100 rounded-btn text-sm font-medium transition-colors"
                >
                  {fmtDate(s.slot_date)} · {s.start_time.slice(0, 5)}–{s.end_time.slice(0, 5)}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Step 3 — Confirm */}
        {step === 3 && selectedSlot && (
          <div>
            <button
              onClick={() => setStep(2)}
              className="text-sm text-brand-muted hover:text-brand-text mb-4 flex items-center gap-1 transition-colors"
            >
              ← Back
            </button>
            <h2 className="text-base font-semibold text-brand-text mb-5">Confirm Appointment</h2>

            <div className="bg-brand-raised rounded-card p-4 border border-brand-border mb-5 space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-brand-muted">Doctor</span>
                <span className="text-brand-text font-medium">Dr. {doctorName(selectedSlot.doctor_name)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-brand-muted">Date</span>
                <span className="text-brand-text font-medium">{fmtDate(selectedSlot.slot_date)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-brand-muted">Time</span>
                <span className="text-brand-text font-medium">
                  {selectedSlot.start_time.slice(0, 5)} – {selectedSlot.end_time.slice(0, 5)}
                </span>
              </div>
            </div>

            <div className="mb-5">
              <label className="block text-sm font-medium text-brand-text mb-1.5">
                Reason for visit <span className="text-brand-muted font-normal">(optional)</span>
              </label>
              <textarea
                value={reason}
                onChange={(e) => setReason(e.target.value)}
                rows={3}
                maxLength={500}
                placeholder="Describe your symptoms or reason…"
                className="w-full border border-brand-border rounded-btn px-3 py-2 text-sm text-brand-text placeholder:text-brand-muted focus:ring-2 focus:ring-teal-600 focus:ring-offset-1 focus:outline-none resize-none transition"
              />
            </div>

            {error && (
              <p className="text-sm text-red-500 bg-red-50 border border-red-100 rounded-btn px-3 py-2 mb-4">
                {error}
              </p>
            )}

            <button
              onClick={handleBook}
              disabled={loading}
              className="w-full bg-teal-600 hover:bg-teal-700 disabled:opacity-60 text-white font-medium py-2.5 rounded-btn text-sm transition-colors"
            >
              {loading ? "Booking…" : "Confirm Booking"}
            </button>
          </div>
        )}
        </motion.div>
        </AnimatePresence>
      </div>
    </DashboardShell>
  );
}
