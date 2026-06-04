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
          A prediction game for fashion trends. The AI surfaces the signal. You call what
          goes mainstream before it does, and prove your eye against everyone else.
        </p>
      </div>

      <hr className="rule" />

      {/* The idea */}
      <section className="space-y-5">
        <p className="text-[10px] tracking-[0.3em] uppercase" style={{ color: "var(--text-muted)" }}>The Idea</p>
        <p className="serif text-2xl font-light leading-relaxed" style={{ color: "var(--text)" }}>
          Every season, a handful of underground trends go mainstream. A handful don't.
          The whole fashion industry spends fortunes trying to tell which is which.
        </p>
        <p className="text-base leading-relaxed" style={{ color: "var(--text-muted)" }}>
          This is a game built on that question. Each emerging trend becomes a market, and
          you bet on whether it breaks. The twist that makes it work: you predict what
          <em> will</em> happen, not what you <em> want</em> to happen. Like calling a World
          Cup winner, your favourite isn't always the smart bet. Read the data, make the call,
          and let your track record do the talking.
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
            body: "The system continuously monitors social platforms, search behaviour, resale marketplaces, and editorial coverage, looking for patterns that suggest a trend is building before it hits the mainstream.",
          },
          {
            n: "02",
            title: "Every signal becomes a scored trend",
            body: "Each signal is scored 1 to 10 on velocity, novelty, and cross-platform confirmation. The score is a deterministic formula, not a number an AI invents. Claude writes the thesis explaining why it matters.",
          },
          {
            n: "03",
            title: "Trends become prediction markets",
            body: "Each trend is paired with a specific, verifiable, time-bound question. Not 'will this be popular?' but something with a clear answer, like 'Will barrel jeans be the trouser of 2026?'",
          },
          {
            n: "04",
            title: "You read the data, then call it",
            body: "Every market opens with a form guide: the score, the momentum, how many platforms confirm it. You start with 1,000 points and buy YES or NO. Prices move in real time using a logarithmic market scoring rule, the same mechanism serious prediction platforms use. Play money only.",
          },
          {
            n: "05",
            title: "Markets resolve. Good calls win.",
            body: "When a market closes, it resolves on real-world evidence. Correct calls pay out, and your accuracy rate builds over time: a public track record of how well you actually read fashion, not how loudly you have opinions.",
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

      {/* Predict, don't wish */}
      <section className="space-y-5">
        <p className="text-[10px] tracking-[0.3em] uppercase" style={{ color: "var(--text-muted)" }}>The One Rule</p>
        <p className="serif text-2xl font-light leading-relaxed" style={{ color: "var(--text)" }}>
          Bet on what will happen, not what you want to happen.
        </p>
        <p className="text-base leading-relaxed" style={{ color: "var(--text-muted)" }}>
          You can love a trend and still know in your gut it won't break. That's the skill the
          game rewards. Every market hands you the evidence up front, so the smart move is to
          read the signal, weigh it, and call it honestly. The leaderboard ranks the people who
          are right, not the people who are loudest.
        </p>
      </section>

      <hr className="rule" />

      {/* Intelligence */}
      <section className="space-y-6">
        <p className="text-[10px] tracking-[0.3em] uppercase" style={{ color: "var(--text-muted)" }}>The Signal Engine</p>
        <p className="text-base leading-relaxed" style={{ color: "var(--text-muted)" }}>
          Fashion Futures watches signals across social platforms, resale marketplaces, search
          behaviour, and editorial coverage. It tracks what people search, save, buy, and sell,
          not just what publications choose to write about.
        </p>
        <p className="text-base leading-relaxed" style={{ color: "var(--text-muted)" }}>
          When the same trend surfaces on several platforms at once, its score is boosted and it
          gets tagged as cross-confirmed. A trend seen on TikTok, Reddit, and Vogue at the same
          time is a far stronger signal than one seen once.
        </p>

        <div className="grid grid-cols-2 sm:grid-cols-3 gap-px mt-4" style={{ background: "var(--border)" }}>
          {[
            { label: "TikTok Hashtags",  icon: "♪", desc: "View count growth" },
            { label: "Pinterest Trends", icon: "⌖", desc: "Search volume shifts" },
            { label: "Reddit Signals",   icon: "◉", desc: "Community discussion" },
            { label: "Editorial RSS",    icon: "✦", desc: "Vogue, Harper's, WWD, ELLE" },
            { label: "Google Trends",    icon: "⊕", desc: "Search velocity" },
            { label: "Claude AI",        icon: "◈", desc: "Thesis layer only" },
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
              body: "Put your trend instincts on the line. Build a track record. See how your reads stack up against everyone else's.",
            },
            {
              label: "Industry professionals",
              body: "Use the market price as an independent read. When the crowd prices a trend strongly, that's conviction cutting through editorial noise.",
            },
            {
              label: "Brands & retailers",
              body: "Aggregated market data shows which trends have real conviction behind them, and which the crowd is quietly skeptical about despite the coverage.",
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

      {/* Under the hood - what's running */}
      <section className="space-y-6">
        <p className="text-[10px] tracking-[0.3em] uppercase" style={{ color: "var(--text-muted)" }}>
          Under the Hood
        </p>
        <p className="serif text-2xl font-light leading-relaxed" style={{ color: "var(--text)" }}>
          The platform runs on a set of autonomous agents.
        </p>
        <div className="space-y-px" style={{ background: "var(--border)" }}>
          {[
            {
              title: "Weekly signal pipeline",
              status: "Live",
              body: "Every Sunday an agent runs the full scraper pipeline, re-scores trends, and updates the markets. New signals surface automatically, no manual work.",
            },
            {
              title: "Cross-platform confirmation",
              status: "Live",
              body: "When a trend appears on multiple sources, an agent merges them and boosts the score. Markets show how many platforms have confirmed a trend.",
            },
            {
              title: "Auto-resolution agent",
              status: "Live",
              body: "An agent checks each closing market against real-world evidence (search spikes, editorial mentions, score trajectory) and resolves YES or NO when the evidence is clear.",
            },
            {
              title: "Trend alerts",
              status: "Live",
              body: "Subscribe to a trend or a score threshold and get notified when it crosses the line, so you can place a call before the crowd catches on.",
            },
            {
              title: "Brand dashboard",
              status: "In progress",
              body: "Aggregate market sentiment across every trend in one view, with conviction scores and API access. For retailers and brands.",
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
                      border: `1px solid ${item.status === "Live" ? "var(--green)" : "var(--border)"}`,
                      color: item.status === "Live" ? "var(--green)" : "var(--text-faint)",
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
          The AI score is a starting point, not a verdict.
        </p>
        <p className="text-sm leading-relaxed" style={{ color: "var(--text-muted)" }}>
          A score of 9.4 means the model sees strong, fast, novel, well-confirmed signals. It
          does not mean the trend will definitely break. That is exactly what the market is for.
          The crowd may agree, disagree, or know something the model doesn't.
        </p>
        <p className="text-sm leading-relaxed" style={{ color: "var(--text-muted)" }}>
          The most interesting markets are the ones where the score and the price disagree.
          That gap is where the real signal lives, and where a sharp call pays off.
        </p>
      </section>

    </div>
  );
}
