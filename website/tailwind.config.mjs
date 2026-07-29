/** @type {import('tailwindcss').Config} */
// Farbtokens direkt aus dem Logo (BRIEF.md Abschnitt 2). Kontraste WCAG AA geprueft.
export default {
  content: ['./src/**/*.{astro,html,js,jsx,md,mdx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        // Marken-Signalfarben (aus dem Logo)
        violett: '#3317E9',
        magenta: '#900B6F',
        signalrot: '#E2081B',
        stahl:    '#959AAF',
        anthrazit:'#12151A',

        // Neutraltoene fuer Flaechen/Text (frei abgeleitet, gedeckt)
        ink: {
          900: '#12151A',
          800: '#1E2129',
          700: '#3A3F4B',
          500: '#606775',
          400: '#7C8390',
          300: '#B4B8C2',
          200: '#D9DBE1',
          100: '#EDEEF1',
          50:  '#F7F8FA',
        },
        surface: '#FFFFFF',
      },
      fontFamily: {
        sans: [
          '-apple-system', 'BlinkMacSystemFont', '"Segoe UI"',
          'Roboto', '"Helvetica Neue"', 'Arial', 'ui-sans-serif', 'system-ui', 'sans-serif',
        ],
      },
      maxWidth: {
        prose: '68ch',
        content: '72rem',
      },
    },
  },
  plugins: [],
};
