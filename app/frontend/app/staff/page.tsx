"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { getStoredUser } from "@/lib/api";
import DashboardShell from "@/components/layout/DashboardShell";

export default function StaffDashboardPage() {
  const router = useRouter();

  useEffect(() => {
    const user = getStoredUser();
    if (!user) {
      router.replace("/login");
      return;
    }
    if (user.role_name === "student") {
      router.replace("/students");
      return;
    }
    if (user.role_name === "doctor") {
      router.replace("/doctors");
      return;
    }
    if (user.role_name === "admin") {
      router.replace("/admin");
      return;
    }
    if (user.role_name !== "staff") {
      router.replace("/login");
    }
  }, [router]);

  return (
    <DashboardShell role="staff" title="Staff Dashboard">
      <div className="rounded-card border border-brand-border bg-white p-6 shadow-card">
        <div className="max-w-xl">
          <p className="text-sm font-medium text-brand-text">Staff access is ready.</p>
          <p className="mt-2 text-sm text-brand-muted">
            Staff can sign in and land here while queue, walk-in, and front-desk workflows are finalized.
          </p>
        </div>
      </div>
    </DashboardShell>
  );
}
