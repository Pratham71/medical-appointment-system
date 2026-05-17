"use client";

import { useState, useEffect, type FormEvent } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { login, setSession } from "@/lib/api";

const PATIENT_ROLES = ["student", "professor", "college-staff", "hostel-staff"];

function isPatientRole(roleName: string) {
  return PATIENT_ROLES.includes(roleName);
}

function Spinner() {
  return (
    <svg
      className="animate-spin h-4 w-4 text-white"
      fill="none"
      viewBox="0 0 24 24"
    >
      <circle
        className="opacity-25"
        cx="12" cy="12" r="10"
        stroke="currentColor"
        strokeWidth="4"
      />
      <path
        className="opacity-75"
        fill="currentColor"
        d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"
      />
    </svg>
  );
}

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [rateLimitSeconds, setRateLimitSeconds] = useState(0);

  useEffect(() => {
    if (rateLimitSeconds <= 0) return;
    const t = setTimeout(() => setRateLimitSeconds((s) => s - 1), 1000);
    return () => clearTimeout(t);
  }, [rateLimitSeconds]);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (rateLimitSeconds > 0) return;
    setError("");
    setLoading(true);
    try {
      const res = await login(email, password);
      setSession(res.access_token, res.user);
      if (res.user.role_name === "doctor") router.replace("/doctors");
      else if (res.user.role_name === "admin") router.replace("/admin");
      else if (res.user.role_name === "staff") router.replace("/staff");
      else if (isPatientRole(res.user.role_name)) router.replace("/students");
      else router.replace("/login");
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Login failed";
      if (msg.includes("429") || msg.toLowerCase().includes("too many")) {
        setRateLimitSeconds(30);
        setError("Too many attempts. Please wait before trying again.");
      } else {
        setError(msg);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex">
      {/* Left panel */}
      <motion.div
        initial={{ opacity: 0, x: -40 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.45, ease: "easeOut" }}
        className="hidden lg:flex lg:w-1/2 flex-col items-center justify-center bg-gradient-to-br from-teal-600 to-teal-700 p-12 relative overflow-hidden"
      >
        <div className="absolute inset-0 opacity-10">
          <svg className="w-full h-full" xmlns="http://www.w3.org/2000/svg">
            <defs>
              <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
                <path d="M 40 0 L 0 0 0 40" fill="none" stroke="white" strokeWidth="1" />
              </pattern>
            </defs>
            <rect width="100%" height="100%" fill="url(#grid)" />
          </svg>
        </div>

        <div className="relative text-center">
          <div className="w-20 h-20 bg-white/20 rounded-2xl flex items-center justify-center mx-auto mb-8">
            <svg className="w-10 h-10 text-white" fill="currentColor" viewBox="0 0 24 24">
              <path d="M19 3H5a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2V5a2 2 0 00-2-2zm-6 14h-2v-4H7v-2h4V7h2v4h4v2h-4v4z" />
            </svg>
          </div>
          <h2 className="font-display text-3xl font-semibold text-white mb-3">
            College Infirmary
          </h2>
          <p className="text-teal-100 text-base">Your health, managed simply.</p>

          <div className="mt-12 grid grid-cols-2 gap-4 text-left">
            {[
              { label: "Book appointments", desc: "Schedule visits with doctors" },
              { label: "Track history", desc: "Access your medical records" },
              { label: "Get certificates", desc: "Medical and fitness certificates" },
              { label: "View prescriptions", desc: "All your prescriptions in one place" },
            ].map((f, i) => (
              <motion.div
                key={f.label}
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, delay: 0.35 + i * 0.07, ease: "easeOut" }}
                className="bg-white/10 rounded-xl p-4"
              >
                <p className="text-white text-sm font-medium">{f.label}</p>
                <p className="text-teal-100 text-xs mt-1">{f.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </motion.div>

      {/* Right panel — form */}
      <motion.div
        initial={{ opacity: 0, x: 40 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.45, ease: "easeOut" }}
        className="flex-1 flex items-center justify-center p-8 bg-white"
      >
        <div className="w-full max-w-sm">
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.35, delay: 0.15, ease: "easeOut" }}
            className="mb-8"
          >
            <div className="lg:hidden w-10 h-10 bg-teal-600 rounded-xl flex items-center justify-center mb-4">
              <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 24 24">
                <path d="M19 3H5a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2V5a2 2 0 00-2-2zm-6 14h-2v-4H7v-2h4V7h2v4h4v2h-4v4z" />
              </svg>
            </div>
            <h1 className="font-display text-2xl font-semibold text-brand-text">
              Welcome back
            </h1>
            <p className="text-brand-muted text-sm mt-1">
              Sign in to your infirmary account
            </p>
          </motion.div>

          <motion.form
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.35, delay: 0.25, ease: "easeOut" }}
            onSubmit={handleSubmit}
            className="space-y-4"
          >
            <div>
              <label className="block text-sm font-medium text-brand-text mb-1.5">
                Email address
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                autoFocus
                placeholder="you@college.edu"
                className="w-full px-3 py-2.5 border border-brand-border rounded-btn text-sm text-brand-text placeholder:text-brand-muted bg-white focus:ring-2 focus:ring-teal-600 focus:ring-offset-1 focus:outline-none transition"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-brand-text mb-1.5">
                Password
              </label>
              <div className="relative">
                <input
                  type={showPassword ? "text" : "password"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  placeholder="Enter password"
                  className="w-full px-3 py-2.5 pr-11 border border-brand-border rounded-btn text-sm text-brand-text placeholder:text-brand-muted bg-white focus:ring-2 focus:ring-teal-600 focus:ring-offset-1 focus:outline-none transition"
                />
                <button
                  type="button"
                  aria-label={showPassword ? "Hide password" : "Show password"}
                  aria-pressed={showPassword}
                  onClick={() => setShowPassword((v) => !v)}
                  className="absolute inset-y-0 right-0 flex min-h-11 w-11 items-center justify-center rounded-r-btn text-brand-muted transition-colors hover:text-teal-700 focus:outline-none focus:ring-2 focus:ring-teal-600 focus:ring-offset-1"
                >
                  {showPassword ? (
                    <svg aria-hidden="true" className="h-5 w-5" fill="none" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.8" viewBox="0 0 24 24">
                      <path d="m3 3 18 18" />
                      <path d="M10.6 10.6a2 2 0 0 0 2.8 2.8" />
                      <path d="M9.9 4.3A10.4 10.4 0 0 1 12 4c5 0 8.5 4.4 9.7 6.2a3 3 0 0 1 0 3.6 17.5 17.5 0 0 1-2.6 3.1" />
                      <path d="M6.6 6.6a17.2 17.2 0 0 0-4.3 3.6 3 3 0 0 0 0 3.6C3.5 15.6 7 20 12 20a10.8 10.8 0 0 0 4.4-.9" />
                    </svg>
                  ) : (
                    <svg aria-hidden="true" className="h-5 w-5" fill="none" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.8" viewBox="0 0 24 24">
                      <path d="M2.3 10.2a3 3 0 0 0 0 3.6C3.5 15.6 7 20 12 20s8.5-4.4 9.7-6.2a3 3 0 0 0 0-3.6C20.5 8.4 17 4 12 4s-8.5 4.4-9.7 6.2Z" />
                      <circle cx="12" cy="12" r="3" />
                    </svg>
                  )}
                </button>
              </div>
            </div>

            {error && (
              <motion.p
                initial={{ opacity: 0, y: -4 }}
                animate={{ opacity: 1, y: 0 }}
                className="text-sm text-red-500 bg-red-50 border border-red-100 rounded-btn px-3 py-2"
              >
                {error}
                {rateLimitSeconds > 0 && (
                  <span className="font-medium"> ({rateLimitSeconds}s)</span>
                )}
              </motion.p>
            )}

            <button
              type="submit"
              disabled={loading || rateLimitSeconds > 0}
              className="w-full flex items-center justify-center gap-2 bg-teal-600 hover:bg-teal-700 disabled:opacity-60 text-white font-medium py-2.5 rounded-btn text-sm transition-colors"
            >
              {loading ? (
                <>
                  <Spinner />
                  Signing in…
                </>
              ) : rateLimitSeconds > 0 ? (
                `Try again in ${rateLimitSeconds}s`
              ) : (
                "Sign in"
              )}
            </button>
          </motion.form>

          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.4 }}
            className="mt-4 text-center text-sm text-brand-muted"
          >
            <button className="text-teal-600 hover:text-teal-700 transition-colors">
              Forgot password?
            </button>
          </motion.p>
        </div>
      </motion.div>
    </div>
  );
}
