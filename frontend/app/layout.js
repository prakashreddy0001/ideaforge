import "./globals.css";
import { Inter, JetBrains_Mono } from "next/font/google";
import { AuthProvider } from "@/components/AuthProvider";
import Navbar from "@/components/Navbar";

const sans = Inter({ subsets: ["latin"], variable: "--font-sans" });
const mono = JetBrains_Mono({ subsets: ["latin"], variable: "--font-mono" });

export const metadata = {
  title: "IdeaForge",
  description:
    "Turn a rough idea into a build-ready package — stack, prompts, docs, and plan.",
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
