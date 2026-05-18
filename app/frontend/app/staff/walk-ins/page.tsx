"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import {
  bookWalkInAppointment,
  getAllSlotsForDoctor,
  getDoctorsForDate,
  getStaffWalkIns,
  getSlots,
  getStoredUser,
  searchStaffPatients,
} from "@/lib/api";
import { doctorName } from "@/lib/utils";
import DashboardShell from "@/components/layout/DashboardShell";
import type {
  AppointmentSlot,
  AppointmentSlotWithStatus,
  AdminAppointmentSummary,
  DoctorAvailabilityStatus,
  StaffPatientSearchResult,
} from "@/lib/types";

function getLocalDateKey(date = new Date()) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

function isFutureSlot(slot: AppointmentSlot, selectedDate: string) {
  if (selectedDate !== getLocalDateKey()) return true;
  const [year, month, day] = slot.slot_date.split("-").map(Number);
  const [hour, minute] = slot.start_time.split(":").map(Number);
  const slotStart = new Date(year, month - 1, day, hour, minute);
  return slotStart > new Date();
}

function fmtDate(value: string) {
  return new Date(value).toLocaleDateString("en-IN", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });
}

export default function StaffWalkInsPage() {
  const router = useRouter();
  const [query, setQuery] = useState("");
  const [patients, setPatients] = useState<StaffPatientSearchResult[]>([]);
  const [selectedPatient, setSelectedPatient] = useState<StaffPatientSearchResult | null>(null);
  const [selectedDate, setSelectedDate] = useState(getLocalDateKey());
  const [doctors, setDoctors] = useState<DoctorAvailabilityStatus[]>([]);
  const [slots, setSlots] = useState<AppointmentSlot[]>([]);
  const [detailedSlots, setDetailedSlots] = useState<AppointmentSlotWithStatus[]>([]);
  const [selectedDoctorId, setSelectedDoctorId] = useState<number | null>(null);
  const [selectedSlot, setSelectedSlot] = useState<AppointmentSlotWithStatus | null>(null);
  const [walkIns, setWalkIns] = useState<AdminAppointmentSummary[]>([]);
  const [walkInStatus, setWalkInStatus] = useState("");
  const [walkInFromDate, setWalkInFromDate] = useState("");
  const [walkInToDate, setWalkInToDate] = useState("");
  const [reason, setReason] = useState("Walk-in consultation");
  const [loadingPatients, setLoadingPatients] = useState(false);
  const [loadingSlots, setLoadingSlots] = useState(false);
  const [loadingWalkIns, setLoadingWalkIns] = useState(false);
  const [booking, setBooking] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const loadWalkIns = useCallback(async () => {
    setLoadingWalkIns(true);
    try {
      const rows = await getStaffWalkIns({ status: walkInStatus || undefined, from_date: walkInFromDate || undefined, to_date: walkInToDate || undefined, limit: 50 });
      setWalkIns(rows);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Could not load walk-in bookings");
    } finally {
      setLoadingWalkIns(false);
    }
  }, [walkInStatus, walkInFromDate, walkInToDate]);

  useEffect(() => {
    const user = getStoredUser();
    if (!user) {
      router.replace("/login");
      return;
    }
    if (user.role_name !== "staff") {
      router.replace("/login");
    }
  }, [router]);

  useEffect(() => {
    setLoadingSlots(true);
    setSelectedDoctorId(null);
    setSelectedSlot(null);
    setDetailedSlots([]);
    Promise.all([
      getDoctorsForDate(selectedDate).then(setDoctors).catch(() => setDoctors([])),
      getSlots(selectedDate).then(setSlots).catch(() => setSlots([])),
    ]).finally(() => setLoadingSlots(false));
  }, [selectedDate]);

  useEffect(() => {
    loadWalkIns();
  }, [loadWalkIns]);

  async function handleSearch() {
    if (query.trim().length < 2) {
      setError("Enter at least 2 characters to search.");
      return;
    }
    setLoadingPatients(true);
    setError("");
    setSuccess("");
    try {
      const results = await searchStaffPatients(query.trim());
      setPatients(results);
      if (results.length === 0) setError("No existing patient matched that search.");
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Patient search failed");
    } finally {
      setLoadingPatients(false);
    }
  }

  async function chooseDoctor(doctorId: number) {
    setSelectedDoctorId(doctorId);
    setSelectedSlot(null);
    setLoadingSlots(true);
    setError("");
    try {
      const rows = await getAllSlotsForDoctor(doctorId, selectedDate);
      setDetailedSlots(rows.filter((slot) => isFutureSlot(slot, selectedDate)));
    } catch (e: unknown) {
      setDetailedSlots([]);
      setError(e instanceof Error ? e.message : "Could not load slots");
    } finally {
      setLoadingSlots(false);
    }
  }

  async function handleBook() {
    if (!selectedPatient || !selectedSlot) return;
    setBooking(true);
    setError("");
    setSuccess("");
    try {
      const booked = await bookWalkInAppointment(selectedPatient.student_id, selectedSlot.slot_id, reason);
      setSuccess(`Walk-in booked as appointment #${booked.appointment_id ?? selectedSlot.slot_id}.`);
      setSelectedSlot(null);
      setDetailedSlots((current) =>
        current.map((slot) =>
          slot.slot_id === booked.slot_id
            ? { ...slot, is_available: false, appointment_status: "booked" }
            : slot
        )
      );
      setSlots((current) => current.filter((slot) => slot.slot_id !== booked.slot_id));
      await loadWalkIns();
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Walk-in booking failed");
      if (selectedDoctorId !== null) {
        getAllSlotsForDoctor(selectedDoctorId, selectedDate)
          .then((rows) => setDetailedSlots(rows.filter((slot) => isFutureSlot(slot, selectedDate))))
          .catch(() => {});
      }
    } finally {
      setBooking(false);
    }
  }

  const availableDoctors = doctors.map((doc) => {
    const futureSlots = slots.filter(
      (slot) =>
        slot.doctor_id === doc.doctor_id &&
        slot.slot_date === selectedDate &&
        isFutureSlot(slot, selectedDate)
    );
    return {
      ...doc,
      visible_slots: futureSlots.length,
      can_select: doc.is_available && futureSlots.length > 0,
    };
  });

  return (
    <DashboardShell role="staff" title="Walk-ins">
      <div className="space-y-5">
        <div className="rounded-card border border-brand-border bg-white p-5 shadow-card">
          <div className="mb-4 flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
            <div>
              <h2 className="text-sm font-semibold text-brand-text">Find Patient</h2>
              <p className="mt-1 text-sm text-brand-muted">Search existing patients by name, roll number, or email.</p>
            </div>
            <div className="flex gap-2">
              <input
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleSearch()}
                placeholder="Name, roll number, email"
                className="w-full min-w-0 rounded-btn border border-brand-border px-3 py-2 text-sm text-brand-text outline-none transition focus:border-teal-300 focus:ring-2 focus:ring-teal-100 sm:w-72"
              />
              <button
                onClick={handleSearch}
                disabled={loadingPatients}
                className="rounded-btn bg-teal-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-teal-700 disabled:opacity-60"
              >
                {loadingPatients ? "Searching" : "Search"}
              </button>
            </div>
          </div>

          {patients.length > 0 && (
            <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
              {patients.map((patient) => {
                const active = selectedPatient?.student_id === patient.student_id;
                return (
                  <button
                    key={patient.student_id}
                    onClick={() => {
                      setSelectedPatient(patient);
                      setSuccess("");
                      setError("");
                    }}
                    className={`rounded-card border p-3 text-left transition-colors ${
                      active
                        ? "border-teal-300 bg-teal-50"
                        : "border-brand-border hover:border-teal-200 hover:bg-brand-raised"
                    }`}
                  >
                    <p className="text-sm font-medium text-brand-text">{patient.student_name}</p>
                    <p className="mt-1 text-xs text-brand-muted">{patient.roll_number} · {patient.department}</p>
                    <p className="mt-1 text-xs text-brand-muted">{patient.email}</p>
                    <span className="mt-2 inline-flex rounded-full bg-white px-2 py-0.5 text-xs font-medium text-teal-700 ring-1 ring-teal-100">
                      {patient.role_name}
                    </span>
                  </button>
                );
              })}
            </div>
          )}
        </div>

        <div className="rounded-card border border-brand-border bg-white p-5 shadow-card">
          <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h2 className="text-sm font-semibold text-brand-text">Choose Slot</h2>
              <p className="mt-1 text-sm text-brand-muted">Select a doctor and an available time for the walk-in.</p>
            </div>
            <input
              type="date"
              value={selectedDate}
              min={getLocalDateKey()}
              onChange={(e) => setSelectedDate(e.target.value)}
              className="rounded-btn border border-brand-border px-3 py-2 text-sm text-brand-text outline-none transition focus:border-teal-300 focus:ring-2 focus:ring-teal-100"
            />
          </div>

          {selectedPatient && (
            <div className="mb-4 rounded-btn border border-teal-100 bg-teal-50 px-3 py-2 text-sm text-teal-800">
              Booking for <span className="font-medium">{selectedPatient.student_name}</span> on {fmtDate(selectedDate)}
            </div>
          )}

          {loadingSlots && <p className="text-sm text-brand-muted animate-pulse">Loading doctors and slots...</p>}

          {!loadingSlots && (
            <div className="grid gap-3 md:grid-cols-[minmax(0,1fr)_minmax(0,1.25fr)]">
              <div className="space-y-2">
                {availableDoctors.map((doc) => {
                  const active = selectedDoctorId === doc.doctor_id;
                  return (
                    <button
                      key={doc.doctor_id}
                      onClick={() => doc.can_select && chooseDoctor(doc.doctor_id)}
                      disabled={!doc.can_select}
                      className={`w-full rounded-card border p-3 text-left transition-colors disabled:cursor-not-allowed disabled:opacity-60 ${
                        active
                          ? "border-teal-300 bg-teal-50"
                          : "border-brand-border hover:border-teal-200 hover:bg-brand-raised"
                      }`}
                    >
                      <div className="flex items-start justify-between gap-3">
                        <div>
                          <p className="text-sm font-medium text-brand-text">Dr. {doctorName(doc.doctor_name)}</p>
                          {doc.specialization && <p className="mt-1 text-xs text-brand-muted">{doc.specialization}</p>}
                        </div>
                        <span className={`rounded-full px-2 py-0.5 text-xs font-medium ring-1 ${
                          doc.can_select
                            ? "bg-teal-50 text-teal-700 ring-teal-100"
                            : "bg-amber-50 text-amber-700 ring-amber-100"
                        }`}>
                          {doc.can_select ? `${doc.visible_slots} slots` : "Unavailable"}
                        </span>
                      </div>
                      {doc.unavailability_note && (
                        <p className="mt-2 text-xs text-amber-700">{doc.unavailability_note}</p>
                      )}
                    </button>
                  );
                })}

                {availableDoctors.length === 0 && (
                  <p className="rounded-card border border-brand-border bg-brand-raised p-4 text-sm text-brand-muted">
                    No doctors found for this date.
                  </p>
                )}
              </div>

              <div className="rounded-card border border-brand-border bg-brand-bg p-4">
                <h3 className="mb-3 text-sm font-semibold text-brand-text">Available Times</h3>
                {selectedDoctorId === null && (
                  <p className="text-sm text-brand-muted">Select a doctor to view time slots.</p>
                )}
                {selectedDoctorId !== null && detailedSlots.length === 0 && !loadingSlots && (
                  <p className="text-sm text-brand-muted">No remaining slots for this doctor.</p>
                )}
                <div className="flex flex-wrap gap-2">
                  {detailedSlots.map((slot, index) => {
                    const available = slot.is_available;
                    const active = selectedSlot?.slot_id === slot.slot_id;
                    return (
                      <motion.button
                        key={slot.slot_id}
                        initial={{ opacity: 0, scale: 0.94 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ duration: 0.15, delay: Math.min(index * 0.03, 0.2) }}
                        disabled={!available}
                        onClick={() => setSelectedSlot(slot)}
                        className={`rounded-btn border px-3 py-2 text-sm font-medium transition-colors disabled:cursor-not-allowed ${
                          active
                            ? "border-teal-600 bg-teal-600 text-white"
                            : available
                              ? "border-teal-200 bg-white text-teal-700 hover:bg-teal-50"
                              : "border-slate-200 bg-slate-50 text-slate-400 line-through"
                        }`}
                      >
                        {slot.start_time.slice(0, 5)}-{slot.end_time.slice(0, 5)}
                      </motion.button>
                    );
                  })}
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="rounded-card border border-brand-border bg-white p-5 shadow-card">
          <h2 className="text-sm font-semibold text-brand-text">Confirm Walk-in</h2>
          <div className="mt-4 grid gap-4 md:grid-cols-[minmax(0,1fr)_220px]">
            <textarea
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              rows={3}
              maxLength={500}
              placeholder="Walk-in consultation"
              className="w-full resize-none rounded-btn border border-brand-border px-3 py-2 text-sm text-brand-text outline-none transition focus:border-teal-300 focus:ring-2 focus:ring-teal-100"
            />
            <button
              onClick={handleBook}
              disabled={!selectedPatient || !selectedSlot || booking}
              className="h-11 self-end rounded-btn bg-teal-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-teal-700 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {booking ? "Booking..." : "Book Walk-in"}
            </button>
          </div>
          {selectedSlot && (
            <p className="mt-3 text-xs text-brand-muted">
              Selected {selectedSlot.start_time.slice(0, 5)}-{selectedSlot.end_time.slice(0, 5)} on {fmtDate(selectedSlot.slot_date)}.
            </p>
          )}
          {error && <p className="mt-3 rounded-btn border border-red-100 bg-red-50 px-3 py-2 text-sm text-red-600">{error}</p>}
          {success && <p className="mt-3 rounded-btn border border-emerald-100 bg-emerald-50 px-3 py-2 text-sm text-emerald-700">{success}</p>}
        </div>

        <div className="rounded-card border border-brand-border bg-white shadow-card">
          <div className="flex flex-col gap-3 border-b border-brand-border px-5 py-4 lg:flex-row lg:items-end lg:justify-between">
            <div>
              <h2 className="text-sm font-semibold text-brand-text">Walk-in Bookings</h2>
              <p className="mt-1 text-sm text-brand-muted">Recent staff-created walk-in appointments.</p>
            </div>
            <div className="grid gap-2 sm:grid-cols-4">
              <select
                value={walkInStatus}
                onChange={(e) => setWalkInStatus(e.target.value)}
                className="rounded-btn border border-brand-border px-3 py-2 text-sm text-brand-text outline-none transition focus:border-teal-300 focus:ring-2 focus:ring-teal-100"
              >
                <option value="">All statuses</option>
                <option value="booked">Booked</option>
                <option value="completed">Completed</option>
                <option value="cancelled">Cancelled</option>
              </select>
              <input
                type="date"
                value={walkInFromDate}
                onChange={(e) => setWalkInFromDate(e.target.value)}
                className="rounded-btn border border-brand-border px-3 py-2 text-sm text-brand-text outline-none transition focus:border-teal-300 focus:ring-2 focus:ring-teal-100"
              />
              <input
                type="date"
                value={walkInToDate}
                onChange={(e) => setWalkInToDate(e.target.value)}
                className="rounded-btn border border-brand-border px-3 py-2 text-sm text-brand-text outline-none transition focus:border-teal-300 focus:ring-2 focus:ring-teal-100"
              />
              <button
                onClick={loadWalkIns}
                disabled={loadingWalkIns}
                className="rounded-btn border border-teal-200 px-3 py-2 text-sm font-medium text-teal-700 transition-colors hover:bg-teal-50 disabled:opacity-60"
              >
                {loadingWalkIns ? "Loading" : "Refresh"}
              </button>
            </div>
          </div>

          {loadingWalkIns && (
            <p className="px-5 py-4 text-sm text-brand-muted animate-pulse">Loading walk-in bookings...</p>
          )}

          {!loadingWalkIns && walkIns.length === 0 && (
            <p className="px-5 py-8 text-center text-sm text-brand-muted">No walk-in bookings found.</p>
          )}

          {!loadingWalkIns && walkIns.length > 0 && (
            <>
              <div className="hidden overflow-x-auto md:block">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-brand-border bg-brand-bg">
                      <th className="px-5 py-3 text-left text-xs font-medium text-brand-muted">Patient</th>
                      <th className="px-5 py-3 text-left text-xs font-medium text-brand-muted">Doctor</th>
                      <th className="px-5 py-3 text-left text-xs font-medium text-brand-muted">Date</th>
                      <th className="px-5 py-3 text-left text-xs font-medium text-brand-muted">Time</th>
                      <th className="px-5 py-3 text-left text-xs font-medium text-brand-muted">Status</th>
                      <th className="px-5 py-3 text-left text-xs font-medium text-brand-muted">Reason</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-brand-border">
                    {walkIns.map((item) => (
                      <tr key={item.appointment_id} className="hover:bg-brand-raised">
                        <td className="px-5 py-3">
                          <p className="font-medium text-brand-text">{item.student_name}</p>
                          <p className="text-xs text-brand-muted">{item.roll_number}</p>
                        </td>
                        <td className="px-5 py-3 text-brand-text">Dr. {doctorName(item.doctor_name)}</td>
                        <td className="px-5 py-3 text-brand-muted">{fmtDate(item.slot_date)}</td>
                        <td className="px-5 py-3 text-brand-muted">{item.start_time.slice(0, 5)}-{item.end_time.slice(0, 5)}</td>
                        <td className="px-5 py-3">
                          <span className="rounded-full bg-teal-50 px-2 py-0.5 text-xs font-medium text-teal-700 ring-1 ring-teal-100">
                            {item.status}
                          </span>
                        </td>
                        <td className="max-w-xs px-5 py-3 text-brand-muted">{item.reason ?? "Walk-in consultation"}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              <div className="divide-y divide-brand-border md:hidden">
                {walkIns.map((item) => (
                  <div key={item.appointment_id} className="p-4">
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <p className="text-sm font-medium text-brand-text">{item.student_name}</p>
                        <p className="mt-0.5 text-xs text-brand-muted">{item.roll_number}</p>
                      </div>
                      <span className="rounded-full bg-teal-50 px-2 py-0.5 text-xs font-medium text-teal-700 ring-1 ring-teal-100">
                        {item.status}
                      </span>
                    </div>
                    <p className="mt-2 text-xs text-brand-muted">
                      Dr. {doctorName(item.doctor_name)} · {fmtDate(item.slot_date)} · {item.start_time.slice(0, 5)}-{item.end_time.slice(0, 5)}
                    </p>
                    <p className="mt-2 text-sm text-brand-text">{item.reason ?? "Walk-in consultation"}</p>
                  </div>
                ))}
              </div>
            </>
          )}
        </div>
      </div>
    </DashboardShell>
  );
}
