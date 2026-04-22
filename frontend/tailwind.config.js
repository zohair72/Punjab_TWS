/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        obsidian: "#0f1312",
        moss: "#1c3a33",
        fern: "#3f7d64",
        brass: "#cf9e58",
        cream: "#f4eee6",
        ember: "#9b503f"
      },
      boxShadow: {
        glow: "0 24px 60px rgba(10, 20, 18, 0.35)"
      },
      backgroundImage: {
        "dashboard-radial":
          "radial-gradient(circle at top left, rgba(82, 143, 112, 0.32), transparent 34%), radial-gradient(circle at top right, rgba(207, 158, 88, 0.25), transparent 30%), linear-gradient(180deg, #101615 0%, #162622 100%)"
      },
      fontFamily: {
        sans: ["Space Grotesk", "Segoe UI", "sans-serif"]
      }
    }
  },
  plugins: []
};

