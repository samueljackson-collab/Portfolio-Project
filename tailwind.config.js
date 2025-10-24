/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {},
  },
  safelist: [
    // Safelist dynamic role colors to prevent purging in production
    'bg-blue-600',
    'bg-green-600',
    'bg-purple-600',
    'bg-orange-500',
    'hover:bg-blue-700',
    'hover:bg-green-700',
    'hover:bg-purple-700',
    'hover:bg-orange-600',
  ],
  plugins: [],
};
