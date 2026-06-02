export default function AboutPage() {
  return (
    <div className="max-w-2xl space-y-16 pt-4">

      {/* Header */}
      <div>
        <p className="text-[10px] tracking-[0.3em] uppercase mb-3" style={{ color: "var(--accent)" }}>
          About
        </p>
        <h1 className="serif text-6xl font-light leading-[1.05] mb-5">
          How it<br /><em style={{ color: "var(--accent)" }}>works.</em>
        </h1>
        <p className="text-base leading-relaxed" style={{ color: "var(--text-muted)" }}>
          A prediction market for fashion micro-trends — where AI surfaces the signal
          and the crowd prices what comes next.
        </p>
      </div>

      <hr className="rule" />

      {/* The idea */}
      <section className="space-y-5">
        <p className="text-[10px] tracking-[0.3em] uppercase" style={{ color: "var(--text-muted)" }}>The Idea</p>
        <p className="serif text-2xl font-light leading-relaxed" style={{ color: "var(--text)" }}>
          Every season, a handful of underground trends go mainstream.
          A handful don't. The fashion industry spends enormous resources
          trying to predict which is which.
        </p>
        <p className="text-base leading-relaxed" style={{ color: "var(--text-muted)" }}>
          We think the crowd, given the right information and proper incentives,
          is better at that prediction than any single analyst. Fashion Futures
          combines AI-powered trend intelligence with prediction market mechanics.
          The AI does the signal work. You decide what it means.
        </p>
      </section>

      <hr className="rule" />

      {/* Steps */}
      <section className="space-y-8">
        <p className="text-[10px] tracking-[0.3em] uppercase" style={{ color: "var(--text-muted)" }}>How It Works</p>

        {[
          {
            n: "01",
            title: "AI scans for signals",
            body: "Our system continuously monitors social platforms, search behavior, resale marketplaces, and runway data — looking for patterns that suggest a trend is building momentum before it surfaces in mainstream media.",
          },
          {
            n: "02",
            title: "Every signal becomes a scored trend",
            body: "Each signal is scored on novelty, velocity, and mainstream potential — 1 to 10. The AI also writes a thesis explaining why the trend matters and what would confirm it going mainstream.",
          },
          {
            n: "03",
            title: "Trends become prediction markets",
            body: "Each scored trend is paired with a specific, resolvable question — not 'will this be popular?' but something concrete, verifiable, and time-bounded. Good questions have clear answers.",
          },
          {
            n: "04",
            title: "You trade with points",
            body: "Every account starts with 1,000 points. Buy YES or NO shares on any open market. Prices update in real time using a logarithmic market scoring rule — the same mechanism used by serious prediction platforms. No real money.",
          },
          {
            n: "05",
            title: "Markets resolve. Winners earn.",
            body: "When a market's resolution date arrives, it closes based on real-world evidence. Correct positions pay out proportional to shares held. Your accuracy rate builds over time — a track record of how well you read fashion signals.",
          },
        ].map((s) => (
          <div key={s.n} className="flex gap-8" style={{ borderTop: "1px solid var(--border)", paddingTop: "1.5rem" }}>
            <span className="serif text-3xl font-light shrink-0 mt-0.5" style={{ color: "var(--accent)" }}>
              {s.n}
            </span>
            <div>
              <p className="font-medium mb-2">{s.title}</p>
              <p className="text-sm leading-relaxed" style={{ color: "var(--text-muted)" }}>{s.body}</p>
            </div>
          </div>
        ))}
      </section>

      <hr className="rule" />

      {/* Intelligence */}
      <section className="space-y-6">
        <p className="text-[10px] tracking-[0.3em] uppercase" style={{ color: "var(--text-muted)" }}>Our Intelligence</p>
        <p className="text-base leading-relaxed" style={{ color: "var(--text-muted)" }}>
          Fashion Futures monitors signals across social platforms, resale marketplaces,
          visual search behavior, and broader cultural data. We look at what people are
          searching for, saving, buying, and selling — not just what publications are covering.
        </p>
        <p className="text-base leading-relaxed" style={{ color: "var(--text-muted)" }}>
          Our AI synthesizes these signals into scored trend assessments and generates
          the market questions. We focus on specificity: a question with a clear,
          verifiable answer is more useful than a vague directional bet.
        </p>

        <div className="grid grid-cols-2 sm:grid-cols-3 gap-px mt-4" style={{ background: "var(--border)" }}>
          {[
            { label: "TikTok Hashtags",  icon: "♪", desc: "WoW view count growth" },
            { label: "Pinterest Trends", icon: "⌖", desc: "MoM & YoY search volume" },
            { label: "Reddit Signals",   icon: "◉", desc: "Community trend discussion" },
            { label: "Editorial RSS",    icon: "✦", desc: "Vogue, Harper's, WWD, ELLE" },
            { label: "Google Trends",    icon: "⊕", desc: "Search velocity data" },
            { label: "Claude AI",        icon: "◈", desc: "Narrative & thesis layer" },
          ].map((s) => (
            <div key={s.label} className="px-5 py-6" style={{ background: "var(--bg-card)" }}>
              <div className="serif text-2xl mb-2" style={{ color: "var(--accent)" }}>{s.icon}</div>
              <p className="text-[10px] tracking-widest uppercase mb-1" style={{ color: "var(--text-muted)" }}>{s.label}</p>
              <p className="text-[10px]" style={{ color: "var(--text-faint)" }}>{s.desc}</p>
            </div>
          ))}
        </div>
      </section>

      <hr className="rule" />

      {/* Who it's for */}
      <section className="space-y-5">
        <p className="text-[10px] tracking-[0.3em] uppercase" style={{ color: "var(--text-muted)" }}>Who It's For</p>
        <div className="space-y-px" style={{ background: "var(--border)" }}>
          {[
            {
              label: "Fashion enthusiasts",
              body: "Put your trend instincts to work. Build a track record. See how your reads compare to the crowd.",
            },
            {
              label: "Industry professionals",
              body: "Use market prices as an independent signal. When the crowd strongly prices YES on a trend, that's crowd-sourced validation cutting through editorial noise.",
            },
            {
              label: "Brands & retailers",
              body: "Aggregated market data tells you which trends have the strongest conviction behind them — and which the crowd is skeptical about despite media coverage.",
            },
          ].map((item) => (
            <div key={item.label} className="px-6 py-5" style={{ background: "var(--bg-card)" }}>
              <p className="text-sm font-medium mb-1">{item.label}</p>
              <p className="text-sm leading-relaxed" style={{ color: "var(--text-muted)" }}>{item.body}</p>
            </div>
          ))}
        </div>
      </section>

      <hr className="rule" />

      {/* What's coming — agentic vision */}
      <section className="space-y-6">
        <p className="text-[10px] tracking-[0.3em] uppercase" style={{ color: "var(--text-muted)" }}>
          On the Roadmap
        </p>
        <p className="serif text-2xl font-light leading-relaxed" style={{ color: "var(--text)" }}>
          The system is designed to become more agentic over time.
        </p>
        <div className="space-y-px" style={{ background: "var(--border)" }}>
          {[
            {
              title: "Auto-resolution agent",
              status: "Planned",
              body: "An AI agent monitors each open market against real-world data (Google Trends spikes, mainstream press coverage, major retailer adoption) and automatically resolves YES or NO when evidence is clear.",
            },
            {
              title: "Trend alert subscriptions",
              status: "Planned",
              body: "Subscribe to any trend. Get notified when its score changes significantly, when a matching market opens, or when the community consensus shifts. Email and push.",
            },
            {
              title: "Portfolio intelligence",
              status: "Planned",
              body: "Your positions mapped against the AI confidence scores. See where you're contrarian (betting NO on a high-conviction AI pick), and where you're aligned. Track your P&L over 90-day resolution cycles.",
            },
            {
              title: "Weekly signal digest",
              status: "Planned",
              body: "Every Sunday, an AI agent runs the full scraper pipeline, compiles the week's biggest signal movers, and emails a digest: which trends accelerated, which faded, which markets resolved.",
            },
            {
              title: "Brand dashboard",
              status: "Concept",
              body: "For retailers and brands: aggregate market sentiment on 50+ trends in a single view. Export conviction scores. See where the crowd diverges from editorial coverage. API access for integration into your own systems.",
            },
          ].map((item) => (
            <div key={item.title} className="px-6 py-5 flex gap-5" style={{ background: "var(--bg-card)" }}>
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-1">
                  <p className="text-sm font-medium">{item.title}</p>
                  <span
                    style={{
                      fontSize: "9px",
                      letterSpacing: "0.12em",
                      textTransform: "uppercase",
                      padding: "1px 7px",
                      border: "1px solid var(--border)",
                      color: "var(--text-faint)",
                      borderRadius: "2px",
                    }}
                  >
                    {item.status}
                  </span>
                </div>
                <p className="text-sm leading-relaxed" style={{ color: "var(--text-muted)" }}>{item.body}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      <hr className="rule" />

      {/* Scoring note */}
      <section className="space-y-4 pb-8">
        <p className="text-[10px] tracking-[0.3em] uppercase" style={{ color: "var(--text-muted)" }}>On the Scoring</p>
        <p className="serif text-xl font-light leading-relaxed" style={{ color: "var(--text)" }}>
          AI scores are a starting point, not a verdict.
        </p>
        <p className="text-sm leading-relaxed" style={{ color: "var(--text-muted)" }}>
          A score of 9.4 means our model sees strong, fast-moving, novel signals — it doesn't
          mean the trend will definitely go mainstream. That's what the market is for. The crowd
          may agree, disagree, or have information the model doesn't.
        </p>
        <p className="text-sm leading-relaxed" style={{ color: "var(--text-muted)" }}>
          The most interesting markets are the ones where the AI score and the market price
          diverge. That gap is where the real signal lives.
        </p>
      </section>

    </div>
  );
}
