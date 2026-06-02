export default function ScoreBadge({ score }: { score: number }) {
  const color =
    score >= 9 ? "#e05252" :
    score >= 8 ? "#c9a96e" :
    score >= 7 ? "#8fa8c8" :
    "rgba(242,237,232,0.3)";

  return (
    <span
      className="inline-flex items-center gap-1.5 text-[11px] tracking-widest uppercase font-medium"
      style={{ color }}
    >
      <span className="w-1.5 h-1.5 rounded-full shrink-0" style={{ background: color }} />
      {score.toFixed(1)}
    </span>
  );
}
