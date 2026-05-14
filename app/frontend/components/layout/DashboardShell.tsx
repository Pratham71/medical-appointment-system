"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getStoredUser } from "@/lib/api";
import Sidebar from "./Sidebar";
import Header from "./Header";

interface Props {
  role: "student" | "doctor";
  title: string;
  children: React.ReactNode;
}

export default function DashboardShell({ role, title, children }: Props) {
  const router = useRouter();
  const [userName, setUserName] = useState("");

  useEffect(() => {
    const user = getStoredUser();
    if (!user) {
      router.replace("/login");
      return;
    }
    setUserName(user.name);
  }, [router]);

  return (
    <div className="min-h-screen bg-brand-bg">
      <Sidebar role={role} />
      <Header title={title} userName={userName} />
      <main className="ml-60 pt-14">
        <div className="p-6 max-w-[1200px]">{children}</div>
      </main>
    </div>
  );
}
