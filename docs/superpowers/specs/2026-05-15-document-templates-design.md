# Document Templates Design

**Date:** 2026-05-15
**Scope:** Medical Report, Prescription (embedded), and Medical Certificate print-ready templates for the College Infirmary student portal.

---

## Overview

Two new dedicated full-page print routes replace the existing basic modal views and plain-text downloads on the student Reports & Certificates page. Each route renders a clinical A4 document matching the app's teal/Outfit design system, with no dashboard chrome (sidebar/header stripped). The browser's native print dialog produces the PDF.

---

## Routing & Layout

| Route | Template | Data source |
|---|---|---|
| `/students/reports/[id]` | Medical Report + Prescription | `getReportDetail(appointment_id)` |
| `/students/certificates/[id]` | Medical Certificate | `getStudentCertificates()` filtered by `certificate_id` |

Both routes use a **shell-less layout** — `app/students/reports/[id]/layout.tsx` and `app/students/certificates/[id]/layout.tsx` each render only `{children}`, overriding the parent `students/layout.tsx` which injects `DashboardShell`.

The existing **"View"** button navigates to the route. The existing **"Download"** button navigates to the same URL with `?print=1` appended, which auto-fires `window.print()` after data loads. A visible "Print / Save as PDF" button also appears on screen (hidden via `@media print`) for manual use.

---

## Data Flow

### Medical Report page
- `id` URL param = `appointment_id`
- Calls `getReportDetail(id)` → `ReportDetail { appointment, note, prescription }`
- `note === null` → diagnosis and remarks sections show "Not recorded"
- `prescription.items.length === 0` → prescription table section is omitted entirely
- Auth guard: `useEffect` checks `getStoredUser()`; redirects to `/login` if absent

### Medical Certificate page
- `id` URL param = `certificate_id`
- Calls `getStudentCertificates()` → finds matching entry by `certificate_id`
- No dedicated single-certificate endpoint exists; client-side filter is acceptable (small list)
- Student name comes from `getStoredUser().name` (session); student ID from `getStoredUser().user_id`
- No roll number or department available in `StudentCertificateSummary` — display numeric student ID only
- Auth guard: same `useEffect` pattern

---

## Template Layouts

### Shared document conventions (DESIGN.md §2–4)
- White page background (`#FFFFFF`), 32px outer margin
- Teal left border strip on the document header (`#0D9488`)
- Body: Outfit 14px / Slate Ink `#0F172A`
- Labels: Outfit 12px / Muted Slate `#64748B`
- IDs, dates, roll numbers: JetBrains Mono 12px
- Section headings: 13px semibold uppercase, teal or slate
- Raised metadata block: `#F8FAFB` background, 1px `#E2E8F0` border, 8px radius
- Footer: doctor name + signature line + "College Infirmary" institution note

### Medical Report (`/students/reports/[id]`)

```
┌─────────────────────────────────────────────┐
│ [teal strip] College Infirmary  MEDICAL REPORT │  header row
│ Report #[appointment_id]  Issued [date]     │  mono IDs
├──────────────┬──────────────────────────────┤
│ Patient      │ Appointment                  │  2-col raised metadata grid
│ Name, ID     │ Date, Time, Doctor           │
├──────────────┴──────────────────────────────┤
│ DIAGNOSIS                                   │  teal section label
│ [diagnosis text or "Not recorded"]          │
├─────────────────────────────────────────────┤
│ REMARKS                                     │
│ [remarks text or "Not recorded"]            │
├─────────────────────────────────────────────┤  (omitted if no prescription)
│ PRESCRIPTION                                │
│ ┌──────────────┬────────┐                   │
│ │ Medicine     │ Dosage │  teal header row  │
│ ├──────────────┼────────┤                   │
│ │ [med name]   │ [dose] │                   │
│ └──────────────┴────────┘                   │
├─────────────────────────────────────────────┤
│ Dr. [name]     ________________________     │  footer + signature line
│ College Infirmary                           │
└─────────────────────────────────────────────┘
```

### Medical Certificate (`/students/certificates/[id]`)

```
┌─────────────────────────────────────────────┐
│ [teal strip] College Infirmary              │  header
│     [CERTIFICATE TYPE — large title]        │  22–24px semibold
│ Certificate #[id]   Issued [date]           │  mono
├─────────────────────────────────────────────┤
│ This certifies that the following student   │  formal statement paragraph
│ was examined at the College Infirmary and   │
│ this certificate was issued on [date].      │
├─────────────────────────────────────────────┤
│ Patient Details (raised block)              │
│ Name · College ID · Appointment Date        │
│ Issuing Doctor · Department                 │
├─────────────────────────────────────────────┤
│ [blank space — seal / official stamp]       │
│ Dr. [name]  ___________________________     │  footer + signature
│ College Infirmary                           │
└─────────────────────────────────────────────┘
```

---

## Print Behaviour

- `?print=1` query param → `useEffect` calls `window.print()` after data finishes loading
- `@media print` CSS: hide Print button, remove `box-shadow`, set `margin: 0`, ensure white background
- A4 page size enforced via `@page { size: A4 portrait; margin: 0; }` in a `<style>` tag on the document
- Missing optional fields are hidden, not shown as empty labels (DESIGN.md §8)

---

## Stitch Screens to Generate

1. **Medical Report template** — full A4 layout with sample data (diagnosis, remarks, prescription table)
2. **Medical Certificate template** — formal certificate layout with sample data

These inform the visual reference before Next.js implementation.

---

## Files to Create / Modify

| Action | File |
|---|---|
| Create | `app/frontend/app/students/reports/[id]/layout.tsx` |
| Create | `app/frontend/app/students/reports/[id]/page.tsx` |
| Create | `app/frontend/app/students/certificates/[id]/layout.tsx` |
| Create | `app/frontend/app/students/certificates/[id]/page.tsx` |
| Modify | `app/frontend/app/students/reports/page.tsx` — update View/Download button hrefs |
