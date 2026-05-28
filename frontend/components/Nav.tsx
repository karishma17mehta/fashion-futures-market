"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";

const links = [
  { href: "/", label: "Markets" },
  { href: "/trends", label: "Trends" },
  { href: "/leaderboard", label: "Leaderboard" },
];

export default function Nav() {
  const path = usePathname();
  return (
    <nav className="border-b border-white/10 bg-[#0a0a0f]/80 backdrop-blur sticky top-0 z-50">
      <div className="max-w-6xl mx-auto px-4 h-14 flex items-center justify-between">
        <Link href="/" className="font-bold text-lg tracking-tight">
          <span className="text-white">Fashion</span>
          <span className="text-rose-400"> Futures</span>
        </Link>
        <div className="flex gap-6 text-sm">
          {links.map((l) => (
            <Link
              key={l.href}
              href={l.href}
              className={path === l.href ? "text-white font-medium" : "text-white/50 hover:text-white transition-colors"}
            >
              {l.label}
            </Link>
          ))}
        </div>
      </div>
    </nav>
  );
}
