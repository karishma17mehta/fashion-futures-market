import { fetchLeaderboard } from "@/lib/api";

const RANK_COLOR: Record<string, string> = {
  legend: "text-yellow-400",
  oracle: "text-violet-400",
  forecaster: "text-blue-400",
  novice: "text-white/40",
};

export default async function LeaderboardPage() {
  const data = await fetchLeaderboard();
  const users: any[] = data.users || [];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Leaderboard</h1>
        <p className="text-white/40 text-sm mt-1">Top trend forecasters ranked by accuracy</p>
      </div>

      {users.length === 0 ? (
        <div className="border border-white/10 rounded-xl p-12 text-center">
          <p className="text-white/30">No traders yet. Be the first to call a trend.</p>
        </div>
      ) : (
        <div className="border border-white/10 rounded-xl overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-white/10 text-white/30 text-xs font-mono uppercase">
                <th className="text-left p-4">#</th>
                <th className="text-left p-4">Trader</th>
                <th className="text-left p-4">Rank</th>
                <th className="text-right p-4">Points</th>
                <th className="text-right p-4">Accuracy</th>
                <th className="text-right p-4">Trades</th>
              </tr>
            </thead>
            <tbody>
              {users.map((u: any, i: number) => (
                <tr key={u.id} className="border-b border-white/5 hover:bg-white/5 transition-colors">
                  <td className="p-4 text-white/30 font-mono">{i + 1}</td>
                  <td className="p-4 font-medium">{u.username}</td>
                  <td className={`p-4 text-xs font-mono uppercase ${RANK_COLOR[u.rank] || "text-white/40"}`}>{u.rank}</td>
                  <td className="p-4 text-right font-mono">{u.points.toLocaleString()}</td>
                  <td className="p-4 text-right font-mono">{(u.accuracy_rate * 100).toFixed(0)}%</td>
                  <td className="p-4 text-right text-white/40">{u.total_trades}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
