"use client";
import { useEffect, useState } from "react";
import { useRouter, usePathname } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { getStoredUser } from "@/lib/api";
import Sidebar from "./Sidebar";
import Header from "./Header";

interface Props {
  role: "student" | "doctor" | "admin" | "staff";
  title: string;
  children: React.ReactNode;
}

export default function DashboardShell({ role, title, children }: Props) {
  const router = useRouter();
  const pathname = usePathname();
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
        <AnimatePresence mode="wait">
          <motion.div
            key={pathname}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -6 }}
            transition={{ duration: 0.2, ease: "easeOut" }}
            className="p-6 max-w-[1200px]"
          >
            {children}
          </motion.div>
        </AnimatePresence>
      </main>
    </div>
  );
}
