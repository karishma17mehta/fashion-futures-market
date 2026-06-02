"use client";
import { useEffect, useState } from "react";
import Link from "next/link";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const USER_ID = "ed19647b-9a4e-4929-9467-d1b6f92a9cd4"; // same as portfolio

interface Alert {
  id: string;
  trend_name: string;
  min_score: number;
  source_filter: string | null;
  active: boolean;
  last_fired: string | null;
  created_at: string;
}

const SOURCES = [
  { value: "", label: "All sources" },
  { value: "tiktok", label: "TikTok" },
  { value: "editorial_rss", label: "Editorial" },
  { value: "reddit", label: "Reddit" },
  { value: "pinterest", label: "Pinterest" },
  { value: "google_trends", label: "Google Trends" },
];

export default function AlertsPage() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [deleting, setDeleting] = useState<string | null>(null);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  // Form state
  const [trendName, setTrendName] = useState("");
  const [minScore, setMinScore] = useState(7.0);
  const [sourceFilter, setSourceFilter] = useState("");

  const loadAlerts = async () => {
    try {
      const r = await fetch(`${API}/alerts/${USER_ID}`);
      const d = await r.json();
      setAlerts(d.alerts || []);
    } catch {
      setError("Could not load alerts — is the backend running?");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadAlerts(); }, []);

  const createAlert = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setSuccess("");
    if (!trendName.trim()) { setError("Enter a trend name or * for all trends"); return; }
    setCreating(true);
    try {
      const r = await fetch(`${API}/alerts/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id: USER_ID,
          trend_name: trendName.trim(),
          min_score: minScore,
          source_filter: sourceFilter || null,
        }),
      });
      if (!r.ok) {
        const d = await r.json();
        setError(d.detail || "Failed to create alert");
      } else {
        setSuccess(`Alert created for "${trendName}"`);
        setTrendName("");
        setMinScore(7.0);
        setSourceFilter("");
        await loadAlerts();
      }
    } catch {
      setError("Network error — backend may be offline");
    } finally {
      setCreating(false);
    }
  };

  const deleteAlert = async (id: string) => {
    setDeleting(id);
    try {
      await fetch(`${API}/alerts/${id}`, { method: "DELETE" });
      setAlerts((prev) => prev.filter((a) => a.id !== id));
    } finally {
      setDeleting(null);
    }
  };

  return (
    <div className="max-w-2xl space-y-10 pt-4 fade-up">
      {/* Back */}
      <Link href="/" className="text-[10px] tracking-widest uppercase transition-colors"
        style={{ color: "var(--text-faint)" }}>
        ← Home
      </Link>

      {/* Header */}
      <div>
        <p className="text-[9px] tracking-[0.3em] uppercase mb-3" style={{ color: "var(--accent)" }}>
          ✦ Trend Intelligence
        </p>
        <h1 className="serif text-4xl font-light mb-3">Alert Subscriptions</h1>
        <p className="text-sm" style={{ color: "var(--text-muted)" }}>
          Get notified when a trend hits your score threshold. Use <code style={{ color: "var(--accent)" }}>*</code> to watch all trends.
        </p>
      </div>

      {/* ── Create Form ─────────────────────────────────────────────────── */}
      <form onSubmit={createAlert}
        className="px-6 py-6 space-y-5"
        style={{ background: "var(--bg-card)", border: "1px solid var(--border)" }}>
        <p className="text-[9px] tracking-[0.3em] uppercase" style={{ color: "var(--text-faint)" }}>
          New Alert
        </p>

        {/* Trend name */}
        <div>
          <label className="block text-[9px] tracking-widest uppercase mb-2"
            style={{ color: "var(--text-faint)" }}>
            Trend Name
          </label>
          <input
            type="text"
            value={trendName}
            onChange={(e) => setTrendName(e.target.value)}
            placeholder='e.g.  Ballet Core  or  * for all trends'
            style={{
              width: "100%",
              background: "var(--bg)",
              border: "1px solid var(--border)",
              color: "var(--text)",
              padding: "10px 14px",
              fontSize: 13,
              fontFamily: "inherit",
              outline: "none",
              borderRadius: 2,
            }}
          />
        </div>

        {/* Score + Source row */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-[9px] tracking-widest uppercase mb-2"
              style={{ color: "var(--text-faint)" }}>
              Min Score — {minScore.toFixed(1)}
            </label>
            <input
              type="range"
              min={4} max={10} step={0.5}
              value={minScore}
              onChange={(e) => setMinScore(parseFloat(e.target.value))}
              style={{ width: "100%", accentColor: "var(--accent)" }}
            />
            <div className="flex justify-between text-[9px] mt-1" style={{ color: "var(--text-faint)" }}>
              <span>4.0</span><span>7.0</span><span>10.0</span>
            </div>
          </div>

          <div>
            <label className="block text-[9px] tracking-widest uppercase mb-2"
              style={{ color: "var(--text-faint)" }}>
              Source Filter
            </label>
            <select
              value={sourceFilter}
              onChange={(e) => setSourceFilter(e.target.value)}
              style={{
                width: "100%",
                background: "var(--bg)",
                border: "1px solid var(--border)",
                color: "var(--text)",
                padding: "10px 14px",
                fontSize: 12,
                fontFamily: "inherit",
                outline: "none",
                borderRadius: 2,
              }}
            >
              {SOURCES.map((s) => (
                <option key={s.value} value={s.value}>{s.label}</option>
              ))}
            </select>
          </div>
        </div>

        {/* Error / success */}
        {error && (
          <p className="text-xs" style={{ color: "#e05a5a" }}>{error}</p>
        )}
        {success && (
          <p className="text-xs" style={{ color: "var(--green)" }}>✓ {success}</p>
        )}

        {/* Submit */}
        <button
          type="submit"
          disabled={creating}
          style={{
            background: creating ? "var(--border)" : "var(--accent)",
            color: creating ? "var(--text-faint)" : "#080808",
            border: "none",
            padding: "10px 24px",
            fontSize: 10,
            letterSpacing: "0.2em",
            textTransform: "uppercase",
            cursor: creating ? "not-allowed" : "pointer",
            fontFamily: "inherit",
            borderRadius: 2,
            transition: "background 0.15s",
          }}
        >
          {creating ? "Creating…" : "Create Alert"}
        </button>
      </form>

      {/* ── Active Alerts ────────────────────────────────────────────────── */}
      <div>
        <p className="text-[9px] tracking-[0.3em] uppercase mb-5" style={{ color: "var(--text-faint)" }}>
          Active Alerts ({alerts.length})
        </p>

        {loading ? (
          <div className="space-y-px">
            {[1, 2, 3].map((i) => (
              <div key={i} className="px-6 py-5 animate-pulse"
                style={{ background: "var(--bg-card)", height: 72 }} />
            ))}
          </div>
        ) : alerts.length === 0 ? (
          <div className="px-6 py-10 text-center"
            style={{ background: "var(--bg-card)", border: "1px solid var(--border)" }}>
            <p className="serif text-2xl font-light mb-2" style={{ color: "var(--text-faint)" }}>
              No alerts yet
            </p>
            <p className="text-xs" style={{ color: "var(--text-faint)" }}>
              Create one above to get notified when trends cross your threshold
            </p>
          </div>
        ) : (
          <div className="space-y-px" style={{ background: "var(--border)" }}>
            {alerts.map((a) => (
              <div key={a.id}
                className="px-6 py-5 flex items-center justify-between gap-4"
                style={{ background: "var(--bg-card)" }}>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-3 mb-1 flex-wrap">
                    <p className="serif text-base font-light">
                      {a.trend_name === "*" ? "All Trends" : a.trend_name}
                    </p>
                    {a.trend_name === "*" && (
                      <span style={{
                        fontSize: 9, letterSpacing: "0.15em", textTransform: "uppercase",
                        color: "var(--accent)", border: "1px solid var(--accent)",
                        padding: "1px 6px", borderRadius: 2,
                      }}>Wildcard</span>
                    )}
                  </div>
                  <div className="flex items-center gap-4 text-[9px]" style={{ color: "var(--text-faint)" }}>
                    <span>Score ≥ {a.min_score.toFixed(1)}</span>
                    {a.source_filter && <span>· {a.source_filter.replace(/_/g, " ")}</span>}
                    {a.last_fired ? (
                      <span>· Last fired {new Date(a.last_fired).toLocaleDateString()}</span>
                    ) : (
                      <span>· Never fired</span>
                    )}
                  </div>
                </div>

                {/* Score pill */}
                <div style={{
                  padding: "4px 12px",
                  background: "rgba(212,168,83,0.1)",
                  border: "1px solid rgba(212,168,83,0.3)",
                  borderRadius: 2,
                  fontSize: 13,
                  color: "var(--accent)",
                  fontVariantNumeric: "tabular-nums",
                  whiteSpace: "nowrap",
                }}>
                  ≥ {a.min_score.toFixed(1)}
                </div>

                {/* Delete */}
                <button
                  onClick={() => deleteAlert(a.id)}
                  disabled={deleting === a.id}
                  style={{
                    background: "none",
                    border: "1px solid var(--border)",
                    color: deleting === a.id ? "var(--text-faint)" : "#e05a5a",
                    padding: "6px 12px",
                    fontSize: 9,
                    letterSpacing: "0.15em",
                    textTransform: "uppercase",
                    cursor: deleting === a.id ? "not-allowed" : "pointer",
                    fontFamily: "inherit",
                    borderRadius: 2,
                    transition: "border-color 0.15s",
                  }}
                >
                  {deleting === a.id ? "…" : "Remove"}
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* ── How it works ─────────────────────────────────────────────────── */}
      <div className="px-6 py-6 space-y-4"
        style={{ background: "var(--bg-card)", border: "1px solid var(--border)" }}>
        <p className="text-[9px] tracking-[0.3em] uppercase" style={{ color: "var(--text-faint)" }}>
          How Alerts Work
        </p>
        <div className="space-y-3 text-xs" style={{ color: "var(--text-muted)" }}>
          <div className="flex gap-3">
            <span style={{ color: "var(--accent)" }}>01</span>
            <p>The weekly pipeline scrapes TikTok, Editorial, Reddit, Pinterest & Google every Sunday at 6am.</p>
          </div>
          <div className="flex gap-3">
            <span style={{ color: "var(--accent)" }}>02</span>
            <p>After scoring, any trend matching your name filter <em>and</em> above your score threshold triggers an alert.</p>
          </div>
          <div className="flex gap-3">
            <span style={{ color: "var(--accent)" }}>03</span>
            <p>Alerts fire at most once per 24 hours. Configure SMTP in <code>.env</code> to receive email notifications.</p>
          </div>
          <div className="flex gap-3">
            <span style={{ color: "var(--accent)" }}>04</span>
            <p>Use <code>*</code> as the trend name to watch all trends above your score threshold — great for discovering new signals.</p>
          </div>
        </div>
      </div>
    </div>
  );
}
