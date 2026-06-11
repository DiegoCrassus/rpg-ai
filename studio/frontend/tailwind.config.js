/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        surface: {
          DEFAULT: "#0f172a",
          card: "#1e293b",
          muted: "#334155",
        },
        studio: {
          accent: "#38bdf8",
          warn: "#fbbf24",
          fail: "#f87171",
        },
      },
    },
  },
  plugins: [],
};
