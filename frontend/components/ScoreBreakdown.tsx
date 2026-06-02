/**
 * ScoreBreakdown — visualizes the 5 scoring components as labeled bars.
 * Used on the trend detail page to show WHY a trend scored what it scored.
 *
 * Components map to the formula weights:
 *   velocity     30%  — growth speed
 *   acceleration 20%  — growth acceleration
 *   novelty      25%  — freshness
 *   volume       10%  — search mass
 *   cross_platform 15% — multi-source confirmation
 */

const COMPONENTS = [
  { key: "velocity",       label: "Velocity",        weight: "30%", desc: "How fast it's growing" },
  { key: "novelty",        label: "Novelty",         weight: "25%", desc: "How fresh the signal is" },
  { key: "acceleration",   label: "Acceleration",    weight: "20%", desc: "Whether growth is speeding up" },
  { key: "cross_platform", label: "Cross-Platform",  weight: "15%", desc: "Multi-source confirmation" },
  { key: "volume",         label: "Volume",          weight: "10%", desc: "Search mass & reach" },
];

function barColor(score: number): string {
  if (score >= 7.5) return "#6abf87";   // green
  if (score >= 5.0) return "#d4a853";   // gold
  if (score >= 3.0) return "rgba(245,240,235,0.3)";
  return "#e86060";                      // red
}

export default function ScoreBreakdown({ components }: { components?: Record<string, number> }) {
  if (!components) return null;

  return (
    <div className="space-y-3">
      {COMPONENTS.map(({ key, label, weight, desc }) => {
        const raw = components[key];
        if (raw === undefined) return null;
        const pct = Math.round((raw / 10) * 100);
        const color = barColor(raw);

        return (
          <div key={key}>
            <div className="flex items-center justify-between mb-1.5">
              <div className="flex items-center gap-2">
                <span
                  className="text-[9px] tracking-widest uppercase"
                  style={{ color: "var(--text-muted)" }}
                >
                  {label}
                </span>
                <span
                  className="text-[9px] tracking-widest uppercase"
                  style={{ color: "var(--text-faint)" }}
                >
                  {weight}
                </span>
              </div>
              <span
                className="text-[11px] font-light"
                style={{ color, fontFamily: "'Cormorant Garamond', Georgia, serif" }}
              >
                {raw.toFixed(1)}
              </span>
            </div>
            {/* Bar track */}
            <div
              style={{
                height: "2px",
                background: "rgba(255,255,255,0.07)",
                borderRadius: "1px",
                overflow: "hidden",
              }}
            >
              <div
                style={{
                  height: "100%",
                  width: `${pct}%`,
                  background: color,
                  borderRadius: "1px",
                  transition: "width 0.6s ease",
                }}
              />
            </div>
            <p
              className="text-[9px] mt-1"
              style={{ color: "var(--text-faint)" }}
            >
              {desc}
            </p>
          </div>
        );
      })}
    </div>
  );
}
