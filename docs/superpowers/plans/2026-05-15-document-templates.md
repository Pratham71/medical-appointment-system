# Document Templates Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add print-ready Medical Report and Medical Certificate full-page routes to the student portal, replacing the current basic modal/text-download pattern.

**Architecture:** Two shell-less Next.js routes (`/students/reports/[id]` and `/students/certificates/[id]`) each render an A4-sized document using Tailwind + inline styles. Shell-less layouts override the parent `DashboardShell`. Auto-print fires via `?print=1` query param. The existing reports list page is simplified to navigate to these routes instead of managing modals.

**Tech Stack:** Next.js 14 App Router, React 18, Tailwind CSS v3 (with `print:` variants), TypeScript 5. No new dependencies needed.

---

## File Map

| Action | File | Responsibility |
|---|---|---|
| Create | `app/frontend/app/students/reports/[id]/page.tsx` | Medical Report + Prescription A4 template |
| Create | `app/frontend/app/students/certificates/[id]/page.tsx` | Medical Certificate A4 template |
| Modify | `app/frontend/app/students/reports/page.tsx` | Replace modal/download logic with route navigation |

> **Note:** No layout files are needed. `app/frontend/app/students/layout.tsx` already passes children through unchanged — `DashboardShell` is used at the page level, not the layout. Document pages that don't call `DashboardShell` are automatically shell-less.

---

## Task 1: Generate Stitch screens for visual reference

*These screens are design artifacts generated via Stitch MCP — they inform the implementation but are not code tasks.*

**Files:** none (Stitch project `4103054473902940983`)

- [ ] **Step 1: Generate Medical Report screen in Stitch**

Use `mcp__stitch__generate_screen_from_text` with project `4103054473902940983`:

```
Title: Medical Report — Document Template

A print-ready A4 portrait document for College Infirmary. White page background, 32px outer margin.

HEADER: 4px teal-600 (#0D9488) left border strip. Left side: "College Infirmary" in 11px uppercase muted label, below it "Medical Report" in 24px semibold slate-900 title. Right side: "Report #1042" and "Issued 15 May 2026" in 12px JetBrains Mono muted text.

METADATA GRID: 2-column grid in a raised block (#F8FAFB background, 1px #E2E8F0 border, 8px radius, 16px padding). Left column: "PATIENT" label in 11px uppercase muted, below "Aisha Kumar" in 14px medium slate-900, below "ID: 21" in 12px JetBrains Mono muted. Right column: "APPOINTMENT" label in 11px uppercase muted, below "12 May 2026" in 14px slate-900, below "09:00 – 09:30" in 12px muted, below "Dr. Ramesh Iyer" in 12px muted.

DIAGNOSIS SECTION: "DIAGNOSIS" in 12px uppercase semibold teal-700 label. Below: "Patient presents with acute pharyngitis and mild fever (101°F). No bacterial infection detected on rapid strep test." in 14px slate-800.

REMARKS SECTION: "REMARKS" in 12px uppercase semibold teal-700 label. Below: "Advised rest for 2 days, increased fluid intake, and saltwater gargling. Return if symptoms persist beyond 5 days." in 14px slate-800.

PRESCRIPTION TABLE: "PRESCRIPTION" label same style as above. Below: a full-width table. Header row in teal-600 background with white text: "Medicine" and "Dosage" columns. Body rows alternating white and #F8FAFB. Row 1: "Paracetamol 500mg" / "1 tablet every 6 hours". Row 2: "Cetirizine 10mg" / "1 tablet at night". Thin 1px #E2E8F0 borders between rows.

FOOTER: Top 1px #E2E8F0 border. Left: "Dr. Ramesh Iyer" in 14px medium slate-900, below "College Infirmary" in 12px muted. Right: a 192px wide signature line (bottom border) with "Signature" in 11px muted below it.
```

- [ ] **Step 2: Generate Medical Certificate screen in Stitch**

Use `mcp__stitch__generate_screen_from_text` with project `4103054473902940983`:

```
Title: Medical Certificate — Document Template

A formal print-ready A4 portrait certificate for College Infirmary. White background, 32px margin.

HEADER: 4px teal-600 left border strip. Left side: "College Infirmary" in 11px uppercase muted label, below "Medical Leave Certificate" in 24px semibold slate-900. Right side: "Certificate #88" and "Issued 15 May 2026" in 12px JetBrains Mono muted.

FORMAL STATEMENT: "This certifies that the following student was examined at the College Infirmary and this Medical Leave Certificate was issued on 15 May 2026." in 14px slate-800, normal line height 1.6.

PATIENT DETAILS BLOCK: Raised block (#F8FAFB background, 1px #E2E8F0 border, 8px radius, 20px padding). Label "PATIENT DETAILS" in 11px uppercase muted. 2×2 grid: "Full Name" / "Aisha Kumar" (medium), "Student ID" / "21" (JetBrains Mono), "Appointment Date" / "12 May 2026", "Issuing Doctor" / "Dr. Ramesh Iyer".

SEAL AREA: A 112px tall dashed border box (2px dashed #E2E8F0, 8px radius). Centered text "OFFICIAL SEAL" in 11px uppercase letter-spaced #D1D5DB.

FOOTER: Top 1px border. Left: "Dr. Ramesh Iyer" in 14px medium slate-900, below "College Infirmary" in 12px muted. Right: 192px signature line + "Signature" label.
```

