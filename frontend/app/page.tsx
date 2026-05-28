import { fetchMarkets, fetchTrends } from "@/lib/api";
import Link from "next/link";
import ScoreBadge from "@/components/ScoreBadge";
import PriceBar from "@/components/PriceBar";

const SOURCE_LABEL: Record<string, string> = {
  wgsn: "WGSN",
  instagram_databutmakeitfashion: "Instagram Data",
  google_trends: "Google Trends",
  reddit: "Reddit",
};

export default async function Home() {
  const [marketsData, trendsData] = await Promise.all([
    fetchMarkets("open"),
    fetchTrends(5, 7.5),
  ]);

  const markets: any[] = marketsData.markets || [];
  const topTrends: any[] = trendsData.trends || [];

  return (
    <div className="space-y-10">
      {/* Hero */}
      <div className="border border-white/10 rounded-2xl p-8 bg-white/5">
        <p className="text-xs font-mono text-rose-400 uppercase tracking-widest mb-3">Prediction Market</p>
        <h1 className="text-4xl font-bold tracking-tight mb-3">
          Trade Fashion Trends<br />Before They Go Mainstream
        </h1>
        <p className="text-white/50 max-w-xl">
          AI scrapes underground fashion signals. You predict which micro-trends break through.
          Early callers earn points. Brands buy the intelligence.
        </p>
        <div className="flex gap-8 mt-6 text-sm">
          <div><span className="text-2xl font-bold">{markets.length}</span><span className="text-white/40 ml-2">Open Markets</span></div>
          <div><span className="text-2xl font-bold">1000</span><span className="text-white/40 ml-2">Starting Points</span></div>
          <div><span className="text-2xl font-bold">4</span><span className="text-white/40 ml-2">Signal Sources</span></div>
        </div>
      </div>

      {/* Top signals */}
      {topTrends.length > 0 && (
        <div>
          <h2 className="text-xs font-mono text-white/40 uppercase tracking-widest mb-4">Top AI Signals Right Now</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {topTrends.map((t: any) => (
              <Link key={t.id} href={`/trends/${t.id}`}
                className="border border-white/10 rounded-xl p-4 hover:border-white/30 hover:bg-white/5 transition-all group">
                <div className="flex items-start justify-between mb-2">
                  <ScoreBadge score={t.ai_score} />
                  <span className="text-xs text-white/30">{SOURCE_LABEL[t.source] || t.source}</span>
                </div>
                <p className="font-medium text-sm group-hover:text-white transition-colors">{t.name}</p>
                <p className="text-xs text-white/40 mt-1 line-clamp-2">{t.description}</p>
              </Link>
            ))}
          </div>
        </div>
      )}

      {/* Markets */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xs font-mono text-white/40 uppercase tracking-widest">Open Markets</h2>
          <Link href="/trends" className="text-xs text-rose-400 hover:text-rose-300">View all trends →</Link>
        </div>
        <div className="space-y-3">
          {markets.slice(0, 15).map((m: any) => (
            <Link key={m.id} href={`/markets/${m.id}`}
              className="flex items-center gap-4 border border-white/10 rounded-xl p-4 hover:border-white/30 hover:bg-white/5 transition-all group">
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium truncate group-hover:text-white transition-colors">{m.question}</p>
                <p className="text-xs text-white/30 mt-0.5">
                  Closes {new Date(m.resolution_date).toLocaleDateString()} · {m.total_volume} pts traded
                </p>
              </div>
              <div className="w-32 shrink-0">
                <PriceBar yes={m.yes_price} no={m.no_price} />
              </div>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}
