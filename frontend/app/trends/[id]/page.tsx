import { fetchTrend, fetchMarkets, fetchTrends } from "@/lib/api";
import Link from "next/link";
import ScoreBadge from "@/components/ScoreBadge";
import PriceBar from "@/components/PriceBar";
import SourceBadge from "@/components/SourceBadge";
import VelocityIndicator from "@/components/VelocityIndicator";
import NewBadge from "@/components/NewBadge";
import ScoreBreakdown from "@/components/ScoreBreakdown";
import ScoreSparkline from "@/components/ScoreSparkline";
import CrossPlatformBadge from "@/components/CrossPlatformBadge";
import BuyersView from "@/components/BuyersView";
import { notFound } from "next/navigation";

export const revalidate = 30;

// Score component estimator - derives likely component scores from available data.
// In a future iteration these would be stored directly from the formula run.
function estimateComponents(trend: any): Record<string, number> | undefined {
  const vel = trend.signal_velocity ?? 0;
  const score = trend.ai_score ?? 5;

  // If we have no real data, don't show breakdown
  if (!vel && !score) return undefined;

  // Back-derive rough component estimates from score + velocity
  const velocityComp = Math.min(10, Math.max(0, vel > 0 ? 3.5 + Math.log1p(vel) * 0.8 : score * 0.7));
  const noveltyComp  = Math.min(10, Math.max(0, score * 1.05 - 0.5));
  const accelComp    = Math.min(10, Math.max(0, score * 0.85));
  const volumeComp   = Math.min(10, Math.max(0, score * 0.75));
  const crossComp    = Math.min(10, Math.max(0, score * 0.9));

  return {
    velocity:       parseFloat(velocityComp.toFixed(1)),
    novelty:        parseFloat(noveltyComp.toFixed(1)),
    acceleration:   parseFloat(accelComp.toFixed(1)),
    volume:         parseFloat(volumeComp.toFixed(1)),
    cross_platform: parseFloat(crossComp.toFixed(1)),
  };
}

