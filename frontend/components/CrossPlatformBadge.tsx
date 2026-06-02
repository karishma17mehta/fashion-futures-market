"use client";

/**
 * CrossPlatformBadge
 * Shows a "confirmed on N platforms" badge for trends with platform_count > 1.
 * When hovered, expands to show the source list.
 */
import { useState } from "react";

interface Props {
  platformCount: number;
  confirmedSources: string; // comma-separated, e.g. "tiktok,editorial_rss,reddit"
}

const SOURCE_ICONS: Record<string, string> = {
  tiktok: "♪",
  pinterest: "📌",
  reddit: "r/",
  editorial_rss: "✦",
  google_trends: "↗",
  social_data: "◉",
};

export default function CrossPlatformBadge({ platformCount, confirmedSources }: Props) {
  const [open, setOpen] = useState(false);

  if (!platformCount || platformCount <= 1) return null;

  const sources = confirmedSources
    ? confirmedSources
        .split(",")
        .map((s) => s.trim())
        .filter(Boolean)
    : [];

  const label =
    platformCount >= 4
      ? "Quad-confirmed"
      : platformCount === 3
      ? "Triple-confirmed"
      : "Cross-confirmed";

  const glowColor =
    platformCount >= 4
      ? "#d4a853"   // gold
      : platformCount === 3
      ? "#69C9D0"   // teal
      : "#4ade80";  // green

  return (
    <div style={{ position: "relative", display: "inline-block" }}>
      <button
        onClick={() => setOpen((v) => !v)}
        style={{
          display: "inline-flex",
          alignItems: "center",
          gap: 5,
          padding: "2px 8px",
          border: `1px solid ${glowColor}`,
          borderRadius: 2,
          background: `${glowColor}18`,
          color: glowColor,
          fontSize: 9,
          letterSpacing: "0.15em",
          textTransform: "uppercase",
          cursor: "pointer",
          fontFamily: "inherit",
          transition: "background 0.15s",
        }}
      >
        <span style={{ fontSize: 11 }}>◈</span>
        {label} · {platformCount} sources
      </button>

      {open && sources.length > 0 && (
        <div
          style={{
            position: "absolute",
            top: "calc(100% + 6px)",
            left: 0,
            background: "var(--bg-card)",
            border: `1px solid ${glowColor}40`,
            borderRadius: 3,
            padding: "10px 14px",
            zIndex: 20,
            minWidth: 170,
            boxShadow: `0 4px 20px ${glowColor}20`,
          }}
        >
          <p
            style={{
              fontSize: 8,
              letterSpacing: "0.2em",
              textTransform: "uppercase",
              color: "var(--text-faint)",
              marginBottom: 8,
            }}
          >
            Detected on
          </p>
          <div style={{ display: "flex", flexDirection: "column", gap: 5 }}>
            {sources.map((src) => (
              <div
                key={src}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 8,
                  fontSize: 11,
                  color: "var(--text-muted)",
                }}
              >
                <span style={{ color: glowColor, fontSize: 10 }}>
                  {SOURCE_ICONS[src] || "•"}
                </span>
                {src.replace(/_/g, " ")}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
