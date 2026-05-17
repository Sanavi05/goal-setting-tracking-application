import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}", "./lib/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        border: "#d7dce2",
        muted: "#f5f6f8",
        ink: "#1f2933",
        accent: "#2563eb"
      }
    }
  },
  plugins: []
};

export default config;
