interface Props {
  label: string;
  value: number | string;
  icon: React.ReactNode;
}

export default function StatsCard({ label, value, icon }: Props) {
  return (
    <div className="bg-white rounded-card border border-brand-border shadow-card p-4 flex items-center gap-4">
      <div className="flex-shrink-0 w-10 h-10 rounded-lg bg-teal-50 flex items-center justify-center text-teal-600">
        {icon}
      </div>
      <div>
        <p className="text-2xl font-semibold text-brand-text">{value}</p>
        <p className="text-sm text-brand-muted mt-0.5">{label}</p>
      </div>
    </div>
  );
}
