/**
 * SourceBadge - shows which platform detected this trend.
 * Distinct color per source so you can instantly tell signal origin.
 */

type Size = "sm" | "md";

const SOURCE_CONFIG: Record<string, { label: string; color: string; bg: string; icon: string }> = {
  tiktok:               { label: "TikTok",    color: "#69C9D0", bg: "rgba(105,201,208,0.1)", icon: "♪" },
  pinterest:            { label: "Pinterest", color: "#E60023", bg: "rgba(230,0,35,0.1)",    icon: "⌖" },
  pinterest_predicts_2026: { label: "Pinterest Predicts", color: "#E60023", bg: "rgba(230,0,35,0.12)", icon: "⌖" },
  pinterest_trends_2026:   { label: "Pinterest",           color: "#E60023", bg: "rgba(230,0,35,0.1)",  icon: "⌖" },
  reddit:               { label: "Reddit",    color: "#FF4500", bg: "rgba(255,69,0,0.1)",    icon: "◉" },
  google_trends:        { label: "Google",    color: "#4285F4", bg: "rgba(66,133,244,0.1)",  icon: "⊕" },
  editorial_rss:        { label: "Editorial", color: "#d4a853", bg: "rgba(212,168,83,0.1)",  icon: "✦" },
  trend_intelligence:   { label: "Intel",     color: "#a78bfa", bg: "rgba(167,139,250,0.1)", icon: "◈" },
  social_data:          { label: "Social",    color: "#34d399", bg: "rgba(52,211,153,0.1)",  icon: "◎" },
  depop_2026:           { label: "Resale",    color: "#FF2D55", bg: "rgba(255,45,85,0.1)",   icon: "◇" },
  tobe_doneger:         { label: "Forecast",  color: "#a78bfa", bg: "rgba(167,139,250,0.1)", icon: "◈" },
  wgsn:                 { label: "WGSN",      color: "#a78bfa", bg: "rgba(167,139,250,0.1)", icon: "◈" },
};

const FALLBACK = { label: "Signal", color: "rgba(245,240,235,0.4)", bg: "rgba(245,240,235,0.06)", icon: "·" };

export default function SourceBadge({ source, size = "sm" }: { source: string; size?: Size }) {
  const cfg = SOURCE_CONFIG[source] || FALLBACK;
  const isMd = size === "md";

  return (
    <span
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: isMd ? "5px" : "4px",
        padding: isMd ? "4px 10px" : "2px 8px",
        fontSize: isMd ? "11px" : "9px",
        letterSpacing: "0.12em",
        textTransform: "uppercase",
        fontFamily: "Inter, sans-serif",
        fontWeight: 400,
        color: cfg.color,
        background: cfg.bg,
        border: `1px solid ${cfg.color}26`,
        borderRadius: "2px",
        whiteSpace: "nowrap",
      }}
    >
      <span style={{ fontSize: isMd ? "12px" : "10px", lineHeight: 1 }}>{cfg.icon}</span>
      {cfg.label}
    </span>
  );
}
