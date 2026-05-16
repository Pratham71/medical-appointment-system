"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  deleteDoctorAvailabilityOverride,
  getDoctorAvailability,
  getStoredUser,
  updateDoctorAvailabilityOverride,
  updateDoctorWeeklyAvailability,
} from "@/lib/api";
import type {
  DoctorAvailabilityOverride,
  DoctorAvailabilitySettings,
  DoctorWeeklyAvailability,
} from "@/lib/types";
import DashboardShell from "@/components/layout/DashboardShell";

function getLocalDateKey(date = new Date()) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

function timeValue(value: string | null) {
  return value ? value.slice(0, 5) : "";
}

function updateWeeklyRows(
  settings: DoctorAvailabilitySettings,
  saved: DoctorWeeklyAvailability
) {
  return {
    ...settings,
    weekly_availability: settings.weekly_availability.map((rule) =>
      rule.weekday === saved.weekday ? saved : rule
    ),
  };
}

function updateOverrideRows(
  settings: DoctorAvailabilitySettings,
  saved: DoctorAvailabilityOverride
) {
  const existing = settings.date_overrides.some(
    (override) => override.override_date === saved.override_date
  );
  const date_overrides = existing
    ? settings.date_overrides.map((override) =>
        override.override_date === saved.override_date ? saved : override
      )
    : [...settings.date_overrides, saved].sort((a, b) =>
        a.override_date.localeCompare(b.override_date)
      );
  return { ...settings, date_overrides };
}

