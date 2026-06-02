"use client";

/**
 * ScoreSparkline
 * Renders a small inline SVG line chart of a trend's score history.
 * Points come from GET /signals/score-history/{trend_id}
 */
import { useEffect, useState } from "react";

interface HistoryPoint {
  recorded_at: string;
  score: number;
}

interface Props {
  trendId: string;
  width?: number;
  height?: number;
}

export default function ScoreSparkline({ trendId, width = 160, height = 40 }: Props) {
  const [points, setPoints] = useState<HistoryPoint[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/signals/score-history/${trendId}`)
      .then((r) => r.json())
      .then((d) => {
        setPoints(d.history || []);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [trendId]);

  if (loading) {
    return (
      <div
        style={{ width, height, background: "var(--bg-card)", borderRadius: 2 }}
        className="animate-pulse"
      />
    );
  }

  if (points.length < 2) {
    return (
      <p className="text-[9px]" style={{ color: "var(--text-faint)" }}>
        Not enough history yet
      </p>
    );
  }

  // Normalise to SVG coords
  const pad = 4;
  const scores = points.map((p) => p.score);
  const minS = Math.min(...scores);
  const maxS = Math.max(...scores);
  const range = maxS - minS || 1;

  const toX = (i: number) => pad + (i / (points.length - 1)) * (width - pad * 2);
  const toY = (s: number) => pad + ((maxS - s) / range) * (height - pad * 2);

  const pathD = points
    .map((p, i) => `${i === 0 ? "M" : "L"} ${toX(i).toFixed(1)} ${toY(p.score).toFixed(1)}`)
    .join(" ");

  // Filled area path
  const areaD =
    pathD +
    ` L ${toX(points.length - 1).toFixed(1)} ${(height - pad).toFixed(1)}` +
    ` L ${pad} ${(height - pad).toFixed(1)} Z`;

  const lastScore = scores[scores.length - 1];
  const firstScore = scores[0];
  const trend = lastScore >= firstScore;
  const lineColor = trend ? "var(--green)" : "#e05a5a";
  const fillColor = trend ? "rgba(74,222,128,0.08)" : "rgba(224,90,90,0.08)";

  // Latest value label
  const lx = toX(points.length - 1);
  const ly = toY(lastScore);

  return (
    <div style={{ position: "relative" }}>
      <svg
        width={width}
        height={height}
        style={{ overflow: "visible", display: "block" }}
      >
        {/* Fill */}
        <path d={areaD} fill={fillColor} />
        {/* Line */}
        <path
          d={pathD}
          fill="none"
          stroke={lineColor}
          strokeWidth={1.5}
          strokeLinejoin="round"
          strokeLinecap="round"
        />
        {/* End dot */}
        <circle cx={lx} cy={ly} r={2.5} fill={lineColor} />
      </svg>
      {/* Score label to the right of the dot */}
      <span
        style={{
          position: "absolute",
          left: lx + 6,
          top: ly - 7,
          fontSize: 9,
          color: lineColor,
          fontVariantNumeric: "tabular-nums",
          whiteSpace: "nowrap",
        }}
      >
        {lastScore.toFixed(1)}
      </span>
    </div>
  );
}
