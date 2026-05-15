# Medical Document Template Design

Purpose: use this file as the design brief for creating report, prescription, and certificate templates in Stitch. These templates should match the current College Infirmary dashboard style while feeling print-ready and official.

## 1. Visual Theme and Atmosphere

The templates should feel clinical, official, and easy to verify. Use a clean document layout with restrained color, strong hierarchy, and enough whitespace for printed use. Avoid decorative layouts, marketing-style hero sections, oversized graphics, or playful visuals.

The design should look like a college infirmary record: formal, readable, and trustworthy.

## 2. Color Palette and Roles

- Clinical Teal (#0D9488): primary accent for headings, section markers, stamps, and key identifiers.
- Deep Teal (#0F766E): hover/strong accent color and official signature/stamp accent.
- Slate Ink (#0F172A): main text, document titles, patient names, and important fields.
- Muted Slate (#64748B): supporting labels, helper text, secondary metadata.
- Soft Border (#E2E8F0): table lines, dividers, field boxes, and document outlines.
- Page Background (#FFFFFF): printable document surface.
- Raised Section Background (#F8FAFB): subtle background for grouped metadata blocks.
- Alert Red (#EF4444): only for warnings, cancelled/invalid states, or critical notes.
- Success Green (#10B981): only for completed/fit/approved states.

## 3. Typography Rules

- Use Outfit or a similar clean sans-serif for all document text.
- Document title: 22-26px, semibold, Slate Ink.
- Section headings: 13-15px, semibold, uppercase optional, Clinical Teal or Slate Ink.
- Body text: 12-14px, regular, Slate Ink.
- Labels: 11-12px, medium, Muted Slate.
- IDs, dates, roll numbers, and appointment numbers may use a compact monospace style.
- Keep letter spacing at 0. Do not use decorative serif headings for medical content.

## 4. Shared Document Layout

- Paper format: A4 portrait.
- Outer margin: 24-32px.
- Header: college/infirmary name on the left, document type on the right or centered.
- Include a small official metadata row near the top: document number, issue date, appointment ID.
- Use clear boxed sections with 1px Soft Border and 8px or smaller corner radius.
- Prefer tables for structured medical data.
- Footer should include doctor name, registration/staff ID if available, signature line, and verification note.
- Leave space for seal/stamp and doctor signature.
- Templates must work both as web previews and printed/downloaded PDFs later.

## 5. Template: Medical Report

### Required Content

- Document title: Medical Report
- Report ID or appointment ID
- Issue date
- Patient name
- College ID / roll number
- Department and year, if available
- Appointment date and time
- Doctor name and specialization
- Diagnosis
- Clinical remarks
- Prescription summary, if present
- Follow-up advice, if present
- Doctor signature block

### Layout Direction

- Start with a compact patient and appointment information grid.
- Put diagnosis and remarks in full-width sections.
- Prescription summary should be a table with medicine, dosage, frequency, duration, and instructions when available.
- Use subdued borders and no heavy shadows for print cleanliness.

## 6. Template: Prescription

### Required Content

- Document title: Prescription
- Prescription ID or appointment ID
- Issue date
- Patient name and college ID / roll number
- Doctor name and specialization
- Diagnosis reference, if available
- Medicine table
- General instructions
- Follow-up date, if available
- Doctor signature block

### Medicine Table Columns

- Medicine name
- Dosage
- Frequency
- Duration
- Timing or instructions

### Layout Direction

- Medicine table should be the visual focus.
- Keep rows tall enough for printed readability.
- Use Clinical Teal only for the table header or left accent, not the whole page.

## 7. Template: Medical Certificate

### Required Content

- Document title based on certificate type.
- Certificate ID
- Issue date
- Patient name
- College ID / roll number
- Department and year, if available
- Appointment reference
- Doctor name and specialization
- Certificate reason or medical summary
- Validity or recommended date range where relevant
- Doctor signature block

### Certificate Types

- Medical Leave Certificate
- Fitness Certificate
- Visit/Attendance Certificate
- Other college infirmary certificate types added later

### Medical Leave Certificate Rules

Medical leave certificates must be more informative than a simple issue record.

- Include leave start date.
- Include leave end date.
- Include total leave duration in days.
- Support quick ranges such as 2-3 days and one week.
- Support a custom start/end date range.
- Include rest recommendation or restriction summary.
- Include return-to-class date when available.

### Layout Direction

- Use a formal certificate layout with stronger title hierarchy.
- Include a clear statement paragraph, for example: this certifies that the student was examined and advised medical leave from start date to end date.
- Put date range in a highlighted metadata block so it is easy for administration to verify.
- Keep enough blank space for official seal and signature.

## 8. Interaction Notes for App Integration

- Student preview modal should display the exact same hierarchy as the downloadable template.
- Download buttons should later produce PDF or print-ready output from these templates.
- Missing optional fields should be hidden instead of showing empty labels.
- Long diagnosis, remarks, and instruction text must wrap cleanly without overlapping.
- Templates should remain readable on mobile preview, but print layout is the priority.
