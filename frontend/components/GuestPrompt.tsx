"use client";
/**
 * Shown on account-only pages/actions when a guest (or logged-out visitor)
 * tries to use them. Nudges them to the auth screen via exitGuest().
 */
import { useAuth } from "@/lib/auth";

export default function GuestPrompt({ title, body }: { title: string; body: string }) {
  const { exitGuest } = useAuth();
  return (
    <div
      className="px-6 py-12 text-center"
      style={{ background: "var(--bg-card)", border: "1px solid var(--border)", borderRadius: 4 }}
    >
      <p className="serif text-3xl font-light mb-3">{title}</p>
      <p className="text-sm leading-relaxed mb-7 mx-auto" style={{ color: "var(--text-muted)", maxWidth: 360 }}>
        {body}
      </p>
      <button
        onClick={exitGuest}
        style={{
          background: "var(--accent)", color: "#080808", border: "none",
          padding: "12px 32px", fontSize: 11, letterSpacing: "0.2em", textTransform: "uppercase",
          fontFamily: "inherit", borderRadius: 3, fontWeight: 500, cursor: "pointer",
        }}
      >
        Create an account →
      </button>
      <p className="text-[10px] tracking-widest uppercase mt-4" style={{ color: "var(--text-faint)" }}>
        Takes 10 seconds · 1,000 points to start
      </p>
    </div>
  );
}
