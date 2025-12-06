"use client";

import { useEffect, useState, Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import Link from "next/link";
import { CheckCircle, XCircle, Loader2 } from "lucide-react";

function VerifyEmailContent() {
    const searchParams = useSearchParams();
    const router = useRouter();
    const token = searchParams.get("token");
    const [status, setStatus] = useState<"loading" | "success" | "error">("loading");
    const [message, setMessage] = useState("Verifying your email...");

    useEffect(() => {
        if (!token) {
            setStatus("error");
            setMessage("Invalid verification link.");
            return;
        }

        const verify = async () => {
            try {
                const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "https://sahkwja1.up.railway.app"}/verify`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ token }),
                });

                if (!res.ok) {
                    const data = await res.json();
                    throw new Error(data.detail || "Verification failed");
                }

                setStatus("success");
                setMessage("Email verified successfully! You can now log in.");

                // Redirect to login after 3 seconds
                setTimeout(() => {
                    router.push("/login");
                }, 3000);
            } catch (err: any) {
                setStatus("error");
                setMessage(err.message || "Verification failed. The link may be invalid or expired.");
            }
        };

        verify();
    }, [token, router]);

    return (
        <div className="min-h-screen bg-cream-gradient dark:bg-dark-gradient flex items-center justify-center p-4">
            <div className="bg-white/80 dark:bg-[#0f172a]/80 backdrop-blur-md p-8 rounded-[2rem] shadow-2xl max-w-md w-full text-center border border-cream-200 dark:border-white/5">
                <div className="flex justify-center mb-6">
                    {status === "loading" && <Loader2 className="w-16 h-16 text-pecan-400 animate-spin" />}
                    {status === "success" && <CheckCircle className="w-16 h-16 text-green-500" />}
                    {status === "error" && <XCircle className="w-16 h-16 text-red-500" />}
                </div>

                <h1 className="text-2xl font-serif font-bold text-coffee-dark dark:text-cream-100 mb-4">
                    {status === "loading" ? "Verifying..." : status === "success" ? "Verified!" : "Verification Failed"}
                </h1>

                <p className="text-coffee-light dark:text-cream-400 mb-8">
                    {message}
                </p>

                {status === "success" && (
                    <Link href="/login" className="inline-block px-8 py-3 bg-coffee-dark dark:bg-violet-sky-dark text-white rounded-xl font-bold hover:scale-105 transition-transform">
                        Go to Login
                    </Link>
                )}

                {status === "error" && (
                    <Link href="/login" className="inline-block px-8 py-3 bg-cream-200 dark:bg-white/10 text-coffee-dark dark:text-cream-100 rounded-xl font-bold hover:bg-cream-300 dark:hover:bg-white/20 transition-colors">
                        Back to Login
                    </Link>
                )}
            </div>
        </div>
    );
}

export default function VerifyEmailPage() {
    return (
        <Suspense fallback={<div className="min-h-screen flex items-center justify-center bg-cream-100 dark:bg-coffee text-cream-500">Loading...</div>}>
            <VerifyEmailContent />
        </Suspense>
    );
}
