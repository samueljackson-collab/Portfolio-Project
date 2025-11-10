/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        slate: {
          800: '#1e293b',
          900: '#0f172a',
        },
      },
    },
  },
  plugins: [],
  safelist: [
    // Safelist dynamic color classes used in the component
    'bg-blue-600',
    'bg-green-600',
    'bg-purple-600',
    'bg-orange-600',
    'hover:bg-blue-700',
    'hover:bg-green-700',
    'hover:bg-purple-700',
    'hover:bg-orange-700',
  ],
}
