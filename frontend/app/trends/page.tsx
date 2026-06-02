"use client";
import { useEffect, useState } from "react";
import { fetchTrends } from "@/lib/api";
import Link from "next/link";
import ScoreBadge from "@/components/ScoreBadge";
import SourceBadge from "@/components/SourceBadge";
import VelocityIndicator from "@/components/VelocityIndicator";
import NewBadge from "@/components/NewBadge";
import CrossPlatformBadge from "@/components/CrossPlatformBadge";

const SOURCE_GROUPS: Record<string, string[]> = {
  all:       [],
  tiktok:    ["tiktok"],
  pinterest: ["pinterest", "pinterest_trends_2026", "pinterest_predicts_2026"],
  editorial: ["editorial_rss"],
  reddit:    ["reddit"],
  intel:     ["trend_intelligence", "social_data", "depop_2026", "tobe_doneger", "wgsn", "google_trends"],
};

const TAB_LABELS: Record<string, string> = {
  all:       "All",
  tiktok:    "TikTok",
  pinterest: "Pinterest",
  editorial: "Editorial",
  reddit:    "Reddit",
  intel:     "Intel",
};

type SortKey = "score" | "velocity" | "newest";

export default function TrendsPage() {
  const [trends, setTrends] = useState<any[]>([]);
  const [activeSource, setActiveSource] = useState<string>("all");
  const [sortBy, setSortBy] = useState<SortKey>("score");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchTrends(500).then((d) => {
      setTrends(d.trends || []);
      setLoading(false);
    });
  }, []);

  // Filter
  const filtered = activeSource === "all"
    ? trends
    : trends.filter((t) => SOURCE_GROUPS[activeSource]?.includes(t.source));

  // Sort
  const sorted = [...filtered].sort((a, b) => {
    if (sortBy === "score")    return b.ai_score - a.ai_score;
    if (sortBy === "velocity") return (b.signal_velocity || 0) - (a.signal_velocity || 0);
    if (sortBy === "newest")   return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
    return 0;
  });

  // Score tiers
  const tier = (score: number) =>
    score >= 9 ? "hot" : score >= 7 ? "strong" : score >= 5 ? "emerging" : "weak";

  const sections = [
    { id: "hot",      label: "High Conviction",    min: 9,   max: 10,  color: "#6abf87" },
    { id: "strong",   label: "Strong Signal",      min: 7,   max: 8.9, color: "#d4a853" },
    { id: "emerging", label: "Emerging",           min: 5,   max: 6.9, color: "rgba(245,240,235,0.5)" },
    { id: "weak",     label: "Early / Low Data",   min: 0,   max: 4.9, color: "rgba(245,240,235,0.25)" },
  ];

  // Count per source for tab labels
  const countBySource: Record<string, number> = { all: trends.length };
  Object.entries(SOURCE_GROUPS).forEach(([key, sources]) => {
    if (key === "all") return;
    countBySource[key] = trends.filter((t) => sources.includes(t.source)).length;
  });

  return (
    <div className="space-y-8 pt-4">

      {/* Header */}
      <div className="fade-up">
        <p className="text-[10px] tracking-[0.3em] uppercase mb-3" style={{ color: "var(--accent)" }}>
          Signal Index
        </p>
        <h1 className="serif text-5xl font-light mb-3">All Trends</h1>
        <p className="text-sm" style={{ color: "var(--text-muted)" }}>
          {trends.length} signals · scored by velocity, novelty &amp; cross-platform confirmation
        </p>
      </div>

      <hr className="rule" />

      {/* Controls */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">

        {/* Source filter tabs */}
        <div className="flex flex-wrap gap-2">
          {Object.keys(TAB_LABELS).map((key) => (
            <button
              key={key}
              onClick={() => setActiveSource(key)}
              className={`filter-tab ${activeSource === key ? "active" : ""}`}
              style={{ color: activeSource === key ? "var(--accent)" : "var(--text-muted)" }}
            >
              {TAB_LABELS[key]}
              {countBySource[key] > 0 && (
                <span
                  style={{
                    marginLeft: "5px",
                    color: activeSource === key ? "var(--accent)" : "var(--text-faint)",
                    fontSize: "9px",
                  }}
                >
                  {countBySource[key]}
                </span>
              )}
            </button>
          ))}
        </div>

        {/* Sort */}
        <div className="flex items-center gap-2">
          <span className="text-[9px] tracking-widest uppercase" style={{ color: "var(--text-faint)" }}>
            Sort:
          </span>
          {(["score", "velocity", "newest"] as SortKey[]).map((s) => (
            <button
              key={s}
              onClick={() => setSortBy(s)}
              className={`filter-tab ${sortBy === s ? "active" : ""}`}
              style={{ color: sortBy === s ? "var(--accent)" : "var(--text-muted)" }}
            >
              {s === "score" ? "Score" : s === "velocity" ? "Velocity" : "Newest"}
            </button>
          ))}
        </div>
      </div>

      {loading && (
        <p className="text-[10px] tracking-widest uppercase text-center py-10" style={{ color: "var(--text-faint)" }}>
          Loading signals…
        </p>
      )}

      {/* Grouped sections (only when sorting by score) */}
      {!loading && sortBy === "score" && sections.map(({ id, label, min, max, color }) => {
        const items = sorted.filter((t) => t.ai_score >= min && t.ai_score <= max);
        if (items.length === 0) return null;
        return (
          <div key={id}>
            <div className="flex items-center gap-3 mb-4">
              <span
                style={{
                  display: "inline-block",
                  width: "6px",
                  height: "6px",
                  borderRadius: "50%",
                  background: color,
                  flexShrink: 0,
                }}
              />
              <p className="text-[10px] tracking-[0.3em] uppercase" style={{ color: "var(--text-muted)" }}>
                {label}
              </p>
              <span className="text-[10px]" style={{ color: "var(--text-faint)" }}>
                ({items.length})
              </span>
            </div>
            <TrendList items={items} />
          </div>
        );
      })}

      {/* Flat list (velocity / newest sort) */}
      {!loading && sortBy !== "score" && (
        <TrendList items={sorted} />
      )}

      {!loading && sorted.length === 0 && (
        <p className="text-sm text-center py-10" style={{ color: "var(--text-faint)" }}>
          No signals found for this filter.
        </p>
      )}
    </div>
  );
}

function TrendList({ items }: { items: any[] }) {
  return (
    <div className="space-y-px" style={{ background: "var(--border)" }}>
      {items.map((t: any) => (
        <Link
          key={t.id}
          href={`/trends/${t.id}`}
          className="hover-tile flex items-start gap-5 px-6 py-5"
        >
          {/* Score */}
          <div className="w-12 shrink-0 pt-0.5">
            <ScoreBadge score={t.ai_score} />
          </div>

          {/* Name + description */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1 flex-wrap">
              <p className="serif text-lg font-light leading-tight">{t.name}</p>
              <NewBadge createdAt={t.created_at} />
              {t.platform_count > 1 && (
                <CrossPlatformBadge
                  platformCount={t.platform_count}
                  confirmedSources={t.confirmed_sources || ""}
                />
              )}
            </div>
            <p className="text-xs leading-relaxed line-clamp-1" style={{ color: "var(--text-muted)" }}>
              {t.description}
            </p>
          </div>

          {/* Meta */}
          <div className="shrink-0 flex flex-col items-end gap-2">
            <SourceBadge source={t.source} />
            {t.signal_velocity > 0 && (
              <VelocityIndicator velocity={t.signal_velocity} />
            )}
          </div>
        </Link>
      ))}
    </div>
  );
}
