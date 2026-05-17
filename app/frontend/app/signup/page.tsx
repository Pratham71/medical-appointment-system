"use client";

import { useState, type FormEvent } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { signup, setSession } from "@/lib/api";
import Select from "@/components/ui/Select";

const DEPARTMENTS = [
  "Computer Science",
  "Electronics & Communication",
  "Mechanical Engineering",
  "Civil Engineering",
  "Chemical Engineering",
  "Biotechnology",
  "Economics",
  "Mathematics",
  "Physics",
  "Humanities",
];

export default function SignupPage() {
  const router = useRouter();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [rollNumber, setRollNumber] = useState("");
  const [department, setDepartment] = useState(DEPARTMENTS[0]);
  const [yearLevel, setYearLevel] = useState(1);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const res = await signup({ name, email, password, roll_number: rollNumber, department, year_level: yearLevel });
      setSession(res.access_token, res.user);
      router.replace("/students");
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Sign up failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-brand-bg flex items-center justify-center px-4 py-10">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="flex items-center gap-3 mb-8 justify-center">
          <div className="w-9 h-9 rounded-lg bg-teal-600 flex items-center justify-center text-white font-bold text-base flex-shrink-0">
            M
          </div>
          <span className="font-semibold text-brand-text text-lg leading-tight">
            College Infirmary
          </span>
        </div>

        <div className="bg-white rounded-card border border-brand-border shadow-card p-8">
          <h1 className="text-xl font-semibold text-brand-text mb-1">Create account</h1>
          <p className="text-sm text-brand-muted mb-6">Register to book appointments at the infirmary.</p>

          {error && (
            <div className="bg-red-50 border border-red-100 text-red-600 text-sm rounded-btn px-4 py-3 mb-5">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-brand-text mb-1.5">Full name</label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
                autoFocus
                placeholder="e.g. Aarav Mehta"
                className="w-full border border-brand-border rounded-btn px-3 py-2.5 text-sm text-brand-text placeholder:text-brand-muted focus:ring-2 focus:ring-teal-600 focus:ring-offset-1 focus:outline-none transition"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-brand-text mb-1.5">College email</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                placeholder="f20230123@dubai.bits-pilani.ac.in"
                className="w-full border border-brand-border rounded-btn px-3 py-2.5 text-sm text-brand-text placeholder:text-brand-muted focus:ring-2 focus:ring-teal-600 focus:ring-offset-1 focus:outline-none transition"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-brand-text mb-1.5">Password</label>
              <div className="relative">
                <input
                  type={showPassword ? "text" : "password"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  minLength={8}
                  placeholder="Min. 8 characters"
                  className="w-full border border-brand-border rounded-btn px-3 py-2.5 text-sm text-brand-text placeholder:text-brand-muted focus:ring-2 focus:ring-teal-600 focus:ring-offset-1 focus:outline-none transition pr-10"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword((v) => !v)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-brand-muted hover:text-brand-text transition-colors"
                >
                  {showPassword ? (
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                    </svg>
                  ) : (
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                  )}
                </button>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-sm font-medium text-brand-text mb-1.5">Roll number</label>
                <input
                  type="text"
                  value={rollNumber}
                  onChange={(e) => setRollNumber(e.target.value)}
                  required
                  placeholder="2023A7PS0123U"
                  className="w-full border border-brand-border rounded-btn px-3 py-2.5 text-sm text-brand-text placeholder:text-brand-muted focus:ring-2 focus:ring-teal-600 focus:ring-offset-1 focus:outline-none transition"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-brand-text mb-1.5">Year</label>
                <Select value={yearLevel} onChange={(e) => setYearLevel(Number(e.target.value))}>
                  {[1, 2, 3, 4, 5, 6].map((y) => (
                    <option key={y} value={y}>Year {y}</option>
                  ))}
                </Select>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-brand-text mb-1.5">Department</label>
              <Select value={department} onChange={(e) => setDepartment(e.target.value)}>
                {DEPARTMENTS.map((d) => (
                  <option key={d} value={d}>{d}</option>
                ))}
              </Select>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-teal-600 hover:bg-teal-700 disabled:opacity-60 text-white font-semibold py-2.5 rounded-btn text-sm transition-colors mt-2"
            >
              {loading ? "Creating account…" : "Create account"}
            </button>
          </form>

          <p className="mt-5 text-center text-sm text-brand-muted">
            Already have an account?{" "}
            <Link href="/login" className="text-teal-600 hover:text-teal-700 font-medium transition-colors">
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
