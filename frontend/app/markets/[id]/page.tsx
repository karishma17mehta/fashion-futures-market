"use client";
import { useEffect, useState, useCallback } from "react";
import { fetchMarket, fetchTrend, placeTrade } from "@/lib/api";
import PriceBar from "@/components/PriceBar";
import SourceBadge from "@/components/SourceBadge";
import ScoreBadge from "@/components/ScoreBadge";
import Link from "next/link";
import { use } from "react";
import { useAuth } from "@/lib/auth";
import GuestPrompt from "@/components/GuestPrompt";

// Price history stored in memory for this session
let priceHistory: { yes: number; no: number; ts: number }[] = [];

function MiniPriceChart({ history }: { history: { yes: number }[] }) {
  if (history.length < 2) return null;
  const prices = history.map((h) => h.yes);
  const min = Math.min(...prices);
  const max = Math.max(...prices);
  const range = max - min || 0.01;
  const w = 140;
  const h = 32;
  const pts = prices.map((p, i) => {
    const x = (i / (prices.length - 1)) * w;
    const y = h - ((p - min) / range) * h;
    return `${x},${y}`;
  });
  const color = prices[prices.length - 1] > prices[0] ? "#6abf87" : "#e86060";

  return (
    <svg width={w} height={h} style={{ display: "block" }}>
      <polyline
        points={pts.join(" ")}
        fill="none"
        stroke={color}
        strokeWidth="1.5"
        strokeLinejoin="round"
      />
      {/* Latest price dot */}
      <circle
        cx={w}
        cy={h - ((prices[prices.length - 1] - min) / range) * h}
        r="2.5"
        fill={color}
      />
    </svg>
  );
}

