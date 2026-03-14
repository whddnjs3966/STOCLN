"use client";

import {
  useEffect,
  useRef,
  useState,
  useCallback,
  type KeyboardEvent,
} from "react";
import { searchStocks, type StockSuggestion } from "@/lib/api";

interface SearchAutocompleteProps {
  value: string;
  onChange: (value: string) => void;
  onSelect: (suggestion: StockSuggestion) => void;
  onSubmit: () => void;
  disabled?: boolean;
  compact?: boolean;
  placeholder?: string;
}

export default function SearchAutocomplete({
  value,
  onChange,
  onSelect,
  onSubmit,
  disabled = false,
  compact = false,
  placeholder = "종목명 또는 종목코드 입력 (예: 삼성전자, AAPL)",
}: SearchAutocompleteProps) {
  const [suggestions, setSuggestions] = useState<StockSuggestion[]>([]);
  const [isLoadingSuggestions, setIsLoadingSuggestions] = useState(false);
  const [suggestionError, setSuggestionError] = useState("");
  const [isOpen, setIsOpen] = useState(false);
  const [activeIndex, setActiveIndex] = useState(-1);

  const containerRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const debounceTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  // Tracks the query that the currently displayed suggestions belong to,
  // so stale responses from an earlier request don't overwrite fresh ones.
  const latestQueryRef = useRef("");

  // Close dropdown when user clicks outside the component
  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (
        containerRef.current &&
        !containerRef.current.contains(e.target as Node)
      ) {
        setIsOpen(false);
        setActiveIndex(-1);
      }
    }

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  // Debounced suggestion fetch
  const fetchSuggestions = useCallback((q: string) => {
    if (debounceTimerRef.current) {
      clearTimeout(debounceTimerRef.current);
    }

    if (!q.trim()) {
      setSuggestions([]);
      setSuggestionError("");
      setIsOpen(false);
      setIsLoadingSuggestions(false);
      return;
    }

    // Show loading spinner immediately so the user gets instant feedback
    setIsLoadingSuggestions(true);
    setSuggestionError("");

    debounceTimerRef.current = setTimeout(async () => {
      latestQueryRef.current = q;
      try {
        const results = await searchStocks(q);
        // Discard the result if a newer query has already been issued
        if (latestQueryRef.current !== q) return;
        setSuggestions(results);
        setIsOpen(true);
        setActiveIndex(-1);
      } catch {
        if (latestQueryRef.current !== q) return;
        setSuggestions([]);
        setSuggestionError("검색 중 오류가 발생했습니다.");
        setIsOpen(true);
      } finally {
        if (latestQueryRef.current === q) {
          setIsLoadingSuggestions(false);
        }
      }
    }, 300);
  }, []);

  // Cleanup the timer on unmount
  useEffect(() => {
    return () => {
      if (debounceTimerRef.current) clearTimeout(debounceTimerRef.current);
    };
  }, []);

  function handleInputChange(e: React.ChangeEvent<HTMLInputElement>) {
    const q = e.target.value;
    onChange(q);
    fetchSuggestions(q);
  }

  function handleSelectSuggestion(suggestion: StockSuggestion) {
    onChange(suggestion.name);
    setSuggestions([]);
    setIsOpen(false);
    setActiveIndex(-1);
    onSelect(suggestion);
  }

  function handleKeyDown(e: KeyboardEvent<HTMLInputElement>) {
    if (!isOpen) {
      if (e.key === "Enter") onSubmit();
      return;
    }

    switch (e.key) {
      case "ArrowDown":
        e.preventDefault();
        setActiveIndex((prev) =>
          prev < suggestions.length - 1 ? prev + 1 : 0
        );
        break;

      case "ArrowUp":
        e.preventDefault();
        setActiveIndex((prev) =>
          prev > 0 ? prev - 1 : suggestions.length - 1
        );
        break;

      case "Enter":
        e.preventDefault();
        if (activeIndex >= 0 && suggestions[activeIndex]) {
          handleSelectSuggestion(suggestions[activeIndex]);
        } else {
          setIsOpen(false);
          onSubmit();
        }
        break;

      case "Escape":
        setIsOpen(false);
        setActiveIndex(-1);
        inputRef.current?.blur();
        break;

      default:
        break;
    }
  }

  const showDropdown = isOpen && value.trim().length > 0;

  return (
    <div ref={containerRef} className="relative flex-1">
      <input
        ref={inputRef}
        type="text"
        value={value}
        onChange={handleInputChange}
        onKeyDown={handleKeyDown}
        onFocus={() => {
          if (suggestions.length > 0 || suggestionError) setIsOpen(true);
        }}
        placeholder={placeholder}
        className={`w-full bg-transparent ${
          compact ? "text-base" : "text-lg"
        } text-foreground placeholder-foreground/30 outline-none`}
        disabled={disabled}
        autoComplete="off"
        spellCheck={false}
      />

      {/* Dropdown */}
      {showDropdown && (
        <div
          className="absolute left-0 top-[calc(100%+12px)] z-[100] w-full min-w-[320px] overflow-hidden rounded-2xl border border-cyan/20 bg-surface/95 shadow-[0_8px_40px_rgba(0,212,255,0.12)] backdrop-blur-xl"
          role="listbox"
        >
          {/* Loading state */}
          {isLoadingSuggestions && (
            <div className="flex items-center gap-3 px-4 py-3 text-sm text-foreground/40">
              <svg
                className="h-4 w-4 animate-spin shrink-0 text-cyan/60"
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
              검색 중...
            </div>
          )}

          {/* Error state */}
          {!isLoadingSuggestions && suggestionError && (
            <div className="flex items-center gap-2 px-4 py-3 text-sm text-red/70">
              <svg
                className="h-4 w-4 shrink-0"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 9v2m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"
                />
              </svg>
              {suggestionError}
            </div>
          )}

          {/* No results state */}
          {!isLoadingSuggestions &&
            !suggestionError &&
            suggestions.length === 0 && (
              <div className="px-4 py-3 text-sm text-foreground/40">
                일치하는 종목이 없습니다.
              </div>
            )}

          {/* Results list */}
          {!isLoadingSuggestions && suggestions.length > 0 && (
            <ul className="max-h-64 overflow-y-auto py-1">
              {suggestions.map((s, i) => (
                <li
                  key={`${s.code}-${i}`}
                  role="option"
                  aria-selected={i === activeIndex}
                  onMouseDown={(e) => {
                    // Prevent the input blur that would close the dropdown
                    // before the click is registered
                    e.preventDefault();
                    handleSelectSuggestion(s);
                  }}
                  onMouseEnter={() => setActiveIndex(i)}
                  className={`flex cursor-pointer items-center justify-between px-4 py-2.5 transition-colors ${
                    i === activeIndex
                      ? "bg-cyan/10 text-foreground"
                      : "text-foreground/80 hover:bg-surface-light"
                  }`}
                >
                  <span className="flex items-center gap-2.5 min-w-0">
                    {/* Active indicator */}
                    <span
                      className={`h-1.5 w-1.5 shrink-0 rounded-full transition-colors ${
                        i === activeIndex ? "bg-cyan" : "bg-transparent"
                      }`}
                    />
                    <span className="truncate font-medium">{s.name}</span>
                  </span>

                  <span className="ml-3 flex shrink-0 items-center gap-2 text-xs">
                    <span className="font-mono text-foreground/50">{s.code}</span>
                    <span
                      className={`rounded-md px-1.5 py-0.5 font-semibold ${
                        s.market === "KOSPI"
                          ? "bg-cyan/10 text-cyan/80"
                          : s.market === "KOSDAQ"
                          ? "bg-green/10 text-green/80"
                          : "bg-yellow/10 text-yellow/80"
                      }`}
                    >
                      {s.market}
                    </span>
                  </span>
                </li>
              ))}
            </ul>
          )}

          {/* Keyboard hint at the bottom */}
          {!isLoadingSuggestions && suggestions.length > 0 && (
            <div className="border-t border-foreground/5 px-4 py-2 flex items-center gap-3 text-[10px] text-foreground/20">
              <span>
                <kbd className="rounded border border-foreground/10 px-1 py-0.5">↑↓</kbd>{" "}
                탐색
              </span>
              <span>
                <kbd className="rounded border border-foreground/10 px-1 py-0.5">Enter</kbd>{" "}
                선택
              </span>
              <span>
                <kbd className="rounded border border-foreground/10 px-1 py-0.5">Esc</kbd>{" "}
                닫기
              </span>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
