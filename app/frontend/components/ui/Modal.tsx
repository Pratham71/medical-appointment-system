"use client";

interface Props {
  title: string;
  message: string;
  confirmLabel?: string;
  cancelLabel?: string;
  danger?: boolean;
  onConfirm: () => void;
  onCancel: () => void;
}

export default function Modal({
  title,
  message,
  confirmLabel = "Confirm",
  cancelLabel = "Cancel",
  danger = false,
  onConfirm,
  onCancel,
}: Props) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="absolute inset-0 bg-black/30" onClick={onCancel} />
      <div className="relative bg-white rounded-card shadow-xl p-6 w-full max-w-sm mx-4 border border-brand-border">
        <h3 className="text-base font-semibold text-brand-text">{title}</h3>
        <p className="mt-2 text-sm text-brand-muted">{message}</p>
        <div className="mt-5 flex gap-3 justify-end">
          <button
            onClick={onCancel}
            className="px-4 py-2 text-sm rounded-btn border border-brand-border text-brand-muted hover:bg-brand-raised transition"
          >
            {cancelLabel}
          </button>
          <button
            onClick={onConfirm}
            className={`px-4 py-2 text-sm rounded-btn text-white font-medium transition ${
              danger
                ? "bg-red-500 hover:bg-red-600"
                : "bg-teal-600 hover:bg-teal-700"
            }`}
          >
            {confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
}
