"use client";

interface StockHeaderProps {
  stockName: string;
  stockNameSub: string;
  stockCode: string;
  market: string;
  currentPrice: number;
  priceChangePct: number;
  analyzedAt: string;
}

export default function StockHeader({
  stockName,
  stockNameSub,
  stockCode,
  market,
  currentPrice,
  priceChangePct,
  analyzedAt,
}: StockHeaderProps) {
  const isPositive = priceChangePct >= 0;
  const priceColor = isPositive ? "text-green" : "text-red";
  const arrow = isPositive ? "+" : "";

  const formatPrice = (price: number): string => {
    if (market === "US") {
      return `$${price.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
    }
    return `${price.toLocaleString("ko-KR")}원`;
  };

  const formatDate = (dateStr: string): string => {
    try {
      const date = new Date(dateStr);
      return date.toLocaleString("ko-KR", {
        year: "numeric",
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      });
    } catch {
      return dateStr;
    }
  };

  return (
    <div className="glass flex flex-wrap items-center justify-between gap-4 rounded-2xl p-5">
      <div className="flex items-center gap-4">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold text-foreground">{stockName}</h1>
            <span className="rounded-lg bg-cyan/10 px-2.5 py-0.5 text-xs font-semibold text-cyan">
              {market}
            </span>
          </div>
          <p className="mt-0.5 text-sm text-foreground/40">
            {stockCode}
            {stockNameSub && <span className="ml-2 text-foreground/25">{stockNameSub}</span>}
          </p>
        </div>
      </div>

      <div className="text-right">
        <div className="text-2xl font-bold tabular-nums text-foreground">
          {formatPrice(currentPrice)}
        </div>
        <div className={`mt-0.5 text-sm font-semibold tabular-nums ${priceColor}`}>
          {arrow}
          {priceChangePct.toFixed(2)}%
        </div>
      </div>

      <div className="w-full border-t border-foreground/5 pt-2">
        <p className="text-xs text-foreground/25">
          분석 시점: {formatDate(analyzedAt)}
        </p>
      </div>
    </div>
  );
}
