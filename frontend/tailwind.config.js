/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx}",  // Ensure your Next.js pages are included
    "./components/**/*.{js,ts,jsx,tsx}" // Include components directory
  ],
  theme: {
    extend: {},
  },
  plugins: [],
};
