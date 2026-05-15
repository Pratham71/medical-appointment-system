"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

interface Props {
  error: Error & { digest?: string };
  reset: () => void;
}

function isServiceUnavailable(error: Error) {
  const msg = error.message.toLowerCase();
  return (
    msg.includes("failed to fetch") ||
    msg.includes("network") ||
    msg.includes("502") ||
    msg.includes("503") ||
    msg.includes("unreachable")
  );
}

export default function ErrorPage({ error, reset }: Props) {
  const router = useRouter();
  const [showDetails, setShowDetails] = useState(false);
  const unavailable = isServiceUnavailable(error);

  useEffect(() => {
    console.error(error);
  }, [error]);

  if (unavailable) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-[#F0F4F6] px-4">
        <div className="text-center max-w-md">
          <div className="w-14 h-14 rounded-full bg-amber-50 flex items-center justify-center mx-auto mb-6">
            <svg className="w-7 h-7 text-amber-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <h1 className="font-['Outfit'] text-xl font-semibold text-slate-900 mb-2">
            Service unavailable
          </h1>
          <p className="font-['Outfit'] text-sm text-slate-500 mb-8">
            The infirmary system is temporarily unreachable. Please try again in a moment.
          </p>
          <button
            onClick={reset}
            className="rounded-[6px] bg-teal-600 px-5 py-2.5 text-sm font-semibold text-white hover:bg-teal-700 transition-colors"
          >
            Try Again
          </button>
          <p className="mt-6 font-['Outfit'] text-xs text-slate-400">
            If this persists, contact the infirmary.
          </p>
        </div>
        <p className="mt-16 font-['Outfit'] text-xs text-slate-400">
          College Infirmary · Medical Appointment System
        </p>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-[#F0F4F6] px-4">
      <div className="text-center max-w-md w-full">
        <p className="font-['Newsreader'] text-8xl font-semibold text-slate-400 leading-none mb-6">
          500
        </p>
        <h1 className="font-['Outfit'] text-xl font-semibold text-slate-900 mb-2">
          Something went wrong
        </h1>
        <p className="font-['Outfit'] text-sm text-slate-500 mb-8">
          An unexpected error occurred. Please try refreshing the page.
        </p>
        <div className="flex items-center justify-center gap-3 mb-6">
          <button
            onClick={reset}
            className="rounded-[6px] bg-teal-600 px-5 py-2.5 text-sm font-semibold text-white hover:bg-teal-700 transition-colors"
          >
            Refresh Page
          </button>
          <button
            onClick={() => router.push("/students")}
            className="rounded-[6px] border border-slate-300 px-5 py-2.5 text-sm font-semibold text-slate-600 hover:bg-slate-50 transition-colors"
          >
            Go to Dashboard
          </button>
        </div>

        <button
          onClick={() => setShowDetails((v) => !v)}
          className="font-['Outfit'] text-xs text-slate-400 hover:text-slate-600 transition-colors"
        >
          {showDetails ? "Hide" : "Show"} error details
        </button>
        {showDetails && (
          <div className="mt-3 rounded-lg border border-slate-200 bg-slate-50 p-4 text-left">
            <p className="font-['JetBrains_Mono'] text-xs text-slate-600 break-all">
              {error.message}
            </p>
            {error.digest && (
              <p className="font-['JetBrains_Mono'] text-xs text-slate-400 mt-1">
                digest: {error.digest}
              </p>
            )}
          </div>
        )}
      </div>
      <p className="mt-16 font-['Outfit'] text-xs text-slate-400">
        College Infirmary · Medical Appointment System
      </p>
    </div>
  );
}
