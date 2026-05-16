"use client";
import { motion } from "framer-motion";

const pulse = {
  animate: { opacity: [0.45, 0.9, 0.45] },
  transition: { repeat: Infinity, duration: 1.6, ease: "easeInOut" },
};

interface Props { className?: string }

export default function Skeleton({ className = "" }: Props) {
  return (
    <motion.div {...pulse} className={`rounded bg-slate-100 ${className}`} />
  );
}

export function SkeletonTableRows({ rows = 4, cols = 5 }: { rows?: number; cols?: number }) {
  return (
    <>
      {Array.from({ length: rows }).map((_, i) => (
        <tr key={i}>
          {Array.from({ length: cols }).map((_, j) => (
            <td key={j} className="px-4 py-3">
              <motion.div
                {...pulse}
                transition={{ ...pulse.transition, delay: i * 0.07 }}
                className={`h-4 rounded bg-slate-100 ${j === 0 ? "w-24" : j === cols - 1 ? "w-12" : "w-full"}`}
              />
            </td>
          ))}
        </tr>
      ))}
    </>
  );
}

export function SkeletonCards({ count = 3 }: { count?: number }) {
  return (
    <div className="space-y-3">
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="rounded-card border border-brand-border bg-white p-4 shadow-card">
          <div className="flex items-center gap-3 mb-2">
            <motion.div {...pulse} transition={{ ...pulse.transition, delay: i * 0.08 }}
              className="h-4 w-28 rounded bg-slate-100" />
            <motion.div {...pulse} transition={{ ...pulse.transition, delay: i * 0.08 + 0.05 }}
              className="h-4 w-16 rounded bg-slate-100" />
          </div>
          <motion.div {...pulse} transition={{ ...pulse.transition, delay: i * 0.08 + 0.1 }}
            className="h-3 w-40 rounded bg-slate-100" />
        </div>
      ))}
    </div>
  );
}
