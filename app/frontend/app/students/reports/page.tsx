"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  getReportDetail,
  getStudentCertificates,
  getStudentReports,
  getStoredUser,
} from "@/lib/api";
import type {
  ReportDetail,
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

function downloadTextFile(filename: string, content: string) {
  const blob = new Blob([content], { type: "text/plain;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
}

function reportText(report: ReportDetail) {
  const lines = [
    "Medical Report",
    "",
    `Appointment: #${report.appointment.appointment_id}`,
    `Date: ${fmtDate(report.appointment.slot_date)}`,
    `Doctor: Dr. ${report.appointment.doctor_name}`,
    `Patient: ${report.appointment.student_name}`,
    "",
    "Diagnosis",
    report.note?.diagnosis ?? "Not recorded",
    "",
    "Remarks",
    report.note?.remarks ?? "Not recorded",
  ];

  if (report.prescription?.items.length) {
    lines.push("", "Prescription");
    report.prescription.items.forEach((item, index) => {
      lines.push(`${index + 1}. ${item.medicine_name} - ${item.dosage}`);
    });
  }

  return lines.join("\n");
}

function certificateText(certificate: StudentCertificateSummary) {
  return [
    "Medical Certificate",
    "",
    `Certificate ID: #${certificate.certificate_id}`,
    `Type: ${certificate.certificate_type}`,
    `Issued: ${fmtDate(certificate.issue_date)}`,
    `Appointment: #${certificate.appointment_id}`,
    `Appointment Date: ${fmtDate(certificate.appointment_date)}`,
    `Doctor: Dr. ${certificate.doctor_name}`,
  ].join("\n");
}

export default function ReportsPage() {
  const router = useRouter();
  const [tab, setTab] = useState<Tab>("reports");
  const [reports, setReports] = useState<StudentReportSummary[]>([]);
  const [certs, setCerts] = useState<StudentCertificateSummary[]>([]);
  const [selectedReport, setSelectedReport] = useState<ReportDetail | null>(null);
  const [selectedCertificate, setSelectedCertificate] =
    useState<StudentCertificateSummary | null>(null);
  const [detailLoadingId, setDetailLoadingId] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const user = getStoredUser();
    if (!user) {
      router.replace("/login");
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

  async function viewReport(appointmentId: number) {
    setError("");
    setDetailLoadingId(appointmentId);
    try {
      setSelectedReport(await getReportDetail(appointmentId));
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to load report");
    } finally {
      setDetailLoadingId(null);
    }
  }

  async function downloadReport(report: StudentReportSummary) {
    setError("");
    setDetailLoadingId(report.appointment_id);
    try {
      const detail = await getReportDetail(report.appointment_id);
      downloadTextFile(`report-${report.appointment_id}.txt`, reportText(detail));
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to download report");
    } finally {
      setDetailLoadingId(null);
    }
  }

  function downloadCertificate(certificate: StudentCertificateSummary) {
    downloadTextFile(
      `certificate-${certificate.certificate_id}.txt`,
      certificateText(certificate)
    );
  }

  return (
    <DashboardShell role="student" title="Reports & Certificates">
      {selectedReport && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          <button
            type="button"
            aria-label="Close report details"
            className="absolute inset-0 bg-black/30"
            onClick={() => setSelectedReport(null)}
          />
          <div className="relative mx-4 w-full max-w-2xl rounded-card border border-brand-border bg-white p-6 shadow-xl">
            <div className="flex items-start justify-between gap-4">
              <div>
                <h2 className="text-base font-semibold text-brand-text">
                  Medical Report
                </h2>
                <p className="mt-1 text-sm text-brand-muted">
                  {fmtDate(selectedReport.appointment.slot_date)} with Dr.{" "}
                  {selectedReport.appointment.doctor_name}
                </p>
              </div>
              <button
                type="button"
                onClick={() => setSelectedReport(null)}
                className="rounded-btn border border-brand-border px-3 py-1.5 text-sm text-brand-muted transition hover:bg-brand-raised"
              >
                Close
              </button>
            </div>

            <div className="mt-5 grid gap-4 text-sm">
              <section>
                <h3 className="font-medium text-brand-text">Diagnosis</h3>
                <p className="mt-1 text-brand-muted">
                  {selectedReport.note?.diagnosis ?? "Not recorded"}
                </p>
              </section>
              <section>
                <h3 className="font-medium text-brand-text">Remarks</h3>
                <p className="mt-1 text-brand-muted">
                  {selectedReport.note?.remarks ?? "Not recorded"}
                </p>
              </section>
              <section>
                <h3 className="font-medium text-brand-text">Prescription</h3>
                {selectedReport.prescription?.items.length ? (
                  <ul className="mt-2 divide-y divide-brand-border rounded-card border border-brand-border">
                    {selectedReport.prescription.items.map((item) => (
                      <li key={item.item_id} className="flex justify-between gap-4 px-3 py-2">
                        <span className="text-brand-text">{item.medicine_name}</span>
                        <span className="text-brand-muted">{item.dosage}</span>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="mt-1 text-brand-muted">No prescription recorded.</p>
                )}
              </section>
            </div>
          </div>
        </div>
      )}

      {selectedCertificate && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          <button
            type="button"
            aria-label="Close certificate details"
            className="absolute inset-0 bg-black/30"
            onClick={() => setSelectedCertificate(null)}
          />
          <div className="relative mx-4 w-full max-w-lg rounded-card border border-brand-border bg-white p-6 shadow-xl">
            <div className="flex items-start justify-between gap-4">
              <div>
                <h2 className="text-base font-semibold text-brand-text">
                  {selectedCertificate.certificate_type}
                </h2>
                <p className="mt-1 text-sm text-brand-muted">
                  Issued {fmtDate(selectedCertificate.issue_date)}
                </p>
              </div>
              <button
                type="button"
                onClick={() => setSelectedCertificate(null)}
                className="rounded-btn border border-brand-border px-3 py-1.5 text-sm text-brand-muted transition hover:bg-brand-raised"
              >
                Close
              </button>
            </div>
            <dl className="mt-5 grid gap-3 text-sm">
              <div className="flex justify-between gap-4">
                <dt className="text-brand-muted">Doctor</dt>
                <dd className="text-brand-text">Dr. {selectedCertificate.doctor_name}</dd>
              </div>
              <div className="flex justify-between gap-4">
                <dt className="text-brand-muted">Appointment</dt>
                <dd className="text-brand-text">
                  {fmtDate(selectedCertificate.appointment_date)}
                </dd>
              </div>
              <div className="flex justify-between gap-4">
                <dt className="text-brand-muted">Certificate ID</dt>
                <dd className="font-mono text-brand-text">
                  #{selectedCertificate.certificate_id}
                </dd>
              </div>
            </dl>
          </div>
        </div>
      )}

      <div className="mb-5 flex border-b border-brand-border">
        {(["reports", "certificates"] as Tab[]).map((item) => (
          <button
            key={item}
            onClick={() => setTab(item)}
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

      {loading && <p className="text-sm text-brand-muted animate-pulse">Loading...</p>}

      {!loading && tab === "reports" && (
        <div className="space-y-3">
          {reports.length === 0 && (
            <p className="text-sm text-brand-muted">No reports available yet.</p>
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
                    {report.prescription_count > 0 ? "Prescription" : "Consultation"}
                  </span>
                </div>
                <p className="text-sm text-brand-muted">Dr. {report.doctor_name}</p>
                {report.diagnosis && (
                  <p className="mt-1 max-w-md truncate text-xs text-brand-muted">
                    {report.diagnosis}
                  </p>
                )}
              </div>
              <div className="ml-4 flex flex-shrink-0 items-center gap-2">
                <button
                  onClick={() => viewReport(report.appointment_id)}
                  className="rounded-btn border border-teal-200 px-2.5 py-1 text-xs text-teal-600 transition-colors hover:border-teal-300 hover:text-teal-700"
                >
                  {detailLoadingId === report.appointment_id ? "Loading..." : "View"}
                </button>
                <button
                  onClick={() => downloadReport(report)}
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
            <p className="text-sm text-brand-muted">No certificates available yet.</p>
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
                <p className="text-sm text-brand-muted">Dr. {certificate.doctor_name}</p>
                <p className="mt-0.5 text-xs text-brand-muted">
                  Appointment: {fmtDate(certificate.appointment_date)}
                </p>
              </div>
              <div className="ml-4 flex flex-shrink-0 items-center gap-2">
                <button
                  onClick={() => setSelectedCertificate(certificate)}
                  className="rounded-btn border border-teal-200 px-2.5 py-1 text-xs text-teal-600 transition-colors hover:border-teal-300 hover:text-teal-700"
                >
                  View
                </button>
                <button
                  onClick={() => downloadCertificate(certificate)}
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
