"use client";

import React, { useState, Suspense, useEffect, useRef } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import Link from "next/link";
import { ArrowLeft, Send } from 'lucide-react';
import ThemeToggle from "@/components/ThemeToggle";
import TypingMessage from "@/components/TypingMessage";
import { StargirlIcon, SageIcon } from "@/components/PersonaIcons";
import Sidebar from "@/components/Sidebar";
import { useSession } from "next-auth/react";
import { createClient } from '@supabase/supabase-js';

// Initialize Supabase Client
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || "";
const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || "";
const supabase = createClient(supabaseUrl, supabaseKey);

function ChatInterface() {
    const searchParams = useSearchParams();
    const router = useRouter();
    const model = searchParams.get("model") || "stargirl";

    const isSage = model === "sage";
    // Theme colors based on persona
    const themeColor = isSage ? "pecan-dark" : "violet-sky";
    const personaName = isSage ? "Sage" : "Stargirl";
    const PersonaIcon = isSage ? SageIcon : StargirlIcon;

    const { data: session } = useSession();
    const [user, setUser] = useState<{ id: string; name: string; email: string } | null>(null);
    const [messages, setMessages] = useState<{ role: 'user' | 'assistant', content: string, isStreaming?: boolean }[]>([]);
    const [input, setInput] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const [isHistoryLoaded, setIsHistoryLoaded] = useState(false);
    const [guestId, setGuestId] = useState<string>("");

    // Initialize Guest ID
    useEffect(() => {
        let id = localStorage.getItem("talk-o-guest-id");
        if (!id) {
            id = crypto.randomUUID();
            localStorage.setItem("talk-o-guest-id", id);
        }
        setGuestId(id);
    }, []);

    // Fetch User & History
    useEffect(() => {
        const init = async () => {
            let currentUserId = "";

            if (session?.user?.email) {
                // Logged in user logic...
                let userId = (session.user as any).id;
                let userName = session.user.name || "User";

                if (!userId) {
                    const { data: profile } = await supabase
                        .from('profiles')
                        .select('id, first_name, last_name')
                        .eq('email', session.user.email)
                        .single();

                    if (profile) {
                        userId = profile.id;
                        userName = `${profile.first_name || ''} ${profile.last_name || ''}`.trim() || userName;
                    }
                }

                if (userId) {
                    currentUserId = userId;
                    const userData = {
                        id: userId,
                        name: userName,
                        email: session.user.email || ""
                    };
                    setUser(userData);
                }
            }

            // If no logged in user, use guest ID
            if (!currentUserId && guestId) {
                currentUserId = guestId;
            }

            // Fetch History
            if (currentUserId) {
                try {
                    const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "https://862j4mcp.up.railway.app"}/history/${currentUserId}`);
                    if (res.ok) {
                        const history = await res.json();
                        // Filter by current persona and map to UI format
                        const personaHistory = history
                            .filter((msg: any) => msg.persona === model)
                            .map((msg: any) => ({
                                role: msg.sender === 'user' ? 'user' : 'assistant',
                                content: msg.message,
                                isStreaming: false
                            }));

                        if (personaHistory.length > 0) {
                            setMessages(personaHistory);
                        } else {
                            setMessages([{
                                role: 'assistant',
                                content: isSage
                                    ? "Hi there. I'm Sage. What's on your mind? We can break down a task or plan your day."
                                    : "Hey. I'm Stargirl. I'm here to listen. How are you feeling right now?"
                            }]);
                        }
                    }
                } catch (error) {
                    console.error("Failed to fetch history:", error);
                }
            } else {
                setMessages([{
                    role: 'assistant',
                    content: isSage
                        ? "Hi there. I'm Sage. What's on your mind? We can break down a task or plan your day."
                        : "Hey. I'm Stargirl. I'm here to listen. How are you feeling right now?"
                }]);
            }
            setIsHistoryLoaded(true);
        };

        if (guestId) {
            init();
        }
    }, [session, model, isSage, guestId]);

    // Auto-scroll to bottom when messages change
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages, isHistoryLoaded]);

    const handleSend = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!input.trim() || isLoading) return;

        const userMessage = { role: 'user' as const, content: input };
        setMessages(prev => [...prev, userMessage]);
        setInput("");
        setIsLoading(true);

        // Add placeholder for assistant response
        setMessages(prev => [...prev, { role: 'assistant', content: "", isStreaming: true }]);

        try {
            // Construct guest email if using guest ID
            const effectiveUserId = user?.id || session?.user?.email || (guestId ? `guest_${guestId}@talk-o.app` : null);

            const apiUrl = process.env.NEXT_PUBLIC_API_URL || "https://862j4mcp.up.railway.app";
            const res = await fetch(`${apiUrl}/chat`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    message: userMessage.content,
                    persona: model,
                    user_id: effectiveUserId
                }),
            });

            if (!res.ok) throw new Error("Failed to get response");

            const data = await res.json();

            // Update the last message (assistant's placeholder) with the real response
            setMessages(prev => {
                const newMessages = [...prev];
                const lastMsg = newMessages[newMessages.length - 1];
                if (lastMsg.role === 'assistant') {
                    lastMsg.content = data.response;
                    lastMsg.isStreaming = true; // Let TypingMessage handle the reveal
                }
                return newMessages;
            });

        } catch (error) {
            console.error("Chat error:", error);
            const targetUrl = process.env.NEXT_PUBLIC_API_URL || "https://862j4mcp.up.railway.app";
            console.error(`Attempted to reach: ${targetUrl}`);
            setMessages(prev => {
                const newMessages = [...prev];
                const lastMsg = newMessages[newMessages.length - 1];
                lastMsg.content = `Debug Error: ${error instanceof Error ? error.message : String(error)} \nTarget: ${targetUrl}`;
                lastMsg.isStreaming = false;
                return newMessages;
            });
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <Sidebar>
            <div className={`h-full flex flex-col bg-cream-gradient dark:bg-dark-gradient font-sans transition-colors duration-500`}>
                {/* Header */}
                <header className={`bg-white/80 dark:bg-[#0f172a]/80 backdrop-blur-md border-b border-cream-200 dark:border-white/5 px-6 py-4 flex items-center justify-between sticky top-0 z-10`}>
                    <div className="flex items-center gap-4">
                        <Link href="/dashboard" className="p-2 hover:bg-cream-100 dark:hover:bg-white/10 rounded-full text-coffee-light dark:text-cream-400 transition-colors">
                            <ArrowLeft className="w-6 h-6" />
                        </Link>
                        <div className="flex items-center gap-4">
                            <div className={`w-12 h-12 rounded-2xl flex items-center justify-center shadow-sm border ${isSage
                                ? 'bg-pecan-light/20 border-pecan-light/50 text-coffee-dark'
                                : 'bg-violet-sky/20 border-violet-sky/50 text-violet-sky-light'
                                }`}>
                                <PersonaIcon className="w-6 h-6" />
                            </div>
                            <div>
                                <h1 className="font-serif font-bold text-xl text-coffee-dark dark:text-cream-50">{personaName}</h1>
                                <p className="text-xs text-coffee-light dark:text-cream-400 flex items-center gap-1.5 font-medium uppercase tracking-wide">
                                    <span className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></span>
                                    Online
                                </p>
                            </div>
                        </div>
                    </div>
                    <ThemeToggle />
                </header>

                {/* Chat Area */}
                <div className="flex-1 overflow-y-auto p-6 sm:p-8 space-y-8">
                    {messages.map((msg, idx) => (
                        <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} animate-fade-in`}>
                            <div className={`max-w-[85%] sm:max-w-[75%] rounded-[2rem] px-6 py-4 text-lg leading-relaxed shadow-sm ${msg.role === 'user'
                                ? (isSage ? 'bg-pecan-dark text-white rounded-br-none font-medium' : 'bg-violet-sky text-white rounded-br-none font-medium')
                                : 'bg-white dark:bg-[#1e1b4b]/50 border border-cream-200 dark:border-white/5 text-coffee-dark dark:text-cream-100 rounded-bl-none backdrop-blur-sm'
                                }`}>
                                {msg.role === 'assistant' ? (
                                    <TypingMessage text={msg.content} streaming={msg.isStreaming} />
                                ) : (
                                    msg.content
                                )}
                            </div>
                        </div>
                    ))}
                    <div ref={messagesEndRef} />
                </div>

                {/* Input Area */}
                <div className="p-6 bg-white/50 dark:bg-[#0f172a]/50 border-t border-cream-200 dark:border-white/5 backdrop-blur-sm">
                    <form onSubmit={handleSend} className="max-w-4xl mx-auto relative flex items-center gap-3">
                        <input
                            type="text"
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            placeholder={`Message ${personaName}...`}
                            disabled={isLoading}
                            className={`w-full pl-8 pr-14 py-5 bg-white dark:bg-[#1e1b4b]/80 border border-cream-200 dark:border-white/10 rounded-full text-coffee-dark dark:text-cream-100 placeholder-cream-400 dark:placeholder-indigo-300/50 focus:outline-none focus:ring-2 focus:ring-${themeColor}/50 transition-all shadow-sm disabled:opacity-50 disabled:cursor-not-allowed`}
                        />
                        <button
                            type="submit"
                            disabled={!input.trim() || isLoading}
                            className={`absolute right-3 p-3 rounded-full ${input.trim() && !isLoading
                                ? (isSage ? 'bg-pecan-dark text-white hover:opacity-90' : 'bg-violet-sky text-white hover:opacity-90')
                                : 'bg-cream-200 dark:bg-white/10 text-cream-400 dark:text-cream-600'
                                } transition-all duration-300`}
                        >
                            {isLoading ? (
                                <svg className="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
                                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                </svg>
                            ) : (
                                <Send className="w-5 h-5" />
                            )}
                        </button>
                    </form>
                </div>

                <style>{`
                    .animate-fade-in {
                        animation: fadeIn 0.5s ease-out forwards;
                        opacity: 0;
                        transform: translateY(10px);
                    }
                    @keyframes fadeIn {
                        to {
                            opacity: 1;
                            transform: translateY(0);
                        }
                    }
                `}</style>
            </div>
        </Sidebar>
    );
}

export default function ChatPage() {
    return (
        <Suspense fallback={<div className="min-h-screen flex items-center justify-center bg-cream-100 dark:bg-coffee text-cream-500">Loading...</div>}>
            <ChatInterface />
        </Suspense>
    );
}
