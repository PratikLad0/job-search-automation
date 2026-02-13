/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: "#0f172a", // slate-900
        secondary: "#334155", // slate-700
        accent: "#3b82f6", // blue-500
        background: "#f8fafc", // slate-50
        surface: "#ffffff",
      },
    },
  },
  plugins: [],
}
