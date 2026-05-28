import { fetchTrend, fetchMarkets } from "@/lib/api";
import Link from "next/link";
import ScoreBadge from "@/components/ScoreBadge";
import PriceBar from "@/components/PriceBar";
import { notFound } from "next/navigation";

export default async function TrendPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const [trend, marketsData] = await Promise.all([fetchTrend(id), fetchMarkets("open")]);

  if (trend.detail === "Trend not found") notFound();

  const relatedMarkets = (marketsData.markets || []).filter((m: any) => m.trend_id === id);

  return (
    <div className="max-w-2xl space-y-8">
      <div>
        <Link href="/trends" className="text-xs text-white/30 hover:text-white/60 mb-4 block">← All Trends</Link>
        <div className="flex items-center gap-3 mb-3">
          <ScoreBadge score={trend.ai_score} />
          <span className="text-xs text-white/30 uppercase font-mono">{trend.source}</span>
          <span className="text-xs text-white/30">·</span>
          <span className="text-xs text-white/30 uppercase font-mono">{trend.status}</span>
        </div>
        <h1 className="text-3xl font-bold">{trend.name}</h1>
        <p className="text-white/50 mt-3">{trend.description}</p>
      </div>

      <div className="border border-white/10 rounded-xl p-5 bg-white/5">
        <p className="text-xs font-mono text-rose-400 uppercase tracking-widest mb-3">AI Thesis</p>
        <p className="text-sm text-white/70 leading-relaxed">{trend.ai_thesis}</p>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div className="border border-white/10 rounded-xl p-4">
          <p className="text-xs text-white/30 mb-1">AI Score</p>
          <p className="text-2xl font-bold">{trend.ai_score.toFixed(1)}<span className="text-white/30 text-sm">/10</span></p>
        </div>
        <div className="border border-white/10 rounded-xl p-4">
          <p className="text-xs text-white/30 mb-1">Signal Velocity</p>
          <p className="text-2xl font-bold">{trend.signal_velocity > 0 ? "+" : ""}{trend.signal_velocity.toFixed(0)}<span className="text-white/30 text-sm">%</span></p>
        </div>
      </div>

      {relatedMarkets.length > 0 && (
        <div>
          <h2 className="text-xs font-mono text-white/40 uppercase tracking-widest mb-3">Markets</h2>
          <div className="space-y-3">
            {relatedMarkets.map((m: any) => (
              <Link key={m.id} href={`/markets/${m.id}`}
                className="block border border-white/10 rounded-xl p-4 hover:border-white/30 hover:bg-white/5 transition-all">
                <p className="text-sm font-medium mb-3">{m.question}</p>
                <PriceBar yes={m.yes_price} no={m.no_price} />
                <p className="text-xs text-white/30 mt-2">
                  Closes {new Date(m.resolution_date).toLocaleDateString()} · {m.total_volume} pts traded
                </p>
              </Link>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
