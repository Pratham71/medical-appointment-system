"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { searchPatients } from "@/lib/api";
import type { PatientSearchResult } from "@/lib/types";
import DashboardShell from "@/components/layout/DashboardShell";

export default function PatientSearchPage() {
  const router = useRouter();
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<PatientSearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [hasSearched, setHasSearched] = useState(false);
  const canSearch = query.trim().length >= 2;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!canSearch) return;
    setLoading(true);
    setError("");
    setHasSearched(true);
    try {
      setResults(await searchPatients(query.trim()));
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Patient search failed");
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <DashboardShell role="doctor" title="Patient History">
      <div className="max-w-2xl rounded-card border border-brand-border bg-white p-6 shadow-card">
        <h2 className="mb-4 text-base font-semibold text-brand-text">
          Look up a Patient
        </h2>
        <form onSubmit={handleSubmit} className="flex gap-3">
          <div className="min-w-0 flex-1">
            <label className="mb-1.5 block text-sm font-medium text-brand-text">
              Name or roll number
            </label>
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="e.g. Aarav or CSE-2026-001"
              minLength={2}
              required
              className="w-full rounded-btn border border-brand-border px-3 py-2.5 text-sm text-brand-text transition placeholder:text-brand-muted focus:outline-none focus:ring-2 focus:ring-teal-600 focus:ring-offset-1"
            />
          </div>
          <button
            type="submit"
            disabled={!canSearch || loading}
            className="mt-6 rounded-btn bg-teal-600 px-5 py-2.5 text-sm font-medium text-white transition-colors hover:bg-teal-700 disabled:opacity-50"
          >
            {loading ? "Searching..." : "Search"}
          </button>
        </form>

        {error && (
          <div className="mt-4 rounded-card border border-red-100 bg-red-50 px-4 py-3 text-sm text-red-600">
            {error}
          </div>
        )}

        <div className="mt-5 space-y-2">
          {results.map((patient) => (
            <button
              key={patient.student_id}
              type="button"
              onClick={() => router.push(`/doctors/patients/${patient.student_id}?name=${encodeURIComponent(patient.student_name)}&roll=${encodeURIComponent(patient.roll_number)}`)}
              className="w-full rounded-card border border-brand-border px-4 py-3 text-left transition hover:border-teal-200 hover:bg-teal-50"
            >
              <div className="flex items-center justify-between gap-4">
                <span className="font-medium text-brand-text">
                  {patient.student_name}
                </span>
                <span className="font-mono text-xs text-brand-muted">
                  {patient.roll_number}
                </span>
              </div>
              <p className="mt-1 text-xs text-brand-muted">
                {patient.department} - Year {patient.year_level}
              </p>
            </button>
          ))}
          {!loading && hasSearched && results.length === 0 && (
            <p className="text-sm text-brand-muted">No student found.</p>
          )}
        </div>
      </div>
    </DashboardShell>
  );
}
