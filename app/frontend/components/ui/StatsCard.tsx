"use client";
import { motion } from "framer-motion";

interface Props {
  label: string;
  value: number | string;
  icon: React.ReactNode;
  index?: number;
}

export default function StatsCard({ label, value, icon, index = 0 }: Props) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: index * 0.08, ease: "easeOut" }}
      whileHover={{ y: -2, transition: { duration: 0.15 } }}
      className="bg-white rounded-card border border-brand-border shadow-card p-4 flex items-center gap-4 cursor-default"
    >
      <div className="flex-shrink-0 w-10 h-10 rounded-lg bg-teal-50 flex items-center justify-center text-teal-600">
        {icon}
      </div>
      <div>
        <p className="text-2xl font-semibold text-brand-text">{value}</p>
        <p className="text-sm text-brand-muted mt-0.5">{label}</p>
      </div>
    </motion.div>
  );
}
