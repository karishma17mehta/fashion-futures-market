export default function PriceBar({ yes, no }: { yes: number; no: number }) {
  const yesPct = Math.round(yes * 100);
  const noPct = Math.round(no * 100);
  return (
    <div className="w-full">
      <div className="flex overflow-hidden h-[3px] rounded-full" style={{ background: "rgba(255,255,255,0.06)" }}>
        <div
          className="transition-all duration-500"
          style={{ width: `${yesPct}%`, background: "var(--green)" }}
        />
        <div
          className="transition-all duration-500"
          style={{ width: `${noPct}%`, background: "var(--red)" }}
        />
      </div>
      <div className="flex justify-between mt-1.5">
        <span className="text-[10px] tracking-widest uppercase" style={{ color: "var(--green)" }}>
          {yesPct}% Yes
        </span>
        <span className="text-[10px] tracking-widest uppercase" style={{ color: "var(--red)" }}>
          {noPct}% No
        </span>
      </div>
    </div>
  );
}
