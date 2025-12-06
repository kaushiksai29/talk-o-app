import type { Metadata } from "next";
import { Fraunces, DM_Sans } from "next/font/google";
import "./globals.css";

const fraunces = Fraunces({
  subsets: ["latin"],
  variable: "--font-fraunces",
  display: "swap",
});

const dmSans = DM_Sans({
  subsets: ["latin"],
  variable: "--font-dm-sans",
  display: "swap",
});

export const metadata: Metadata = {
  title: "Talk-o | Your ADHD Support Companion",
  description: "Chat with Stargirl and Sage - AI companions designed to support people with ADHD through meaningful conversations and guidance.",
  icons: {
    icon: '/icon.png',
  },
};

import { Providers } from "./providers";

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body
        className={`${fraunces.variable} ${dmSans.variable} antialiased bg-cream-gradient dark:bg-dark-gradient text-cream-900 dark:text-cream-100 min-h-screen transition-colors duration-500`}
      >
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
