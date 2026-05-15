"use client";
import { Suspense } from "react";
import { useEffect, useState } from "react";
import { useParams, useRouter, useSearchParams } from "next/navigation";
import { getStudentCertificates, getStoredUser } from "@/lib/api";
import type { AuthenticatedUser, StudentCertificateSummary } from "@/lib/types";

function fmtDate(d: string) {
  return new Date(d).toLocaleDateString("en-IN", {
    day: "numeric",
    month: "long",
    year: "numeric",
  });
}

function leaveDays(start: string, end: string): number {
  return (
    Math.round(
      (new Date(end).getTime() - new Date(start).getTime()) /
        (1000 * 60 * 60 * 24)
    ) + 1
  );
}

function CertificateDocumentPageInner() {
  const params = useParams();
  const router = useRouter();
  const searchParams = useSearchParams();
  const rawId = Array.isArray(params.id) ? params.id[0] : params.id;
  const id = rawId ? Number(rawId) : NaN;
  const autoPrint = searchParams.get("print") === "1";

  const [certificate, setCertificate] =
    useState<StudentCertificateSummary | null>(null);
  const [user, setUser] = useState<AuthenticatedUser | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const storedUser = getStoredUser();
    if (!storedUser) {
      router.replace("/login");
      setLoading(false);
      return;
    }
    if (isNaN(id) || id <= 0) {
      setError("Invalid certificate ID");
      setLoading(false);
      return;
    }
    setUser(storedUser);
    getStudentCertificates()
      .then((certs) => {
        const found = certs.find((c) => c.certificate_id === id) ?? null;
        if (!found) {
          setError("Certificate not found");
          return;
        }
        setCertificate(found);
      })
      .catch((e: unknown) =>
        setError(
          e instanceof Error ? e.message : "Failed to load certificate"
        )
      )
      .finally(() => setLoading(false));
  }, [id, router]);

  useEffect(() => {
    if (autoPrint && certificate && !loading) {
      window.print();
    }
  }, [autoPrint, certificate, loading]);

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-100">
        <p className="animate-pulse text-sm text-gray-500">
          Loading certificate…
        </p>
      </div>
    );
  }

  if (error || !certificate) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center gap-3 bg-gray-100">
        <p className="text-sm text-red-600">
          {error || "Certificate not found"}
        </p>
        <button
          onClick={() => router.back()}
          className="rounded border border-gray-200 bg-white px-3 py-1.5 text-sm text-gray-600 shadow-sm hover:bg-gray-50"
        >
          ← Back
        </button>
      </div>
    );
  }

  const issueDate = fmtDate(certificate.issue_date);
  const issuedBeforeAppointment =
    new Date(certificate.issue_date) < new Date(certificate.appointment_date);
  const isMedicalLeave = certificate.certificate_type
    .toLowerCase()
    .includes("leave");
  const isFitness = certificate.certificate_type
    .toLowerCase()
    .includes("fitness");

  const hasDates =
    isMedicalLeave &&
    !!certificate.leave_start_date &&
    !!certificate.leave_end_date;
  const days = hasDates
    ? leaveDays(certificate.leave_start_date!, certificate.leave_end_date!)
    : null;

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

      {/* Data inconsistency warning — hidden when printing */}
      {issuedBeforeAppointment && (
        <div className="no-print fixed left-1/2 top-4 z-10 -translate-x-1/2 rounded border border-amber-200 bg-amber-50 px-4 py-2 text-xs text-amber-700 shadow-sm">
          Issue date precedes appointment date — possible data error
        </div>
      )}

      {/* Page wrapper */}
      <div className="min-h-screen bg-gray-100 py-8 print:bg-white print:py-0">
        {/* A4 document */}
        <div
          className="mx-auto bg-white shadow-lg print:shadow-none"
          style={{ width: "794px", minHeight: "1123px", padding: "32px" }}
        >
          {/* Header */}
          <div className="mb-8 flex items-start justify-between border-l-4 border-teal-600 pl-4">
            <div>
              <p className="text-xs font-medium uppercase tracking-wide text-gray-400">
                College Infirmary
              </p>
              <h1 className="mt-1 font-['Outfit'] text-2xl font-semibold text-gray-900">
                {certificate.certificate_type}
              </h1>
            </div>
            <div className="text-right">
              <p className="font-mono text-xs text-gray-400">
                Certificate #{certificate.certificate_id}
              </p>
              <p className="mt-0.5 font-mono text-xs text-gray-400">
                Issued {issueDate}
              </p>
            </div>
          </div>

          {/* Formal statement — type-aware */}
          <div className="mb-8">
            {isMedicalLeave && (
              <p className="text-sm leading-relaxed text-gray-800">
                This certifies that{" "}
                <strong>{user?.name ?? "the above-named student"}</strong> was
                examined at the College Infirmary on{" "}
                <strong>{fmtDate(certificate.appointment_date)}</strong> and is
                hereby granted medical leave
                {hasDates ? (
                  <>
                    {" "}from{" "}
                    <strong>{fmtDate(certificate.leave_start_date!)}</strong> to{" "}
                    <strong>{fmtDate(certificate.leave_end_date!)}</strong> (
                    {days} {days === 1 ? "day" : "days"})
                  </>
                ) : (
                  <> for the recommended duration as advised by the attending doctor</>
                )}
                .
              </p>
            )}
            {isFitness && (
              <p className="text-sm leading-relaxed text-gray-800">
                This certifies that{" "}
                <strong>{user?.name ?? "the above-named student"}</strong> was
                examined at the College Infirmary on{" "}
                <strong>{fmtDate(certificate.appointment_date)}</strong> and is
                declared medically fit to resume academic and physical
                activities.
              </p>
            )}
            {!isMedicalLeave && !isFitness && (
              <p className="text-sm leading-relaxed text-gray-800">
                This certifies that the following student was examined at the
                College Infirmary and this{" "}
                <strong>{certificate.certificate_type}</strong> was issued on{" "}
                <strong>{issueDate}</strong>.
              </p>
            )}
          </div>

          {/* Patient details */}
          <div className="mb-8 rounded-lg border border-gray-200 bg-gray-50 p-5">
            <p className="mb-3 text-xs font-medium uppercase tracking-wide text-gray-400">
              Patient Details
            </p>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <p className="mb-0.5 text-xs text-gray-400">Full Name</p>
                <p className="font-medium text-gray-900">
                  {user?.name ?? "—"}
                </p>
              </div>
              <div>
                <p className="mb-0.5 text-xs text-gray-400">Student ID</p>
                <p className="font-mono text-gray-900">
                  {user?.user_id ?? "—"}
                </p>
              </div>
              <div>
                <p className="mb-0.5 text-xs text-gray-400">
                  Appointment Date
                </p>
                <p className="text-gray-900">
                  {fmtDate(certificate.appointment_date)}
                </p>
              </div>
              <div>
                <p className="mb-0.5 text-xs text-gray-400">Issuing Doctor</p>
                <p className="text-gray-900">Dr. {certificate.doctor_name}</p>
              </div>
            </div>
          </div>

          {/* Medical Leave — leave period block */}
          {isMedicalLeave && (
            <div className="mb-8 rounded-lg border border-teal-100 bg-teal-50 p-5">
              <p className="mb-3 text-xs font-medium uppercase tracking-wide text-teal-600">
                Leave Period
              </p>
              <div className="grid grid-cols-3 gap-4 text-sm">
                <div>
                  <p className="mb-0.5 text-xs text-gray-400">From</p>
                  <p className="font-medium text-gray-900">
                    {certificate.leave_start_date
                      ? fmtDate(certificate.leave_start_date)
                      : "—"}
                  </p>
                </div>
                <div>
                  <p className="mb-0.5 text-xs text-gray-400">Until</p>
                  <p className="font-medium text-gray-900">
                    {certificate.leave_end_date
                      ? fmtDate(certificate.leave_end_date)
                      : "—"}
                  </p>
                </div>
                <div>
                  <p className="mb-0.5 text-xs text-gray-400">Duration</p>
                  <p className="font-medium text-gray-900">
                    {days != null ? `${days} ${days === 1 ? "day" : "days"}` : "—"}
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Fitness — clearance notes block */}
          {isFitness && (
            <div className="mb-8 rounded-lg border border-teal-100 bg-teal-50 p-5">
              <p className="mb-2 text-xs font-medium uppercase tracking-wide text-teal-600">
                Clearance Details
              </p>
              <p className="text-sm leading-relaxed text-gray-800">
                {certificate.certificate_notes ?? "—"}
              </p>
            </div>
          )}

          {/* Seal space */}
          <div className="mb-8 flex h-28 items-center justify-center rounded-lg border-2 border-dashed border-gray-200">
            <p className="text-xs uppercase tracking-widest text-gray-300">
              Official Seal
            </p>
          </div>

          {/* Footer */}
          <div className="border-t border-gray-200 pt-6">
            <div className="flex items-end justify-between">
              <div>
                <p className="text-sm font-medium text-gray-900">
                  Dr. {certificate.doctor_name}
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

export default function CertificateDocumentPage() {
  return (
    <Suspense
      fallback={
        <div className="flex min-h-screen items-center justify-center bg-gray-100">
          <p className="animate-pulse text-sm text-gray-500">Loading…</p>
        </div>
      }
    >
      <CertificateDocumentPageInner />
    </Suspense>
  );
}