export default function DoctorAvailabilityPage() {
  const router = useRouter();
  const [settings, setSettings] = useState<DoctorAvailabilitySettings | null>(null);
  const [loading, setLoading] = useState(true);
  const [savingKey, setSavingKey] = useState("");
  const [error, setError] = useState("");
  const [overrideDate, setOverrideDate] = useState(getLocalDateKey());
  const [overrideAvailable, setOverrideAvailable] = useState(false);
  const [overrideStart, setOverrideStart] = useState("");
  const [overrideEnd, setOverrideEnd] = useState("");
  const [overrideNote, setOverrideNote] = useState("");

  useEffect(() => {
    const user = getStoredUser();
    if (!user) { router.replace("/login"); setLoading(false); return; }
    if (user.role_name === "student") { router.replace("/students"); setLoading(false); return; }
    if (user.role_name === "admin") { router.replace("/admin"); setLoading(false); return; }
    if (user.role_name === "staff") { router.replace("/staff"); setLoading(false); return; }
    if (user.role_name !== "doctor") { router.replace("/login"); setLoading(false); return; }

    getDoctorAvailability()
      .then(setSettings)
      .catch((e: unknown) => setError(e instanceof Error ? e.message : "Failed to load"))
      .finally(() => setLoading(false));
  }, [router]);

  function patchWeekly(weekday: number, patch: Partial<DoctorWeeklyAvailability>) {
    if (!settings) return;
    setSettings({
      ...settings,
      weekly_availability: settings.weekly_availability.map((rule) =>
        rule.weekday === weekday ? { ...rule, ...patch } : rule
      ),
    });
  }

  async function saveWeekly(rule: DoctorWeeklyAvailability) {
    setError("");
    setSavingKey(`weekly-${rule.weekday}`);
    try {
      const saved = await updateDoctorWeeklyAvailability(rule.weekday, {
        is_available: rule.is_available,
        start_time: rule.is_available ? rule.start_time : null,
        end_time: rule.is_available ? rule.end_time : null,
      });
      setSettings((current) => (current ? updateWeeklyRows(current, saved) : current));
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to save");
    } finally {
      setSavingKey("");
    }
  }

  async function saveOverride() {
    if (!settings || !overrideDate) return;
    setError("");
    setSavingKey("override");
    try {
      const saved = await updateDoctorAvailabilityOverride(overrideDate, {
        is_available: overrideAvailable,
        start_time: overrideAvailable ? overrideStart || null : null,
        end_time: overrideAvailable ? overrideEnd || null : null,
        note: overrideNote.trim() || null,
      });
      setSettings((current) => (current ? updateOverrideRows(current, saved) : current));
      setOverrideNote("");
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to save");
    } finally {
      setSavingKey("");
    }
  }

  async function removeOverride(overrideDateToRemove: string) {
    if (!settings) return;
    setError("");
    setSavingKey(`override-${overrideDateToRemove}`);
    try {
      await deleteDoctorAvailabilityOverride(overrideDateToRemove);
      setSettings({
        ...settings,
        date_overrides: settings.date_overrides.filter(
          (override) => override.override_date !== overrideDateToRemove
        ),
      });
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to remove");
    } finally {
      setSavingKey("");
    }
  }

  const overrideTimeInvalid =
    overrideAvailable && Boolean(overrideStart) !== Boolean(overrideEnd);

  return (
    <DashboardShell role="doctor" title="Availability">
      {error && (
        <div className="bg-red-50 border border-red-100 text-red-600 text-sm rounded-card px-4 py-3 mb-6">
          {error}
        </div>
      )}

      {loading && <div className="text-brand-muted text-sm animate-pulse">Loading...</div>}

      {settings && (
        <div className="space-y-6">
          <div className="bg-white rounded-card border border-brand-border shadow-card overflow-hidden">
            <div className="px-5 py-3.5 border-b border-brand-border">
              <h2 className="text-sm font-semibold text-brand-text">Weekly availability</h2>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="bg-brand-raised border-b border-brand-border">
                    <th className="text-left px-4 py-3 text-xs font-semibold text-brand-muted uppercase tracking-wide">Day</th>
                    <th className="text-left px-4 py-3 text-xs font-semibold text-brand-muted uppercase tracking-wide">Available</th>
                    <th className="text-left px-4 py-3 text-xs font-semibold text-brand-muted uppercase tracking-wide">Start</th>
                    <th className="text-left px-4 py-3 text-xs font-semibold text-brand-muted uppercase tracking-wide">End</th>
                    <th className="text-left px-4 py-3 text-xs font-semibold text-brand-muted uppercase tracking-wide">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-brand-border">
                  {settings.weekly_availability.map((rule) => (
                    <tr key={rule.weekday} className="hover:bg-brand-raised transition-colors">
                      <td className="px-4 py-3 font-medium text-brand-text">
                        {rule.weekday_name}
                      </td>
                      <td className="px-4 py-3">
                        <input
                          type="checkbox"
                          checked={rule.is_available}
                          onChange={(e) =>
                            patchWeekly(rule.weekday, {
                              is_available: e.target.checked,
                              start_time: e.target.checked ? rule.start_time : null,
                              end_time: e.target.checked ? rule.end_time : null,
                            })
                          }
                          className="h-4 w-4 accent-teal-600"
                          aria-label={`${rule.weekday_name} availability`}
                        />
                      </td>
                      <td className="px-4 py-3">
                        <input
                          type="time"
                          value={timeValue(rule.start_time)}
                          disabled={!rule.is_available}
                          onChange={(e) =>
                            patchWeekly(rule.weekday, {
                              start_time: e.target.value || null,
                            })
                          }
                          className="h-9 rounded-md border border-brand-border px-2 text-sm text-brand-text disabled:bg-brand-raised disabled:text-brand-muted"
                        />
                      </td>
                      <td className="px-4 py-3">
                        <input
                          type="time"
                          value={timeValue(rule.end_time)}
                          disabled={!rule.is_available}
                          onChange={(e) =>
                            patchWeekly(rule.weekday, {
                              end_time: e.target.value || null,
                            })
                          }
                          className="h-9 rounded-md border border-brand-border px-2 text-sm text-brand-text disabled:bg-brand-raised disabled:text-brand-muted"
                        />
                      </td>
                      <td className="px-4 py-3">
                        <button
                          onClick={() => saveWeekly(rule)}
                          disabled={savingKey === `weekly-${rule.weekday}`}
                          className="px-3 py-2 rounded-md bg-teal-600 text-white text-xs font-medium hover:bg-teal-700 disabled:opacity-60"
                        >
                          {savingKey === `weekly-${rule.weekday}` ? "Saving" : "Save"}
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className="bg-white rounded-card border border-brand-border shadow-card overflow-hidden">
            <div className="px-5 py-3.5 border-b border-brand-border">
              <h2 className="text-sm font-semibold text-brand-text">Date overrides</h2>
            </div>
            <div className="p-5 grid grid-cols-1 md:grid-cols-6 gap-3 items-end border-b border-brand-border">
              <label className="text-xs font-medium text-brand-muted">
                Date
                <input
                  type="date"
                  value={overrideDate}
                  onChange={(e) => setOverrideDate(e.target.value)}
                  className="mt-1 h-10 w-full rounded-md border border-brand-border px-3 text-sm text-brand-text"
                />
              </label>
              <label className="text-xs font-medium text-brand-muted flex flex-col gap-2">
                Available
                <input
                  type="checkbox"
                  checked={overrideAvailable}
                  onChange={(e) => setOverrideAvailable(e.target.checked)}
                  className="h-4 w-4 accent-teal-600"
                />
              </label>
              <label className="text-xs font-medium text-brand-muted">
                Start
                <input
                  type="time"
                  value={overrideStart}
                  disabled={!overrideAvailable}
                  onChange={(e) => setOverrideStart(e.target.value)}
                  className="mt-1 h-10 w-full rounded-md border border-brand-border px-3 text-sm text-brand-text disabled:bg-brand-raised disabled:text-brand-muted"
                />
              </label>
              <label className="text-xs font-medium text-brand-muted">
                End
                <input
                  type="time"
                  value={overrideEnd}
                  disabled={!overrideAvailable}
                  onChange={(e) => setOverrideEnd(e.target.value)}
                  className="mt-1 h-10 w-full rounded-md border border-brand-border px-3 text-sm text-brand-text disabled:bg-brand-raised disabled:text-brand-muted"
                />
              </label>
              <label className="text-xs font-medium text-brand-muted">
                Note
                <input
                  type="text"
                  value={overrideNote}
                  onChange={(e) => setOverrideNote(e.target.value)}
                  maxLength={255}
                  className="mt-1 h-10 w-full rounded-md border border-brand-border px-3 text-sm text-brand-text"
                />
              </label>
              <button
                onClick={saveOverride}
                disabled={savingKey === "override" || overrideTimeInvalid || !overrideDate}
                className="h-10 rounded-md bg-teal-600 text-white text-sm font-medium hover:bg-teal-700 disabled:opacity-60"
              >
                {savingKey === "override" ? "Saving" : "Save override"}
              </button>
            </div>

            {settings.date_overrides.length === 0 ? (
              <div className="p-6 text-center text-brand-muted text-sm">
                No date overrides set.
              </div>
            ) : (
              <table className="w-full text-sm">
                <thead>
                  <tr className="bg-brand-raised border-b border-brand-border">
                    <th className="text-left px-4 py-3 text-xs font-semibold text-brand-muted uppercase tracking-wide">Date</th>
                    <th className="text-left px-4 py-3 text-xs font-semibold text-brand-muted uppercase tracking-wide">Status</th>
                    <th className="text-left px-4 py-3 text-xs font-semibold text-brand-muted uppercase tracking-wide">Time</th>
                    <th className="text-left px-4 py-3 text-xs font-semibold text-brand-muted uppercase tracking-wide">Note</th>
                    <th className="text-left px-4 py-3 text-xs font-semibold text-brand-muted uppercase tracking-wide">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-brand-border">
                  {settings.date_overrides.map((override) => (
                    <tr key={override.override_date} className="hover:bg-brand-raised transition-colors">
                      <td className="px-4 py-3 font-mono text-xs text-brand-text">
                        {override.override_date}
                      </td>
                      <td className="px-4 py-3">
                        <span className={`inline-flex rounded-full px-2 py-1 text-xs font-medium ${
                          override.is_available
                            ? "bg-teal-50 text-teal-700"
                            : "bg-red-50 text-red-700"
                        }`}>
                          {override.is_available ? "Available" : "Unavailable"}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-brand-muted">
                        {override.start_time && override.end_time
                          ? `${timeValue(override.start_time)}-${timeValue(override.end_time)}`
                          : "Full day"}
                      </td>
                      <td className="px-4 py-3 text-brand-muted">
                        {override.note || "None"}
                      </td>
                      <td className="px-4 py-3">
                        <button
                          onClick={() => removeOverride(override.override_date)}
                          disabled={savingKey === `override-${override.override_date}`}
                          className="text-xs text-red-600 hover:text-red-700 font-medium disabled:opacity-60"
                        >
                          Remove
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>
      )}
    </DashboardShell>
  );
}
