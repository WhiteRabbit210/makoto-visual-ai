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
          purple: '#7C3AED',
          'purple-light': '#A78BFA',
          'purple-dark': '#6D28D9',
          blue: '#3B82F6',
          'blue-light': '#DBEAFE',
          'blue-lighter': '#EFF6FF',
          green: '#10B981',
          'green-light': '#D1FAE5',
        },
        bg: {
          primary: '#FFFFFF',
          secondary: '#FAFBFD',
          tertiary: '#F7F8FA',
          card: '#FFFFFF',
          hover: '#F9FAFB',
          glass: 'rgba(255, 255, 255, 0.85)',
          'glass-dark': 'rgba(249, 250, 251, 0.95)',
          gradient: 'linear-gradient(135deg, #E0E7FF 0%, #E9D5FF 100%)',
        },
        text: {
          primary: '#111827',
          secondary: '#6B7280',
          muted: '#9CA3AF',
          light: '#D1D5DB',
        },
        border: {
          DEFAULT: '#E5E7EB',
          light: '#F3F4F6',
          dark: '#D1D5DB',
          glass: 'rgba(229, 231, 235, 0.5)',
        },
        status: {
          success: '#10B981',
          warning: '#F59E0B',
          error: '#EF4444',
          info: '#3B82F6',
        }
      },
      boxShadow: {
        'sm': '0 1px 2px rgba(0, 0, 0, 0.05)',
        'md': '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
        'lg': '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
        'glass': '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
        'glow': '0 0 15px rgba(124, 58, 237, 0.1)',
      },
      backdropBlur: {
        xs: '2px',
        sm: '4px',
        md: '8px',
        lg: '12px',
        xl: '16px',
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'gradient-mesh': 'url("data:image/svg+xml,%3Csvg width="100" height="100" xmlns="http://www.w3.org/2000/svg"%3E%3Cdefs%3E%3Cfilter id="noiseFilter"%3E%3CfeTurbulence type="turbulence" baseFrequency="0.65" numOctaves="4" stitchTiles="stitch"/%3E%3C/filter%3E%3C/defs%3E%3Crect width="100%25" height="100%25" filter="url(%23noiseFilter)" opacity="0.02"/%3E%3C/svg%3E")',
      }
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
  ],
}