"use client";

import { useState, useCallback } from "react";
import { analyzeStock, type StockAnalysis, type StockSuggestion } from "@/lib/api";
import SearchAutocomplete from "./SearchAutocomplete";

interface SearchBarProps {
  onResult: (data: StockAnalysis) => void;
  onLoading: (loading: boolean) => void;
  onError: (error: string) => void;
  compact?: boolean;
}

export default function SearchBar({
  onResult,
  onLoading,
  onError,
  compact = false,
}: SearchBarProps) {
  const [query, setQuery] = useState("");
  const [market, setMarket] = useState<"KR" | "US">("KR");
  const [isSearching, setIsSearching] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  const triggerAnalysis = useCallback(
    async (queryOverride?: string, marketOverride?: "KR" | "US") => {
      const q = (queryOverride ?? query).trim();
      const m = marketOverride ?? market;

      if (!q || isSearching) return;

      setIsSearching(true);
      setErrorMessage("");
      onLoading(true);

      try {
        const result = await analyzeStock(q, m);
        onResult(result);
      } catch (err) {
        const message =
          err instanceof Error ? err.message : "알 수 없는 오류가 발생했습니다.";
        setErrorMessage(message);
        onError(message);
      } finally {
        setIsSearching(false);
        onLoading(false);
      }
    },
    [query, market, isSearching, onResult, onLoading, onError]
  );

  // Called when the user clicks a suggestion from the dropdown
  const handleSelect = useCallback(
    (suggestion: StockSuggestion) => {
      // Override market based on what the backend returned, falling back to
      // the user's current toggle selection if the market is unrecognised.
      const inferredMarket: "KR" | "US" =
        suggestion.market === "NYSE" || suggestion.market === "NASDAQ"
          ? "US"
          : "KR";
      setQuery(suggestion.name);
      setMarket(inferredMarket);
      triggerAnalysis(suggestion.name, inferredMarket);
    },
    [triggerAnalysis]
  );

  return (
    <div className={`w-full ${compact ? "max-w-2xl" : "max-w-3xl"} mx-auto`}>
      <div
        className={`relative flex items-center gap-3 rounded-2xl border border-cyan/20 bg-surface/80 backdrop-blur-xl ${
          compact ? "p-2 pl-4" : "p-3 pl-6"
        } transition-all duration-300 focus-within:border-cyan/50 focus-within:shadow-[0_0_30px_rgba(0,212,255,0.15)] hover:border-cyan/30`}
      >
        {/* Search icon */}
        <svg
          className="h-5 w-5 shrink-0 text-cyan/60"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
          />
        </svg>

        {/* Autocomplete input with dropdown */}
        <SearchAutocomplete
          value={query}
          onChange={setQuery}
          onSelect={handleSelect}
          onSubmit={() => triggerAnalysis()}
          disabled={isSearching}
          compact={compact}
        />

        {/* Market toggle */}
        <div className="flex shrink-0 items-center gap-1 rounded-xl bg-surface-light p-1">
          <button
            onClick={() => setMarket("KR")}
            className={`rounded-lg px-3 py-1.5 text-xs font-semibold transition-all ${
              market === "KR"
                ? "bg-cyan/20 text-cyan shadow-sm"
                : "text-foreground/40 hover:text-foreground/60"
            }`}
          >
            KR
          </button>
          <button
            onClick={() => setMarket("US")}
            className={`rounded-lg px-3 py-1.5 text-xs font-semibold transition-all ${
              market === "US"
                ? "bg-cyan/20 text-cyan shadow-sm"
                : "text-foreground/40 hover:text-foreground/60"
            }`}
          >
            US
          </button>
        </div>

        {/* Search button */}
        <button
          onClick={() => triggerAnalysis()}
          disabled={isSearching || !query.trim()}
          className={`shrink-0 rounded-xl bg-cyan/90 ${
            compact ? "px-4 py-2" : "px-6 py-2.5"
          } font-semibold text-background transition-all hover:bg-cyan disabled:cursor-not-allowed disabled:opacity-40`}
        >
          {isSearching ? (
            <span className="flex items-center gap-2">
              <svg
                className="h-4 w-4 animate-spin"
                viewBox="0 0 24 24"
                fill="none"
              >
                <circle
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="3"
                  className="opacity-25"
                />
                <path
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
                  className="opacity-75"
                />
              </svg>
              분석중
            </span>
          ) : (
            "분석"
          )}
        </button>
      </div>

      {/* Keyboard hint */}
      {!compact && (
        <p className="mt-3 text-center text-xs text-foreground/25">
          <kbd className="rounded border border-foreground/10 px-1.5 py-0.5 text-[10px]">
            Enter
          </kbd>{" "}
          를 눌러 검색
        </p>
      )}

      {/* Error toast */}
      {errorMessage && (
        <div className="mt-3 animate-fade-in rounded-xl border border-red/20 bg-red/10 px-4 py-3 text-sm text-red">
          <span className="mr-2">⚠</span>
          {errorMessage}
        </div>
      )}
    </div>
  );
}
