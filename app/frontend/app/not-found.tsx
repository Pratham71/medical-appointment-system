"use client";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";

export default function NotFound() {
  const router = useRouter();

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-[#F0F4F6] px-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.35, ease: "easeOut" }}
        className="text-center max-w-md"
      >
        <p className="font-['Newsreader'] text-8xl font-semibold text-teal-600 leading-none mb-6">
          404
        </p>
        <h1 className="font-['Outfit'] text-xl font-semibold text-slate-900 mb-2">
          Page not found
        </h1>
        <p className="font-['Outfit'] text-sm text-slate-500 mb-8">
          The page you&apos;re looking for doesn&apos;t exist or has been moved.
        </p>
        <div className="flex items-center justify-center gap-3">
          <button
            onClick={() => router.push("/students")}
            className="rounded-[6px] bg-teal-600 px-5 py-2.5 text-sm font-semibold text-white hover:bg-teal-700 transition-colors"
          >
            Go to Dashboard
          </button>
          <button
            onClick={() => router.back()}
            className="rounded-[6px] border border-slate-300 px-5 py-2.5 text-sm font-semibold text-slate-600 hover:bg-slate-50 transition-colors"
          >
            Go Back
          </button>
        </div>
      </motion.div>
      <p className="mt-16 font-['Outfit'] text-xs text-slate-400">
        College Infirmary · Medical Appointment System
      </p>
    </div>
  );
}
