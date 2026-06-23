"use client";

import { useEffect, useState, useCallback } from "react";
import { fetchLatestReport } from "@/lib/api";

const BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

type Brief = {
  headline?: string;
  category?: string;
  assortment_role?: string;
  price_tier?: string;
  peak_window?: string;
  buy_guidance?: string;
  markdown_risk?: string;
  confidence?: string;
};

type ReportTrend = {
  id: string;
  name: string;
  score: number;
  velocity: number;
  status: string;
  platform_count: number;
  sources: string[];
  cross_confirmed: boolean;
  thesis: string;
  market_question?: string | null;
  image_url?: string | null;
  brief: Brief;
};

type Report = {
  title: string;
  season_label: string;
  period: string;
  generated_at: string;
  prepared_by: string;
  executive_summary: string;
  methodology: string;
  trend_count: number;
  trends: ReportTrend[];
};

const ROLE_COLORS: Record<string, string> = {
  Core:      "rgba(106,191,135,0.18)",
  Fashion:   "rgba(212,168,83,0.18)",
  Statement: "rgba(139,92,246,0.18)",
  Test:      "rgba(100,116,139,0.18)",
};
const ROLE_TEXT: Record<string, string> = {
  Core:      "var(--green)",
  Fashion:   "var(--accent)",
  Statement: "#a78bfa",
  Test:      "rgba(245,240,235,0.45)",
};

const CONF_COLOR: Record<string, string> = {
  high:        "var(--green)",
  medium:      "var(--accent)",
  speculative: "var(--red)",
};

const ACCENT_PALETTE = [
  "#d4a853","#6abf87","#a78bfa","#60a5fa","#f472b6","#fb923c",
];

function Chip({ label, color, bg }: { label: string; color: string; bg: string }) {
  return (
    <span
      className="inline-block text-[10px] tracking-[0.18em] uppercase px-2.5 py-1 rounded-sm font-medium"
      style={{ color, background: bg }}
    >
      {label}
    </span>
  );
}

function ScoreRing({ score }: { score: number }) {
  const r = 28, circ = 2 * Math.PI * r;
  const fill = (score / 10) * circ;
  return (
    <svg width="72" height="72" viewBox="0 0 72 72" className="shrink-0">
      <circle cx="36" cy="36" r={r} fill="none" stroke="rgba(255,255,255,0.08)" strokeWidth="4" />
      <circle
        cx="36" cy="36" r={r}
        fill="none"
        stroke="var(--accent)"
        strokeWidth="4"
        strokeDasharray={`${fill} ${circ}`}
        strokeLinecap="round"
        transform="rotate(-90 36 36)"
        style={{ filter: "drop-shadow(0 0 6px rgba(212,168,83,0.5))" }}
      />
      <text x="36" y="38" textAnchor="middle" dominantBaseline="middle"
        fill="var(--accent)" fontSize="14" fontFamily="'Cormorant Garamond', Georgia, serif" fontWeight="400">
        {score.toFixed(1)}
      </text>
    </svg>
  );
}

