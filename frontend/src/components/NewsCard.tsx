"use client";

interface NewsItem {
  title: string;
  description: string;
  link: string;
  pub_date: string;
}

interface NewsCardProps {
  news: NewsItem[];
}

function stripHtml(html: string): string {
  return html.replace(/<[^>]*>/g, "").replace(/&[^;]+;/g, " ").trim();
}

function formatDate(dateStr: string): string {
  try {
    const date = new Date(dateStr);
    return date.toLocaleDateString("ko-KR", {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return dateStr;
  }
}

export default function NewsCard({ news }: NewsCardProps) {
  const items = news.slice(0, 5);

  return (
    <div className="glass flex h-full flex-col rounded-2xl p-5">
      <h3 className="mb-4 text-sm font-semibold text-foreground/50">
        News Highlights
      </h3>
      <div className="flex flex-1 flex-col gap-2 overflow-y-auto">
        {items.length === 0 && (
          <p className="text-sm text-foreground/30">뉴스가 없습니다.</p>
        )}
        {items.map((item, i) => (
          <a
            key={i}
            href={item.link}
            target="_blank"
            rel="noopener noreferrer"
            className="group rounded-xl border border-transparent bg-surface-light/50 p-3 transition-all duration-200 hover:border-cyan/20 hover:bg-surface-light"
          >
            <p className="text-sm font-medium leading-snug text-foreground/80 transition-colors group-hover:text-cyan">
              {stripHtml(item.title)}
            </p>
            <div className="mt-1.5 flex items-center justify-between">
              <span className="text-xs text-foreground/30">
                {formatDate(item.pub_date)}
              </span>
              <svg
                className="h-3 w-3 text-foreground/20 transition-colors group-hover:text-cyan/60"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"
                />
              </svg>
            </div>
          </a>
        ))}
      </div>
    </div>
  );
}
