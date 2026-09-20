/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Scientific dashboard theme
        primary: {
          50: '#f0f9ff',
          100: '#e0f2fe',
          200: '#bae6fd',
          300: '#7dd3fc',
          400: '#38bdf8',
          500: '#0ea5e9',
          600: '#0284c7',
          700: '#0369a1',
          800: '#075985',
          900: '#0c4a6e',
          950: '#082f49',
        },
        // Ecological green accent
        eco: {
          400: '#2dd4bf',
          500: '#14b8a6',
          600: '#0d9488',
        },
        // Financial amber
        fin: {
          400: '#fbbf24',
          500: '#f59e0b',
          600: '#d97706',
        },
        // Dark navy for backgrounds
        navy: {
          800: '#1e293b',
          900: '#0f172a',
          950: '#0a1628',
        }
      },
      fontFamily: {
        mono: ['IBM Plex Mono', 'monospace'],
        serif: ['Source Serif 4', 'Georgia', 'serif'],
      }
    },
  },
  plugins: [],
}
