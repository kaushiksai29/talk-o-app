import NextAuth, { NextAuthOptions } from "next-auth";
import GoogleProvider from "next-auth/providers/google";
import CredentialsProvider from "next-auth/providers/credentials";

export const authOptions: NextAuthOptions = {
    providers: [
        GoogleProvider({
            clientId: process.env.GOOGLE_CLIENT_ID || "",
            clientSecret: process.env.GOOGLE_CLIENT_SECRET || "",
        }),
        CredentialsProvider({
            name: "Credentials",
            credentials: {
                email: { label: "Email", type: "email" },
                password: { label: "Password", type: "password" }
            },
            async authorize(credentials) {
                if (!credentials?.email || !credentials?.password) return null;

                try {
                    const formData = new FormData();
                    formData.append("email", credentials.email);
                    formData.append("password", credentials.password);

                    const apiUrl = process.env.NEXT_PUBLIC_API_URL || "https://talk-o-app-production.up.railway.app";
                    const res = await fetch(`${apiUrl}/login`, {
                        method: "POST",
                        body: formData,
                    });

                    if (res.ok) {
                        const user = await res.json();
                        return user; // { id, email, name, access_token }
                    }
                    return null;
                } catch (e) {
                    console.error("Login authorization failed", e);
                    return null;
                }
            }
        })
    ],
    pages: {
        signIn: '/login',
    },
    callbacks: {
        async jwt({ token, account, user }: { token: any, account: any, user?: any }) {
            if (account) {
                token.provider = account.provider;
            }
            if (user) {
                token.userId = user.id;
            }
            return token;
        },
        async session({ session, token }: { session: any, token: any }) {
            if (token.userId) {
                session.user.id = token.userId;
            }

            // Sync OAuth users with backend
            if (token.provider === "google" && session?.user?.email) {
                try {
                    const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'https://talk-o-app-production.up.railway.app'}/users`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            email: session.user.email,
                            name: session.user.name || "User",
                            provider: "google",
                            image: session.user.image
                        })
                    });

                    if (res.ok) {
                        const userData = await res.json();
                        session.user.id = userData.id;
                    }
                } catch (e) {
                    console.error("Failed to sync OAuth user with backend", e);
                }
            }
            return session;
        }
    }
};
