"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { fetchMarkets, fetchTrends } from "@/lib/api";
import PriceBar from "@/components/PriceBar";
import SourceBadge from "@/components/SourceBadge";
import ScoreBadge from "@/components/ScoreBadge";

type Sort = "volume" | "closing" | "newest" | "score";

const SORTS: { key: Sort; label: string }[] = [
  { key: "volume",  label: "Most Traded" },
  { key: "score",   label: "Highest Score" },
  { key: "closing", label: "Closing Soon" },
  { key: "newest",  label: "Newest" },
];

export default function MarketsPage() {
  const [markets, setMarkets] = useState<any[]>([]);
  const [trendMap, setTrendMap] = useState<Record<string, any>>({});
  const [sort, setSort] = useState<Sort>("volume");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([fetchMarkets("open"), fetchTrends(400)]).then(([mData, tData]) => {
      setMarkets(mData.markets || []);
      const map: Record<string, any> = {};
      (tData.trends || []).forEach((t: any) => { map[t.id] = t; });
      setTrendMap(map);
      setLoading(false);
    });
  }, []);

  const scoreOf = (m: any) => trendMap[m.trend_id]?.ai_score ?? 0;

  const sorted = [...markets].sort((a, b) => {
    switch (sort) {
      case "volume":  return (b.total_volume || 0) - (a.total_volume || 0);
      case "score":   return scoreOf(b) - scoreOf(a);
      case "closing": return +new Date(a.resolution_date) - +new Date(b.resolution_date);
      case "newest":  return +new Date(b.created_at) - +new Date(a.created_at);
    }
  });

  return (
    <div className="space-y-8 pt-4 fade-up">
      {/* Header */}
      <div>
        <Link href="/" className="text-[10px] tracking-widest uppercase" style={{ color: "var(--text-faint)" }}>
          ← Home
        </Link>
        <h1 className="serif text-4xl font-light mt-4 mb-2">Open Markets</h1>
        <p className="text-sm" style={{ color: "var(--text-muted)" }}>
          {loading ? "Loading…" : `${markets.length} prediction markets open for trading`}
        </p>
      </div>

      {/* Sort tabs */}
      <div className="flex gap-2 flex-wrap">
        {SORTS.map((s) => (
          <button
            key={s.key}
            onClick={() => setSort(s.key)}
            className="text-[10px] tracking-widest uppercase px-3 py-2 transition-colors"
            style={{
              border: `1px solid ${sort === s.key ? "var(--accent)" : "var(--border)"}`,
              color: sort === s.key ? "var(--accent)" : "var(--text-muted)",
              background: sort === s.key ? "var(--accent-dim)" : "transparent",
              borderRadius: 2,
            }}
          >
            {s.label}
          </button>
        ))}
      </div>

      {/* List */}
      {loading ? (
        <div className="space-y-px">
          {[...Array(8)].map((_, i) => (
            <div key={i} className="px-6 py-5 animate-pulse" style={{ background: "var(--bg-card)", height: 76 }} />
          ))}
        </div>
      ) : (
        <div className="space-y-px" style={{ background: "var(--border)" }}>
          {sorted.map((m, i) => {
            const trend = trendMap[m.trend_id];
            return (
              <Link key={m.id} href={`/markets/${m.id}`} className="hover-tile flex items-center gap-5 px-6 py-5">
                <span
                  className="text-[11px] font-light shrink-0 w-6 text-right"
                  style={{ color: "var(--text-faint)", fontFamily: "'Cormorant Garamond', serif" }}
                >
                  {i + 1}
                </span>

                {trend && <div className="shrink-0"><ScoreBadge score={trend.ai_score} /></div>}

                <div className="flex-1 min-w-0">
                  <p className="text-sm leading-snug mb-1.5" style={{ fontWeight: 400 }}>{m.question}</p>
                  <div className="flex items-center gap-3 flex-wrap">
                    {trend && <SourceBadge source={trend.source} />}
                    <span className="text-[10px] tracking-widest uppercase" style={{ color: "var(--text-faint)" }}>
                      Closes {new Date(m.resolution_date).toLocaleDateString("en-US", { month: "short", day: "numeric" })}
                    </span>
                    {m.total_volume > 0 && (
                      <span className="text-[10px]" style={{ color: "var(--accent)" }}>{m.total_volume} pts traded</span>
                    )}
                  </div>
                </div>

                <div className="w-28 shrink-0">
                  <PriceBar yes={m.yes_price} no={m.no_price} />
                  <div className="flex justify-between mt-1.5">
                    <span className="text-[9px]" style={{ color: "var(--green)" }}>{Math.round(m.yes_price * 100)}¢</span>
                    <span className="text-[9px]" style={{ color: "var(--red)" }}>{Math.round(m.no_price * 100)}¢</span>
                  </div>
                </div>
              </Link>
            );
          })}
        </div>
      )}
    </div>
  );
}
