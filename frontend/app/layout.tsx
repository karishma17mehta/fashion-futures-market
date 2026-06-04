import type { Metadata } from "next";
import "./globals.css";
import Nav from "@/components/Nav";
import { AuthProvider } from "@/lib/auth";
import AuthGate from "@/components/AuthGate";

export const metadata: Metadata = {
  title: "Fashion Futures Market",
  description: "Trade fashion micro-trends before they go mainstream",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;1,300;1,400&family=Inter:wght@300;400;500&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="min-h-screen" style={{ background: "var(--bg)", color: "var(--text)" }}>
        <AuthProvider>
          <AuthGate>
            <Nav />
            <main className="max-w-5xl mx-auto px-5 py-10">{children}</main>
            <footer className="max-w-5xl mx-auto px-5 py-10 mt-16">
              <hr className="rule mb-6" />
              <div className="flex items-center justify-between">
                <span className="serif italic text-lg" style={{ color: "var(--accent)" }}>Fashion Futures</span>
                <span className="text-xs tracking-widest uppercase" style={{ color: "var(--text-faint)" }}>
                  Prediction Intelligence · 2026
                </span>
              </div>
            </footer>
          </AuthGate>
        </AuthProvider>
      </body>
    </html>
  );
}
