/**
 * BuyersView
 * ==========
 * Translates a trend's raw signals into a merchant's decision: the call,
 * the window to act, suggested categories, and the risk.
 *
 * Everything here is DERIVED DETERMINISTICALLY from the trend's own fields
 * (score, velocity, status, platform confirmation) — no LLM-authored numbers.
 * This is the "so what do I do Monday morning" layer.
 */

interface Trend {
  ai_score: number;
  signal_velocity: number;
  status: string;
  platform_count?: number;
  confirmed_sources?: string | null;
  source: string;
  name: string;
}

type Call = "STRONG BUY" | "BUY" | "WATCH" | "HOLD" | "TOO LATE";

function deriveCall(t: Trend): { call: Call; blurb: string; color: string } {
  const score = t.ai_score ?? 0;
  const vel = t.signal_velocity ?? 0;
  const status = (t.status || "").toLowerCase();

  if (status === "mainstream" || status === "dead") {
    return {
      call: "TOO LATE",
      blurb: "Already mainstream — the margin window has closed. Markdown risk if you enter now.",
      color: "var(--text-muted)",
    };
  }
  if (score >= 8 && vel > 0) {
    return {
      call: "STRONG BUY",
      blurb: "Accelerating with multi-signal strength. Commit core units now, before competitors price it in.",
      color: "var(--green)",
    };
  }
  if (score >= 6.5) {
    return {
      call: "BUY",
      blurb: "Past the noise threshold and climbing. Open a test buy; scale on the next confirmation.",
      color: "var(--green)",
    };
  }
  if (score >= 5) {
    return {
      call: "WATCH",
      blurb: "Real signal, not yet proven. Sample, don't commit — re-check in 2–3 weeks.",
      color: "var(--accent)",
    };
  }
  return {
    call: "HOLD",
    blurb: "Below the actionable threshold. Note it, but no buy rationale yet.",
    color: "var(--text-faint)",
  };
}

function deriveWindow(t: Trend): string {
  const vel = t.signal_velocity ?? 0;
  const score = t.ai_score ?? 0;
  const status = (t.status || "").toLowerCase();
  if (status === "mainstream" || status === "dead") return "Window closed";
  if (vel >= 20) return "2–6 weeks — move fast";
  if (vel >= 8 || score >= 7.5) return "8–12 weeks";
  if (score >= 5) return "1 quarter build";
  return "3–6 month watch";
}

// Map trend-name keywords to merchant categories.
const CATEGORY_RULES: { match: RegExp; cats: string[] }[] = [
  { match: /quiet luxury|old money|quarter zip|tailor|minimal|edited|capsule/i, cats: ["Knitwear", "Outerwear", "Tailoring"] },
  { match: /ballet|coquette|romantic|bow|lace/i, cats: ["Dresses", "Knitwear", "Accessories"] },
  { match: /golf|tennis|preppy|sport|athleisure|gorpcore/i, cats: ["Polos", "Outerwear", "Footwear"] },
  { match: /academia|library|tweed|scholar/i, cats: ["Knitwear", "Trousers", "Outerwear"] },
  { match: /nostalgia|vintage|thrift|retro|y2k|90s|denim/i, cats: ["Denim", "Tops", "Accessories"] },
  { match: /nails|beauty|glow|skin|makeup/i, cats: ["Beauty", "Accessories"] },
  { match: /summer|resort|linen|coastal|beach/i, cats: ["Dresses", "Swim", "Linen"] },
];

function deriveCategories(name: string): string[] {
  for (const rule of CATEGORY_RULES) {
    if (rule.match.test(name)) return rule.cats;
  }
  return ["Tops", "Outerwear", "Accessories"]; // sensible default
}

function deriveRisk(t: Trend): { label: string; detail: string; tone: "low" | "med" | "high" } {
  const platforms = t.platform_count ?? 1;
  const sources = (t.confirmed_sources || t.source || "").toLowerCase();
  const editorial = /editorial|world_news|wwd|vogue/.test(sources);

  if (platforms >= 3 || (platforms >= 2 && editorial)) {
    return { label: "Low risk", detail: "Confirmed across multiple platforms — durable signal.", tone: "low" };
  }
  if (platforms === 2) {
    return { label: "Moderate risk", detail: "Two-source signal. Watch for editorial pickup to confirm.", tone: "med" };
  }
  // single platform
  if (/tiktok|reddit/.test(sources)) {
    return { label: "High risk", detail: "Single social platform, no editorial confirmation — could be a flash.", tone: "high" };
  }
  return { label: "Moderate risk", detail: "Single-source signal — needs cross-platform confirmation.", tone: "med" };
}

export default function BuyersView({ trend }: { trend: Trend }) {
  const { call, blurb, color } = deriveCall(trend);
  const window = deriveWindow(trend);
  const categories = deriveCategories(trend.name);
  const risk = deriveRisk(trend);

  const riskColor =
    risk.tone === "low" ? "var(--green)" : risk.tone === "high" ? "#e05a5a" : "var(--accent)";

  return (
    <div
      className="px-6 py-6"
      style={{ background: "var(--bg-card)", border: "1px solid var(--border)" }}
    >
      <div className="flex items-center justify-between mb-5">
        <p className="text-[9px] tracking-[0.3em] uppercase" style={{ color: "var(--text-faint)" }}>
          The Buyer&apos;s View
        </p>
        <p className="text-[9px]" style={{ color: "var(--text-faint)" }}>
          Derived from signal data
        </p>
      </div>

      {/* The call */}
      <div className="flex items-baseline gap-3 mb-2 flex-wrap">
        <span
          className="text-[11px] tracking-[0.2em] uppercase px-2.5 py-1"
          style={{ color, border: `1px solid ${color}`, borderRadius: 2 }}
        >
          {call}
        </span>
        <span className="text-xs" style={{ color: "var(--text-faint)" }}>
          {window}
        </span>
      </div>
      <p className="text-sm leading-relaxed mb-6" style={{ color: "var(--text-muted)" }}>
        {blurb}
      </p>

      {/* Detail grid */}
      <div className="grid grid-cols-2 gap-px" style={{ background: "var(--border)" }}>
        <div className="px-4 py-4" style={{ background: "var(--bg-card)" }}>
          <p className="text-[8px] tracking-widest uppercase mb-2" style={{ color: "var(--text-faint)" }}>
            Suggested Categories
          </p>
          <div className="flex flex-wrap gap-1.5">
            {categories.map((c) => (
              <span
                key={c}
                className="text-[10px] px-2 py-0.5"
                style={{
                  color: "var(--text-muted)",
                  border: "1px solid var(--border)",
                  borderRadius: 2,
                }}
              >
                {c}
              </span>
            ))}
          </div>
        </div>
        <div className="px-4 py-4" style={{ background: "var(--bg-card)" }}>
          <p className="text-[8px] tracking-widest uppercase mb-2" style={{ color: "var(--text-faint)" }}>
            Risk
          </p>
          <p className="text-xs font-medium mb-1" style={{ color: riskColor }}>
            {risk.label}
          </p>
          <p className="text-[10px] leading-snug" style={{ color: "var(--text-faint)" }}>
            {risk.detail}
          </p>
        </div>
      </div>
    </div>
  );
}