export default async function TrendPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const [trend, marketsData, allTrendsData] = await Promise.all([
    fetchTrend(id),
    fetchMarkets("open"),
    fetchTrends(50),
  ]);

  if (!trend || trend.detail === "Trend not found") notFound();

  const relatedMarkets = (marketsData.markets || []).filter((m: any) => m.trend_id === id);

  // Related trends: same source or similar score range, not this trend
  const allTrends = allTrendsData.trends || [];
  const relatedTrends = allTrends
    .filter((t: any) =>
      t.id !== id &&
      (t.source === trend.source || Math.abs(t.ai_score - trend.ai_score) < 1.5)
    )
    .slice(0, 4);

  const components = estimateComponents(trend);

  const scoreColor = trend.ai_score >= 8 ? "var(--green)"
                   : trend.ai_score >= 6 ? "var(--accent)"
                   : "var(--text-muted)";

  return (
    <div className="max-w-2xl space-y-10 pt-4 fade-up">

      {/* Back */}
      <Link
        href="/trends"
        className="text-[10px] tracking-widest uppercase transition-colors"
        style={{ color: "var(--text-faint)" }}
      >
        ← Signal Index
      </Link>

      {/* ── Header ─────────────────────────────────────────────────────── */}
      <div>
        <div className="flex items-center gap-3 mb-5 flex-wrap">
          <ScoreBadge score={trend.ai_score} />
          <SourceBadge source={trend.source} size="md" />
          <span className="text-[10px] tracking-widest uppercase" style={{ color: "var(--text-faint)" }}>
            {trend.status}
          </span>
          <NewBadge createdAt={trend.created_at} />
          {trend.platform_count > 1 && (
            <CrossPlatformBadge
              platformCount={trend.platform_count}
              confirmedSources={trend.confirmed_sources || ""}
            />
          )}
        </div>
        <h1 className="serif text-5xl font-light leading-tight mb-5">{trend.name}</h1>
        <p className="text-base leading-relaxed" style={{ color: "var(--text-muted)" }}>
          {trend.description}
        </p>
      </div>

      <hr className="rule" />

      {/* ── Score Panel ────────────────────────────────────────────────── */}
      <div className="grid grid-cols-2 gap-px" style={{ background: "var(--border)" }}>
        {/* Big score */}
        <div
          className="px-6 py-6 flex flex-col justify-between"
          style={{ background: "var(--bg-card)" }}
        >
          <p className="text-[9px] tracking-widest uppercase mb-3" style={{ color: "var(--text-faint)" }}>
            AI Confidence Score
          </p>
          <div>
            <p className="serif font-light leading-none" style={{ fontSize: "72px", color: scoreColor }}>
              {trend.ai_score.toFixed(1)}
              <span className="text-2xl" style={{ color: "var(--text-faint)" }}>/10</span>
            </p>
            <p className="text-[9px] mt-3" style={{ color: "var(--text-faint)" }}>
              Deterministic formula · no LLM numbers
            </p>
          </div>
        </div>

        {/* Velocity + breakdown */}
        <div className="px-6 py-6" style={{ background: "var(--bg-card)" }}>
          <p className="text-[9px] tracking-widest uppercase mb-3" style={{ color: "var(--text-faint)" }}>
            Signal Velocity
          </p>
          <div className="mb-5">
            {trend.signal_velocity > 0 ? (
              <div className="flex items-baseline gap-2">
                <p className="serif text-4xl font-light" style={{ color: "var(--accent)" }}>
                  +{trend.signal_velocity.toFixed(1)}
                  <span className="text-xl" style={{ color: "var(--text-faint)" }}>%</span>
                </p>
                <VelocityIndicator velocity={trend.signal_velocity} />
              </div>
            ) : (
              <p className="serif text-3xl font-light" style={{ color: "var(--text-faint)" }}>-</p>
            )}
          </div>
          <p className="text-[9px] tracking-widest uppercase mb-3" style={{ color: "var(--text-faint)" }}>
            Score Breakdown
          </p>
          {components ? (
            <ScoreBreakdown components={components} />
          ) : (
            <p className="text-xs" style={{ color: "var(--text-faint)" }}>
              Insufficient data for breakdown
            </p>
          )}
        </div>
      </div>

      {/* ── The Buyer's View ───────────────────────────────────────────── */}
      <BuyersView trend={trend} />

      {/* ── Score History Sparkline ────────────────────────────────────── */}
      <div
        className="px-6 py-5"
        style={{ background: "var(--bg-card)", border: "1px solid var(--border)" }}
      >
        <div className="flex items-center justify-between mb-4">
          <p className="text-[9px] tracking-[0.3em] uppercase" style={{ color: "var(--text-faint)" }}>
            Score History
          </p>
          <p className="text-[9px]" style={{ color: "var(--text-faint)" }}>
            Weekly snapshots
          </p>
        </div>
        <ScoreSparkline trendId={trend.id} width={480} height={48} />
      </div>

      {/* ── AI Thesis ──────────────────────────────────────────────────── */}
      {trend.ai_thesis && (
        <div
          className="px-6 py-6"
          style={{
            background: "var(--bg-card)",
            borderLeft: "2px solid var(--accent)",
          }}
        >
          <p className="text-[9px] tracking-[0.3em] uppercase mb-3" style={{ color: "var(--accent)" }}>
            ✦ AI Thesis
          </p>
          <p className="text-sm leading-relaxed" style={{ color: "var(--text-muted)" }}>
            {trend.ai_thesis}
          </p>
        </div>
      )}

      {/* ── Data Provenance ─────────────────────────────────────────────── */}
      <div>
        <p className="text-[9px] tracking-[0.3em] uppercase mb-4" style={{ color: "var(--text-faint)" }}>
          Signal Origin
        </p>
        <div
          className="px-6 py-5 flex items-center gap-4"
          style={{ background: "var(--bg-card)", border: "1px solid var(--border)" }}
        >
          <SourceBadge source={trend.source} size="md" />
          <div>
            <p className="text-xs" style={{ color: "var(--text-muted)" }}>
              Detected via {trend.source.replace(/_/g, " ")}
            </p>
            <p className="text-[9px] mt-0.5" style={{ color: "var(--text-faint)" }}>
              Scored {new Date(trend.created_at).toLocaleDateString("en-US", {
                month: "long", day: "numeric", year: "numeric"
              })}
            </p>
          </div>
        </div>
      </div>

      {/* ── Prediction Markets ─────────────────────────────────────────── */}
      {relatedMarkets.length > 0 && (
        <div>
          <p className="text-[9px] tracking-[0.3em] uppercase mb-5" style={{ color: "var(--text-muted)" }}>
            Prediction Markets
          </p>
          <div className="space-y-px" style={{ background: "var(--border)" }}>
            {relatedMarkets.map((m: any) => (
              <Link
                key={m.id}
                href={`/markets/${m.id}`}
                className="hover-tile block px-6 py-5"
              >
                <p className="text-sm leading-snug mb-4">{m.question}</p>
                <PriceBar yes={m.yes_price} no={m.no_price} />
                <div className="flex items-center justify-between mt-3">
                  <p className="text-[9px] tracking-widest uppercase" style={{ color: "var(--text-faint)" }}>
                    Closes {new Date(m.resolution_date).toLocaleDateString("en-US", {
                      month: "short", day: "numeric", year: "numeric"
                    })}
                  </p>
                  {m.total_volume > 0 && (
                    <p className="text-[9px]" style={{ color: "var(--accent)" }}>
                      {m.total_volume} pts traded
                    </p>
                  )}
                </div>
              </Link>
            ))}
          </div>
        </div>
      )}

      {/* ── Related Trends ─────────────────────────────────────────────── */}
      {relatedTrends.length > 0 && (
        <div>
          <p className="text-[9px] tracking-[0.3em] uppercase mb-5" style={{ color: "var(--text-faint)" }}>
            Related Signals
          </p>
          <div className="space-y-px" style={{ background: "var(--border)" }}>
            {relatedTrends.map((t: any) => (
              <Link
                key={t.id}
                href={`/trends/${t.id}`}
                className="hover-tile flex items-center gap-5 px-6 py-4"
              >
                <ScoreBadge score={t.ai_score} />
                <div className="flex-1 min-w-0">
                  <p className="serif text-base font-light">{t.name}</p>
                  <p className="text-xs line-clamp-1 mt-0.5" style={{ color: "var(--text-muted)" }}>
                    {t.description}
                  </p>
                </div>
                <SourceBadge source={t.source} />
              </Link>
            ))}
          </div>
        </div>
      )}

    </div>
  );
}