---

## Task 2: Medical Report page

**Files:**
- Create: `app/frontend/app/students/reports/[id]/page.tsx`

- [ ] **Step 1: Create the report page**

Create `app/frontend/app/students/reports/[id]/page.tsx`:

```tsx
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
```

- [ ] **Step 2: Verify the file was created**

Run:
```powershell
Test-Path "app/frontend/app/students/reports/[id]/page.tsx"
```

Expected: `True`

- [ ] **Step 3: Commit**

```bash
git add app/frontend/app/students/reports/
git commit -m "feat: add medical report document template page"
```

---

## Task 3: Medical Certificate page

**Files:**
- Create: `app/frontend/app/students/certificates/[id]/page.tsx`

- [ ] **Step 1: Create the certificate page**

Create `app/frontend/app/students/certificates/[id]/page.tsx`:

```tsx
"use client";
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

export default function CertificateDocumentPage() {
  const params = useParams();
  const router = useRouter();
  const searchParams = useSearchParams();
  const id = Number(params.id);
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
      return;
    }
    setUser(storedUser);
    getStudentCertificates()
      .then((certs) => {
        const found = certs.find((c) => c.certificate_id === id) ?? null;
        if (!found) setError("Certificate not found");
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
      <div className="flex min-h-screen items-center justify-center bg-gray-100">
        <p className="text-sm text-red-600">
          {error || "Certificate not found"}
        </p>
      </div>
    );
  }

  const issueDate = fmtDate(certificate.issue_date);

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

          {/* Formal statement */}
          <div className="mb-8">
            <p className="text-sm leading-relaxed text-gray-800">
              This certifies that the following student was examined at the
              College Infirmary and this{" "}
              <strong>{certificate.certificate_type}</strong> was issued on{" "}
              <strong>{issueDate}</strong>.
            </p>
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
```

- [ ] **Step 2: Verify the file was created**

Run:
```powershell
Test-Path "app/frontend/app/students/certificates/[id]/page.tsx"
```

Expected: `True`

- [ ] **Step 3: Commit**

```bash
git add app/frontend/app/students/certificates/
git commit -m "feat: add medical certificate document template page"
```

---

## Task 4: Simplify reports list page

Replace modal/text-download logic with route navigation. The new page is much simpler — no modals, no state for selected items, no download functions.

**Files:**
- Modify: `app/frontend/app/students/reports/page.tsx`

- [ ] **Step 1: Replace the entire file**

Overwrite `app/frontend/app/students/reports/page.tsx` with:

```tsx
"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  getStudentCertificates,
  getStudentReports,
  getStoredUser,
} from "@/lib/api";
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

export default function ReportsPage() {
  const router = useRouter();
  const [tab, setTab] = useState<Tab>("reports");
  const [reports, setReports] = useState<StudentReportSummary[]>([]);
  const [certs, setCerts] = useState<StudentCertificateSummary[]>([]);
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

  return (
    <DashboardShell role="student" title="Reports & Certificates">
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
                  Dr. {report.doctor_name}
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
                  Dr. {certificate.doctor_name}
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
```

- [ ] **Step 2: Commit**

```bash
git add app/frontend/app/students/reports/page.tsx
git commit -m "feat: replace report/certificate modals with document template routes"
```

---

## Task 5: End-to-end verification

- [ ] **Step 1: Start both servers**

Terminal 1 (backend):
```bash
cd app/backend
uv run uvicorn app.backend.app.main:app --reload
```

Terminal 2 (frontend):
```bash
cd app/frontend
npm run dev
```

- [ ] **Step 2: Log in as a student and navigate to Reports & Certificates**

Open `http://localhost:3000/login` and sign in with a student account (see seed data for credentials).

Navigate to **Reports & Certificates** in the sidebar.

- [ ] **Step 3: Test the View flow**

Click **View** on a report row. Expected:
- Browser navigates to `/students/reports/[id]`
- Page renders without sidebar/header (just the A4 document)
- Patient name, appointment date, diagnosis/remarks visible
- "Print / Save as PDF" button visible top-right
- "← Back" button returns to the list

- [ ] **Step 4: Test the Download flow**

Click **Download** on a report row. Expected:
- Browser navigates to `/students/reports/[id]?print=1`
- Document renders, then browser print dialog opens automatically

- [ ] **Step 5: Test certificates**

Switch to the **Certificates** tab. Click **View** on a certificate row. Expected:
- Browser navigates to `/students/certificates/[id]`
- Student name and ID from session visible in Patient Details block
- Formal statement paragraph shows the certificate type and issue date
- "Official Seal" dashed box visible

- [ ] **Step 6: Verify TypeScript compiles**

```bash
cd app/frontend
npx tsc --noEmit
```

Expected: no errors
