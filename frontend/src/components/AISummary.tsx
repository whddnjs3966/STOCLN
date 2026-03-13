"use client";

import { useEffect, useState } from "react";

interface AISummaryProps {
  summary: string;
}

export default function AISummary({ summary }: AISummaryProps) {
  const [displayedText, setDisplayedText] = useState("");
  const [isComplete, setIsComplete] = useState(false);

  useEffect(() => {
    setDisplayedText("");
    setIsComplete(false);

    let index = 0;
    const interval = setInterval(() => {
      if (index < summary.length) {
        setDisplayedText(summary.slice(0, index + 1));
        index++;
      } else {
        setIsComplete(true);
        clearInterval(interval);
      }
    }, 15);

    return () => clearInterval(interval);
  }, [summary]);

  return (
    <div className="glass flex h-full flex-col rounded-2xl p-5">
      <div className="mb-3 flex items-center gap-2">
        <div className="h-2 w-2 animate-pulse rounded-full bg-green" />
        <h3 className="text-sm font-semibold text-foreground/50">
          AI Briefing
        </h3>
      </div>
      <div className="flex-1 overflow-y-auto rounded-xl bg-background/50 p-4 font-mono">
        <div className="flex items-start gap-2">
          <span className="shrink-0 text-cyan/60">&gt;</span>
          <p className="whitespace-pre-wrap text-sm leading-relaxed text-foreground/70">
            {displayedText}
            {!isComplete && (
              <span className="ml-0.5 inline-block h-4 w-1.5 animate-pulse bg-cyan/70" />
            )}
          </p>
        </div>
      </div>
    </div>
  );
}
