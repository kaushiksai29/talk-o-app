"use client";

import { useState, useEffect } from "react";

export default function ThemeToggle() {
    const [darkMode, setDarkMode] = useState(false);

    useEffect(() => {
        if (typeof window !== "undefined") {
            const isDark = document.documentElement.classList.contains("dark");
            setDarkMode(isDark);
        }
    }, []);

    const toggleTheme = () => {
        const newMode = !darkMode;
        setDarkMode(newMode);
        if (newMode) {
            document.documentElement.classList.add("dark");
            localStorage.theme = 'dark';
        } else {
            document.documentElement.classList.remove("dark");
            localStorage.theme = 'light';
        }
    };

    return (
        <button
            onClick={toggleTheme}
            className="relative w-16 h-8 rounded-full bg-cream-300 dark:bg-coffee-light border border-cream-400 dark:border-coffee-light transition-colors duration-300 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-cream-400 dark:focus:ring-coffee-light"
            aria-label="Toggle Theme"
        >
            <div
                className={`absolute top-1 left-1 w-6 h-6 rounded-full shadow-sm transform transition-transform duration-300 flex items-center justify-center ${darkMode
                    ? "translate-x-8 bg-coffee-dark text-cream-100"
                    : "translate-x-0 bg-white text-orange-400"
                    }`}
            >
                {darkMode ? (
                    <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
                    </svg>
                ) : (
                    <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
                    </svg>
                )}
            </div>
        </button>
    );
}
