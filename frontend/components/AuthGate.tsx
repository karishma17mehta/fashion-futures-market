"use client";
/**
 * Entry flow for non-authenticated visitors:
 *   1. Dramatic splash  ("Trade wisely") → Enter
 *   2. Login / signup    (or "just browsing" → guest mode)
 * Logged-in users and guests fall straight through to the app.
 */
import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "@/lib/auth";

// Routes viewable without signing in (e.g. legal pages).
const PUBLIC_PATHS = ["/terms"];

export default function AuthGate({ children }: { children: React.ReactNode }) {
  const { user, loading, isGuest, login, signup, continueAsGuest } = useAuth();
  const pathname = usePathname();
  const [entered, setEntered] = useState(false);
  const [mode, setMode] = useState<"login" | "signup">("signup");
  const [email, setEmail] = useState("");
  const [name, setName] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  if (loading) {
    return (
      <div style={{ minHeight: "100vh", display: "grid", placeItems: "center", background: "var(--bg)" }}>
        <p className="text-xs tracking-widest uppercase" style={{ color: "var(--text-faint)" }}>Loading…</p>
      </div>
    );
  }

  // Logged in OR browsing as guest OR on a public page → show the app.
  if (user || isGuest || PUBLIC_PATHS.includes(pathname)) return <>{children}</>;

  // ── Splash ──────────────────────────────────────────────────────────────
  if (!entered) {
    return (
      <div style={splashWrap}>
        <div className="fade-up" style={{ textAlign: "center", maxWidth: 620, padding: 24 }}>
          <p className="text-[10px] tracking-[0.4em] uppercase mb-8" style={{ color: "var(--text-faint)" }}>
            Fashion Prediction Intelligence
          </p>
          <h1 className="serif font-light" style={{ fontSize: "clamp(44px, 8vw, 92px)", lineHeight: 1.05, letterSpacing: "-0.01em" }}>
            Trade the future<br />
            of <span style={{ fontStyle: "italic", color: "var(--accent)" }}>fashion</span>.
          </h1>
          <p className="text-base leading-relaxed mt-8 mx-auto" style={{ color: "var(--text-muted)", maxWidth: 460 }}>
            Every emerging aesthetic becomes a market - backed by real signal data.
            Predict what goes mainstream before it does, and prove your eye against everyone else.
            Read the signals. Trade wisely.
          </p>
          <button onClick={() => setEntered(true)} style={{ ...primaryBtn, width: "auto", padding: "15px 48px", marginTop: 44 }}>
            Enter the market →
          </button>
          <p className="text-[10px] tracking-widest uppercase mt-6" style={{ color: "var(--text-faint)" }}>
            Play money · No risk · Just foresight
          </p>
        </div>
      </div>
    );
  }

  // ── Auth ────────────────────────────────────────────────────────────────
  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setBusy(true);
    const res = mode === "signup" ? await signup(email, name, password) : await login(email, password);
    setBusy(false);
    if (!res.ok) setError(res.error || "Something went wrong.");
  };
  const swap = (m: "login" | "signup") => { setMode(m); setError(""); };

  return (
    <div style={{ minHeight: "100vh", display: "grid", placeItems: "center", background: "var(--bg)", padding: 24 }}>
      <div style={{ width: "100%", maxWidth: 420 }} className="fade-up">
        <div style={{ textAlign: "center", marginBottom: 32 }}>
          <p className="serif italic text-3xl font-light" style={{ color: "var(--accent)" }}>Fashion Futures</p>
          <p className="text-[10px] tracking-[0.3em] uppercase mt-2" style={{ color: "var(--text-faint)" }}>
            Prediction Intelligence
          </p>
        </div>

        <h1 className="serif text-3xl font-light mb-3" style={{ textAlign: "center" }}>
          {mode === "signup" ? "Create your account" : "Welcome back"}
        </h1>
        <p className="text-sm leading-relaxed mb-7" style={{ color: "var(--text-muted)", textAlign: "center" }}>
          {mode === "signup"
            ? "Start with 1,000 points to bet on emerging fashion trends."
            : "Log in to your portfolio and points."}
        </p>

        <form onSubmit={submit} style={{ display: "flex", flexDirection: "column", gap: 12 }}>
          <input autoFocus type="email" value={email} autoComplete="email"
            onChange={(e) => { setEmail(e.target.value); setError(""); }} placeholder="Email" style={inputStyle(false)} />
          {mode === "signup" && (
            <input type="text" value={name} maxLength={24}
              onChange={(e) => { setName(e.target.value); setError(""); }}
              placeholder="Display name (shown on leaderboard)" style={inputStyle(false)} />
          )}
          <input type="password" value={password}
            autoComplete={mode === "signup" ? "new-password" : "current-password"}
            onChange={(e) => { setPassword(e.target.value); setError(""); }} placeholder="Password" style={inputStyle(!!error)} />

          {error && <p className="text-xs" style={{ color: "#e05a5a", textAlign: "center" }}>{error}</p>}

          <button type="submit" disabled={busy} style={{ ...primaryBtn, opacity: busy ? 0.5 : 1, cursor: busy ? "not-allowed" : "pointer" }}>
            {busy ? "Please wait…" : mode === "signup" ? "Create account →" : "Log in →"}
          </button>
        </form>

        {mode === "signup" && (
          <p className="text-[10px] leading-relaxed mt-4" style={{ color: "var(--text-faint)", textAlign: "center" }}>
            By creating an account you agree to our{" "}
            <Link href="/terms" style={{ color: "var(--text-muted)", textDecoration: "underline" }}>
              Terms &amp; Privacy
            </Link>
            . Play money only - no real wagering.
          </p>
        )}

        <p className="text-xs mt-6" style={{ color: "var(--text-faint)", textAlign: "center" }}>
          {mode === "signup"
            ? <>Already have an account? <button onClick={() => swap("login")} style={linkBtn}>Log in</button></>
            : <>New here? <button onClick={() => swap("signup")} style={linkBtn}>Create an account</button></>}
        </p>

        {/* Guest path */}
        <div style={{ marginTop: 24, paddingTop: 20, borderTop: "1px solid var(--border)", textAlign: "center" }}>
          <button onClick={continueAsGuest} className="text-xs tracking-widest uppercase transition-colors"
            style={{ color: "var(--text-muted)", background: "none", border: "none", cursor: "pointer", fontFamily: "inherit" }}>
            Just browsing - explore without an account →
          </button>
        </div>
      </div>
    </div>
  );
}

const splashWrap: React.CSSProperties = {
  minHeight: "100vh",
  display: "grid",
  placeItems: "center",
  background: "radial-gradient(ellipse at 50% 35%, rgba(212,168,83,0.08), var(--bg) 60%)",
};

function inputStyle(err: boolean): React.CSSProperties {
  return {
    width: "100%", background: "var(--bg-card)",
    border: `1px solid ${err ? "#e05a5a" : "var(--border)"}`,
    color: "var(--text)", padding: "13px 16px", fontSize: 15,
    fontFamily: "inherit", outline: "none", borderRadius: 3,
  };
}

const primaryBtn: React.CSSProperties = {
  width: "100%", background: "var(--accent)", color: "#080808", border: "none",
  padding: "13px 24px", fontSize: 11, letterSpacing: "0.2em", textTransform: "uppercase",
  fontFamily: "inherit", borderRadius: 3, fontWeight: 500, marginTop: 4, cursor: "pointer",
};

const linkBtn: React.CSSProperties = {
  background: "none", border: "none", color: "var(--accent)", cursor: "pointer",
  fontFamily: "inherit", fontSize: "inherit", padding: 0, textDecoration: "underline",
};
