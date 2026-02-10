import "./globals.css";
import { Inter, JetBrains_Mono } from "next/font/google";
import { AuthProvider } from "@/components/AuthProvider";
import Navbar from "@/components/Navbar";

const sans = Inter({ subsets: ["latin"], variable: "--font-sans" });
const mono = JetBrains_Mono({ subsets: ["latin"], variable: "--font-mono" });

const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL || "https://ideaforge.dev";

export const metadata = {
  metadataBase: new URL(SITE_URL),
  title: {
    default: "IdeaForge — Turn Ideas into Build-Ready Packages",
    template: "%s | IdeaForge",
  },
  description:
    "Transform any product idea into an optimized tech stack, code-gen prompts, documentation, and a phased implementation plan.",
  keywords: [
    "AI code generation",
    "build package",
    "tech stack selection",
    "code prompts",
    "SaaS builder",
    "implementation plan",
  ],
  authors: [{ name: "IdeaForge" }],
  creator: "IdeaForge",
  openGraph: {
    type: "website",
    locale: "en_US",
    url: SITE_URL,
    siteName: "IdeaForge",
    title: "IdeaForge — Turn Ideas into Build-Ready Packages",
    description:
      "Drop in a product idea and get a tech stack, code-gen prompts, full documentation, and an implementation plan — all in one pass.",
    images: [
      {
        url: "/og-image.png",
        width: 1200,
        height: 630,
        alt: "IdeaForge — AI-Powered Build Packages",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "IdeaForge — Turn Ideas into Build-Ready Packages",
    description:
      "Drop in a product idea and get a tech stack, code-gen prompts, full documentation, and an implementation plan.",
    images: ["/og-image.png"],
  },
  icons: {
    icon: "/icon.svg",
  },
  manifest: "/manifest.webmanifest",
};

export const viewport = {
  themeColor: "#0a0a0f",
  width: "device-width",
  initialScale: 1,
};

export default function RootLayout({ children }) {
  return (
    <html lang="en" className={`${sans.variable} ${mono.variable}`}>
      <body>
        <AuthProvider>
          <Navbar />
          <div className="app-content">
            {children}
          </div>
        </AuthProvider>
      </body>
    </html>
  );
}
