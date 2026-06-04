"use client";
/**
 * Gates the app behind email+password auth.
 * - Restoring session: minimal loader.
 * - No user: login / signup screen (toggle).
 * - User present: renders the app.
 */
import { useState } from "react";
import { useAuth } from "@/lib/auth";

export default function AuthGate({ children }: { children: React.ReactNode }) {
  const { user, loading, login, signup } = useAuth();
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

  if (user) return <>{children}</>;

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setBusy(true);
    const res = mode === "signup"
      ? await signup(email, name, password)
      : await login(email, password);
    setBusy(false);
    if (!res.ok) setError(res.error || "Something went wrong.");
    // On success the provider sets `user`, which swaps in the app automatically.
  };

  const swap = (m: "login" | "signup") => { setMode(m); setError(""); };

  return (
    <div style={{ minHeight: "100vh", display: "grid", placeItems: "center", background: "var(--bg)", padding: 24 }}>
      <div style={{ width: "100%", maxWidth: 420 }} className="fade-up">
        {/* Wordmark */}
        <div style={{ textAlign: "center", marginBottom: 36 }}>
          <p className="serif italic text-3xl font-light" style={{ color: "var(--accent)" }}>Fashion Futures</p>
          <p className="text-[10px] tracking-[0.3em] uppercase mt-2" style={{ color: "var(--text-faint)" }}>
            Prediction Intelligence
          </p>
        </div>

        <h1 className="serif text-3xl font-light mb-3" style={{ textAlign: "center" }}>
          {mode === "signup" ? "Trade trends before they break" : "Welcome back"}
        </h1>
        <p className="text-sm leading-relaxed mb-7" style={{ color: "var(--text-muted)", textAlign: "center" }}>
          {mode === "signup"
            ? "Create an account and get 1,000 points to bet on emerging fashion trends."
            : "Log in to your portfolio and points."}
        </p>

        <form onSubmit={submit} style={{ display: "flex", flexDirection: "column", gap: 12 }}>
          <input
            autoFocus type="email" value={email}
            onChange={(e) => { setEmail(e.target.value); setError(""); }}
            placeholder="Email" autoComplete="email" style={inputStyle(false)}
          />
          {mode === "signup" && (
            <input
              type="text" value={name} maxLength={24}
              onChange={(e) => { setName(e.target.value); setError(""); }}
              placeholder="Display name (shown on leaderboard)" style={inputStyle(false)}
            />
          )}
          <input
            type="password" value={password}
            onChange={(e) => { setPassword(e.target.value); setError(""); }}
            placeholder="Password"
            autoComplete={mode === "signup" ? "new-password" : "current-password"}
            style={inputStyle(!!error)}
          />

          {error && <p className="text-xs" style={{ color: "#e05a5a", textAlign: "center" }}>{error}</p>}

          <button type="submit" disabled={busy} style={{ ...primaryBtn, opacity: busy ? 0.5 : 1, cursor: busy ? "not-allowed" : "pointer" }}>
            {busy ? "Please wait…" : mode === "signup" ? "Create account →" : "Log in →"}
          </button>
        </form>

        {/* Toggle */}
        <p className="text-xs mt-6" style={{ color: "var(--text-faint)", textAlign: "center" }}>
          {mode === "signup" ? (
            <>Already have an account?{" "}
              <button onClick={() => swap("login")} style={linkBtn}>Log in</button>
            </>
          ) : (
            <>New here?{" "}
              <button onClick={() => swap("signup")} style={linkBtn}>Create an account</button>
            </>
          )}
        </p>
      </div>
    </div>
  );
}

function inputStyle(err: boolean): React.CSSProperties {
  return {
    width: "100%",
    background: "var(--bg-card)",
    border: `1px solid ${err ? "#e05a5a" : "var(--border)"}`,
    color: "var(--text)",
    padding: "13px 16px",
    fontSize: 15,
    fontFamily: "inherit",
    outline: "none",
    borderRadius: 3,
  };
}

const primaryBtn: React.CSSProperties = {
  width: "100%",
  background: "var(--accent)",
  color: "#080808",
  border: "none",
  padding: "13px 24px",
  fontSize: 11,
  letterSpacing: "0.2em",
  textTransform: "uppercase",
  fontFamily: "inherit",
  borderRadius: 3,
  fontWeight: 500,
  marginTop: 4,
};

const linkBtn: React.CSSProperties = {
  background: "none",
  border: "none",
  color: "var(--accent)",
  cursor: "pointer",
  fontFamily: "inherit",
  fontSize: "inherit",
  padding: 0,
  textDecoration: "underline",
};
