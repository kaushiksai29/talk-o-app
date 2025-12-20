"use client";

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import {
    Home,
    MessageSquare,
    Settings,
    LogOut,
    Menu,
    X,
    User,
    History
} from 'lucide-react';
import { useSession, signOut } from "next-auth/react";
import SettingsModal from './SettingsModal';

// Initialize Supabase Client (Client-side) - kept for other usages if any, but auth via NextAuth
// const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || "";
// const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || "";
// const supabaseClient = createClient(supabaseUrl, supabaseKey);

interface SidebarProps {
    children: React.ReactNode;
    userName?: string;
    userEmail?: string;
}

export default function Sidebar({ children }: { children: React.ReactNode }) {
    const { data: session } = useSession();
    const [isOpen, setIsOpen] = useState(true); // Default open
    const [isSettingsOpen, setIsSettingsOpen] = useState(false);
    const pathname = usePathname();
    const router = useRouter();
    const [isMobile, setIsMobile] = useState(false);

    // Handle resize - just to detect mobile state
    useEffect(() => {
        const handleResize = () => {
            setIsMobile(window.innerWidth < 1024);
            if (window.innerWidth < 1024) {
                setIsOpen(false); // Default close on mobile
            } else {
                setIsOpen(true); // Default open on desktop
            }
        };

        // Initial check
        handleResize();

        window.addEventListener('resize', handleResize);
        return () => window.removeEventListener('resize', handleResize);
    }, []);

    const handleLogout = async () => {
        await signOut({ callbackUrl: '/login' });
    };

    const navItems = [
        { name: 'Dashboard', href: '/dashboard', icon: Home },
        { name: 'New Chat', href: '/dashboard', icon: MessageSquare }, // Dashboard is where you pick persona
        // { name: 'History', href: '/history', icon: History }, // TODO: Implement History Page
    ];

    return (
        <div className="min-h-screen flex bg-cream-50 dark:bg-[#0f172a] transition-colors duration-500">
            <SettingsModal
                isOpen={isSettingsOpen}
                onClose={() => setIsSettingsOpen(false)}
                userId={(session?.user as any)?.id || session?.user?.email}
            />
            {/* Menu Button (Visible on all screens now) */}
            <button
                onClick={() => setIsOpen(!isOpen)}
                className="fixed top-4 left-4 z-50 p-2 bg-white/80 dark:bg-[#1e1b4b]/80 backdrop-blur-md rounded-lg shadow-sm border border-cream-200 dark:border-white/10 text-coffee-dark dark:text-cream-100 hover:bg-cream-100 dark:hover:bg-white/10 transition-colors"
            >
                {isOpen ? <X size={24} /> : <Menu size={24} />}
            </button>

            {/* Sidebar */}
            <aside
                className={`
                    fixed inset-y-0 left-0 z-40
                    w-72 bg-white/90 dark:bg-[#1e1b4b]/90 backdrop-blur-xl
                    border-r border-cream-200 dark:border-white/5
                    transform transition-transform duration-300 ease-in-out
                    ${isOpen ? 'translate-x-0' : '-translate-x-full'}
                    flex flex-col
                `}
            >
                {/* Logo Area */}
                <div className="p-8 border-b border-cream-100 dark:border-white/5">
                    <Link href="/" className="font-serif text-2xl font-bold tracking-tight flex items-center gap-2">
                        <div className="flex -space-x-2">
                            <div className="w-6 h-6 rounded-full bg-purple-400 opacity-90"></div>
                            <div className="w-6 h-6 rounded-full bg-emerald-400 opacity-90"></div>
                        </div>
                        <span className="bg-clip-text text-transparent bg-gradient-to-r from-purple-600 to-emerald-600">Talk-o</span>
                    </Link>
                </div>

                {/* User Profile Summary */}
                <div className="p-6 mx-4 mt-4 rounded-2xl bg-cream-100/50 dark:bg-white/5 border border-cream-200 dark:border-white/5 flex items-center gap-4">

                    <div className="flex-1 min-w-0">
                        <h3 className="font-serif font-bold text-coffee-dark dark:text-cream-50 truncate">
                            {session?.user?.name || "User"}
                        </h3>
                        {/* Removed Free Plan as requested */}
                    </div>
                </div>

                {/* Navigation */}
                <nav className="flex-1 px-4 py-8 space-y-2">
                    {navItems.map((item) => {
                        const Icon = item.icon;
                        // Don't highlight New Chat
                        const isActive = pathname === item.href && item.name !== 'New Chat';

                        return (
                            <Link
                                key={item.name}
                                href={item.href}
                                className={`
                                    flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200
                                    ${isActive
                                        ? 'bg-coffee-dark text-white shadow-lg shadow-coffee-dark/20 dark:bg-violet-sky dark:shadow-violet-sky/20'
                                        : 'text-coffee-light dark:text-cream-300 hover:bg-cream-100 dark:hover:bg-white/5'
                                    }
                                `}
                            >
                                <Icon size={20} />
                                <span className="font-medium">{item.name}</span>
                            </Link>
                        );
                    })}

                    <button
                        onClick={() => setIsSettingsOpen(true)}
                        className="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-coffee-light dark:text-cream-300 hover:bg-cream-100 dark:hover:bg-white/5 transition-all duration-200"
                    >
                        <Settings size={20} />
                        <span className="font-medium">Settings</span>
                    </button>
                </nav>

                {/* Footer / Logout */}
                <div className="p-6 border-t border-cream-100 dark:border-white/5">
                    <button
                        onClick={handleLogout}
                        className="w-full flex items-center justify-center gap-2 px-4 py-3 rounded-xl border border-cream-200 dark:border-white/10 text-coffee-light dark:text-cream-400 hover:bg-red-50 hover:text-red-500 hover:border-red-200 dark:hover:bg-red-900/10 dark:hover:text-red-400 dark:hover:border-red-900/30 transition-all duration-200"
                    >
                        <LogOut size={18} />
                        <span className="font-medium">Sign Out</span>
                    </button>
                </div>
            </aside>

            {/* Main Content Area */}
            <main className={`flex-1 relative overflow-hidden flex flex-col h-screen transition-all duration-300 ${isOpen && !isMobile ? 'ml-72' : ''}`}>
                {children}
            </main>
        </div>
    );
}
