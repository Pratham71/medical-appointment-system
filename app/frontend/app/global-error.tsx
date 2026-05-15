"use client";

interface Props {
  error: Error & { digest?: string };
  reset: () => void;
}

export default function GlobalError({ reset }: Props) {
  return (
    <html lang="en">
      <body style={{ margin: 0, background: "#F0F4F6", fontFamily: "Outfit, sans-serif" }}>
        <div style={{ minHeight: "100vh", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", padding: "1rem" }}>
          <div style={{ textAlign: "center", maxWidth: "28rem" }}>
            <p style={{ fontFamily: "Newsreader, serif", fontSize: "6rem", fontWeight: 600, color: "#94a3b8", lineHeight: 1, marginBottom: "1.5rem" }}>
              500
            </p>
            <h1 style={{ fontSize: "1.25rem", fontWeight: 600, color: "#0f172a", marginBottom: "0.5rem" }}>
              Something went wrong
            </h1>
            <p style={{ fontSize: "0.875rem", color: "#64748b", marginBottom: "2rem" }}>
              A critical error occurred. Please refresh the page.
            </p>
            <button
              onClick={reset}
              style={{ borderRadius: "6px", background: "#0d9488", color: "#fff", padding: "0.625rem 1.25rem", fontSize: "0.875rem", fontWeight: 600, border: "none", cursor: "pointer" }}
            >
              Refresh Page
            </button>
          </div>
        </div>
      </body>
    </html>
  );
}
