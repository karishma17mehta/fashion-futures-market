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

export async function createUser(username: string) {
  const res = await fetch(`${BASE}/users/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username }),
  });
  return res.json();
}
