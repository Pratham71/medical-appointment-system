import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        teal: {
          600: "#0D9488",
          700: "#0F766E",
        },
        brand: {
          bg: "#F0F4F6",
          surface: "#FFFFFF",
          raised: "#F8FAFB",
          border: "#E2E8F0",
          text: "#0F172A",
          muted: "#64748B",
        },
      },
      fontFamily: {
        sans: ["var(--font-outfit)", "sans-serif"],
        display: ["var(--font-newsreader)", "serif"],
        mono: ["var(--font-jetbrains)", "monospace"],
      },
      borderRadius: {
        card: "8px",
        btn: "6px",
      },
      boxShadow: {
        card: "0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.04)",
      },
    },
  },
  plugins: [],
};

export default config;
