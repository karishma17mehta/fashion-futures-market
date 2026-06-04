"use client";
/**
 * SignalTicker - horizontally scrolling live signal feed.
 * Shows the most recent detected trends in a Bloomberg-style ticker.
 */
import { useEffect, useState } from "react";

interface TickerItem {
  id: string;
  name: string;
  ai_score: number;
  source: string;
  signal_velocity: number;
}

const SOURCE_ICONS: Record<string, string> = {
  tiktok: "♪",
  pinterest: "⌖",
  pinterest_predicts_2026: "⌖",
  pinterest_trends_2026: "⌖",
  reddit: "◉",
  google_trends: "⊕",
  editorial_rss: "✦",
  trend_intelligence: "◈",
  social_data: "◎",
  depop_2026: "◇",
};

function scoreColor(score: number) {
  if (score >= 8) return "#6abf87";
  if (score >= 6) return "#d4a853";
  return "rgba(245,240,235,0.5)";
}

export default function SignalTicker({ items }: { items: TickerItem[] }) {
  const [offset, setOffset] = useState(0);

  // Duplicate items for seamless loop
  const doubled = [...items, ...items];

  useEffect(() => {
    if (items.length === 0) return;
    const interval = setInterval(() => {
      setOffset((prev) => {
        // Reset after half the total width (~items.length * 220px per item)
        const halfWidth = items.length * 220;
        return prev >= halfWidth ? 0 : prev + 0.6;
      });
    }, 16);
    return () => clearInterval(interval);
  }, [items.length]);

  if (items.length === 0) return null;

  return (
    <div
      style={{
        borderTop: "1px solid var(--border)",
        borderBottom: "1px solid var(--border)",
        background: "rgba(255,255,255,0.02)",
        overflow: "hidden",
        height: "36px",
        display: "flex",
        alignItems: "center",
        position: "relative",
      }}
    >
      {/* LIVE badge */}
      <div
        style={{
          position: "absolute",
          left: 0,
          top: 0,
          bottom: 0,
          zIndex: 10,
          display: "flex",
          alignItems: "center",
          paddingLeft: "16px",
          paddingRight: "20px",
          background: "linear-gradient(to right, var(--bg) 85%, transparent)",
          gap: "6px",
        }}
      >
        <span
          style={{
            width: "6px",
            height: "6px",
            borderRadius: "50%",
            background: "#6abf87",
            display: "inline-block",
            animation: "pulse 2s infinite",
          }}
        />
        <span
          style={{
            fontSize: "9px",
            letterSpacing: "0.2em",
            textTransform: "uppercase",
            color: "#6abf87",
            fontWeight: 500,
          }}
        >
          Live Signals
        </span>
      </div>

      {/* Scrolling content */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: "0",
          transform: `translateX(calc(120px - ${offset}px))`,
          willChange: "transform",
          paddingLeft: "80px",
        }}
      >
        {doubled.map((item, i) => (
          <div
            key={`${item.id}-${i}`}
            style={{
              display: "flex",
              alignItems: "center",
              gap: "8px",
              padding: "0 24px",
              borderRight: "1px solid var(--border)",
              whiteSpace: "nowrap",
              minWidth: "220px",
            }}
          >
            <span style={{ fontSize: "10px", color: "rgba(245,240,235,0.25)" }}>
              {SOURCE_ICONS[item.source] || "·"}
            </span>
            <span
              style={{
                fontSize: "11px",
                color: "var(--text)",
                fontFamily: "'Cormorant Garamond', Georgia, serif",
                fontWeight: 300,
                letterSpacing: "0.02em",
              }}
            >
              {item.name}
            </span>
            <span
              style={{
                fontSize: "10px",
                fontWeight: 500,
                color: scoreColor(item.ai_score),
              }}
            >
              {item.ai_score.toFixed(1)}
            </span>
          </div>
        ))}
      </div>

      {/* Right fade */}
      <div
        style={{
          position: "absolute",
          right: 0,
          top: 0,
          bottom: 0,
          width: "60px",
          background: "linear-gradient(to left, var(--bg), transparent)",
          pointerEvents: "none",
        }}
      />
    </div>
  );
}
