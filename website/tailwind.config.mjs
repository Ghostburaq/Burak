/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{astro,html,js,jsx,md,mdx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        ink: {
          950: '#0B1220',
          900: '#0F172A',
          800: '#1E293B',
          700: '#334155',
          500: '#64748B',
          300: '#CBD5E1',
          200: '#E2E8F0',
          100: '#F1F5F9',
          50: '#F8FAFC',
        },
        accent: {
          DEFAULT: '#B45309',
          soft: '#F5E4CC',
        },
        surface: '#FFFFFF',
      },
      fontFamily: {
        sans: [
          'Inter',
          'ui-sans-serif',
          'system-ui',
          '-apple-system',
          'Segoe UI',
          'Roboto',
          'Helvetica Neue',
          'Arial',
          'sans-serif',
        ],
      },
      maxWidth: {
        prose: '68ch',
        content: '72rem',
      },
      typography: () => ({}),
    },
  },
  plugins: [],
};
