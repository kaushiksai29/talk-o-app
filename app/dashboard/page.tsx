"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { ArrowRight } from 'lucide-react';
import ThemeToggle from "@/components/ThemeToggle";
import { StargirlIcon, SageIcon } from "@/components/PersonaIcons";
import Sidebar from "@/components/Sidebar";
import { createClient } from '@supabase/supabase-js';
import { useSession } from "next-auth/react";
import { useRouter } from "next/navigation";

// Initialize Supabase Client
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || "";
const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || "";
const supabase = createClient(supabaseUrl, supabaseKey);

export default function Dashboard() {
    const { data: session, status } = useSession();
    const router = useRouter();
    const [user, setUser] = useState<{ name: string; email: string } | null>(null);
    const [loading, setLoading] = useState(true);

    // Auth Guard
    useEffect(() => {
        if (status === "unauthenticated") {
            router.push("/login?callbackUrl=/dashboard");
        }
    }, [status, router]);

    useEffect(() => {
        const getUser = async () => {
            if (status !== "authenticated" || !session?.user) return;

            // Fetch profile for name
            const { data: profile } = await supabase
                .from('profiles')
                .select('first_name, last_name')
                .eq('id', (session.user as any).id)
                .single();

            const name = profile
                ? `${profile.first_name} ${profile.last_name}`.trim()
                : session.user.name || session.user.email?.split('@')[0] || "User";

            setUser({
                name: name || "Friend",
                email: session.user.email || ""
            });
            setLoading(false);
        };

        if (status === "authenticated") {
            getUser();
        } else if (status === "unauthenticated") {
            setLoading(false);
        }
    }, [session, status]);

    if (loading || status === "loading") {
        return <div className="min-h-screen flex items-center justify-center bg-cream-50 dark:bg-[#0f172a] text-coffee-light dark:text-cream-400">Loading...</div>;
    }

    return (
        <Sidebar>
            <div className="h-full overflow-y-auto bg-cream-gradient dark:bg-dark-gradient font-sans text-coffee-dark dark:text-cream-100 transition-colors duration-500 flex flex-col">
                {/* Header (Mobile Only - Sidebar handles desktop) */}
                <header className="lg:hidden p-6 flex justify-end items-center">
                    <ThemeToggle />
                </header>

                {/* Desktop Theme Toggle (Absolute) */}
                <div className="hidden lg:block absolute top-6 right-6 z-10">
                    <ThemeToggle />
                </div>

                {/* Main Content */}
                <main className="flex-1 flex flex-col items-center justify-center p-6 animate-fade-in">
                    <div className="text-center mb-12 max-w-2xl">
                        <h1 className="font-serif text-4xl md:text-5xl font-bold text-coffee-dark dark:text-cream-50 mb-4">
                            Hi, {user?.name?.split(' ')[0] || "there"}
                        </h1>
                        <p className="text-coffee-light dark:text-cream-300 text-lg">
                            Who do you want to talk to today?
                        </p>
                    </div>

                    <div className="grid md:grid-cols-2 gap-8 max-w-5xl w-full">
                        {/* Stargirl Card - Dark Violet Sky */}
                        <Link href="/chat?model=stargirl" className="group relative h-[450px] rounded-[2.5rem] overflow-hidden cursor-pointer transition-all duration-500 hover:-translate-y-2 hover:shadow-2xl hover:shadow-violet-sky/20">
                            {/* Background Layers */}
                            <div className="absolute inset-0 bg-gradient-to-br from-violet-sky-light via-[#8EC5FC] to-violet-sky-dark animate-gradient-shift"></div>
                            {/* Stars Pattern */}
                            <div className="absolute inset-0 opacity-40 animate-twinkle"
                                style={{
                                    backgroundImage: `
                                     radial-gradient(2px 2px at 20% 30%, white, transparent),
                                     radial-gradient(2px 2px at 60% 70%, white, transparent),
                                     radial-gradient(1px 1px at 50% 50%, white, transparent),
                                     radial-gradient(2px 2px at 80% 10%, white, transparent),
                                     radial-gradient(1px 1px at 10% 60%, white, transparent),
                                     radial-gradient(2px 2px at 95% 85%, white, transparent),
                                     radial-gradient(1px 1px at 40% 20%, white, transparent),
                                     radial-gradient(1px 1px at 70% 40%, white, transparent)
                                   `,
                                    backgroundSize: '250px 250px'
                                }}>
                            </div>
                            {/* Watercolor Overlay */}
                            <div className="absolute inset-0 opacity-30"
                                style={{
                                    background: `
                                     radial-gradient(ellipse at 30% 40%, rgba(224,195,252,0.4) 0%, transparent 60%),
                                     radial-gradient(ellipse at 70% 60%, rgba(142,197,252,0.3) 0%, transparent 55%),
                                     radial-gradient(ellipse at 50% 30%, rgba(200,210,252,0.2) 0%, transparent 65%)
                                   `
                                }}>
                            </div>

                            <div className="relative h-full p-8 flex flex-col justify-between text-white">
                                <div className="w-16 h-16 bg-white/10 backdrop-blur-md rounded-2xl flex items-center justify-center shadow-inner border border-white/20">
                                    <StargirlIcon className="w-8 h-8" />
                                </div>
                                <div>
                                    <h3 className="font-serif text-4xl font-bold mb-2">Stargirl</h3>
                                    <p className="text-violet-sky-light text-lg font-medium mb-6">Your Late-Night Confidant</p>
                                    <p className="text-white/80 leading-relaxed">
                                        Perfect for venting, emotional support, and late-night thoughts. She's here to validate and understand you.
                                    </p>
                                </div>
                                <div className="absolute bottom-8 right-8 opacity-0 group-hover:opacity-100 transition-opacity duration-300 transform translate-x-4 group-hover:translate-x-0">
                                    <div className="w-12 h-12 bg-white text-violet-sky-dark rounded-full flex items-center justify-center shadow-lg">
                                        <ArrowRight className="w-6 h-6" />
                                    </div>
                                </div>
                            </div>
                        </Link>

                        {/* Sage Card - Light Pecan */}
                        <Link href="/chat?model=sage" className="group relative h-[450px] rounded-[2.5rem] overflow-hidden cursor-pointer transition-all duration-500 hover:-translate-y-2 hover:shadow-2xl hover:shadow-pecan/20">
                            {/* Background Layers */}
                            <div className="absolute inset-0 bg-gradient-to-br from-[#D4FC79] via-[#B5E89D] to-[#96E6A1] animate-gradient-shift"></div>
                            {/* Grid Pattern */}
                            <div className="absolute inset-0 opacity-20"
                                style={{
                                    backgroundImage: `
                                     linear-gradient(rgba(255,255,255,0.5) 1.5px, transparent 1.5px),
                                     linear-gradient(90deg, rgba(255,255,255,0.5) 1.5px, transparent 1.5px)
                                   `,
                                    backgroundSize: '35px 35px'
                                }}>
                            </div>
                            {/* Nature Gradient Overlay */}
                            <div className="absolute inset-0 opacity-30"
                                style={{
                                    background: `
                                     radial-gradient(ellipse at 40% 50%, rgba(212,252,121,0.4) 0%, transparent 65%),
                                     radial-gradient(ellipse at 70% 40%, rgba(150,230,161,0.3) 0%, transparent 60%),
                                     radial-gradient(ellipse at 30% 70%, rgba(181,232,157,0.25) 0%, transparent 58%)
                                   `
                                }}>
                            </div>

                            <div className="relative h-full p-8 flex flex-col justify-between text-coffee-dark">
                                <div className="w-16 h-16 bg-white/50 backdrop-blur-md rounded-2xl flex items-center justify-center shadow-sm border border-white/50">
                                    <SageIcon className="w-8 h-8" />
                                </div>
                                <div>
                                    <h3 className="font-serif text-4xl font-bold mb-2">Sage</h3>
                                    <p className="text-coffee-light text-lg font-medium mb-6">Your Daily Guide</p>
                                    <p className="text-coffee-light leading-relaxed">
                                        Ideal for planning, breaking down tasks, and finding resources. He helps you navigate the chaos with logic.
                                    </p>
                                </div>
                                <div className="absolute bottom-8 right-8 opacity-0 group-hover:opacity-100 transition-opacity duration-300 transform translate-x-4 group-hover:translate-x-0">
                                    <div className="w-12 h-12 bg-coffee-dark text-white rounded-full flex items-center justify-center shadow-lg">
                                        <ArrowRight className="w-6 h-6" />
                                    </div>
                                </div>
                            </div>
                        </Link>
                    </div>
                </main>
            </div>
        </Sidebar>
    );
}
