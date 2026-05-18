"use client";
import { useEffect, useState, useCallback } from "react";
import Select from "@/components/ui/Select";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import {
  activateUser,
  assignUserRole,
  deactivateUser,
  getAdminUsers,
  getStoredUser,
} from "@/lib/api";
import type {
  AdminUserSummary,
  AdminRoleAssignmentRequest,
  AdminRoleAssignmentResponse,
  AssignableRole,
} from "@/lib/types";
import DashboardShell from "@/components/layout/DashboardShell";
import ToastContainer, { useToast } from "@/components/ui/Toast";

const ROLE_BADGE: Record<string, string> = {
  student: "bg-blue-50 text-blue-700 ring-1 ring-blue-200",
  professor: "bg-purple-50 text-purple-700 ring-1 ring-purple-200",
  "college-staff": "bg-cyan-50 text-cyan-700 ring-1 ring-cyan-200",
  "hostel-staff": "bg-indigo-50 text-indigo-700 ring-1 ring-indigo-200",
  doctor: "bg-teal-50 text-teal-700 ring-1 ring-teal-200",
  staff: "bg-slate-100 text-slate-600 ring-1 ring-slate-200",
  admin: "bg-amber-50 text-amber-700 ring-1 ring-amber-200",
};

const ROLES: AssignableRole[] = [
  "student", "professor", "college-staff", "hostel-staff", "doctor", "staff", "admin",
];

interface RoleForm {
  role_name: AssignableRole;
  roll_number: string;
  department: string;
  year_level: string;
  employee_number: string;
  specialization: string;
}

function RoleAssignModal({
  user,
  onClose,
  onSuccess,
}: {
  user: AdminUserSummary;
  onClose: () => void;
  onSuccess: (res: AdminRoleAssignmentResponse) => void;
}) {
  const [form, setForm] = useState<RoleForm>({
    role_name: (ROLES.includes(user.role_name as AssignableRole) ? user.role_name : "student") as AssignableRole,
    roll_number: "",
    department: "",
    year_level: "",
    employee_number: "",
    specialization: "",
  });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  const needsAcademic =
    form.role_name === "student" || form.role_name === "professor" ||
    form.role_name === "college-staff" || form.role_name === "hostel-staff";
  const needsEmployee = form.role_name === "doctor" || form.role_name === "staff";

  async function handleSubmit() {
    setError("");
    setSaving(true);
    try {
      const payload: AdminRoleAssignmentRequest = { role_name: form.role_name };
      if (needsAcademic) {
        payload.roll_number = form.roll_number;
        payload.department = form.department;
        payload.year_level = parseInt(form.year_level, 10);
      }
      if (needsEmployee) {
        payload.employee_number = form.employee_number;
        if (form.specialization) payload.specialization = form.specialization;
      }
      const res = await assignUserRole(user.user_id, payload);
      onSuccess(res);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to assign role");
    } finally {
      setSaving(false);
    }
  }

  const field = (label: string, key: keyof RoleForm, placeholder: string, type = "text") => (
    <div>
      <label className="block text-xs font-medium text-brand-muted mb-1">{label}</label>
      <input
        type={type}
        value={form[key]}
        onChange={(e) => setForm({ ...form, [key]: e.target.value })}
        placeholder={placeholder}
        className="w-full border border-brand-border rounded-btn px-3 py-2 text-sm text-brand-text focus:outline-none focus:ring-2 focus:ring-teal-500"
      />
    </div>
  );

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 z-50 flex items-end sm:items-center justify-center"
    >
      <div className="absolute inset-0 bg-black/30" onClick={onClose} />
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: 20 }}
        transition={{ duration: 0.2, ease: "easeOut" }}
        className="relative bg-white rounded-t-2xl sm:rounded-card shadow-xl p-6 w-full sm:max-w-md sm:mx-4 border border-brand-border max-h-[90vh] overflow-y-auto"
      >
        <h3 className="text-base font-semibold text-brand-text">Assign Role</h3>
        <p className="mt-1 text-sm text-brand-muted">{user.name} · {user.email}</p>

        {error && <p className="mt-3 text-sm text-red-600">{error}</p>}

        <div className="mt-4 space-y-3">
          <div>
            <label className="block text-xs font-medium text-brand-muted mb-1">Role</label>
            <Select value={form.role_name} onChange={(e) => setForm({ ...form, role_name: e.target.value as AssignableRole })}>
              {ROLES.map((r) => (
                <option key={r} value={r}>{r.charAt(0).toUpperCase() + r.slice(1)}</option>
              ))}
            </Select>
          </div>
          {needsAcademic && (
            <>
              {field("Roll Number", "roll_number", "e.g. 2021A7PS123P")}
              {field("Department", "department", "e.g. Computer Science")}
              <div>
                <label className="block text-xs font-medium text-brand-muted mb-1">Year Level</label>
                <Select value={form.year_level} onChange={(e) => setForm({ ...form, year_level: e.target.value })}>
                  <option value="">Select year</option>
                  {[1, 2, 3, 4, 5, 6].map((y) => (
                    <option key={y} value={y}>Year {y}</option>
                  ))}
                </Select>
              </div>
            </>
          )}
          {needsEmployee && (
            <>
              {field("Employee Number", "employee_number", "e.g. EMP001")}
              {field("Specialization (optional)", "specialization", "e.g. General Medicine")}
            </>
          )}
        </div>

        <div className="mt-5 flex gap-3 justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm rounded-btn border border-brand-border text-brand-muted hover:bg-brand-raised transition"
          >
            Cancel
          </button>
          <button
            onClick={handleSubmit}
            disabled={saving}
            className="px-4 py-2 text-sm rounded-btn bg-teal-600 hover:bg-teal-700 text-white font-medium transition disabled:opacity-50"
          >
            {saving ? "Saving…" : "Assign Role"}
          </button>
        </div>
      </motion.div>
    </motion.div>
  );
}

