"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { getStoredUser } from "@/lib/api";
import DashboardShell from "@/components/layout/DashboardShell";

export default function AdminDashboardPage() {
  const router = useRouter();

  useEffect(() => {
    const user = getStoredUser();
    if (!user) { router.replace("/login"); return; }
    if (user.role_name === "student") { router.replace("/students"); return; }
    if (user.role_name === "doctor") { router.replace("/doctors"); return; }
    if (user.role_name !== "admin") { router.replace("/login"); return; }
  }, [router]);

  return (
    <DashboardShell role="admin" title="Admin Dashboard">
      <div className="bg-white rounded-card border border-brand-border shadow-card p-6">
        <div className="max-w-xl">
          <p className="text-sm font-medium text-brand-text">Admin dashboard is pending.</p>
          <p className="text-sm text-brand-muted mt-2">
            Backend admin access exists for protected records, but the admin UI still needs its own dashboard workflow.
          </p>
        </div>
      </div>
    </DashboardShell>
  );
}
