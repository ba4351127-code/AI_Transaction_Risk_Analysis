/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // Exact User Reference 2 Palette:
        lime: {
          DEFAULT: '#A0FF99',
          400: '#A0FF99',
          300: '#B8FFB3',
          500: '#7CEE74',
          600: '#58D350',
        },
        forest: {
          DEFAULT: '#1D3A1E',
          950: '#070E08',
          900: '#0C180E',
          850: '#122314',
          800: '#172C18',
          700: '#1D3A1E',
          600: '#29502B',
          500: '#366938',
        },
        fintech: {
          black: '#020202',      // Pure black canvas
          surface: '#0A120B',    // Elevated card surface
          panel: '#101C12',      // Container panel
          border: 'rgba(160, 255, 153, 0.15)', // Subtle lime border
          borderMuted: 'rgba(255, 255, 255, 0.08)',
          muted: '#8A998A',      // Editorial secondary text
        },
        risk: {
          low: '#A0FF99',        // Lime green for safe/approve
          medium: '#F59E0B',     // Amber for review
          high: '#EF4444',       // Red for block
          critical: '#991B1B',   // Deep crimson for freeze
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
        editorial: ['Inter', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        'lime-glow': '0 0 25px -4px rgba(160, 255, 153, 0.35)',
        'lime-sm': '0 0 12px -2px rgba(160, 255, 153, 0.25)',
        'forest-card': '0 8px 30px rgba(2, 2, 2, 0.6)',
      }
    },
  },
  plugins: [],
}
