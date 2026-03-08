import type { Metadata, Viewport } from "next";
import { Inter, Outfit, Geist_Mono } from "next/font/google";
import { Providers } from "@/providers/Providers";
import "./globals.css";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
  display: "swap",
});

const outfit = Outfit({
  variable: "--font-outfit",
  subsets: ["latin"],
  display: "swap",
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
  display: "swap",
});

export const metadata: Metadata = {
  title: {
    default: "AssignMind — AI-Powered Team Collaboration",
    template: "%s | AssignMind",
  },
  description:
    "AI-powered academic team collaboration platform. Upload assignments, distribute tasks intelligently, and collaborate with your team.",
  keywords: [
    "team collaboration",
    "AI assignment",
    "task distribution",
    "academic",
    "kanban",
  ],
  authors: [{ name: "AssignMind" }],
  manifest: "/manifest.json",
};

export const viewport: Viewport = {
  themeColor: "#6366f1",
  width: "device-width",
  initialScale: 1,
};

interface RootLayoutProps {
  children: React.ReactNode;
}

export default function RootLayout({ children }: Readonly<RootLayoutProps>) {
  return (
    <html lang="en" dir="ltr" suppressHydrationWarning>
      <head>
        <link rel="apple-touch-icon" href="/icons/icon-192x192.png" />
        <meta name="apple-mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />
        <meta name="mobile-web-app-capable" content="yes" />
      </head>
      <body
        className={`${inter.variable} ${outfit.variable} ${geistMono.variable} antialiased`}
      >
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}

