import Link from "next/link";

export const metadata = {
  title: "Terms & Privacy · Fashion Futures",
};

const LAST_UPDATED = "June 4, 2026";

export default function TermsPage() {
  return (
    <div className="max-w-2xl mx-auto pt-4 pb-20 fade-up">
      <Link href="/" className="text-[10px] tracking-widest uppercase" style={{ color: "var(--text-faint)" }}>
        ← Home
      </Link>

      <h1 className="serif text-4xl font-light mt-5 mb-2">Terms &amp; Privacy</h1>
      <p className="text-[10px] tracking-widest uppercase mb-12" style={{ color: "var(--text-faint)" }}>
        Last updated {LAST_UPDATED}
      </p>

      {/* ── Disclaimer ─────────────────────────────────────────────────── */}
      <section
        className="px-6 py-6 mb-12"
        style={{ background: "var(--bg-card)", borderLeft: "2px solid var(--accent)" }}
      >
        <p className="text-[9px] tracking-[0.3em] uppercase mb-3" style={{ color: "var(--accent)" }}>
          ✦ Important Disclaimer
        </p>
        <p className="text-sm leading-relaxed" style={{ color: "var(--text-muted)" }}>
          Fashion Futures is a <strong style={{ color: "var(--text)" }}>play-money game and research tool</strong>.
          All points, balances, and "trades" are virtual and have <strong style={{ color: "var(--text)" }}>no
          monetary value</strong>. Nothing here can be bought, sold, withdrawn, or exchanged for real money,
          goods, or services. The platform involves no real-money wagering and is not gambling.
          Trend scores and market prices are informational only and are
          <strong style={{ color: "var(--text)" }}> not financial, investment, or trading advice</strong>.
          Predictions may be wrong. Use the platform for entertainment and exploration.
        </p>
      </section>

      {/* ── Terms of Service ───────────────────────────────────────────── */}
      <Section title="Terms of Service">
        <P><B>1. Acceptance.</B> By creating an account or using Fashion Futures (the "Service"),
          you agree to these Terms. If you do not agree, do not use the Service.</P>
        <P><B>2. Eligibility.</B> You must be at least 13 years old (or the minimum digital-consent
          age in your jurisdiction) to use the Service.</P>
        <P><B>3. Play-money only.</B> The Service uses virtual points with no real-world value.
          Points cannot be purchased, redeemed, transferred, or cashed out. We may adjust, reset,
          or remove points and markets at any time.</P>
        <P><B>4. Your account.</B> You are responsible for keeping your password confidential and for
          activity under your account. Provide accurate information and do not impersonate others.</P>
        <P><B>5. Acceptable use.</B> Do not abuse, scrape, overload, reverse-engineer, or attempt to
          gain unauthorized access to the Service, other accounts, or our systems. Do not use the
          Service for any unlawful purpose.</P>
        <P><B>6. Intellectual property.</B> The Service, including its software, design, content, and
          branding, is owned by Fashion Futures and protected by copyright and other laws. You receive
          no ownership rights by using it.</P>
        <P><B>7. No warranty.</B> The Service is provided "as is," without warranties of any kind. We
          do not guarantee accuracy, availability, or that predictions or scores are correct.</P>
        <P><B>8. Limitation of liability.</B> To the fullest extent permitted by law, we are not liable
          for any indirect, incidental, or consequential damages arising from your use of the Service.</P>
        <P><B>9. Changes &amp; termination.</B> We may modify the Service or these Terms at any time,
          and may suspend or terminate accounts that violate these Terms.</P>
      </Section>

      {/* ── Privacy Policy ─────────────────────────────────────────────── */}
      <Section title="Privacy Policy">
        <P><B>What we collect.</B> When you create an account we store your email address, your chosen
          display name, and a securely hashed version of your password (we never store your password in
          plain text). As you use the Service we record your in-game activity — trades, points, positions,
          badges, and the time you were last active.</P>
        <P><B>How we use it.</B> We use this data to operate the game (run your portfolio, leaderboard,
          and alerts) and to understand aggregate usage patterns so we can improve the product. Your email
          is private and is not shown publicly; only your display name appears on the leaderboard.</P>
        <P><B>What we don't do.</B> We do not sell your personal data. We do not share it with third
          parties except as needed to run the Service (e.g. our hosting and database providers) or where
          required by law.</P>
        <P><B>Cookies &amp; local storage.</B> We store a session token in your browser's local storage
          to keep you signed in. We do not use third-party advertising trackers.</P>
        <P><B>Data retention &amp; your choices.</B> We keep your data while your account is active. You may
          request access to, or deletion of, your account and associated data by contacting us.</P>
        <P><B>Contact.</B> Questions about these Terms or your data? Reach us at{" "}
          <span style={{ color: "var(--accent)" }}>hello@fashionfutures.app</span>.</P>
      </Section>

      <p className="text-[10px] mt-12" style={{ color: "var(--text-faint)" }}>
        This is a play-money product for entertainment and research. It is not affiliated with any
        publication, retailer, or brand referenced within it.
      </p>
    </div>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="mb-12">
      <h2 className="serif text-2xl font-light mb-5">{title}</h2>
      <div className="space-y-4">{children}</div>
    </section>
  );
}

function P({ children }: { children: React.ReactNode }) {
  return <p className="text-sm leading-relaxed" style={{ color: "var(--text-muted)" }}>{children}</p>;
}

function B({ children }: { children: React.ReactNode }) {
  return <strong style={{ color: "var(--text)" }}>{children}</strong>;
}
