"use client";
/**
 * Email + password auth with JWT sessions.
 * - Token persisted in localStorage; restored on load via /auth/me.
 * - Display name (username) is public; email is the private login id.
 */
import { createContext, useContext, useEffect, useState, useCallback } from "react";
import { signupRequest, loginRequest, fetchMe } from "@/lib/api";

export type AuthUser = {
  id: string;
  username: string;
  points: number;
  xp?: number;
  streak_days?: number;
  rank?: string;
  accuracy_rate?: number;
  total_trades?: number;
  markets_won?: number;
  markets_lost?: number;
};

type Result = { ok: boolean; error?: string };

type AuthContextType = {
  user: AuthUser | null;
  loading: boolean;
  isGuest: boolean;
  signup: (email: string, username: string, password: string) => Promise<Result>;
  login: (email: string, password: string) => Promise<Result>;
  logout: () => void;
  refresh: () => Promise<void>;
  continueAsGuest: () => void;
  exitGuest: () => void;   // leave guest mode → show the auth screen
};

const TOKEN_KEY = "ff_token";
const GUEST_KEY = "ff_guest";
const AuthContext = createContext<AuthContextType | undefined>(undefined);

/** Turn a FastAPI error body into a readable string. */
function errMessage(body: any, fallback: string): string {
  if (!body) return fallback;
  if (typeof body.detail === "string") return body.detail;
  if (Array.isArray(body.detail) && body.detail[0]?.msg) {
    return body.detail[0].msg.replace(/^Value error,\s*/, "");
  }
  return fallback;
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [loading, setLoading] = useState(true);
  const [isGuest, setIsGuest] = useState(false);

  const continueAsGuest = useCallback(() => {
    localStorage.setItem(GUEST_KEY, "1");
    setIsGuest(true);
  }, []);
  const exitGuest = useCallback(() => {
    localStorage.removeItem(GUEST_KEY);
    setIsGuest(false);
  }, []);

  // Restore session from token on mount; also restore guest mode.
  useEffect(() => {
    if (typeof window === "undefined") { setLoading(false); return; }
    if (localStorage.getItem(GUEST_KEY)) setIsGuest(true);
    const token = localStorage.getItem(TOKEN_KEY);
    if (!token) { setLoading(false); return; }
    fetchMe(token)
      .then((u) => {
        if (u && u.id) setUser(u as AuthUser);
        else localStorage.removeItem(TOKEN_KEY); // expired/invalid
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const signup = useCallback(async (email: string, username: string, password: string): Promise<Result> => {
    const { ok, body } = await signupRequest(email.trim().toLowerCase(), username.trim(), password);
    if (ok && body.token) {
      localStorage.setItem(TOKEN_KEY, body.token);
      setUser(body.user as AuthUser);
      setIsGuest(false);
      return { ok: true };
    }
    return { ok: false, error: errMessage(body, "Could not create your account.") };
  }, []);

  const login = useCallback(async (email: string, password: string): Promise<Result> => {
    const { ok, body } = await loginRequest(email.trim().toLowerCase(), password);
    if (ok && body.token) {
      localStorage.setItem(TOKEN_KEY, body.token);
      setUser(body.user as AuthUser);
      setIsGuest(false);
      return { ok: true };
    }
    return { ok: false, error: errMessage(body, "Could not log you in.") };
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(GUEST_KEY);
    setUser(null);
  }, []);

  const refresh = useCallback(async () => {
    const token = localStorage.getItem(TOKEN_KEY);
    if (!token) return;
    const u = await fetchMe(token);
    if (u && u.id) setUser(u as AuthUser);
  }, []);

  return (
    <AuthContext.Provider value={{ user, loading, isGuest, signup, login, logout, refresh, continueAsGuest, exitGuest }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within <AuthProvider>");
  return ctx;
}
