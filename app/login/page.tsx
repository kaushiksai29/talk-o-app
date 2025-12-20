"use client";

import React, { useState, useEffect, Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { signIn, useSession } from "next-auth/react";
import Link from "next/link";
import { ArrowLeft, LogIn, UserPlus } from 'lucide-react';
import ThemeToggle from "@/components/ThemeToggle";

function LoginContent() {
    const { data: session } = useSession();
    const searchParams = useSearchParams();
    const router = useRouter();
    const initialMode = searchParams.get("mode") === "register" ? "register" : "login";
    const [mode, setMode] = useState<"login" | "register">(initialMode);

    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [confirmPassword, setConfirmPassword] = useState("");
    const [firstName, setFirstName] = useState("");
    const [lastName, setLastName] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState("");
    const [successMessage, setSuccessMessage] = useState("");

    useEffect(() => {
        if (session) {
            router.push("/dashboard");
        }
    }, [session, router]);

    useEffect(() => {
        if (searchParams.get("mode") === "register") {
            setMode("register");
        } else {
            setMode("login");
        }
    }, [searchParams]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        setError("");
        setSuccessMessage("");

        try {
            if (mode === "register") {
                if (password !== confirmPassword) {
                    throw new Error("Passwords do not match");
                }

                const formData = new FormData();
                formData.append("email", email);
                formData.append("password", password);
                formData.append("first_name", firstName);
                formData.append("last_name", lastName);

                const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "https://talk-o-app-production.up.railway.app"}/register`, {
                    method: "POST",
                    body: formData,
                });

                if (!res.ok) {
                    const data = await res.json();
                    throw new Error(data.detail || "Registration failed");
                }

                setSuccessMessage("Registration successful! Please check your email to verify your account.");
                // Don't auto-login, wait for verification
            } else {
                const res = await signIn("credentials", {
                    email,
                    password,
                    redirect: false,
                });

                if (res?.error) throw new Error("Invalid credentials");
                router.push("/dashboard");
            }
        } catch (err: any) {
            setError(err.message);
        } finally {
            setIsLoading(false);
        }
    };

    const handleGuestLogin = async () => {
        setIsLoading(true);
        try {
            await signIn("credentials", {
                email: "guest@talk-o.app",
                password: "guest_password",
                redirect: false,
            });
            router.push("/dashboard");
        } catch (err) {
            setError("Guest login failed");
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-cream-gradient dark:bg-dark-gradient font-sans text-coffee-dark dark:text-cream-100 transition-colors duration-500 flex flex-col items-center justify-center p-4 relative overflow-hidden">
            {/* Background Blobs */}
            <div className="absolute top-[-20%] right-[-10%] w-[600px] h-[600px] bg-pecan-300/30 dark:bg-violet-sky/20 rounded-full blur-[100px]"></div>
            <div className="absolute bottom-[-10%] left-[-10%] w-[500px] h-[500px] bg-sage-light/30 dark:bg-emerald-500/10 rounded-full blur-[100px]"></div>

            <div className="absolute top-6 left-6 z-10">
                <Link href="/" className="p-2 bg-white/50 dark:bg-white/5 backdrop-blur-md rounded-full hover:bg-white/80 dark:hover:bg-white/10 transition-colors flex items-center justify-center">
                    <ArrowLeft className="w-6 h-6 text-coffee-dark dark:text-cream-100" />
                </Link>
            </div>
            <div className="absolute top-6 right-6 z-10">
                <ThemeToggle />
            </div>

            <div className="w-full max-w-md bg-white/80 dark:bg-[#0f172a]/80 rounded-[2.5rem] shadow-2xl p-8 sm:p-10 relative z-10 border border-cream-200 dark:border-white/5 backdrop-blur-md animate-fade-in my-8">
                <div className="text-center mb-8">
                    <h1 className="font-serif text-4xl font-bold text-coffee-dark dark:text-cream-100 mb-2">
                        {mode === "login" ? "Welcome Back" : "Join Talk-o"}
                    </h1>
                    <p className="text-coffee-light dark:text-cream-400">
                        {mode === "login" ? "Your companions are waiting." : "Start your journey to clarity."}
                    </p>
                </div>

                {error && (
                    <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-300 text-sm rounded-2xl text-center border border-red-100 dark:border-red-900/30">
                        {error}
                    </div>
                )}

                {successMessage && (
                    <div className="mb-6 p-4 bg-green-50 dark:bg-green-900/20 text-green-600 dark:text-green-300 text-sm rounded-2xl text-center border border-green-100 dark:border-green-900/30">
                        {successMessage}
                    </div>
                )}

                <div className="space-y-6">
                    <form onSubmit={handleSubmit} className="space-y-4">
                        {mode === "register" && (
                            <div className="grid grid-cols-2 gap-4">
                                <div className="space-y-2">
                                    <label className="text-sm font-medium text-coffee-light dark:text-cream-400 ml-1">First Name</label>
                                    <input
                                        type="text"
                                        required
                                        value={firstName}
                                        onChange={(e) => setFirstName(e.target.value)}
                                        className="w-full px-4 py-3 bg-white dark:bg-white/5 border border-cream-200 dark:border-white/10 rounded-2xl text-coffee-dark dark:text-cream-100 placeholder-cream-400 focus:outline-none focus:ring-2 focus:ring-pecan-dark/50 dark:focus:ring-violet-sky/50 transition-all font-sans"
                                        placeholder="Jane"
                                    />
                                </div>
                                <div className="space-y-2">
                                    <label className="text-sm font-medium text-coffee-light dark:text-cream-400 ml-1">Last Name</label>
                                    <input
                                        type="text"
                                        required
                                        value={lastName}
                                        onChange={(e) => setLastName(e.target.value)}
                                        className="w-full px-4 py-3 bg-white dark:bg-white/5 border border-cream-200 dark:border-white/10 rounded-2xl text-coffee-dark dark:text-cream-100 placeholder-cream-400 focus:outline-none focus:ring-2 focus:ring-pecan-dark/50 dark:focus:ring-violet-sky/50 transition-all font-sans"
                                        placeholder="Doe"
                                    />
                                </div>
                            </div>
                        )}

                        <div className="space-y-2">
                            <label className="text-sm font-medium text-coffee-light dark:text-cream-400 ml-1">Email</label>
                            <input
                                type="email"
                                required
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                className="w-full px-4 py-3 bg-white dark:bg-white/5 border border-cream-200 dark:border-white/10 rounded-2xl text-coffee-dark dark:text-cream-100 placeholder-cream-400 focus:outline-none focus:ring-2 focus:ring-pecan-dark/50 dark:focus:ring-violet-sky/50 transition-all font-sans"
                                placeholder="jane@example.com"
                            />
                        </div>

                        <div className="space-y-2">
                            <label className="text-sm font-medium text-coffee-light dark:text-cream-400 ml-1">Password</label>
                            <input
                                type="password"
                                required
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                className="w-full px-4 py-3 bg-white dark:bg-white/5 border border-cream-200 dark:border-white/10 rounded-2xl text-coffee-dark dark:text-cream-100 placeholder-cream-400 focus:outline-none focus:ring-2 focus:ring-pecan-dark/50 dark:focus:ring-violet-sky/50 transition-all font-sans"
                                placeholder="••••••••"
                            />
                        </div>

                        {mode === "register" && (
                            <div className="space-y-2">
                                <label className="text-sm font-medium text-coffee-light dark:text-cream-400 ml-1">Confirm Password</label>
                                <input
                                    type="password"
                                    required
                                    value={confirmPassword}
                                    onChange={(e) => setConfirmPassword(e.target.value)}
                                    className="w-full px-4 py-3 bg-white dark:bg-white/5 border border-cream-200 dark:border-white/10 rounded-2xl text-coffee-dark dark:text-cream-100 placeholder-cream-400 focus:outline-none focus:ring-2 focus:ring-pecan-dark/50 dark:focus:ring-violet-sky/50 transition-all font-sans"
                                    placeholder="••••••••"
                                />
                            </div>
                        )}

                        <button
                            type="submit"
                            disabled={isLoading}
                            className="w-full py-4 bg-coffee-dark dark:bg-violet-sky-dark text-white font-bold rounded-2xl hover:scale-[1.02] active:scale-[0.98] transition-all shadow-lg shadow-coffee/20 dark:shadow-violet-sky/20 flex items-center justify-center gap-2 disabled:opacity-70 disabled:hover:scale-100"
                        >
                            {isLoading ? (
                                <div className="w-6 h-6 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                            ) : mode === "login" ? (
                                <><LogIn className="w-5 h-5" /> Sign In</>
                            ) : (
                                <><UserPlus className="w-5 h-5" /> Create Account</>
                            )}
                        </button>
                    </form>

                    <div className="relative">
                        <div className="absolute inset-0 flex items-center">
                            <div className="w-full border-t border-cream-200 dark:border-white/10"></div>
                        </div>
                        <div className="relative flex justify-center text-xs uppercase">
                            <span className="bg-white dark:bg-[#0f172a] px-2 text-coffee-light dark:text-cream-400">Or continue with</span>
                        </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                        <button
                            onClick={() => signIn("google", { callbackUrl: "/dashboard" })}
                            className="flex items-center justify-center gap-2 py-3 px-4 bg-white dark:bg-white/5 border border-cream-200 dark:border-white/10 rounded-2xl text-coffee-dark dark:text-cream-200 font-medium hover:bg-cream-50 dark:hover:bg-white/10 transition-colors"
                        >
                            <svg className="w-5 h-5" viewBox="0 0 24 24">
                                <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4" />
                                <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853" />
                                <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05" />
                                <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335" />
                            </svg>
                            Google
                        </button>
                        <button
                            onClick={handleGuestLogin}
                            className="flex items-center justify-center gap-2 py-3 px-4 bg-white dark:bg-white/5 border border-cream-200 dark:border-white/10 rounded-2xl text-coffee-dark dark:text-cream-200 font-medium hover:bg-cream-50 dark:hover:bg-white/10 transition-colors"
                        >
                            Guest Mode
                        </button>
                    </div>

                    <div className="text-center">
                        <button
                            onClick={() => setMode(mode === "login" ? "register" : "login")}
                            className="text-sm text-coffee-light dark:text-cream-400 hover:text-pecan-dark dark:hover:text-violet-sky-light transition-colors"
                        >
                            {mode === "login" ? "Don't have an account? Create one" : "Already have an account? Sign in"}
                        </button>
                    </div>
                </div>
            </div>

            <style>{`
                .animate-fade-in {
                    animation: fadeIn 0.8s ease-out forwards;
                    opacity: 0;
                    transform: translateY(20px);
                }
                @keyframes fadeIn {
                    to {
                        opacity: 1;
                        transform: translateY(0);
                    }
                }
            `}</style>
        </div>
    );
}

export default function LoginPage() {
    return (
        <Suspense fallback={<div className="min-h-screen flex items-center justify-center bg-cream-100 dark:bg-coffee text-cream-500">Loading...</div>}>
            <LoginContent />
        </Suspense>
    );
}
