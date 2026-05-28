import { fetchTrends } from "@/lib/api";
import Link from "next/link";
import ScoreBadge from "@/components/ScoreBadge";

const SOURCE_LABEL: Record<string, string> = {
  wgsn: "WGSN",
  instagram_databutmakeitfashion: "Instagram Data",
  google_trends: "Google Trends",
  reddit: "Reddit",
};

const SOURCE_COLOR: Record<string, string> = {
  wgsn: "text-violet-400",
  instagram_databutmakeitfashion: "text-pink-400",
  google_trends: "text-blue-400",
  reddit: "text-orange-400",
};

export default async function TrendsPage() {
  const data = await fetchTrends(100);
  const trends: any[] = data.trends || [];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">All Trends</h1>
        <p className="text-white/40 text-sm mt-1">{trends.length} trends tracked across 4 sources</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {trends.map((t: any) => (
          <Link key={t.id} href={`/trends/${t.id}`}
            className="border border-white/10 rounded-xl p-5 hover:border-white/30 hover:bg-white/5 transition-all group">
            <div className="flex items-start justify-between mb-3">
              <ScoreBadge score={t.ai_score} />
              <span className={`text-xs font-mono ${SOURCE_COLOR[t.source] || "text-white/30"}`}>
                {SOURCE_LABEL[t.source] || t.source}
              </span>
            </div>
            <p className="font-semibold group-hover:text-white transition-colors">{t.name}</p>
            <p className="text-xs text-white/40 mt-2 line-clamp-3">{t.description}</p>
            <div className="mt-3 flex items-center gap-3 text-xs text-white/30">
              <span>Velocity: <span className="text-white/50">{t.signal_velocity > 0 ? "+" : ""}{t.signal_velocity.toFixed(0)}%</span></span>
              <span>Status: <span className="text-white/50">{t.status}</span></span>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