export default function MarketPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const [market, setMarket]   = useState<any>(null);
  const [trend, setTrend]     = useState<any>(null);
  const [amount, setAmount]   = useState(50);
  const [result, setResult]   = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState<{ yes: number; no: number; ts: number }[]>([]);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const { user, refresh } = useAuth();
  const userId = user?.id;

  const loadMarket = useCallback(async () => {
    const m = await fetchMarket(id);
    setMarket(m);
    setLastUpdated(new Date());
    // Append to in-memory price history
    setHistory((prev) => {
      const next = [...prev, { yes: m.yes_price, no: m.no_price, ts: Date.now() }];
      return next.slice(-30); // keep last 30 data points
    });
    // Load trend if we have a trend_id and haven't loaded it yet
    if (m.trend_id) {
      fetchTrend(m.trend_id).then((t) => { if (!t.detail) setTrend(t); });
    }
  }, [id]);

  useEffect(() => {
    loadMarket();
    // Auto-refresh every 15s
    const interval = setInterval(loadMarket, 15000);
    return () => clearInterval(interval);
  }, [loadMarket]);

  async function trade(position: "yes" | "no") {
    if (!userId) return;
    setLoading(true);
    setResult(null);
    const res = await placeTrade(id, userId, position, amount);
    setResult(res);
    await loadMarket();
    await refresh();  // update points shown in the nav
    setLoading(false);
  }

  if (!market) return (
    <div className="pt-20 text-center">
      <p className="text-[10px] tracking-widest uppercase" style={{ color: "var(--text-faint)" }}>
        Loading market…
      </p>
    </div>
  );

  const isOpen = market.status === "open";
  const yesPrice = Math.round(market.yes_price * 100);
  const noPrice  = Math.round(market.no_price  * 100);
  const priceChange = history.length >= 2
    ? Math.round((history[history.length - 1].yes - history[0].yes) * 100)
    : 0;

  return (
    <div className="max-w-xl space-y-10 pt-4 fade-up">

      {/* Back */}
      <Link
        href="/"
        className="text-[10px] tracking-widest uppercase"
        style={{ color: "var(--text-faint)" }}
      >
        ← Markets
      </Link>

      {/* ── Header ─────────────────────────────────────────────────────── */}
      <div>
        <div className="flex items-center gap-3 mb-5 flex-wrap">
          <span
            className="text-[9px] tracking-widest uppercase px-2.5 py-1"
            style={{
              color:  isOpen ? "var(--green)" : "var(--text-faint)",
              border: `1px solid ${isOpen ? "var(--green)" : "var(--border)"}`,
            }}
          >
            {isOpen ? "● Open" : "Closed"}
          </span>
          {trend && <SourceBadge source={trend.source} />}
          {market.total_volume > 0 && (
            <span className="text-[9px] tracking-widest uppercase" style={{ color: "var(--accent)" }}>
              {market.total_volume} pts traded
            </span>
          )}
          {lastUpdated && (
            <span className="text-[9px]" style={{ color: "var(--text-faint)" }}>
              Updated {lastUpdated.toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit" })}
            </span>
          )}
        </div>

        <h1 className="serif text-3xl font-light leading-snug mb-3">{market.question}</h1>
        <p className="text-[9px] tracking-widest uppercase" style={{ color: "var(--text-faint)" }}>
          Resolves {new Date(market.resolution_date).toLocaleDateString("en-US", {
            month: "long", day: "numeric", year: "numeric"
          })}
        </p>
      </div>

      <hr className="rule" />

      {/* ── Trend Context ───────────────────────────────────────────────── */}
      {trend && (
        <div
          className="px-6 py-5"
          style={{ background: "var(--bg-card)", border: "1px solid var(--border)" }}
        >
          <p className="text-[9px] tracking-[0.3em] uppercase mb-3" style={{ color: "var(--text-faint)" }}>
            Underlying Trend
          </p>
          <Link href={`/trends/${trend.id}`} className="group">
            <div className="flex items-start gap-4">
              <ScoreBadge score={trend.ai_score} />
              <div>
                <p className="serif text-lg font-light group-hover:text-white transition-colors">
                  {trend.name}
                </p>
                {trend.ai_thesis && (
                  <p className="text-xs mt-1 line-clamp-2" style={{ color: "var(--text-muted)" }}>
                    {trend.ai_thesis}
                  </p>
                )}
              </div>
            </div>
          </Link>
        </div>
      )}

      {/* ── Price Panel ─────────────────────────────────────────────────── */}
      <div>
        <div className="flex items-center justify-between mb-5">
          <p className="text-[9px] tracking-[0.3em] uppercase" style={{ color: "var(--text-muted)" }}>
            Current Probability
          </p>
          {history.length >= 2 && (
            <span
              style={{
                fontSize: "10px",
                color: priceChange > 0 ? "var(--green)" : priceChange < 0 ? "var(--red)" : "var(--text-faint)",
              }}
            >
              {priceChange > 0 ? "+" : ""}{priceChange}¢ this session
            </span>
          )}
        </div>

        <PriceBar yes={market.yes_price} no={market.no_price} />

        <div className="grid grid-cols-2 gap-px mt-4" style={{ background: "var(--border)" }}>
          <div className="px-6 py-5" style={{ background: "var(--bg-card)" }}>
            <p className="text-[9px] tracking-widest uppercase mb-2" style={{ color: "var(--text-faint)" }}>
              YES — Will Break
            </p>
            <p className="serif text-5xl font-light" style={{ color: "var(--green)" }}>
              {yesPrice}¢
            </p>
            <p className="text-[9px] mt-2" style={{ color: "var(--text-faint)" }}>
              Implied probability {yesPrice}%
            </p>
          </div>
          <div className="px-6 py-5 flex flex-col justify-between" style={{ background: "var(--bg-card)" }}>
            <div>
              <p className="text-[9px] tracking-widest uppercase mb-2" style={{ color: "var(--text-faint)" }}>
                NO — Will Fade
              </p>
              <p className="serif text-5xl font-light" style={{ color: "var(--red)" }}>
                {noPrice}¢
              </p>
            </div>
            {history.length >= 2 && (
              <div className="mt-3">
                <p className="text-[9px] mb-1" style={{ color: "var(--text-faint)" }}>
                  Session price chart
                </p>
                <MiniPriceChart history={history} />
              </div>
            )}
          </div>
        </div>
      </div>

      {/* ── Trade ───────────────────────────────────────────────────────── */}
      {/* Guest — prompt to sign up before trading */}
      {isOpen && !user && (
        <div>
          <p className="text-[9px] tracking-[0.3em] uppercase mb-5" style={{ color: "var(--text-muted)" }}>
            Place a Trade
          </p>
          <GuestPrompt
            title="Sign up to trade this market"
            body="Create an account to place a bet on this trend. You'll start with 1,000 points."
          />
        </div>
      )}

      {isOpen && user && (
        <div>
          <p className="text-[9px] tracking-[0.3em] uppercase mb-5" style={{ color: "var(--text-muted)" }}>
            Place a Trade
          </p>

          <div
            className="px-6 py-6 space-y-6"
            style={{ background: "var(--bg-card)", border: "1px solid var(--border)" }}
          >
            {/* Amount slider */}
            <div>
              <div className="flex justify-between mb-3">
                <span className="text-[9px] tracking-widest uppercase" style={{ color: "var(--text-faint)" }}>
                  Points to stake
                </span>
                <span className="serif text-2xl font-light" style={{ color: "var(--accent)" }}>
                  {amount}
                  <span className="text-sm" style={{ color: "var(--text-faint)" }}> pts</span>
                </span>
              </div>
              <input
                type="range" min={10} max={500} step={10} value={amount}
                onChange={(e) => setAmount(Number(e.target.value))}
                className="w-full"
                style={{ accentColor: "var(--accent)" }}
              />
              {/* Quick amounts */}
              <div className="flex gap-2 mt-3">
                {[25, 50, 100, 200].map((v) => (
                  <button
                    key={v}
                    onClick={() => setAmount(v)}
                    style={{
                      padding: "3px 10px",
                      fontSize: "9px",
                      letterSpacing: "0.1em",
                      border: `1px solid ${amount === v ? "var(--accent)" : "var(--border)"}`,
                      color: amount === v ? "var(--accent)" : "var(--text-faint)",
                      background: amount === v ? "var(--accent-dim)" : "transparent",
                      borderRadius: "2px",
                      cursor: "pointer",
                    }}
                  >
                    {v}
                  </button>
                ))}
              </div>
            </div>

            {/* Payout preview */}
            <div
              className="grid grid-cols-2 gap-3 text-center text-[10px]"
              style={{ borderTop: "1px solid var(--border)", paddingTop: "16px" }}
            >
              <div>
                <p style={{ color: "var(--text-faint)" }}>If YES wins</p>
                <p className="serif text-xl font-light mt-1" style={{ color: "var(--green)" }}>
                  +{Math.round(amount * (1 / market.yes_price - 1))} pts
                </p>
              </div>
              <div>
                <p style={{ color: "var(--text-faint)" }}>If NO wins</p>
                <p className="serif text-xl font-light mt-1" style={{ color: "var(--red)" }}>
                  +{Math.round(amount * (1 / market.no_price - 1))} pts
                </p>
              </div>
            </div>

            {/* Buttons */}
            <div className="grid grid-cols-2 gap-3">
              <button
                onClick={() => trade("yes")}
                disabled={loading}
                className="py-4 text-xs tracking-widest uppercase font-medium transition-all disabled:opacity-40"
                style={{
                  border: "1px solid var(--green)",
                  color: "var(--green)",
                  background: "rgba(91,171,122,0.08)",
                }}
                onMouseEnter={e => (e.currentTarget.style.background = "rgba(91,171,122,0.18)")}
                onMouseLeave={e => (e.currentTarget.style.background = "rgba(91,171,122,0.08)")}
              >
                {loading ? "…" : `Yes — It Breaks (${yesPrice}¢)`}
              </button>
              <button
                onClick={() => trade("no")}
                disabled={loading}
                className="py-4 text-xs tracking-widest uppercase font-medium transition-all disabled:opacity-40"
                style={{
                  border: "1px solid var(--red)",
                  color: "var(--red)",
                  background: "rgba(224,82,82,0.08)",
                }}
                onMouseEnter={e => (e.currentTarget.style.background = "rgba(224,82,82,0.18)")}
                onMouseLeave={e => (e.currentTarget.style.background = "rgba(224,82,82,0.08)")}
              >
                {loading ? "…" : `No — It Fades (${noPrice}¢)`}
              </button>
            </div>

            {/* Result */}
            {result && !result.detail && (
              <div
                className="text-center py-3"
                style={{ borderTop: "1px solid var(--border)" }}
              >
                <p className="text-xs" style={{ color: "var(--text-muted)" }}>
                  Bought{" "}
                  <span style={{ color: "var(--text)" }}>
                    {result.shares_bought?.toFixed(2)} shares
                  </span>
                  {" "}· New YES:{" "}
                  <span style={{ color: "var(--green)" }}>
                    {Math.round((result.new_yes_price || 0) * 100)}¢
                  </span>
                </p>
              </div>
            )}
            {result?.detail && (
              <p className="text-xs text-center" style={{ color: "var(--red)" }}>
                {result.detail}
              </p>
            )}
          </div>
        </div>
      )}

      {/* ── Resolution Criteria ─────────────────────────────────────────── */}
      <div>
        <p className="text-[9px] tracking-[0.3em] uppercase mb-3" style={{ color: "var(--text-muted)" }}>
          Resolution Criteria
        </p>
        <div
          className="px-6 py-5"
          style={{ background: "var(--bg-card)", borderLeft: "2px solid var(--border)" }}
        >
          <p className="text-sm leading-relaxed" style={{ color: "var(--text-muted)" }}>
            {market.resolution_criteria}
          </p>
        </div>
      </div>

    </div>
  );
}
