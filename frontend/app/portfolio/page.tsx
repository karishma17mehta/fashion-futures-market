"use client";
import { useEffect, useState } from "react";
import { fetchPositions, fetchUser } from "@/lib/api";
import Link from "next/link";
import PriceBar from "@/components/PriceBar";
import ScoreBadge from "@/components/ScoreBadge";
import SourceBadge from "@/components/SourceBadge";
import { useAuth } from "@/lib/auth";
import GuestPrompt from "@/components/GuestPrompt";

type Position = {
  id: string;
  market_id: string;
  position: "yes" | "no";
  shares: number;
  cost: number;
  payout: number | null;
  market_question: string;
  market_status: string;
  market_yes_price: number;
  market_no_price: number;
  resolution_date: string;
  trend_id: string;
  trend_name: string;
  trend_score: number;
  trend_source: string;
  current_price: number;
  current_value: number;
  pnl: number;
  pnl_pct: number;
  created_at: string;
};

function PnlBadge({ pnl, pct }: { pnl: number; pct: number }) {
  const isPos = pnl >= 0;
  const color = isPos ? "var(--green)" : "var(--red)";
  return (
    <div style={{ textAlign: "right" }}>
      <p
        className="serif text-lg font-light"
        style={{ color }}
      >
        {isPos ? "+" : ""}{pnl}
        <span style={{ fontSize: "11px", color: "var(--text-faint)" }}> pts</span>
      </p>
      <p style={{ fontSize: "10px", color }}>
        {isPos ? "+" : ""}{pct}%
      </p>
    </div>
  );
}

function StatusPill({ status }: { status: string }) {
  const isOpen     = status === "open";
  const isYes      = status === "resolved_yes";
  const isNo       = status === "resolved_no";
  const color = isOpen ? "var(--accent)" : isYes ? "var(--green)" : isNo ? "var(--red)" : "var(--text-faint)";
  const label = isOpen ? "Open" : isYes ? "Resolved YES" : isNo ? "Resolved NO" : status;
  return (
    <span style={{
      fontSize: "9px",
      letterSpacing: "0.12em",
      textTransform: "uppercase",
      padding: "2px 7px",
      border: `1px solid ${color}`,
      color,
      borderRadius: "2px",
    }}>
      {label}
    </span>
  );
}

