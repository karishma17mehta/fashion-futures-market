"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";

const links = [
  { href: "/",           label: "Markets" },
  { href: "/trends",     label: "Signals" },
  { href: "/portfolio",  label: "Portfolio" },
  { href: "/alerts",     label: "Alerts" },
  { href: "/leaderboard",label: "Leaderboard" },

];

export default function Nav() {
  const path = usePathname();
  return (
    <nav
      className="sticky top-0 z-50 backdrop-blur-md"
      style={{ borderBottom: "1px solid var(--border)", background: "rgba(8,8,8,0.85)" }}
    >
      <div className="max-w-5xl mx-auto px-5 h-14 flex items-center justify-between">
        {/* Wordmark */}
        <Link href="/" className="flex items-baseline gap-2">
          <span className="serif italic text-xl font-light" style={{ color: "var(--accent)" }}>
            Fashion Futures
          </span>
          <span
            className="text-[10px] tracking-[0.2em] uppercase hidden sm:inline"
            style={{ color: "var(--text-faint)" }}
          >
            Market
          </span>
        </Link>

        {/* Links */}
        <div className="flex items-center gap-7">
          {links.map((l) => {
            const active = path === l.href;
            return (
              <Link
                key={l.href}
                href={l.href}
                className="text-xs tracking-widest uppercase transition-colors duration-200"
                style={{ color: active ? "var(--accent)" : "var(--text-muted)" }}
              >
                {l.label}
              </Link>
            );
          })}
        </div>
      </div>
    </nav>
  );
}
