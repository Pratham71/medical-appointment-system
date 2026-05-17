interface Props {
  status: string;
}

const MAP: Record<string, string> = {
  booked: "bg-teal-50 text-teal-700 ring-1 ring-teal-200",
  confirmed: "bg-teal-50 text-teal-700 ring-1 ring-teal-200",
  pending: "bg-amber-50 text-amber-700 ring-1 ring-amber-200",
  unread: "bg-red-50 text-red-600 ring-1 ring-red-200",
  acknowledged: "bg-amber-50 text-amber-700 ring-1 ring-amber-200",
  resolved: "bg-emerald-50 text-emerald-700 ring-1 ring-emerald-200",
  cancelled: "bg-red-50 text-red-600 ring-1 ring-red-200",
  completed: "bg-emerald-50 text-emerald-700 ring-1 ring-emerald-200",
};

export default function StatusBadge({ status }: Props) {
  const key = status.toLowerCase();
  const cls = MAP[key] ?? "bg-slate-100 text-slate-600 ring-1 ring-slate-200";
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${cls}`}>
      {status.charAt(0).toUpperCase() + status.slice(1).toLowerCase()}
    </span>
  );
}