export default function PortfolioPage() {
  const { user: authUser } = useAuth();
  const [data, setData]   = useState<{ positions: Position[]; summary: any } | null>(null);
  const [user, setUser]   = useState<any>(null);
  const [filter, setFilter] = useState<"all" | "open" | "resolved">("all");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!authUser?.id) return;
    Promise.all([fetchPositions(authUser.id), fetchUser(authUser.id)]).then(([posData, userData]) => {
      setData(posData);
      setUser(userData);
      setLoading(false);
    });
  }, [authUser?.id]);

  // Guest / logged-out visitor - no portfolio to show.
  if (!authUser) {
    return (
      <div className="max-w-2xl mx-auto pt-10 fade-up">
        <GuestPrompt
          title="Your portfolio lives here"
          body="Create an account to place trades, track your positions, and watch your points grow as your calls pay off."
        />
      </div>
    );
  }

  const positions: Position[] = data?.positions || [];
  const summary = data?.summary || {};

  const filtered = filter === "all"      ? positions
                 : filter === "open"     ? positions.filter((p) => p.market_status === "open")
                 : positions.filter((p) => p.market_status !== "open");

  const openPnl = positions
    .filter((p) => p.market_status === "open")
    .reduce((sum, p) => sum + p.pnl, 0);

  // Resolved payout
  const resolved = positions.filter((p) => p.market_status !== "open");
  const totalPayout = resolved.reduce((sum, p) => sum + (p.payout || 0), 0);
  const totalStaked  = resolved.reduce((sum, p) => sum + p.cost, 0);
  const resolvedPnl  = totalPayout - totalStaked;

  if (loading) return (
    <div className="pt-20 text-center">
      <p className="text-[10px] tracking-widest uppercase" style={{ color: "var(--text-faint)" }}>
        Loading portfolio…
      </p>
    </div>
  );

  return (
    <div className="space-y-10 pt-4 fade-up max-w-3xl">

      {/* Header */}
      <div>
        <p className="text-[10px] tracking-[0.3em] uppercase mb-3" style={{ color: "var(--accent)" }}>
          Portfolio
        </p>
        <h1 className="serif text-5xl font-light mb-2">
          {user?.username || "Your"} Positions
        </h1>
        <p className="text-sm" style={{ color: "var(--text-muted)" }}>
          {summary.total_positions || 0} total trades · {user?.points || 0} pts balance
        </p>
      </div>

      <hr className="rule" />

      {/* Summary cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-px" style={{ background: "var(--border)" }}>
        {[
          {
            label: "Balance",
            value: `${user?.points || 0}`,
            unit: "pts",
            color: "var(--accent)",
          },
          {
            label: "Open P&L",
            value: `${openPnl >= 0 ? "+" : ""}${openPnl}`,
            unit: "pts",
            color: openPnl >= 0 ? "var(--green)" : "var(--red)",
          },
          {
            label: "Resolved P&L",
            value: `${resolvedPnl >= 0 ? "+" : ""}${resolvedPnl}`,
            unit: "pts",
            color: resolvedPnl >= 0 ? "var(--green)" : "var(--red)",
          },
          {
            label: "Accuracy",
            value: user?.accuracy_rate ? `${(user.accuracy_rate * 100).toFixed(0)}%` : "-",
            unit: "",
            color: "var(--text)",
          },
        ].map((stat) => (
          <div key={stat.label} className="px-5 py-5" style={{ background: "var(--bg-card)" }}>
            <p className="text-[9px] tracking-widest uppercase mb-2" style={{ color: "var(--text-faint)" }}>
              {stat.label}
            </p>
            <p className="serif text-3xl font-light" style={{ color: stat.color }}>
              {stat.value}
              {stat.unit && (
                <span className="text-sm" style={{ color: "var(--text-faint)" }}> {stat.unit}</span>
              )}
            </p>
          </div>
        ))}
      </div>

      {/* Rank banner */}
      {user?.rank && (
        <div
          className="px-6 py-4 flex items-center justify-between"
          style={{ background: "var(--bg-card)", border: "1px solid var(--border)", borderLeft: "2px solid var(--accent)" }}
        >
          <div>
            <p className="text-[9px] tracking-widest uppercase" style={{ color: "var(--text-faint)" }}>Rank</p>
            <p className="serif text-xl font-light capitalize mt-0.5">{user.rank}</p>
          </div>
          <div className="text-right">
            <p className="text-[9px] tracking-widest uppercase" style={{ color: "var(--text-faint)" }}>Total Trades</p>
            <p className="serif text-xl font-light">{user.total_trades || 0}</p>
          </div>
          <div className="text-right">
            <p className="text-[9px] tracking-widest uppercase" style={{ color: "var(--text-faint)" }}>Win Rate</p>
            <p className="serif text-xl font-light" style={{ color: user.accuracy_rate > 0.5 ? "var(--green)" : "var(--text)" }}>
              {user.accuracy_rate ? `${(user.accuracy_rate * 100).toFixed(0)}%` : "-"}
            </p>
          </div>
        </div>
      )}

      {/* Filter tabs */}
      <div className="flex gap-2">
        {(["all", "open", "resolved"] as const).map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`filter-tab ${filter === f ? "active" : ""}`}
            style={{ color: filter === f ? "var(--accent)" : "var(--text-muted)" }}
          >
            {f === "all" ? `All (${positions.length})` : f === "open" ? `Open (${summary.open_positions || 0})` : `Resolved (${resolved.length})`}
          </button>
        ))}
      </div>

      {/* Positions list */}
      {filtered.length === 0 ? (
        <div className="text-center py-16">
          <p className="serif text-2xl font-light mb-3" style={{ color: "var(--text-faint)" }}>
            No positions yet.
          </p>
          <p className="text-sm mb-6" style={{ color: "var(--text-faint)" }}>
            Browse open markets and make your first prediction.
          </p>
          <Link
            href="/"
            className="text-[10px] tracking-widest uppercase"
            style={{ color: "var(--accent)" }}
          >
            Browse Markets →
          </Link>
        </div>
      ) : (
        <div className="space-y-px" style={{ background: "var(--border)" }}>
          {filtered.map((p) => {
            const isOpen     = p.market_status === "open";
            const didWin     = p.payout !== null && p.payout > 0;
            const isResolved = p.market_status !== "open";

            return (
              <Link
                key={p.id}
                href={`/markets/${p.market_id}`}
                className="hover-tile flex items-start gap-5 px-6 py-5"
              >
                {/* Position badge */}
                <div className="shrink-0 pt-0.5">
                  <span
                    style={{
                      display: "inline-block",
                      padding: "3px 10px",
                      fontSize: "10px",
                      letterSpacing: "0.12em",
                      textTransform: "uppercase",
                      fontWeight: 500,
                      border: `1px solid ${p.position === "yes" ? "var(--green)" : "var(--red)"}`,
                      color: p.position === "yes" ? "var(--green)" : "var(--red)",
                      background: p.position === "yes" ? "rgba(106,191,135,0.08)" : "rgba(232,96,96,0.08)",
                      borderRadius: "2px",
                    }}
                  >
                    {p.position.toUpperCase()}
                  </span>
                </div>

                {/* Main content */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1 flex-wrap">
                    <p className="text-sm leading-snug">{p.market_question}</p>
                  </div>
                  <div className="flex items-center gap-3 mt-1 flex-wrap">
                    <StatusPill status={p.market_status} />
                    {p.trend_source && <SourceBadge source={p.trend_source} />}
                    <span className="text-[9px]" style={{ color: "var(--text-faint)" }}>
                      {p.shares.toFixed(2)} shares · {p.cost} pts staked
                    </span>
                    {p.resolution_date && (
                      <span className="text-[9px]" style={{ color: "var(--text-faint)" }}>
                        {isOpen ? "Closes" : "Closed"}{" "}
                        {new Date(p.resolution_date).toLocaleDateString("en-US", { month: "short", day: "numeric" })}
                      </span>
                    )}
                  </div>
                  {/* Price bar for open positions */}
                  {isOpen && (
                    <div className="mt-3 max-w-[200px]">
                      <PriceBar yes={p.market_yes_price} no={p.market_no_price} />
                    </div>
                  )}
                </div>

                {/* P&L / Payout */}
                <div className="shrink-0">
                  {isResolved ? (
                    <div style={{ textAlign: "right" }}>
                      {didWin ? (
                        <>
                          <p className="text-[9px] tracking-widest uppercase mb-1" style={{ color: "var(--green)" }}>
                            Won
                          </p>
                          <p className="serif text-xl font-light" style={{ color: "var(--green)" }}>
                            +{p.payout}
                            <span className="text-xs" style={{ color: "var(--text-faint)" }}> pts</span>
                          </p>
                        </>
                      ) : (
                        <>
                          <p className="text-[9px] tracking-widest uppercase mb-1" style={{ color: "var(--red)" }}>
                            Lost
                          </p>
                          <p className="serif text-xl font-light" style={{ color: "var(--red)" }}>
                            −{p.cost}
                            <span className="text-xs" style={{ color: "var(--text-faint)" }}> pts</span>
                          </p>
                        </>
                      )}
                    </div>
                  ) : (
                    <PnlBadge pnl={p.pnl} pct={p.pnl_pct} />
                  )}
                </div>
              </Link>
            );
          })}
        </div>
      )}

    </div>
  );
}
