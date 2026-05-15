"use client";
import { useEffect, useState } from "react";
import { useParams, useRouter, useSearchParams } from "next/navigation";
import { getReportDetail, getStoredUser } from "@/lib/api";
import type { ReportDetail } from "@/lib/types";

function fmtDate(d: string) {
  return new Date(d).toLocaleDateString("en-IN", {
    day: "numeric",
    month: "long",
    year: "numeric",
  });
}

function fmtTime(t: string) {
  return t.slice(0, 5);
}

export default function ReportDocumentPage() {
  const params = useParams();
  const router = useRouter();
  const searchParams = useSearchParams();
  const id = Number(params.id);
  const autoPrint = searchParams.get("print") === "1";

  const [report, setReport] = useState<ReportDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const user = getStoredUser();
    if (!user) {
      router.replace("/login");
      return;
    }
    getReportDetail(id)
      .then(setReport)
      .catch((e: unknown) =>
        setError(e instanceof Error ? e.message : "Failed to load report")
      )
      .finally(() => setLoading(false));
  }, [id, router]);

  useEffect(() => {
    if (autoPrint && report && !loading) {
      window.print();
    }
  }, [autoPrint, report, loading]);

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-100">
        <p className="animate-pulse text-sm text-gray-500">Loading report…</p>
      </div>
    );
  }

  if (error || !report) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-100">
        <p className="text-sm text-red-600">{error || "Report not found"}</p>
      </div>
    );
  }

  const { appointment, note, prescription } = report;
  const issueDate = fmtDate(new Date().toISOString().split("T")[0]);

  return (
    <>
      <style>{`
        @media print {
          .no-print { display: none !important; }
          body { margin: 0; background: white; }
        }
        @page { size: A4 portrait; margin: 0; }
      `}</style>

      {/* Controls — hidden when printing */}
      <div className="no-print fixed right-4 top-4 z-10 flex gap-2">
        <button
          onClick={() => router.back()}
          className="rounded border border-gray-200 bg-white px-3 py-1.5 text-sm text-gray-600 shadow-sm hover:bg-gray-50"
        >
          ← Back
        </button>
        <button
          onClick={() => window.print()}
          className="rounded bg-teal-600 px-3 py-1.5 text-sm font-medium text-white shadow-sm hover:bg-teal-700"
        >
          Print / Save as PDF
        </button>
      </div>

      {/* Page wrapper */}
      <div className="min-h-screen bg-gray-100 py-8 print:bg-white print:py-0">
        {/* A4 document */}
        <div
          className="mx-auto bg-white shadow-lg print:shadow-none"
          style={{ width: "794px", minHeight: "1123px", padding: "32px" }}
        >
          {/* Header */}
          <div className="mb-6 flex items-start justify-between border-l-4 border-teal-600 pl-4">
            <div>
              <p className="text-xs font-medium uppercase tracking-wide text-gray-400">
                College Infirmary
              </p>
              <h1 className="mt-0.5 font-['Outfit'] text-2xl font-semibold text-gray-900">
                Medical Report
              </h1>
            </div>
            <div className="text-right">
              <p className="font-mono text-xs text-gray-400">
                Report #{appointment.appointment_id}
              </p>
              <p className="mt-0.5 font-mono text-xs text-gray-400">
                Issued {issueDate}
              </p>
            </div>
          </div>

          {/* Metadata grid */}
          <div className="mb-6 grid grid-cols-2 gap-4 rounded-lg border border-gray-200 bg-gray-50 p-4">
            <div>
              <p className="mb-2 text-xs font-medium uppercase tracking-wide text-gray-400">
                Patient
              </p>
              <p className="text-sm font-medium text-gray-900">
                {appointment.student_name}
              </p>
              <p className="mt-0.5 font-mono text-xs text-gray-500">
                ID: {appointment.student_id}
              </p>
            </div>
            <div>
              <p className="mb-2 text-xs font-medium uppercase tracking-wide text-gray-400">
                Appointment
              </p>
              <p className="text-sm text-gray-900">
                {fmtDate(appointment.slot_date)}
              </p>
              <p className="mt-0.5 text-xs text-gray-500">
                {fmtTime(appointment.start_time)} –{" "}
                {fmtTime(appointment.end_time)}
              </p>
              <p className="mt-0.5 text-xs text-gray-500">
                Dr. {appointment.doctor_name}
              </p>
            </div>
          </div>

          {/* Diagnosis */}
          <div className="mb-5">
            <h2 className="mb-2 text-xs font-semibold uppercase tracking-wider text-teal-700">
              Diagnosis
            </h2>
            <p className="text-sm leading-relaxed text-gray-800">
              {note?.diagnosis ?? "Not recorded"}
            </p>
          </div>

          {/* Remarks */}
          <div className="mb-5">
            <h2 className="mb-2 text-xs font-semibold uppercase tracking-wider text-teal-700">
              Remarks
            </h2>
            <p className="text-sm leading-relaxed text-gray-800">
              {note?.remarks ?? "Not recorded"}
            </p>
          </div>

          {/* Prescription — only when items exist */}
          {prescription && prescription.items.length > 0 && (
            <div className="mb-6">
              <h2 className="mb-2 text-xs font-semibold uppercase tracking-wider text-teal-700">
                Prescription
              </h2>
              <table className="w-full border-collapse text-sm">
                <thead>
                  <tr className="bg-teal-600 text-white">
                    <th className="px-3 py-2 text-left text-xs font-medium">
                      Medicine
                    </th>
                    <th className="px-3 py-2 text-left text-xs font-medium">
                      Dosage
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {prescription.items.map((item, i) => (
                    <tr
                      key={item.item_id}
                      className={i % 2 === 0 ? "bg-white" : "bg-gray-50"}
                    >
                      <td className="border-b border-gray-100 px-3 py-2 text-gray-900">
                        {item.medicine_name}
                      </td>
                      <td className="border-b border-gray-100 px-3 py-2 text-gray-600">
                        {item.dosage}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* Footer */}
          <div className="mt-auto border-t border-gray-200 pt-16">
            <div className="flex items-end justify-between">
              <div>
                <p className="text-sm font-medium text-gray-900">
                  Dr. {appointment.doctor_name}
                </p>
                <p className="mt-0.5 text-xs text-gray-500">
                  College Infirmary
                </p>
              </div>
              <div className="text-right">
                <div className="mb-1 w-48 border-b border-gray-400" />
                <p className="text-xs text-gray-400">Signature</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}