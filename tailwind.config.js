/** @type {import('tailwindcss').Config} */
module.exports = {
    darkMode: 'class',
    content: [
        "./pages/**/*.{js,ts,jsx,tsx,mdx}",
        "./components/**/*.{js,ts,jsx,tsx,mdx}",
        "./app/**/*.{js,ts,jsx,tsx,mdx}",
    ],
    theme: {
        extend: {
            fontFamily: {
                serif: ["var(--font-fraunces)", "serif"],
                sans: ["var(--font-dm-sans)", "sans-serif"],
            },
            colors: {
                cream: {
                    DEFAULT: "#FDF9F2", // Updated to guide's warm cream
                    50: '#FDF9F2',
                    100: '#FAF5EF',
                    200: '#F5EFE6',
                    300: '#EBE0D1',
                    400: '#DCC8B0',
                    500: '#CDB090',
                    600: '#BE9870',
                    700: '#A68058',
                    800: '#8C6844',
                    900: '#735030',
                },
                pecan: {
                    DEFAULT: '#CDB090',
                    light: '#E6DCC8',
                    dark: '#8C6844',
                    100: '#F5EFE6',
                    200: '#EBE0D1',
                    300: '#DCC8B0',
                    400: '#CDB090',
                },
                coffee: {
                    DEFAULT: '#4A3B32',
                    light: '#6B584C',
                    dark: '#2C221C',
                },
                // Stargirl (Nighttime/Emotional)
                stargirl: {
                    primary: '#8B5CF6',
                    secondary: '#6366F1',
                    light: '#E9D5FF',
                    dark: '#5B21B6',
                    glow: 'rgba(139, 92, 246, 0.3)',
                },
                // Sage (Daytime/Productive)
                sage: {
                    DEFAULT: '#9CAF88', // Keep existing default for backward compat if needed
                    primary: '#22C55E',
                    secondary: '#4ADE80',
                    light: '#DCFCE7',
                    dark: '#166534',
                    glow: 'rgba(34, 197, 94, 0.3)',
                },
                // Accents
                teal: {
                    DEFAULT: '#14B8A6',
                },
                amber: {
                    DEFAULT: '#F59E0B',
                },
                'violet-sky': {
                    DEFAULT: '#4C1D95',
                    light: '#6D28D9',
                    dark: '#2E1065',
                },
                indigo: {
                    900: '#1e1b4b',
                    950: '#0f0e2a',
                },
                purple: {
                    900: '#3b0764',
                }
            },
            borderRadius: {
                '4xl': '2rem',
                '5xl': '2.5rem',
            },
            backgroundImage: {
                "gradient-radial": "radial-gradient(var(--tw-gradient-stops))",
                "gradient-conic": "conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))",
                "noise": "url(\"data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)' opacity='0.05'/%3E%3C/svg%3E\")",
                'cream-gradient': 'linear-gradient(to bottom right, #FDF9F2, #F5EFE6)',
                'dark-gradient': 'linear-gradient(to bottom right, #2E1065, #1e1b4b, #0f172a)',
                // New Gradients from Guide
                'hero-gradient': 'linear-gradient(135deg, rgba(139, 92, 246, 0.1) 0%, #FDF9F2 50%, rgba(94, 234, 212, 0.1) 100%)',
                'hero-gradient-dark': 'linear-gradient(135deg, rgba(139, 92, 246, 0.15) 0%, #020617 50%, rgba(94, 234, 212, 0.15) 100%)',
                'stargirl-gradient': 'linear-gradient(135deg, #6366F1, #8B5CF6, #A78BFA)',
                'sage-gradient': 'linear-gradient(135deg, #22C55E, #4ADE80, #86EFAC)',
                'stargirl-section': 'linear-gradient(180deg, rgba(99, 102, 241, 0.05) 0%, rgba(139, 92, 246, 0.08) 100%)',
                'sage-section': 'linear-gradient(180deg, rgba(34, 197, 94, 0.05) 0%, rgba(134, 239, 172, 0.08) 100%)',
            },
            keyframes: {
                float: {
                    '0%, 100%': { transform: 'translateY(0)' },
                    '50%': { transform: 'translateY(-10px)' },
                },
                gentleFloat: {
                    '0%, 100%': { transform: 'translateY(0)' },
                    '50%': { transform: 'translateY(-10px)' },
                },
                breathe: {
                    '0%, 100%': { transform: 'scale(1)' },
                    '50%': { transform: 'scale(1.02)' },
                },
                gradientShift: {
                    '0%, 100%': { backgroundPosition: '0% 50%' },
                    '50%': { backgroundPosition: '100% 50%' },
                },
                twinkle: {
                    '0%, 100%': { opacity: '1' },
                    '50%': { opacity: '0.7' },
                },
                leafFloat: {
                    '0%, 100%': { backgroundPosition: '0 0' },
                    '50%': { backgroundPosition: '20px 20px' },
                },
                fadeUp: {
                    'from': { opacity: '0', transform: 'translateY(25px)' },
                    'to': { opacity: '1', transform: 'translateY(0)' },
                },
                bubbleIn: {
                    'from': { opacity: '0', transform: 'scale(0.96)' },
                    'to': { opacity: '1', transform: 'scale(1)' },
                }
            },
            animation: {
                'float': 'float 6s ease-in-out infinite',
                'gentle-float': 'gentleFloat 6s ease-in-out infinite',
                'breathe': 'breathe 4s ease-in-out infinite',
                'gradient-shift': 'gradientShift 15s ease infinite',
                'twinkle': 'twinkle 6s ease-in-out infinite',
                'leaf-float': 'leafFloat 12s ease-in-out infinite',
                'fade-up': 'fadeUp 0.7s ease-out forwards',
                'bubble-in': 'bubbleIn 0.5s ease-out forwards',
            },
        },
    },
    plugins: [],
};
