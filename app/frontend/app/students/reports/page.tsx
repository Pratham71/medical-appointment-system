"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getStudentReports, getStudentCertificates, getStoredUser } from "@/lib/api";
import type { StudentReportSummary, StudentCertificateSummary } from "@/lib/types";
import DashboardShell from "@/components/layout/DashboardShell";

type Tab = "reports" | "certificates";

function fmtDate(d: string) {
  return new Date(d).toLocaleDateString("en-IN", { day: "numeric", month: "short", year: "numeric" });
}

export default function ReportsPage() {
  const router = useRouter();
  const [tab, setTab] = useState<Tab>("reports");
  const [reports, setReports] = useState<StudentReportSummary[]>([]);
  const [certs, setCerts] = useState<StudentCertificateSummary[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const user = getStoredUser();
    if (!user) { router.replace("/login"); return; }
    Promise.all([getStudentReports(), getStudentCertificates()])
      .then(([r, c]) => { setReports(r); setCerts(c); })
      .finally(() => setLoading(false));
  }, [router]);

  return (
    <DashboardShell role="student" title="Reports & Certificates">
      {/* Tabs */}
      <div className="flex border-b border-brand-border mb-5">
        {(["reports", "certificates"] as Tab[]).map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`px-4 py-2.5 text-sm font-medium border-b-2 -mb-px capitalize transition-colors ${
              tab === t
                ? "border-teal-600 text-teal-700"
                : "border-transparent text-brand-muted hover:text-brand-text"
            }`}
          >
            {t}
          </button>
        ))}
      </div>

      {loading && <p className="text-brand-muted text-sm animate-pulse">Loading…</p>}

      {/* Reports */}
      {!loading && tab === "reports" && (
        <div className="space-y-3">
          {reports.length === 0 && (
            <p className="text-brand-muted text-sm">No reports available yet.</p>
          )}
          {reports.map((r) => (
            <div
              key={r.appointment_id}
              className="bg-white rounded-card border border-brand-border shadow-card p-4 flex items-center justify-between"
            >
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-3 mb-1">
                  <span className="text-sm font-medium text-brand-text">
                    {fmtDate(r.appointment_date)}
                  </span>
                  <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs bg-blue-50 text-blue-700 ring-1 ring-blue-200">
                    {r.prescription_count > 0 ? "Prescription" : "Consultation"}
                  </span>
                </div>
                <p className="text-sm text-brand-muted">Dr. {r.doctor_name}</p>
                {r.diagnosis && (
                  <p className="text-xs text-brand-muted mt-1 truncate max-w-md">
                    {r.diagnosis}
                  </p>
                )}
              </div>
              <div className="flex items-center gap-2 ml-4 flex-shrink-0">
                {r.prescription_count > 0 && (
                  <span className="text-xs text-brand-muted">
                    {r.prescription_count} prescription{r.prescription_count !== 1 ? "s" : ""}
                  </span>
                )}
                <button className="text-xs text-teal-600 hover:text-teal-700 border border-teal-200 hover:border-teal-300 px-2.5 py-1 rounded-btn transition-colors">
                  View
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Certificates */}
      {!loading && tab === "certificates" && (
        <div className="space-y-3">
          {certs.length === 0 && (
            <p className="text-brand-muted text-sm">No certificates available yet.</p>
          )}
          {certs.map((c) => (
            <div
              key={c.certificate_id}
              className="bg-white rounded-card border border-brand-border shadow-card p-4 flex items-center justify-between"
            >
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-1">
                  <span className="text-sm font-medium text-brand-text">
                    {c.certificate_type}
                  </span>
                  <span className="text-xs text-brand-muted">
                    Issued {fmtDate(c.issue_date)}
                  </span>
                </div>
                <p className="text-sm text-brand-muted">Dr. {c.doctor_name}</p>
                <p className="text-xs text-brand-muted mt-0.5">
                  Appointment: {fmtDate(c.appointment_date)}
                </p>
              </div>
              <div className="flex items-center gap-2 ml-4 flex-shrink-0">
                <button className="text-xs text-teal-600 hover:text-teal-700 border border-teal-200 hover:border-teal-300 px-2.5 py-1 rounded-btn transition-colors">
                  View
                </button>
                <button className="text-xs text-brand-muted hover:text-brand-text border border-brand-border hover:border-slate-400 px-2.5 py-1 rounded-btn transition-colors">
                  Download
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </DashboardShell>
  );
}
