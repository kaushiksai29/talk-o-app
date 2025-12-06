import NextAuth, { NextAuthOptions } from "next-auth";
import GoogleProvider from "next-auth/providers/google";

export const authOptions: NextAuthOptions = {
    providers: [
        GoogleProvider({
            clientId: process.env.GOOGLE_CLIENT_ID || "",
            clientSecret: process.env.GOOGLE_CLIENT_SECRET || "",
        }),
    ],
    pages: {
        signIn: '/login',
    },
    callbacks: {
        async jwt({ token, account }: { token: any, account: any }) {
            if (account) {
                token.provider = account.provider;
            }
            return token;
        },
        async session({ session, token }: { session: any, token: any }) {
            // Send user to backend to ensure they exist in our DB
            try {
                if (session?.user?.email) {
                    let provider = token.provider || "credentials";
                    if (provider === "azure-ad") provider = "microsoft";

                    // Fix: Added missing parentheses for fetch call
                    const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'https://talk-o-app-production.up.railway.app'}/users`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            email: session.user.email,
                            name: session.user.name || "User",
                            provider: provider,
                            image: session.user.image
                        })
                    });

                    if (res.ok) {
                        const userData = await res.json();
                        session.user.id = userData.id;
                    }
                }
            } catch (e) {
                console.error("Failed to sync user with backend", e);
            }
            return session;
        }
    }
};
