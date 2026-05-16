"use client";
import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { sendEmergencyAlert } from "@/lib/api";
import ToastContainer, { useToast } from "@/components/ui/Toast";

const EMERGENCY_CONTACTS = [
  { label: "College Infirmary", number: "+971-4-XXX-XXXX", description: "Medical emergencies" },
  { label: "Hostel Warden", number: "+971-4-XXX-XXXX", description: "Hostel / accommodation" },
  { label: "Campus Security", number: "+971-4-XXX-XXXX", description: "Security & safety" },
];

export default function EmergencyButton() {
  const [open, setOpen] = useState(false);
  const [alertSending, setAlertSending] = useState(false);
  const { toasts, show, dismiss } = useToast();

  const handleSendAlert = async () => {
    setAlertSending(true);
    try {
      await sendEmergencyAlert("Student triggered emergency alert from app");
      show("Alert sent to infirmary", "success");
    } catch {
      show("Alert failed — please call directly", "warning");
    } finally {
      setAlertSending(false);
    }
  };

  const handleDial = (contact: typeof EMERGENCY_CONTACTS[0]) => {
    show(`Dialling ${contact.label}…`, "info");
  };

  return (
    <>
      <ToastContainer toasts={toasts} onDismiss={dismiss} />

      {/* Floating button */}
      <motion.button
        onClick={() => setOpen(true)}
        animate={{ scale: [1, 1.06, 1] }}
        transition={{ repeat: Infinity, duration: 2.4, ease: "easeInOut" }}
        className="fixed bottom-6 right-6 z-40 flex h-14 w-14 items-center justify-center rounded-full bg-red-500 text-white shadow-lg hover:bg-red-600 transition-colors"
        aria-label="Emergency contacts"
      >
        <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
        </svg>
      </motion.button>

      {/* Modal */}
      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.15 }}
            className="fixed inset-0 z-50 flex items-center justify-center px-4"
          >
            <div className="absolute inset-0 bg-black/40" onClick={() => setOpen(false)} />
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 8 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 8 }}
              transition={{ duration: 0.2, ease: "easeOut" }}
              className="relative w-full max-w-sm rounded-card bg-white shadow-xl border border-brand-border"
            >
              {/* Header */}
              <div className="flex items-center gap-3 border-b border-brand-border px-5 py-4">
                <div className="flex h-9 w-9 items-center justify-center rounded-full bg-red-100">
                  <svg className="h-5 w-5 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" />
                  </svg>
                </div>
                <div>
                  <h3 className="text-sm font-semibold text-brand-text">Emergency Contacts</h3>
                  <p className="text-xs text-brand-muted">Tap a number to call directly</p>
                </div>
                <button
                  onClick={() => setOpen(false)}
                  className="ml-auto text-brand-muted hover:text-brand-text transition-colors"
                >
                  <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              {/* Contacts */}
              <div className="p-4 space-y-2">
                {EMERGENCY_CONTACTS.map((contact) => (
                  <a
                    key={contact.label}
                    href={`tel:${contact.number}`}
                    onClick={() => handleDial(contact)}
                    className="flex items-center justify-between rounded-lg border border-brand-border px-4 py-3 hover:border-red-200 hover:bg-red-50 transition-colors group"
                  >
                    <div>
                      <p className="text-sm font-medium text-brand-text group-hover:text-red-700">
                        {contact.label}
                      </p>
                      <p className="text-xs text-brand-muted">{contact.description}</p>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-xs text-brand-muted group-hover:text-red-600">
                        {contact.number}
                      </span>
                      <svg className="h-4 w-4 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                      </svg>
                    </div>
                  </a>
                ))}
              </div>

              <div className="px-4 pb-3">
                <button
                  onClick={handleSendAlert}
                  disabled={alertSending}
                  className="w-full rounded-lg bg-red-500 py-2.5 text-sm font-medium text-white hover:bg-red-600 disabled:opacity-60 transition-colors"
                >
                  {alertSending ? "Sending…" : "Send Alert to Infirmary"}
                </button>
              </div>

              <div className="px-5 pb-4">
                <p className="text-xs text-brand-muted text-center">
                  For life-threatening emergencies call <strong>999</strong>
                </p>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
