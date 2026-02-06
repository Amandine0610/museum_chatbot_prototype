/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                'rwanda-blue': '#00A3E0',
                'rwanda-yellow': '#F4C430',
                'rwanda-green': '#248351',
                'museum-bg': '#f5f5f0',
            },
            fontFamily: {
                sans: ['Inter', 'sans-serif'],
            }
        },
    },
    plugins: [],
}
