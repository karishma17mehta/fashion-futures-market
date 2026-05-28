export default function PriceBar({ yes, no }: { yes: number; no: number }) {
  const yesPct = Math.round(yes * 100);
  const noPct = Math.round(no * 100);
  return (
    <div className="w-full">
      <div className="flex rounded overflow-hidden h-2 bg-white/10">
        <div className="bg-emerald-500 transition-all" style={{ width: `${yesPct}%` }} />
        <div className="bg-rose-500 transition-all" style={{ width: `${noPct}%` }} />
      </div>
      <div className="flex justify-between mt-1 text-xs text-white/50">
        <span className="text-emerald-400 font-mono">{yesPct}% YES</span>
        <span className="text-rose-400 font-mono">{noPct}% NO</span>
      </div>
    </div>
  );
}
