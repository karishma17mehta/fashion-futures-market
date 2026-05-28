"use client";
import { useEffect, useState } from "react";
import { fetchMarket, placeTrade } from "@/lib/api";
import PriceBar from "@/components/PriceBar";
import Link from "next/link";
import { use } from "react";

export default function MarketPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const [market, setMarket] = useState<any>(null);
  const [amount, setAmount] = useState(50);
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const userId = "ed19647b-9a4e-4929-9467-d1b6f92a9cd4"; // demo user

  useEffect(() => {
    fetchMarket(id).then(setMarket);
  }, [id]);

  async function trade(position: "yes" | "no") {
    setLoading(true);
    setResult(null);
    const res = await placeTrade(id, userId, position, amount);
    setResult(res);
    const updated = await fetchMarket(id);
    setMarket(updated);
    setLoading(false);
  }

  if (!market) return <div className="text-white/30 text-sm">Loading...</div>;

  return (
    <div className="max-w-xl space-y-8">
      <div>
        <Link href="/" className="text-xs text-white/30 hover:text-white/60 mb-4 block">← Markets</Link>
        <p className="text-xs font-mono text-white/30 uppercase tracking-widest mb-2">
          {market.status === "open" ? "🟢 Open" : "⚫ Closed"} · {market.total_volume} pts traded
        </p>
        <h1 className="text-2xl font-bold leading-snug">{market.question}</h1>
        <p className="text-xs text-white/30 mt-2">
          Resolves {new Date(market.resolution_date).toLocaleDateString()}
        </p>
      </div>

      <div className="border border-white/10 rounded-xl p-5">
        <p className="text-xs font-mono text-white/30 uppercase tracking-widest mb-4">Current Odds</p>
        <PriceBar yes={market.yes_price} no={market.no_price} />
        <div className="grid grid-cols-2 gap-3 mt-4 text-center">
          <div className="border border-emerald-500/20 rounded-lg p-3 bg-emerald-500/5">
            <p className="text-2xl font-bold text-emerald-400">{Math.round(market.yes_price * 100)}¢</p>
            <p className="text-xs text-white/30 mt-1">YES price</p>
          </div>
          <div className="border border-rose-500/20 rounded-lg p-3 bg-rose-500/5">
            <p className="text-2xl font-bold text-rose-400">{Math.round(market.no_price * 100)}¢</p>
            <p className="text-xs text-white/30 mt-1">NO price</p>
          </div>
        </div>
      </div>

      {market.status === "open" && (
        <div className="border border-white/10 rounded-xl p-5 space-y-4">
          <p className="text-xs font-mono text-white/30 uppercase tracking-widest">Place a Trade</p>
          <div>
            <label className="text-xs text-white/40 block mb-2">Amount (points)</label>
            <input
              type="range" min={10} max={500} step={10} value={amount}
              onChange={(e) => setAmount(Number(e.target.value))}
              className="w-full accent-rose-400"
            />
            <p className="text-center text-lg font-bold mt-1">{amount} pts</p>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <button onClick={() => trade("yes")} disabled={loading}
              className="py-3 rounded-xl bg-emerald-500/20 border border-emerald-500/30 text-emerald-300 font-semibold hover:bg-emerald-500/30 transition-all disabled:opacity-40">
              YES
            </button>
            <button onClick={() => trade("no")} disabled={loading}
              className="py-3 rounded-xl bg-rose-500/20 border border-rose-500/30 text-rose-300 font-semibold hover:bg-rose-500/30 transition-all disabled:opacity-40">
              NO
            </button>
          </div>
          {result && !result.detail && (
            <div className="text-xs text-white/50 text-center border border-white/10 rounded-lg p-3">
              Bought <span className="text-white">{result.shares_bought?.toFixed(2)} shares</span> ·
              New YES price: <span className="text-emerald-400">{Math.round((result.new_yes_price || 0) * 100)}¢</span>
            </div>
          )}
          {result?.detail && (
            <p className="text-xs text-rose-400 text-center">{result.detail}</p>
          )}
        </div>
      )}

      <div className="border border-white/10 rounded-xl p-5">
        <p className="text-xs font-mono text-white/30 uppercase tracking-widest mb-3">Resolution Criteria</p>
        <p className="text-sm text-white/50 leading-relaxed">{market.resolution_criteria}</p>
      </div>
    </div>
  );
}
