/** @type {import('tailwindcss').Config} */
export default {
    darkMode: 'class',
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                'museum': {
                    'brown-dark': '#4A3728',     // Headers, primary buttons
                    'brown-medium': '#8B6B4C',   // Secondary buttons, accents
                    'brown-light': '#A68D74',    // Hover states, borders
                    'cream-dark': '#E5DED5',     // Card backgrounds
                    'cream-light': '#F5F0EA',    // Main screen background
                    'gold': '#C5A059',           // Highlight accents
                    'text-main': '#2C1E12',      // Primary text
                    'text-muted': '#6B5D51',     // Secondary text
                    'night': {
                        'bg': '#0f0e0d',
                        'surface': '#1a1816',
                        'elevated': '#252220',
                        'border': '#3a342f',
                        'text': '#ebe7e2',
                        'muted': '#9c9188',
                    },
                }
            },
            fontFamily: {
                sans: ['Inter', 'sans-serif'],
                display: ['Outfit', 'sans-serif'], // Added for headings
            },
            boxShadow: {
                'premium': '0 10px 30px -5px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1)',
                'card': '0 20px 40px -10px rgba(74, 55, 40, 0.15)',
            }
        },
    },
    plugins: [],
}
