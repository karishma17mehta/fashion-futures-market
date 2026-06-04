import { fetchMarkets, fetchTrends } from "@/lib/api";
import Link from "next/link";
import ScoreBadge from "@/components/ScoreBadge";
import PriceBar from "@/components/PriceBar";
import SourceBadge from "@/components/SourceBadge";
import VelocityIndicator from "@/components/VelocityIndicator";
import NewBadge from "@/components/NewBadge";
import SignalTicker from "@/components/SignalTicker";

// Always render fresh so prices reflect the latest trades (no stale cache).
export const dynamic = "force-dynamic";

export default async function Home() {
  const [marketsData, trendsData, allTrendsData] = await Promise.all([
    fetchMarkets("open"),
    fetchTrends(6, 8.0),
    fetchTrends(40),
  ]);

  const markets: any[]    = marketsData.markets  || [];
  const topTrends: any[]  = trendsData.trends    || [];
  const allTrends: any[]  = allTrendsData.trends || [];

  // Breaking = created in last 48h
  const breaking = allTrends
    .filter((t: any) => {
      const age = Date.now() - new Date(t.created_at).getTime();
      return age < 48 * 60 * 60 * 1000;
    })
    .slice(0, 20);

  // Platform breakdown for stats
  const bySource = allTrends.reduce((acc: Record<string, number>, t: any) => {
    const src = t.source?.includes("tiktok") ? "tiktok"
              : t.source?.includes("pinterest") ? "pinterest"
              : t.source?.includes("editorial") ? "editorial"
              : t.source?.includes("reddit") ? "reddit"
              : "other";
    acc[src] = (acc[src] || 0) + 1;
    return acc;
  }, {});

  // Hottest market (highest trading volume)
  const hottestMarket = [...markets].sort((a, b) => b.total_volume - a.total_volume)[0];

  // Markets shown on the homepage: most-traded first (so a market you trade
  // surfaces here), then by the underlying trend's score for the untraded rest.
  const scoreById: Record<string, number> = {};
  allTrends.forEach((t: any) => { scoreById[t.id] = t.ai_score ?? 0; });
  const displayMarkets = [...markets].sort((a, b) => {
    const vol = (b.total_volume || 0) - (a.total_volume || 0);
    if (vol !== 0) return vol;
    return (scoreById[b.trend_id] ?? 0) - (scoreById[a.trend_id] ?? 0);
  });

  return (
    <div className="space-y-0">

      {/* ── Signal Ticker ─────────────────────────────────────────────────── */}
      {breaking.length > 0 && (
        <div style={{ margin: "0 -20px 0" }}>
          <SignalTicker items={breaking} />
        </div>
      )}

      {/* ── Hero ─────────────────────────────────────────────────────────── */}
      <div className="pt-12 pb-6 fade-up">
        <p className="text-[10px] tracking-[0.35em] uppercase mb-6" style={{ color: "var(--accent)" }}>
          Fashion Prediction Intelligence
        </p>
        <h1 className="serif text-6xl md:text-7xl font-light leading-[1.05] mb-6">
          Call the trend<br />
          <em className="score-glow" style={{ color: "var(--accent)" }}>before</em> it breaks.
        </h1>
        <p className="text-base max-w-lg leading-relaxed" style={{ color: "var(--text-muted)" }}>
          Every market comes with the data - score, momentum, cross-platform confirmation.
          Read the signals, predict what goes mainstream, and prove your eye against everyone else.
          Not what you <em>want</em> to trend. What <em>will</em>.
        </p>

        {/* Stats row */}
        <div className="flex flex-wrap gap-0 mt-12" style={{ borderTop: "1px solid var(--border)" }}>
          {[
            { value: markets.length,     label: "Open Markets" },
            { value: allTrends.length,   label: "Trends Tracked" },
            { value: breaking.length,    label: "New This Week" },
            { value: "5",                label: "Signal Sources" },
          ].map((stat, i) => (
            <div
              key={i}
              className="flex-1 min-w-[120px] py-5"
              style={{
                borderRight: i < 3 ? "1px solid var(--border)" : undefined,
                paddingLeft: i === 0 ? 0 : "2rem",
              }}
            >
              <p className="serif text-4xl font-light score-glow" style={{ color: "var(--accent)" }}>
                {stat.value}
              </p>
              <p className="text-[9px] tracking-widest uppercase mt-1.5" style={{ color: "var(--text-faint)" }}>
                {stat.label}
              </p>
            </div>
          ))}
        </div>
      </div>

      <hr className="rule" />

      {/* ── Source Intelligence Bar ───────────────────────────────────────── */}
      <div className="py-6 fade-up">
        <p className="text-[9px] tracking-[0.3em] uppercase mb-4" style={{ color: "var(--text-faint)" }}>
          Signal Sources Active This Week
        </p>
        <div className="flex flex-wrap gap-3">
          {[
            { source: "tiktok",       count: bySource.tiktok || 0 },
            { source: "pinterest",    count: bySource.pinterest || 0 },
            { source: "editorial_rss",count: bySource.editorial || 0 },
            { source: "reddit",       count: bySource.reddit || 0 },
            { source: "google_trends",count: 0 },
          ].filter(s => s.count > 0 || s.source === "google_trends").map(({ source, count }) => (
            <div key={source} className="flex items-center gap-2">
              <SourceBadge source={source} />
              {count > 0 && (
                <span className="text-[9px]" style={{ color: "var(--text-faint)" }}>
                  {count} signals
                </span>
              )}
            </div>
          ))}
        </div>
      </div>

      <hr className="rule" />

      {/* ── Hottest Market ────────────────────────────────────────────────── */}
      {hottestMarket && hottestMarket.total_volume > 0 && (
        <>
          <div className="py-8 fade-up">
            <p className="text-[9px] tracking-[0.3em] uppercase mb-5" style={{ color: "var(--text-muted)" }}>
              Most Traded Right Now
            </p>
            <Link
              href={`/markets/${hottestMarket.id}`}
              className="hover-tile flex items-center justify-between p-6 group"
              style={{ border: "1px solid var(--border)" }}
            >
              <div className="flex-1 min-w-0 pr-6">
                <p className="serif text-2xl font-light leading-snug mb-2">{hottestMarket.question}</p>
                <p className="text-[10px] tracking-widest uppercase" style={{ color: "var(--text-faint)" }}>
                  {hottestMarket.total_volume} pts traded ·
                  Closes {new Date(hottestMarket.resolution_date).toLocaleDateString("en-US", { month: "short", day: "numeric" })}
                </p>
              </div>
              <div className="w-36 shrink-0">
                <PriceBar yes={hottestMarket.yes_price} no={hottestMarket.no_price} />
                <div className="flex justify-between mt-2">
                  <span className="text-[9px]" style={{ color: "var(--green)" }}>
                    YES {Math.round(hottestMarket.yes_price * 100)}¢
                  </span>
                  <span className="text-[9px]" style={{ color: "var(--red)" }}>
                    NO {Math.round(hottestMarket.no_price * 100)}¢
                  </span>
                </div>
              </div>
            </Link>
          </div>
          <hr className="rule" />
        </>
      )}

      {/* ── Top AI Signals ────────────────────────────────────────────────── */}
      {topTrends.length > 0 && (
        <div className="py-8 fade-up">
          <div className="flex items-center justify-between mb-8">
            <div>
              <p className="text-[9px] tracking-[0.3em] uppercase mb-1" style={{ color: "var(--text-muted)" }}>
                Highest-Confidence Signals
              </p>
              <p className="text-[9px]" style={{ color: "var(--text-faint)" }}>
                Score ≥ 8.0 · multi-source verified
              </p>
            </div>
            <Link
              href="/trends"
              className="text-[10px] tracking-widest uppercase transition-colors"
              style={{ color: "var(--accent)" }}
            >
              All {allTrends.length} signals →
            </Link>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-px"
            style={{ background: "var(--border)" }}>
            {topTrends.map((t: any) => (
              <Link
                key={t.id}
                href={`/trends/${t.id}`}
                className="hover-tile group flex flex-col p-6"
              >
                {/* Top row: score + new badge */}
                <div className="flex items-start justify-between mb-3">
                  <ScoreBadge score={t.ai_score} />
                  <NewBadge createdAt={t.created_at} />
                </div>

                {/* Name */}
                <p className="serif text-xl font-light leading-tight mb-2 flex-1">{t.name}</p>

                {/* Description */}
                <p className="text-xs leading-relaxed line-clamp-2 mb-4" style={{ color: "var(--text-muted)" }}>
                  {t.description}
                </p>

                {/* Footer: source + velocity */}
                <div className="flex items-center justify-between mt-auto pt-3"
                  style={{ borderTop: "1px solid var(--border)" }}>
                  <SourceBadge source={t.source} />
                  {t.signal_velocity > 0 && (
                    <VelocityIndicator velocity={t.signal_velocity} />
                  )}
                </div>
              </Link>
            ))}
          </div>
        </div>
      )}

      <hr className="rule" />

      {/* ── Open Markets ─────────────────────────────────────────────────── */}
      <div className="py-8 fade-up">
        <div className="flex items-center justify-between mb-8">
          <div>
            <p className="text-[9px] tracking-[0.3em] uppercase mb-1" style={{ color: "var(--text-muted)" }}>
              Open Prediction Markets
            </p>
            <p className="text-[9px]" style={{ color: "var(--text-faint)" }}>
              Resolving in 90 days · call early, earn more
            </p>
          </div>
          <Link
            href="/markets"
            className="text-[10px] tracking-widest uppercase"
            style={{ color: "var(--accent)" }}
          >
            Browse all →
          </Link>
        </div>

        <div className="space-y-px" style={{ background: "var(--border)" }}>
          {displayMarkets.slice(0, 12).map((m: any, i: number) => (
            <Link
              key={m.id}
              href={`/markets/${m.id}`}
              className="hover-tile flex items-center gap-6 px-6 py-5"
            >
              {/* Row number */}
              <span
                className="text-[11px] font-light shrink-0 w-5 text-right"
                style={{ color: "var(--text-faint)", fontFamily: "'Cormorant Garamond', serif" }}
              >
                {i + 1}
              </span>

              <div className="flex-1 min-w-0">
                <p className="text-sm leading-snug mb-1" style={{ fontWeight: 400 }}>
                  {m.question}
                </p>
                <p className="text-[10px] tracking-widest uppercase" style={{ color: "var(--text-faint)" }}>
                  Closes {new Date(m.resolution_date).toLocaleDateString("en-US", {
                    month: "short", day: "numeric", year: "numeric"
                  })}
                  {m.total_volume > 0 && (
                    <span className="ml-3" style={{ color: "var(--accent)" }}>
                      {m.total_volume} pts
                    </span>
                  )}
                </p>
              </div>

              <div className="w-28 shrink-0">
                <PriceBar yes={m.yes_price} no={m.no_price} />
                <div className="flex justify-between mt-1.5">
                  <span className="text-[9px]" style={{ color: "var(--green)" }}>
                    {Math.round(m.yes_price * 100)}¢
                  </span>
                  <span className="text-[9px]" style={{ color: "var(--red)" }}>
                    {Math.round(m.no_price * 100)}¢
                  </span>
                </div>
              </div>
            </Link>
          ))}
        </div>

        {markets.length > 12 && (
          <div className="text-center mt-6">
            <Link
              href="/markets"
              className="text-[10px] tracking-widest uppercase"
              style={{ color: "var(--text-faint)" }}
            >
              + {markets.length - 12} more markets →
            </Link>
          </div>
        )}
      </div>

    </div>
  );
}
