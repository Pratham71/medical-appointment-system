"use client";
import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import {
  getDoctorAppointmentDetail,
  getReportDetail,
  saveNotes,
  savePrescription,
  issueCertificate,
  completeAppointment,
  getStoredUser,
} from "@/lib/api";
import type { DoctorAppointmentDetail } from "@/lib/types";
import DashboardShell from "@/components/layout/DashboardShell";
import StatusBadge from "@/components/ui/StatusBadge";

type Tab = "notes" | "prescription" | "certificate";

interface PrescriptionRow {
  medicine_name: string;
  dosage: string;
}

function fmtDate(d: string) {
  return new Date(d).toLocaleDateString("en-IN", { day: "numeric", month: "long", year: "numeric" });
}

export default function AppointmentDetailPage() {
  const params = useParams();
  const router = useRouter();
  const id = Number(params.id);

  const [detail, setDetail] = useState<DoctorAppointmentDetail | null>(null);
  const [tab, setTab] = useState<Tab>("notes");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);
  const [successMsg, setSuccessMsg] = useState("");

  // Notes state
  const [diagnosis, setDiagnosis] = useState("");
  const [remarks, setRemarks] = useState("");

  // Prescription state
  const [prescRows, setPrescRows] = useState<PrescriptionRow[]>([{ medicine_name: "", dosage: "" }]);

  // Certificate state
  const [certTypeId, setCertTypeId] = useState("1");

  useEffect(() => {
    const user = getStoredUser();
    if (!user) { router.replace("/login"); return; }
    Promise.all([getDoctorAppointmentDetail(id), getReportDetail(id)])
      .then(([d, report]) => {
        setDetail(d);
        const note = report.note;
        if (note?.diagnosis ?? d.diagnosis) {
          setDiagnosis(note?.diagnosis ?? d.diagnosis ?? "");
        }
        if (note?.remarks ?? d.remarks) {
          setRemarks(note?.remarks ?? d.remarks ?? "");
        }
        if (report.prescription?.items.length) {
          setPrescRows(
            report.prescription.items.map((item) => ({
              medicine_name: item.medicine_name,
              dosage: item.dosage,
            }))
          );
        }
      })
      .catch((e: unknown) => setError(e instanceof Error ? e.message : "Failed to load"))
      .finally(() => setLoading(false));
  }, [id, router]);

  const handleSaveNotes = async () => {
    if (!diagnosis.trim()) return;
    setSaving(true);
    setError("");
    try {
      await saveNotes(id, diagnosis, remarks);
      setSuccessMsg("Notes saved.");
      setTimeout(() => setSuccessMsg(""), 3000);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Save failed");
    } finally {
      setSaving(false);
    }
  };

  const handleSavePrescription = async () => {
    const valid = prescRows.filter((r) => r.medicine_name.trim() && r.dosage.trim());
    if (!valid.length) return;
    setSaving(true);
    setError("");
    try {
      await savePrescription(id, valid);
      setSuccessMsg("Prescription saved.");
      setTimeout(() => setSuccessMsg(""), 3000);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Save failed");
    } finally {
      setSaving(false);
    }
  };

  const handleIssueCert = async () => {
    setSaving(true);
    setError("");
    try {
      await issueCertificate(id, Number(certTypeId));
      setSuccessMsg("Certificate issued.");
      setTimeout(() => setSuccessMsg(""), 3000);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Issue failed");
    } finally {
      setSaving(false);
    }
  };

  const handleComplete = async () => {
    setSaving(true);
    try {
      await completeAppointment(id);
      router.push("/doctors/appointments");
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to mark complete");
      setSaving(false);
    }
  };

  const tabs: { key: Tab; label: string }[] = [
    { key: "notes", label: "Notes" },
    { key: "prescription", label: "Prescription" },
    { key: "certificate", label: "Certificate" },
  ];

  return (
    <DashboardShell role="doctor" title="Appointment Detail">
      <div className="mb-4">
        <button
          onClick={() => router.push("/doctors/appointments")}
          className="text-sm text-brand-muted hover:text-brand-text flex items-center gap-1 transition-colors"
        >
          ← Appointments
        </button>
      </div>

      {loading && <p className="text-brand-muted text-sm animate-pulse">Loading…</p>}

      {error && (
        <div className="bg-red-50 border border-red-100 text-red-600 text-sm rounded-card px-4 py-3 mb-5">{error}</div>
      )}

      {successMsg && (
        <div className="bg-emerald-50 border border-emerald-100 text-emerald-700 text-sm rounded-card px-4 py-3 mb-5">{successMsg}</div>
      )}

      {detail && (
        <div className="space-y-5">
          {/* Patient info card */}
          <div className="bg-white rounded-card border-l-4 border-teal-600 border-t border-r border-b border-brand-border shadow-card p-5">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-full bg-teal-600 flex items-center justify-center text-white font-semibold text-base flex-shrink-0">
                {detail.student_name.split(" ").slice(0, 2).map((w) => w[0]).join("")}
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-3 flex-wrap">
                  <h2 className="text-base font-semibold text-brand-text">{detail.student_name}</h2>
                  <StatusBadge status={detail.status} />
                </div>
                <p className="text-xs font-mono text-brand-muted mt-0.5">
                  ID: {detail.student_id} · {detail.student_email}
                </p>
              </div>
              <div className="text-right text-sm text-brand-muted flex-shrink-0">
                <p>{fmtDate(detail.slot_date)}</p>
                <p className="font-mono text-xs mt-0.5">
                  {detail.start_time.slice(0, 5)} – {detail.end_time.slice(0, 5)}
                </p>
              </div>
            </div>
          </div>

          {/* Tabs */}
          <div className="bg-white rounded-card border border-brand-border shadow-card overflow-hidden">
            <div className="flex border-b border-brand-border">
              {tabs.map((t) => (
                <button
                  key={t.key}
                  onClick={() => setTab(t.key)}
                  className={`px-5 py-3 text-sm font-medium border-b-2 -mb-px transition-colors ${
                    tab === t.key
                      ? "border-teal-600 text-teal-700"
                      : "border-transparent text-brand-muted hover:text-brand-text"
                  }`}
                >
                  {t.label}
                </button>
              ))}
            </div>

            <div className="p-5">
              {/* Notes */}
              {tab === "notes" && (
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-brand-text mb-1.5">
                      Diagnosis <span className="text-red-500">*</span>
                    </label>
                    <textarea
                      value={diagnosis}
                      onChange={(e) => setDiagnosis(e.target.value)}
                      rows={3}
                      maxLength={255}
                      placeholder="Primary diagnosis…"
                      className="w-full border border-brand-border rounded-btn px-3 py-2 text-sm text-brand-text placeholder:text-brand-muted focus:ring-2 focus:ring-teal-600 focus:ring-offset-1 focus:outline-none resize-none transition"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-brand-text mb-1.5">
                      Clinical Remarks <span className="text-brand-muted font-normal">(optional)</span>
                    </label>
                    <textarea
                      value={remarks}
                      onChange={(e) => setRemarks(e.target.value)}
                      rows={4}
                      maxLength={1000}
                      placeholder="Additional notes, observations…"
                      className="w-full border border-brand-border rounded-btn px-3 py-2 text-sm text-brand-text placeholder:text-brand-muted focus:ring-2 focus:ring-teal-600 focus:ring-offset-1 focus:outline-none resize-none transition"
                    />
                  </div>
                  <button
                    onClick={handleSaveNotes}
                    disabled={saving || !diagnosis.trim()}
                    className="bg-teal-600 hover:bg-teal-700 disabled:opacity-50 text-white text-sm font-medium px-5 py-2.5 rounded-btn transition-colors"
                  >
                    {saving ? "Saving…" : "Save Notes"}
                  </button>
                </div>
              )}

              {/* Prescription */}
              {tab === "prescription" && (
                <div className="space-y-4">
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="border-b border-brand-border">
                          <th className="text-left py-2 pr-3 text-xs font-semibold text-brand-muted uppercase tracking-wide">Medicine</th>
                          <th className="text-left py-2 pr-3 text-xs font-semibold text-brand-muted uppercase tracking-wide">Dose</th>
                          <th className="py-2 w-8"></th>
                        </tr>
                      </thead>
                      <tbody>
                        {prescRows.map((row, i) => (
                          <tr key={i}>
                            <td className="py-1.5 pr-3">
                              <input
                                value={row.medicine_name}
                                onChange={(e) => setPrescRows((p) => p.map((r, j) => j === i ? { ...r, medicine_name: e.target.value } : r))}
                                placeholder="e.g. Paracetamol 500mg"
                                className="w-full border border-brand-border rounded px-2 py-1.5 text-sm focus:ring-2 focus:ring-teal-600 focus:ring-offset-0 focus:outline-none"
                              />
                            </td>
                            <td className="py-1.5 pr-3">
                              <input
                                value={row.dosage}
                                onChange={(e) => setPrescRows((p) => p.map((r, j) => j === i ? { ...r, dosage: e.target.value } : r))}
                                placeholder="e.g. 1 tablet twice daily"
                                className="w-full border border-brand-border rounded px-2 py-1.5 text-sm focus:ring-2 focus:ring-teal-600 focus:ring-offset-0 focus:outline-none"
                              />
                            </td>
                            <td className="py-1.5">
                              {prescRows.length > 1 && (
                                <button
                                  onClick={() => setPrescRows((p) => p.filter((_, j) => j !== i))}
                                  className="text-red-400 hover:text-red-600 transition-colors text-lg leading-none"
                                >
                                  ×
                                </button>
                              )}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                  <div className="flex items-center gap-4">
                    <button
                      onClick={() => setPrescRows((p) => [...p, { medicine_name: "", dosage: "" }])}
                      className="text-sm text-teal-600 hover:text-teal-700 transition-colors font-medium"
                    >
                      + Add Row
                    </button>
                    <button
                      onClick={handleSavePrescription}
                      disabled={saving}
                      className="bg-teal-600 hover:bg-teal-700 disabled:opacity-50 text-white text-sm font-medium px-5 py-2.5 rounded-btn transition-colors"
                    >
                      {saving ? "Saving…" : "Save Prescription"}
                    </button>
                  </div>
                </div>
              )}

              {/* Certificate */}
              {tab === "certificate" && (
                <div className="space-y-4 max-w-sm">
                  {detail.certificate_id ? (
                    <div className="bg-emerald-50 border border-emerald-200 rounded-card p-4 text-sm text-emerald-700">
                      Certificate already issued: <strong>{detail.certificate_type}</strong>
                    </div>
                  ) : (
                    <>
                      <div>
                        <label className="block text-sm font-medium text-brand-text mb-1.5">
                          Certificate Type
                        </label>
                        <select
                          value={certTypeId}
                          onChange={(e) => setCertTypeId(e.target.value)}
                          className="w-full border border-brand-border rounded-btn px-3 py-2.5 text-sm text-brand-text focus:ring-2 focus:ring-teal-600 focus:ring-offset-1 focus:outline-none"
                        >
                          <option value="1">Medical Certificate</option>
                          <option value="2">Fitness Certificate</option>
                          <option value="3">Sick Leave Certificate</option>
                        </select>
                      </div>
                      <button
                        onClick={handleIssueCert}
                        disabled={saving}
                        className="bg-teal-600 hover:bg-teal-700 disabled:opacity-50 text-white text-sm font-medium px-5 py-2.5 rounded-btn transition-colors"
                      >
                        {saving ? "Issuing…" : "Issue Certificate"}
                      </button>
                    </>
                  )}
                </div>
              )}
            </div>
          </div>

          {/* Mark Complete */}
          {detail.status.toLowerCase() !== "completed" && (
            <button
              onClick={handleComplete}
              disabled={saving}
              className="w-full bg-teal-600 hover:bg-teal-700 disabled:opacity-50 text-white font-medium py-3 rounded-btn text-sm transition-colors"
            >
              {saving ? "Processing…" : "Mark Appointment Complete"}
            </button>
          )}
        </div>
      )}
    </DashboardShell>
  );
}
