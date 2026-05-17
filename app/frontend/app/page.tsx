"use client";
import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { getStoredUser } from "@/lib/api";

const PATIENT_ROLES = ["student", "professor", "college-staff", "hostel-staff"];

function isPatientRole(roleName: string) {
  return PATIENT_ROLES.includes(roleName);
}

export default function RootPage() {
  const router = useRouter();

  useEffect(() => {
    const user = getStoredUser();
    if (!user) {
      router.replace("/login");
    } else if (user.role_name === "doctor") {
      router.replace("/doctors");
    } else if (user.role_name === "admin") {
      router.replace("/admin");
    } else if (user.role_name === "staff") {
      router.replace("/staff");
    } else if (isPatientRole(user.role_name)) {
      router.replace("/students");
    } else {
      router.replace("/login");
    }
  }, [router]);

  return null;
}
