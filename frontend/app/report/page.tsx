"use client";

import { useEffect, useState } from "react";
import { fetchLatestReport } from "@/lib/api";

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

function Label({ children }: { children: React.ReactNode }) {
  return (
    <p
      className="text-[10px] tracking-[0.25em] uppercase print-muted"
      style={{ color: "var(--text-faint)" }}
    >
      {children}
    </p>
  );
}

function ConfidenceDot({ level }: { level?: string }) {
  const l = (level || "").toLowerCase();
  const color =
    l === "high" ? "var(--green)" : l === "medium" ? "var(--accent)" : "var(--red)";
  return (
    <span className="inline-flex items-center gap-2">
      <span
        className="inline-block rounded-full"
        style={{ width: 7, height: 7, background: color }}
      />
      <span style={{ color: "var(--text)" }}>{level || "—"}</span>
    </span>
  );
}

function BriefField({ label, value }: { label: string; value?: string }) {
  if (!value) return null;
  return (
    <div className="brief-cell">
      <Label>{label}</Label>
      <p className="mt-1.5 text-sm leading-snug print-muted" style={{ color: "var(--text)" }}>
        {value}
      </p>
    </div>
  );
}

export default function ReportPage() {
  const [report, setReport] = useState<Report | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchLatestReport().then((d) => {
      setReport(d);
      setLoading(false);
    });
  }, []);

  if (loading) {
    return (
      <p className="text-sm py-20 text-center" style={{ color: "var(--text-faint)" }}>
        Compiling report…
      </p>
    );
  }

  if (!report) {
    return (
      <div className="max-w-xl py-16 space-y-4">
        <h1 className="serif text-4xl font-light">No report yet</h1>
        <p className="text-sm leading-relaxed" style={{ color: "var(--text-muted)" }}>
          Generate one from the backend:
        </p>
        <pre
          className="text-xs p-4 rounded"
          style={{ background: "var(--bg-card)", border: "1px solid var(--border)" }}
        >
          cd backend{"\n"}python -m agents.trend_report
        </pre>
      </div>
    );
  }

  return (
    <div className="report-sheet space-y-16 pb-10">
      {/* ── Cover ────────────────────────────────────────────────────────── */}
      <header className="report-cover pt-6">
        <div className="flex items-center justify-between no-print mb-12">
          <Label>{report.period} · Trend Intelligence</Label>
          <button
            onClick={() => window.print()}
            className="text-[10px] tracking-[0.2em] uppercase px-4 py-2 transition-colors"
            style={{ border: "1px solid var(--border)", color: "var(--accent)" }}
          >
            Download PDF
          </button>
        </div>

        <p className="text-[11px] tracking-[0.35em] uppercase mb-6 print-accent" style={{ color: "var(--accent)" }}>
          {report.title}
        </p>
        <h1 className="serif font-light leading-[0.95] mb-8" style={{ fontSize: "clamp(3rem, 9vw, 6.5rem)" }}>
          {report.season_label}
        </h1>

        <div className="flex flex-wrap gap-x-10 gap-y-2">
          <div>
            <Label>Reporting Period</Label>
            <p className="text-sm mt-1" style={{ color: "var(--text)" }}>{report.period}</p>
          </div>
          <div>
            <Label>Signals Covered</Label>
            <p className="text-sm mt-1" style={{ color: "var(--text)" }}>{report.trend_count} trends</p>
          </div>
          <div>
            <Label>Prepared By</Label>
            <p className="text-sm mt-1" style={{ color: "var(--text)" }}>{report.prepared_by}</p>
          </div>
        </div>
      </header>

      {/* ── Executive summary ────────────────────────────────────────────── */}
      <section className="report-card max-w-3xl">
        <Label>Executive Read</Label>
        <div className="mt-4 space-y-4">
          {report.executive_summary.split("\n").filter(Boolean).map((para, i) => (
            <p
              key={i}
              className="serif font-light leading-relaxed print-muted"
              style={{ fontSize: "1.35rem", color: "var(--text)" }}
            >
              {para}
            </p>
          ))}
        </div>
      </section>

      <hr className="rule" />

      {/* ── Trend briefs ─────────────────────────────────────────────────── */}
      <section className="space-y-12">
        <Label>The Calls · Ranked by Signal Strength</Label>

        {report.trends.map((t, i) => (
          <article key={t.id} className="report-card" style={{ borderTop: "1px solid var(--border)", paddingTop: "2rem" }}>
            {/* Row head */}
            <div className="flex items-start justify-between gap-6 flex-wrap">
              <div className="flex items-baseline gap-5">
                <span
                  className="serif text-3xl font-light print-accent"
                  style={{ color: "var(--accent)" }}
                >
                  {String(i + 1).padStart(2, "0")}
                </span>
                <div>
                  <h2 className="serif text-3xl font-light leading-tight">{t.name}</h2>
                  {t.brief?.headline && (
                    <p className="mt-1 text-sm italic print-muted" style={{ color: "var(--text-muted)" }}>
                      {t.brief.headline}
                    </p>
                  )}
                </div>
              </div>
              <div className="text-right">
                <span className="serif text-4xl font-light score-glow print-accent" style={{ color: "var(--accent)" }}>
                  {t.score.toFixed(1)}
                </span>
                <span className="text-xs" style={{ color: "var(--text-faint)" }}> / 10</span>
              </div>
            </div>

            {/* Signal evidence strip */}
            <div className="flex flex-wrap gap-x-8 gap-y-2 mt-5 mb-6">
              <span className="text-xs" style={{ color: "var(--text-muted)" }}>
                <span style={{ color: "var(--text-faint)" }}>Velocity </span>
                {t.velocity > 0 ? `+${t.velocity}%` : `${t.velocity}%`}
              </span>
              <span className="text-xs" style={{ color: "var(--text-muted)" }}>
                <span style={{ color: "var(--text-faint)" }}>Status </span>
                {t.status}
              </span>
              <span className="text-xs" style={{ color: "var(--text-muted)" }}>
                <span style={{ color: "var(--text-faint)" }}>Confirmation </span>
                {t.cross_confirmed ? `${t.platform_count} platforms` : "single source"}
              </span>
              {t.sources.length > 0 && (
                <span className="text-xs" style={{ color: "var(--text-muted)" }}>
                  <span style={{ color: "var(--text-faint)" }}>Sources </span>
                  {t.sources.slice(0, 4).join(", ")}
                </span>
              )}
            </div>

            {/* Thesis */}
            {t.thesis && (
              <p className="text-[15px] leading-relaxed max-w-3xl mb-6 print-muted" style={{ color: "var(--text-muted)" }}>
                {t.thesis}
              </p>
            )}

            {/* Merch brief grid */}
            <div className="max-w-3xl">
              <Label>Merch Brief</Label>
              <div className="brief-grid mt-3">
                <BriefField label="Category" value={t.brief?.category} />
                <BriefField label="Assortment Role" value={t.brief?.assortment_role} />
                <BriefField label="Price Tier" value={t.brief?.price_tier} />
                <BriefField label="Peak Window" value={t.brief?.peak_window} />
                <BriefField label="Buy Guidance" value={t.brief?.buy_guidance} />
                <BriefField label="Markdown Risk" value={t.brief?.markdown_risk} />
              </div>
              <div className="flex items-center justify-between mt-3 px-1">
                <Label>Conviction</Label>
                <span className="text-sm">
                  <ConfidenceDot level={t.brief?.confidence} />
                </span>
              </div>
            </div>
          </article>
        ))}
      </section>

      <hr className="rule" />

      {/* ── Methodology ──────────────────────────────────────────────────── */}
      <section className="report-card max-w-3xl">
        <Label>Methodology</Label>
        <p className="text-sm leading-relaxed mt-3 print-muted" style={{ color: "var(--text-muted)" }}>
          {report.methodology}
        </p>
        <p className="text-[10px] mt-4" style={{ color: "var(--text-faint)" }}>
          Generated {new Date(report.generated_at).toLocaleDateString()} · Signal scores are deterministic and
          reproducible from source data · Commercial read is analyst interpretation, not financial advice.
        </p>
      </section>
    </div>
  );
}