export default function AdminUsersPage() {
  const router = useRouter();
  const { toasts, show, dismiss } = useToast();
  const [users, setUsers] = useState<AdminUserSummary[]>([]);
  const [query, setQuery] = useState("");
  const [roleFilter, setRoleFilter] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [selected, setSelected] = useState<AdminUserSummary | null>(null);
  const [confirmTarget, setConfirmTarget] = useState<AdminUserSummary | null>(null);

  const fetchUsers = useCallback((q: string, role: string) => {
    setLoading(true);
    setError("");
    getAdminUsers(q || undefined, role || undefined)
      .then(setUsers)
      .catch((e: unknown) => setError(e instanceof Error ? e.message : "Failed to load"))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    const user = getStoredUser();
    if (!user) { router.replace("/login"); return; }
    if (user.role_name !== "admin") { router.replace("/login"); return; }
    fetchUsers("", "");
  }, [router, fetchUsers]);

  function handleSearch() { fetchUsers(query, roleFilter); }

  function handleRoleSuccess(res: AdminRoleAssignmentResponse) {
    setSelected(null);
    show(`${res.name} is now ${res.role_name}`, "success");
    fetchUsers(query, roleFilter);
  }

  async function handleToggleActive(user: AdminUserSummary) {
    if (!user.is_active) {
      try {
        const res = await activateUser(user.user_id);
        show(res.message, "success");
        fetchUsers(query, roleFilter);
      } catch (e: unknown) {
        show(e instanceof Error ? e.message : "Failed to activate user", "warning");
      }
      return;
    }
    setConfirmTarget(user);
  }

  async function handleConfirmDeactivate() {
    if (!confirmTarget) return;
    setConfirmTarget(null);
    try {
      const res = await deactivateUser(confirmTarget.user_id);
      show(res.message, "success");
      fetchUsers(query, roleFilter);
    } catch (e: unknown) {
      show(e instanceof Error ? e.message : "Failed to deactivate user", "warning");
    }
  }

  return (
    <DashboardShell role="admin" title="Users">
      <AnimatePresence>
        {confirmTarget && (
          <motion.div
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 flex items-end sm:items-center justify-center px-4"
          >
            <div className="absolute inset-0 bg-black/40" onClick={() => setConfirmTarget(null)} />
            <motion.div
              initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: 20 }}
              transition={{ duration: 0.18, ease: "easeOut" }}
              className="relative w-full sm:max-w-sm rounded-t-2xl sm:rounded-card bg-white shadow-xl border border-brand-border p-6"
            >
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-full bg-red-50 flex items-center justify-center flex-shrink-0">
                  <svg className="w-5 h-5 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636" />
                  </svg>
                </div>
                <div>
                  <h3 className="text-sm font-semibold text-brand-text">Deactivate user</h3>
                  <p className="text-xs text-brand-muted mt-0.5">This will block their login immediately</p>
                </div>
              </div>
              <p className="text-sm text-brand-text mb-1">
                Are you sure you want to deactivate <span className="font-semibold">{confirmTarget.name}</span>?
              </p>
              <p className="text-xs text-brand-muted mb-5">
                {confirmTarget.email} · <span className="capitalize">{confirmTarget.role_name}</span>
              </p>
              <div className="flex gap-3">
                <button
                  onClick={() => setConfirmTarget(null)}
                  className="flex-1 px-4 py-2 text-sm rounded-btn border border-brand-border text-brand-muted hover:bg-brand-raised transition"
                >
                  Cancel
                </button>
                <button
                  onClick={handleConfirmDeactivate}
                  className="flex-1 px-4 py-2 text-sm rounded-btn bg-red-500 hover:bg-red-600 text-white font-medium transition"
                >
                  Deactivate
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      <div className="space-y-4">
        {/* Search bar */}
        <div className="bg-white rounded-card border border-brand-border shadow-card p-4 flex flex-wrap gap-3 items-center">
          <input
            type="text"
            placeholder="Search by name or email…"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSearch()}
            className="flex-1 min-w-[160px] border border-brand-border rounded-btn px-3 py-2 text-sm text-brand-text focus:outline-none focus:ring-2 focus:ring-teal-500"
          />
          <Select value={roleFilter} onChange={(e) => setRoleFilter(e.target.value)}>
            <option value="">All roles</option>
            {ROLES.map((r) => (
              <option key={r} value={r}>{r.charAt(0).toUpperCase() + r.slice(1)}</option>
            ))}
          </Select>
          <button
            onClick={handleSearch}
            className="px-4 py-2 text-sm bg-teal-600 hover:bg-teal-700 text-white rounded-btn font-medium transition"
          >
            Search
          </button>
        </div>

        {/* Table / Cards */}
        <div className="bg-white rounded-card border border-brand-border shadow-card">
          {error && (
            <div className="px-5 py-4 text-sm text-red-600 bg-red-50 border-b border-brand-border">{error}</div>
          )}

          {loading && (
            <div className="px-5 py-8 text-center text-brand-muted text-sm animate-pulse">Loading…</div>
          )}

          {!loading && users.length === 0 && !error && (
            <div className="px-5 py-8 text-center text-brand-muted text-sm">No users found</div>
          )}

          {!loading && users.length > 0 && (
            <>
              {/* Desktop table */}
              <div className="hidden md:block overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-brand-border bg-brand-bg">
                      <th className="text-left px-5 py-3 text-xs font-medium text-brand-muted">Name</th>
                      <th className="text-left px-5 py-3 text-xs font-medium text-brand-muted">Email</th>
                      <th className="text-left px-5 py-3 text-xs font-medium text-brand-muted">Role</th>
                      <th className="text-left px-5 py-3 text-xs font-medium text-brand-muted">ID</th>
                      <th className="text-left px-5 py-3 text-xs font-medium text-brand-muted">Active</th>
                      <th className="text-left px-5 py-3 text-xs font-medium text-brand-muted">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-brand-border">
                    {users.map((u) => (
                      <tr key={u.user_id} className="hover:bg-brand-raised transition-colors">
                        <td className="px-5 py-3 font-medium text-brand-text">{u.name}</td>
                        <td className="px-5 py-3 text-brand-muted">{u.email}</td>
                        <td className="px-5 py-3">
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${ROLE_BADGE[u.role_name] ?? ROLE_BADGE.staff}`}>
                            {u.role_name.charAt(0).toUpperCase() + u.role_name.slice(1)}
                          </span>
                        </td>
                        <td className="px-5 py-3 text-brand-muted text-xs">{u.student_id ?? u.staff_id ?? "—"}</td>
                        <td className="px-5 py-3">
                          <span className={`inline-flex items-center gap-1.5 text-xs font-medium ${u.is_active ? "text-emerald-600" : "text-slate-400"}`}>
                            <span className={`w-1.5 h-1.5 rounded-full ${u.is_active ? "bg-emerald-500" : "bg-slate-300"}`} />
                            {u.is_active ? "Active" : "Inactive"}
                          </span>
                        </td>
                        <td className="px-5 py-3">
                          <div className="flex flex-wrap gap-2">
                            {u.role_name === "admin" ? (
                              <span className="text-xs text-brand-muted border border-brand-border px-2.5 py-1 rounded-btn opacity-40 cursor-not-allowed select-none">
                                Protected
                              </span>
                            ) : (
                              <>
                                <button
                                  onClick={() => setSelected(u)}
                                  className="text-xs text-teal-600 hover:text-teal-700 border border-teal-200 hover:border-teal-300 px-2.5 py-1 rounded-btn transition-colors font-medium"
                                >
                                  Change Role
                                </button>
                                <button
                                  onClick={() => handleToggleActive(u)}
                                  aria-label={u.is_active ? "Remove user" : "Activate user"}
                                  className={`text-xs border px-2.5 py-1 rounded-btn transition-colors font-medium ${
                                    u.is_active
                                      ? "text-red-600 hover:text-red-700 border-red-200 hover:border-red-300"
                                      : "text-emerald-600 hover:text-emerald-700 border-emerald-200 hover:border-emerald-300"
                                  }`}
                                >
                                  {u.is_active ? "Deactivate" : "Activate"}
                                </button>
                              </>
                            )}
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Mobile cards */}
              <div className="md:hidden divide-y divide-brand-border">
                {users.map((u) => (
                  <div key={u.user_id} className="p-4">
                    <div className="flex items-start justify-between gap-3">
                      <div className="min-w-0">
                        <p className="font-medium text-brand-text">{u.name}</p>
                        <p className="text-xs text-brand-muted mt-0.5">{u.email}</p>
                        {(u.student_id ?? u.staff_id) && (
                          <p className="text-xs text-brand-muted font-mono mt-0.5">{u.student_id ?? u.staff_id}</p>
                        )}
                      </div>
                      <div className="flex flex-col items-end gap-1.5 flex-shrink-0">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${ROLE_BADGE[u.role_name] ?? ROLE_BADGE.staff}`}>
                          {u.role_name.charAt(0).toUpperCase() + u.role_name.slice(1)}
                        </span>
                        <span className={`inline-flex items-center gap-1 text-xs font-medium ${u.is_active ? "text-emerald-600" : "text-slate-400"}`}>
                          <span className={`w-1.5 h-1.5 rounded-full ${u.is_active ? "bg-emerald-500" : "bg-slate-300"}`} />
                          {u.is_active ? "Active" : "Inactive"}
                        </span>
                      </div>
                    </div>
                    {u.role_name !== "admin" && (
                      <div className="mt-3 flex gap-2">
                        <button
                          onClick={() => setSelected(u)}
                          className="text-xs text-teal-600 hover:text-teal-700 border border-teal-200 hover:border-teal-300 px-2.5 py-1.5 rounded-btn transition-colors font-medium"
                        >
                          Change Role
                        </button>
                        <button
                          onClick={() => handleToggleActive(u)}
                          aria-label={u.is_active ? "Remove user" : "Activate user"}
                          className={`text-xs border px-2.5 py-1.5 rounded-btn transition-colors font-medium ${
                            u.is_active
                              ? "text-red-600 hover:text-red-700 border-red-200 hover:border-red-300"
                              : "text-emerald-600 hover:text-emerald-700 border-emerald-200 hover:border-emerald-300"
                          }`}
                        >
                          {u.is_active ? "Deactivate" : "Activate"}
                        </button>
                      </div>
                    )}
                    {u.role_name === "admin" && (
                      <p className="mt-2 text-xs text-brand-muted opacity-60">Protected — cannot be modified</p>
                    )}
                  </div>
                ))}
              </div>
            </>
          )}

          {!loading && (
            <div className="px-5 py-3 border-t border-brand-border text-xs text-brand-muted">
              {users.length} user{users.length !== 1 ? "s" : ""}
            </div>
          )}
        </div>
      </div>

      <AnimatePresence>
        {selected && (
          <RoleAssignModal user={selected} onClose={() => setSelected(null)} onSuccess={handleRoleSuccess} />
        )}
      </AnimatePresence>

      <ToastContainer toasts={toasts} onDismiss={dismiss} />
    </DashboardShell>
  );
}
