"use client";
import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { getStoredUser } from "@/lib/api";

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
    } else {
      router.replace("/students");
    }
  }, [router]);

  return null;
}
