export default function ScoreBadge({ score }: { score: number }) {
  const color =
    score >= 8 ? "bg-rose-500/20 text-rose-300 border-rose-500/30" :
    score >= 6 ? "bg-amber-500/20 text-amber-300 border-amber-500/30" :
                 "bg-white/10 text-white/50 border-white/10";
  return (
    <span className={`text-xs font-mono px-2 py-0.5 rounded border ${color}`}>
      {score.toFixed(1)}
    </span>
  );
}
