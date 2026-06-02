import { fetchLeaderboard } from "@/lib/api";

const RANK_COLOR: Record<string, string> = {
  legend: "#c9a96e",
  oracle: "#a78bfa",
  forecaster: "#8fa8c8",
  novice: "rgba(242,237,232,0.3)",
};

export default async function LeaderboardPage() {
  const data = await fetchLeaderboard();
  const users: any[] = data.users || [];

  return (
    <div className="space-y-12 pt-4">

      <div>
        <p className="text-[10px] tracking-[0.3em] uppercase mb-3" style={{ color: "var(--accent)" }}>
          Rankings
        </p>
        <h1 className="serif text-5xl font-light mb-3">Leaderboard</h1>
        <p className="text-sm" style={{ color: "var(--text-muted)" }}>
          Top forecasters ranked by prediction accuracy
        </p>
      </div>

      <hr className="rule" />

      {users.length === 0 ? (
        <div className="py-20 text-center" style={{ border: "1px solid var(--border)" }}>
          <p className="serif text-2xl font-light mb-2" style={{ color: "var(--text-faint)" }}>
            No traders yet.
          </p>
          <p className="text-sm" style={{ color: "var(--text-faint)" }}>
            Be the first to call a trend.
          </p>
        </div>
      ) : (
        <div>
          <div
            className="grid px-6 py-3 text-[10px] tracking-widest uppercase"
            style={{
              gridTemplateColumns: "2rem 1fr 6rem 6rem 6rem 5rem",
              color: "var(--text-faint)",
              borderBottom: "1px solid var(--border)",
            }}
          >
            <span>#</span>
            <span>Forecaster</span>
            <span className="text-right">Rank</span>
            <span className="text-right">Points</span>
            <span className="text-right">Accuracy</span>
            <span className="text-right">Trades</span>
          </div>

          <div className="space-y-px" style={{ background: "var(--border)" }}>
            {users.map((u: any, i: number) => (
              <div
                key={u.id}
                className="hover-tile grid items-center px-6 py-4"
                style={{ gridTemplateColumns: "2rem 1fr 6rem 6rem 6rem 5rem" }}
              >
                <span className="serif text-lg font-light" style={{ color: "var(--text-faint)" }}>
                  {i + 1}
                </span>
                <span className="serif text-lg font-light">{u.username}</span>
                <span
                  className="text-right text-[10px] tracking-widest uppercase"
                  style={{ color: RANK_COLOR[u.rank] || "var(--text-faint)" }}
                >
                  {u.rank}
                </span>
                <span className="text-right text-sm" style={{ color: "var(--accent)" }}>
                  {u.points.toLocaleString()}
                </span>
                <span className="text-right text-sm">
                  {(u.accuracy_rate * 100).toFixed(0)}%
                </span>
                <span className="text-right text-sm" style={{ color: "var(--text-faint)" }}>
                  {u.total_trades}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

    </div>
  );
}
