import type { Config } from "tailwindcss";

// Palette rose/pastel — douce et accueillante en surface, tout en gardant
// les couleurs de priorité distinctes et contrastées (inspirées du triage
// d'urgence réel, échelle ESI) pour que la lisibilité clinique de la file
// d'attente ne soit jamais sacrifiée à l'esthétique.
const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        canvas: "#FDF2F6",
        ink: "#3B2832",
        surface: "#FFFFFF",
        line: "#F3D9E4",
        brand: {
          DEFAULT: "#D6608C",
          deep: "#A8456B",
          light: "#FBE6EF",
        },
        priority: {
          urgence: "#C0152F",
          grossesse: "#8B5CF6",
          senior: "#C2780A",
          normal: "#D6608C",
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
