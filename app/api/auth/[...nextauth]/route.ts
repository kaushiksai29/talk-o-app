import NextAuth from "next-auth";
import GoogleProvider from "next-auth/providers/google";
import AzureADProvider from "next-auth/providers/azure-ad";
import AppleProvider from "next-auth/providers/apple";
import CredentialsProvider from "next-auth/providers/credentials";

export const authOptions = {
    providers: [
        GoogleProvider({
            clientId: process.env.GOOGLE_CLIENT_ID || "",
            clientSecret: process.env.GOOGLE_CLIENT_SECRET || "",
        }),
        AzureADProvider({
            clientId: process.env.AZURE_AD_CLIENT_ID || "",
            clientSecret: process.env.AZURE_AD_CLIENT_SECRET || "",
            tenantId: process.env.AZURE_AD_TENANT_ID,
        }),
        AppleProvider({
            clientId: process.env.APPLE_ID || "",
            clientSecret: {
                appleId: process.env.APPLE_ID || "",
                teamId: process.env.APPLE_TEAM_ID || "",
                privateKey: (process.env.APPLE_PRIVATE_KEY || "").replace(/\\n/g, "\n"),
                keyId: process.env.APPLE_KEY_ID || "",
            },
        }),
        CredentialsProvider({
            name: "Credentials",
            credentials: {
                email: { label: "Email", type: "text" },
                password: { label: "Password", type: "password" }
            },
            async authorize(credentials) {
                if (!credentials?.email || !credentials?.password) return null;

                try {
                    const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/login`, {
                        method: "POST",
                        headers: { "Content-Type": "application/x-www-form-urlencoded" },
                        body: new URLSearchParams({
                            email: credentials.email,
                            password: credentials.password,
                        }),
                    });

                    const user = await res.json();

                    if (res.ok && user) {
                        return user;
                    }
                    return null;
                } catch (e) {
                    console.error("Login failed", e);
                    return null;
                }
            }
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

                    const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/users`, {
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

const handler = NextAuth(authOptions);

export { handler as GET, handler as POST };