export default function ReportPage() {
  const [report, setReport] = useState<Report | null>(null);
  const [loading, setLoading] = useState(true);
  const [regenerating, setRegenerating] = useState(false);

  const loadReport = useCallback(() => {
    setLoading(true);
    fetchLatestReport().then((d) => {
      setReport(d);
      setLoading(false);
    });
  }, []);

  useEffect(() => { loadReport(); }, [loadReport]);

  const handleRegenerate = async () => {
    setRegenerating(true);
    try {
      const res = await fetch(`${BASE}/reports/generate`, { method: "POST" });
      if (res.ok) {
        const fresh = await res.json();
        setReport(fresh);
      }
    } finally {
      setRegenerating(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-32">
        <div className="text-center space-y-3">
          <p className="serif italic text-2xl" style={{ color: "var(--accent)" }}>Compiling signals…</p>
          <p className="text-xs tracking-widest uppercase" style={{ color: "var(--text-faint)" }}>Reading the data</p>
        </div>
      </div>
    );
  }

  if (!report) {
    return (
      <div className="max-w-xl py-16 space-y-4">
        <h1 className="serif text-4xl font-light">No report yet</h1>
        <p className="text-sm leading-relaxed" style={{ color: "var(--text-muted)" }}>
          Generate the first one:
        </p>
        <pre className="text-xs p-4" style={{ background: "var(--bg-card)", border: "1px solid var(--border)" }}>
          cd backend{"\n"}python -m agents.trend_report
        </pre>
        <p className="text-xs" style={{ color: "var(--text-faint)" }}>
          Or hit the button above once you have the backend running.
        </p>
      </div>
    );
  }

  const genDate = new Date(report.generated_at).toLocaleDateString("en-GB", {
    day: "numeric", month: "long", year: "numeric",
  });

  return (
    <div className="space-y-0 pb-16">

      {/* ── Top bar: controls ──────────────────────────────────────── */}
      <div className="flex items-center justify-between mb-12 no-print flex-wrap gap-3">
        <div>
          <p className="text-[10px] tracking-[0.3em] uppercase" style={{ color: "var(--text-faint)" }}>
            Last generated {genDate}
          </p>
          <p className="text-xs mt-0.5" style={{ color: "var(--text-faint)" }}>
            {report.trend_count} trends · auto-updates when new signals arrive
          </p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={handleRegenerate}
            disabled={regenerating}
            className="text-[10px] tracking-[0.2em] uppercase px-4 py-2 transition-all"
            style={{
              border: "1px solid var(--border)",
              color: regenerating ? "var(--text-faint)" : "var(--text-muted)",
              cursor: regenerating ? "not-allowed" : "pointer",
            }}
          >
            {regenerating ? "Regenerating…" : "Regenerate"}
          </button>
          <button
            onClick={() => window.print()}
            className="text-[10px] tracking-[0.2em] uppercase px-4 py-2 transition-all"
            style={{ border: "1px solid var(--accent)", color: "var(--accent)" }}
          >
            Export PDF
          </button>
        </div>
      </div>

      {/* ── Cover ─────────────────────────────────────────────────── */}
      <header className="mb-20">
        <p className="text-[11px] tracking-[0.4em] uppercase mb-5" style={{ color: "var(--accent)" }}>
          {report.title} · {report.period}
        </p>
        <h1
          className="serif font-light leading-[0.9] mb-8"
          style={{ fontSize: "clamp(3.5rem, 12vw, 8rem)", letterSpacing: "-0.01em" }}
        >
          {report.season_label}
        </h1>
        <div
          className="flex flex-wrap gap-x-12 gap-y-3 pt-6"
          style={{ borderTop: "1px solid var(--border)" }}
        >
          {[
            ["Reporting Period", report.period],
            ["Trends Covered", `${report.trend_count} signals`],
            ["Prepared By", report.prepared_by],
          ].map(([label, val]) => (
            <div key={label}>
              <p className="text-[10px] tracking-[0.2em] uppercase" style={{ color: "var(--text-faint)" }}>{label}</p>
              <p className="text-sm mt-1" style={{ color: "var(--text)" }}>{val}</p>
            </div>
          ))}
        </div>
      </header>

      {/* ── Executive Summary ─────────────────────────────────────── */}
      <section className="mb-20 max-w-3xl">
        <p className="text-[10px] tracking-[0.3em] uppercase mb-6" style={{ color: "var(--text-faint)" }}>
          Executive Read
        </p>
        <div className="space-y-5">
          {report.executive_summary.split("\n").filter(Boolean).map((para, i) => (
            <p
              key={i}
              className="serif font-light leading-relaxed"
              style={{ fontSize: i === 0 ? "1.45rem" : "1.2rem", color: "var(--text)" }}
            >
              {para}
            </p>
          ))}
        </div>
      </section>

      <div style={{ borderTop: "1px solid var(--border)", marginBottom: "4rem" }} />

      {/* ── Trend Cards ───────────────────────────────────────────── */}
      <p className="text-[10px] tracking-[0.3em] uppercase mb-10" style={{ color: "var(--text-faint)" }}>
        The Calls · Ranked by Signal Strength
      </p>

      <div className="space-y-1">
        {report.trends.map((t, i) => {
          const accent = ACCENT_PALETTE[i % ACCENT_PALETTE.length];
          const role = t.brief?.assortment_role || "";
          const conf = (t.brief?.confidence || "").toLowerCase();

          return (
            <article
              key={t.id}
              className="report-card"
              style={{ marginBottom: "3.5rem" }}
            >
              {/* Hero: image OR gradient panel */}
              <div
                className="relative w-full overflow-hidden"
                style={{ height: 280, background: "var(--bg-card)" }}
              >
                {t.image_url ? (
                  <img
                    src={t.image_url}
                    alt={t.name}
                    className="w-full h-full object-cover"
                    style={{ filter: "brightness(0.55)" }}
                  />
                ) : (
                  /* Editorial fallback: big score number + gradient */
                  <div
                    className="absolute inset-0 flex items-center justify-center"
                    style={{
                      background: `linear-gradient(135deg, rgba(8,8,8,0.95) 0%, ${accent}22 100%)`,
                    }}
                  >
                    <span
                      className="serif font-light select-none"
                      style={{ fontSize: "10rem", color: `${accent}18`, lineHeight: 1 }}
                    >
                      {t.score.toFixed(0)}
                    </span>
                  </div>
                )}

                {/* Overlay gradient (always) */}
                <div
                  className="absolute inset-0"
                  style={{
                    background:
                      "linear-gradient(to top, rgba(8,8,8,0.97) 0%, rgba(8,8,8,0.5) 55%, transparent 100%)",
                  }}
                />

                {/* Overlay content */}
                <div className="absolute inset-0 flex flex-col justify-between p-6">
                  <div className="flex items-center justify-between">
                    <span
                      className="text-[10px] tracking-[0.3em] uppercase px-2.5 py-1"
                      style={{ background: "rgba(8,8,8,0.7)", color: accent }}
                    >
                      {String(i + 1).padStart(2, "0")} · {report.period}
                    </span>
                    {t.cross_confirmed && (
                      <span
                        className="text-[10px] tracking-[0.2em] uppercase px-2.5 py-1"
                        style={{ background: "rgba(8,8,8,0.7)", color: "var(--green)" }}
                      >
                        Cross-confirmed · {t.platform_count} platforms
                      </span>
                    )}
                  </div>

                  <div>
                    <h2 className="serif font-light leading-tight mb-1" style={{ fontSize: "clamp(1.6rem, 4vw, 2.4rem)", color: "#fff" }}>
                      {t.name}
                    </h2>
                    {t.brief?.headline && (
                      <p className="text-sm italic max-w-2xl" style={{ color: "rgba(255,255,255,0.7)" }}>
                        {t.brief.headline}
                      </p>
                    )}
                  </div>
                </div>
              </div>

              {/* Below-image row: score + chips + velocity */}
              <div
                className="flex items-center justify-between flex-wrap gap-4 px-1 py-4"
                style={{ borderBottom: "1px solid var(--border)" }}
              >
                <div className="flex items-center gap-4">
                  <ScoreRing score={t.score} />
                  <div className="space-y-1.5">
                    {role && (
                      <Chip
                        label={role}
                        color={ROLE_TEXT[role] || "var(--text-muted)"}
                        bg={ROLE_COLORS[role] || "rgba(255,255,255,0.06)"}
                      />
                    )}
                    {t.brief?.category && (
                      <div>
                        <span className="text-xs ml-0.5" style={{ color: "var(--text-muted)" }}>
                          {t.brief.category}
                        </span>
                      </div>
                    )}
                  </div>
                </div>

                <div className="flex flex-wrap gap-x-8 gap-y-1 text-right">
                  <div>
                    <p className="text-[10px] tracking-widest uppercase" style={{ color: "var(--text-faint)" }}>Velocity</p>
                    <p className="text-sm" style={{ color: t.velocity > 0 ? "var(--green)" : "var(--text-muted)" }}>
                      {t.velocity > 0 ? "+" : ""}{t.velocity}%
                    </p>
                  </div>
                  <div>
                    <p className="text-[10px] tracking-widest uppercase" style={{ color: "var(--text-faint)" }}>Status</p>
                    <p className="text-sm capitalize" style={{ color: "var(--text)" }}>{t.status}</p>
                  </div>
                  {t.brief?.price_tier && (
                    <div>
                      <p className="text-[10px] tracking-widest uppercase" style={{ color: "var(--text-faint)" }}>Price Tier</p>
                      <p className="text-sm" style={{ color: "var(--text)" }}>{t.brief.price_tier}</p>
                    </div>
                  )}
                  {t.brief?.peak_window && (
                    <div>
                      <p className="text-[10px] tracking-widest uppercase" style={{ color: "var(--text-faint)" }}>Peak Window</p>
                      <p className="text-sm" style={{ color: "var(--accent)" }}>{t.brief.peak_window}</p>
                    </div>
                  )}
                </div>
              </div>

              {/* Thesis */}
              {t.thesis && (
                <p
                  className="text-[15px] leading-relaxed max-w-3xl mt-5 px-1"
                  style={{ color: "var(--text-muted)" }}
                >
                  {t.thesis}
                </p>
              )}

              {/* Merch Brief: two big callout boxes */}
              {(t.brief?.buy_guidance || t.brief?.markdown_risk) && (
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-px mt-5" style={{ background: "var(--border)" }}>
                  {t.brief?.buy_guidance && (
                    <div className="p-5" style={{ background: "var(--bg-card)" }}>
                      <p className="text-[10px] tracking-[0.2em] uppercase mb-2" style={{ color: "var(--text-faint)" }}>
                        Buy Guidance
                      </p>
                      <p className="text-sm leading-relaxed" style={{ color: "var(--text)" }}>
                        {t.brief.buy_guidance}
                      </p>
                    </div>
                  )}
                  {t.brief?.markdown_risk && (
                    <div className="p-5" style={{ background: "var(--bg-card)" }}>
                      <p className="text-[10px] tracking-[0.2em] uppercase mb-2" style={{ color: "var(--text-faint)" }}>
                        Markdown Risk
                      </p>
                      <p className="text-sm leading-relaxed" style={{ color: "var(--text)" }}>
                        {t.brief.markdown_risk}
                      </p>
                    </div>
                  )}
                </div>
              )}

              {/* Conviction footer */}
              <div
                className="flex items-center justify-between px-1 pt-4 mt-1"
                style={{ borderTop: "1px solid var(--border)" }}
              >
                <div className="flex items-center gap-2">
                  <span
                    className="inline-block rounded-full"
                    style={{
                      width: 8, height: 8,
                      background: CONF_COLOR[conf] || "var(--text-faint)",
                      boxShadow: `0 0 8px ${CONF_COLOR[conf] || "transparent"}`,
                    }}
                  />
                  <span className="text-xs tracking-widest uppercase" style={{ color: "var(--text-faint)" }}>
                    Conviction
                  </span>
                  <span className="text-sm" style={{ color: "var(--text)" }}>
                    {t.brief?.confidence || "—"}
                  </span>
                </div>
                <div className="flex flex-wrap gap-2">
                  {t.sources.slice(0, 4).map((s) => (
                    <span
                      key={s}
                      className="text-[10px] tracking-[0.1em] uppercase px-2 py-0.5"
                      style={{ background: "var(--bg-hover)", color: "var(--text-faint)" }}
                    >
                      {s.replace(/_/g, " ")}
                    </span>
                  ))}
                </div>
              </div>
            </article>
          );
        })}
      </div>

      {/* ── Methodology ───────────────────────────────────────────── */}
      <div style={{ borderTop: "1px solid var(--border)", paddingTop: "3rem", marginTop: "2rem" }}>
        <p className="text-[10px] tracking-[0.3em] uppercase mb-3" style={{ color: "var(--text-faint)" }}>
          Methodology
        </p>
        <p className="text-sm leading-relaxed max-w-2xl" style={{ color: "var(--text-faint)" }}>
          {report.methodology}
        </p>
        <p className="text-[10px] mt-3" style={{ color: "var(--text-faint)" }}>
          Generated {genDate} · Scores are deterministic and reproducible from source data ·
          Commercial read is analyst interpretation, not financial advice.
        </p>
      </div>
    </div>
  );
}
