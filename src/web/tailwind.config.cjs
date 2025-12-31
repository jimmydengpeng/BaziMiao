/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./index.html", "./src/**/*.{vue,js,ts,jsx,tsx}"],
  corePlugins: {
    preflight: false
  },
  theme: {
    extend: {
      colors: {
        bg: "var(--bg)",
        panel: "var(--panel)",
        accent: "var(--accent)",
        "accent-2": "var(--accent-2)",
        text: "var(--text)",
        muted: "var(--muted)",
        card: "var(--card)",
        border: "var(--border)"
      }
    }
  },
  plugins: []
};

