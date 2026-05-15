"use client";
import { Suspense } from "react";
import { useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import {
  getStudentCertificates,
  getStudentReports,
  getStoredUser,
} from "@/lib/api";
import { doctorName } from "@/lib/utils";
import type {
  StudentCertificateSummary,
  StudentReportSummary,
} from "@/lib/types";
import DashboardShell from "@/components/layout/DashboardShell";

type Tab = "reports" | "certificates";

function fmtDate(d: string) {
  return new Date(d).toLocaleDateString("en-IN", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });
}

function ReportsPageInner() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const initialTab: Tab =
    searchParams.get("tab") === "certificates" ? "certificates" : "reports";
  const [tab, setTab] = useState<Tab>(initialTab);
  const [reports, setReports] = useState<StudentReportSummary[]>([]);
  const [certs, setCerts] = useState<StudentCertificateSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const user = getStoredUser();
    if (!user) {
      router.replace("/login");
      setLoading(false);
      return;
    }
    Promise.all([getStudentReports(), getStudentCertificates()])
      .then(([reportRows, certificateRows]) => {
        setReports(reportRows);
        setCerts(certificateRows);
      })
      .catch((e: unknown) =>
        setError(e instanceof Error ? e.message : "Failed to load records")
      )
      .finally(() => setLoading(false));
  }, [router]);

  function switchTab(item: Tab) {
    setTab(item);
    router.replace(`/students/reports?tab=${item}`);
  }

  return (
    <DashboardShell role="student" title="Reports & Certificates">
      <div className="mb-5 flex border-b border-brand-border">
        {(["reports", "certificates"] as Tab[]).map((item) => (
          <button
            key={item}
            onClick={() => switchTab(item)}
            className={`-mb-px border-b-2 px-4 py-2.5 text-sm font-medium capitalize transition-colors ${
              tab === item
                ? "border-teal-600 text-teal-700"
                : "border-transparent text-brand-muted hover:text-brand-text"
            }`}
          >
            {item}
          </button>
        ))}
      </div>

      {error && (
        <div className="mb-5 rounded-card border border-red-100 bg-red-50 px-4 py-3 text-sm text-red-600">
          {error}
        </div>
      )}

      {loading && (
        <p className="animate-pulse text-sm text-brand-muted">Loading...</p>
      )}

      {!loading && tab === "reports" && (
        <div className="space-y-3">
          {reports.length === 0 && (
            <p className="text-sm text-brand-muted">
              No reports available yet.
            </p>
          )}
          {reports.map((report) => (
            <div
              key={report.appointment_id}
              className="flex items-center justify-between rounded-card border border-brand-border bg-white p-4 shadow-card"
            >
              <div className="min-w-0 flex-1">
                <div className="mb-1 flex items-center gap-3">
                  <span className="text-sm font-medium text-brand-text">
                    {fmtDate(report.appointment_date)}
                  </span>
                  <span className="inline-flex items-center rounded-full bg-blue-50 px-2 py-0.5 text-xs text-blue-700 ring-1 ring-blue-200">
                    {report.prescription_count > 0
                      ? "Prescription"
                      : "Consultation"}
                  </span>
                </div>
                <p className="text-sm text-brand-muted">
                  Dr. {doctorName(report.doctor_name)}
                </p>
                {report.diagnosis && (
                  <p className="mt-1 max-w-md truncate text-xs text-brand-muted">
                    {report.diagnosis}
                  </p>
                )}
              </div>
              <div className="ml-4 flex flex-shrink-0 items-center gap-2">
                <button
                  onClick={() =>
                    router.push(
                      `/students/reports/${report.appointment_id}`
                    )
                  }
                  className="rounded-btn border border-teal-200 px-2.5 py-1 text-xs text-teal-600 transition-colors hover:border-teal-300 hover:text-teal-700"
                >
                  View
                </button>
                <button
                  onClick={() =>
                    router.push(
                      `/students/reports/${report.appointment_id}?print=1`
                    )
                  }
                  className="rounded-btn border border-brand-border px-2.5 py-1 text-xs text-brand-muted transition-colors hover:border-slate-400 hover:text-brand-text"
                >
                  Download
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {!loading && tab === "certificates" && (
        <div className="space-y-3">
          {certs.length === 0 && (
            <p className="text-sm text-brand-muted">
              No certificates available yet.
            </p>
          )}
          {certs.map((certificate) => (
            <div
              key={certificate.certificate_id}
              className="flex items-center justify-between rounded-card border border-brand-border bg-white p-4 shadow-card"
            >
              <div className="flex-1">
                <div className="mb-1 flex items-center gap-3">
                  <span className="text-sm font-medium text-brand-text">
                    {certificate.certificate_type}
                  </span>
                  <span className="text-xs text-brand-muted">
                    Issued {fmtDate(certificate.issue_date)}
                  </span>
                </div>
                <p className="text-sm text-brand-muted">
                  Dr. {doctorName(certificate.doctor_name)}
                </p>
                <p className="mt-0.5 text-xs text-brand-muted">
                  Appointment: {fmtDate(certificate.appointment_date)}
                </p>
              </div>
              <div className="ml-4 flex flex-shrink-0 items-center gap-2">
                <button
                  onClick={() =>
                    router.push(
                      `/students/certificates/${certificate.certificate_id}`
                    )
                  }
                  className="rounded-btn border border-teal-200 px-2.5 py-1 text-xs text-teal-600 transition-colors hover:border-teal-300 hover:text-teal-700"
                >
                  View
                </button>
                <button
                  onClick={() =>
                    router.push(
                      `/students/certificates/${certificate.certificate_id}?print=1`
                    )
                  }
                  className="rounded-btn border border-brand-border px-2.5 py-1 text-xs text-brand-muted transition-colors hover:border-slate-400 hover:text-brand-text"
                >
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

export default function ReportsPage() {
  return (
    <Suspense
      fallback={
        <DashboardShell role="student" title="Reports & Certificates">
          <p className="animate-pulse text-sm text-brand-muted">Loading...</p>
        </DashboardShell>
      }
    >
      <ReportsPageInner />
    </Suspense>
  );
}
