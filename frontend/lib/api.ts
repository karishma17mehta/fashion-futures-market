const BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function fetchTrends(limit = 30, minScore?: number) {
  const params = new URLSearchParams({ limit: String(limit) });
  if (minScore) params.set("min_score", String(minScore));
  const res = await fetch(`${BASE}/trends/?${params}`, { cache: "no-store" });
  return res.json();
}

export async function fetchTrend(id: string) {
  const res = await fetch(`${BASE}/trends/${id}`, { cache: "no-store" });
  return res.json();
}

export async function fetchMarkets(status = "open") {
  const res = await fetch(`${BASE}/markets/?status=${status}`, { cache: "no-store" });
  return res.json();
}

export async function fetchMarket(id: string) {
  const res = await fetch(`${BASE}/markets/${id}`, { cache: "no-store" });
  return res.json();
}

export async function placeTrade(marketId: string, userId: string, position: "yes" | "no", amount: number) {
  const res = await fetch(`${BASE}/markets/${marketId}/trade`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_id: userId, position, amount }),
  });
  return res.json();
}

export async function fetchUser(id: string) {
  const res = await fetch(`${BASE}/users/${id}`, { cache: "no-store" });
  return res.json();
}

export async function fetchLeaderboard() {
  const res = await fetch(`${BASE}/users/leaderboard`, { cache: "no-store" });
  return res.json();
}

export async function fetchPositions(userId: string) {
  const res = await fetch(`${BASE}/users/${userId}/positions`, { cache: "no-store" });
  return res.json();
}

export async function fetchSignals(params?: {
  limit?: number;
  min_score?: number;
  source?: string;
  cross_platform_only?: boolean;
}) {
  const p = new URLSearchParams();
  if (params?.limit)                p.set("limit", String(params.limit));
  if (params?.min_score)            p.set("min_score", String(params.min_score));
  if (params?.source)               p.set("source", params.source);
  if (params?.cross_platform_only)  p.set("cross_platform_only", "true");
  const res = await fetch(`${BASE}/signals/top?${p}`, { cache: "no-store" });
  return res.json();
}

// ── Auth ──────────────────────────────────────────────────────────────────
export async function signupRequest(email: string, username: string, password: string) {
  const res = await fetch(`${BASE}/auth/signup`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, username, password }),
  });
  const body = await res.json().catch(() => ({}));
  return { ok: res.ok, status: res.status, body };
}

export async function loginRequest(email: string, password: string) {
  const res = await fetch(`${BASE}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  const body = await res.json().catch(() => ({}));
  return { ok: res.ok, status: res.status, body };
}

export async function fetchMe(token: string) {
  const res = await fetch(`${BASE}/auth/me`, {
    headers: { Authorization: `Bearer ${token}` },
    cache: "no-store",
  });
  if (!res.ok) return null;
  return res.json();
}

export async function fetchLatestReport() {
  const res = await fetch(`${BASE}/reports/latest`, { cache: "no-store" });
  if (!res.ok) return null;
  return res.json();
}
