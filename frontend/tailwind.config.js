/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                'museum-brown': '#5D4037',     // Dark Brown for headers/primary buttons
                'museum-gold': '#8D6E63',      // Lighter brown/gold for accents
                'museum-cream': '#F5F5F0',     // Light background 
                'museum-card': '#FFFFFF',      // White cards
                'museum-text': '#3E2723',      // Dark text
                'museum-overlay': 'rgba(0,0,0,0.5)',
            },
            fontFamily: {
                sans: ['Inter', 'sans-serif'],
            },
            backgroundImage: {
                'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
            }
        },
    },
    plugins: [],
}
