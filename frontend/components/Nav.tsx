"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "@/lib/auth";

const links = [
  { href: "/",           label: "Markets" },
  { href: "/trends",     label: "Signals" },
  { href: "/report",     label: "Report" },
  { href: "/portfolio",  label: "Portfolio" },
  { href: "/alerts",     label: "Alerts" },
  { href: "/leaderboard",label: "Leaderboard" },
  { href: "/about",      label: "About" },
];

export default function Nav() {
  const path = usePathname();
  const { user, logout, isGuest, exitGuest } = useAuth();
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

          {/* Account */}
          {user ? (
            <div className="flex items-center gap-3 pl-5" style={{ borderLeft: "1px solid var(--border)" }}>
              <div className="text-right leading-tight">
                <p className="text-xs" style={{ color: "var(--text)" }}>{user.username}</p>
                <p className="text-[10px]" style={{ color: "var(--accent)" }}>
                  {user.points.toLocaleString()} pts
                </p>
              </div>
              <button
                onClick={logout}
                title="Log out"
                className="text-[10px] tracking-widest uppercase transition-colors"
                style={{ color: "var(--text-faint)" }}
              >
                Log out
              </button>
            </div>
          ) : isGuest ? (
            <button
              onClick={exitGuest}
              className="text-[10px] tracking-widest uppercase pl-5"
              style={{ color: "var(--accent)", borderLeft: "1px solid var(--border)" }}
            >
              Sign up / Log in
            </button>
          ) : null}
        </div>
      </div>
    </nav>
  );
}
