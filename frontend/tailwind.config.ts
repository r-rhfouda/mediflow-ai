import type { Config } from "tailwindcss";

// Palette inspirée des codes couleur réels utilisés en triage d'urgence
// (ESI — Emergency Severity Index) : chaque niveau de priorité a une
// couleur dédiée, cohérente avec ce que connaissent déjà les pros de santé.
const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        canvas: "#F7F7F4",
        ink: "#161B22",
        surface: "#FFFFFF",
        line: "#E2E4E1",
        brand: {
          DEFAULT: "#0E6B5C",
          deep: "#0A4A40",
          light: "#E4F0EC",
        },
        priority: {
          urgence: "#C0152F",
          grossesse: "#6D28D9",
          senior: "#B45309",
          normal: "#0E6B5C",
        },
      },
      fontFamily: {
        display: ["var(--font-display)", "sans-serif"],
        body: ["var(--font-body)", "sans-serif"],
        mono: ["var(--font-mono)", "monospace"],
      },
      borderRadius: {
        DEFAULT: "8px",
      },
    },
  },
  plugins: [],
};

export default config;
