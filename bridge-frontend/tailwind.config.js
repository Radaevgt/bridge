/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#1A56DB',
          light: '#EBF2FF',
          dark: '#1E3A5F',
        },
        gray: {
          50: '#F9FAFB',
        },
        text: {
          primary: '#111827',
          secondary: '#6B7280',
        },
        border: '#E5E7EB',
        error: '#EF4444',
        success: '#10B981',
      },
    },
  },
  plugins: [],
}
