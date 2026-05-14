"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import DashboardShell from "@/components/layout/DashboardShell";

export default function PatientSearchPage() {
  const router = useRouter();
  const [studentId, setStudentId] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const id = parseInt(studentId, 10);
    if (id > 0) router.push(`/doctors/patients/${id}`);
  };

  return (
    <DashboardShell role="doctor" title="Patient History">
      <div className="bg-white rounded-card border border-brand-border shadow-card p-6 max-w-sm">
        <h2 className="text-base font-semibold text-brand-text mb-4">Look up a Patient</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-brand-text mb-1.5">
              Student ID
            </label>
            <input
              type="number"
              value={studentId}
              onChange={(e) => setStudentId(e.target.value)}
              placeholder="e.g. 1"
              min="1"
              required
              className="w-full border border-brand-border rounded-btn px-3 py-2.5 text-sm font-mono text-brand-text placeholder:text-brand-muted focus:ring-2 focus:ring-teal-600 focus:ring-offset-1 focus:outline-none transition"
            />
          </div>
          <button
            type="submit"
            className="w-full bg-teal-600 hover:bg-teal-700 text-white font-medium py-2.5 rounded-btn text-sm transition-colors"
          >
            View History
          </button>
        </form>
        <p className="mt-4 text-xs text-brand-muted">
          Tip: you can also open patient history directly from an appointment&apos;s detail page.
        </p>
      </div>
    </DashboardShell>
  );
}
