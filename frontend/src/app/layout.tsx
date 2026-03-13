import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "StockSight - AI 기반 3D 주식 예측 플랫폼",
  description:
    "AI와 3D 시각화를 활용한 차세대 주식 분석 플랫폼. 뉴스 감성, 펀더멘털, 기술적 분석, 매크로 지표를 종합하여 투자 인사이트를 제공합니다.",
  keywords: ["주식", "AI", "예측", "3D", "StockSight", "투자"],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ko">
      <body className={`${inter.variable} font-sans antialiased`}>
        {children}
      </body>
    </html>
  );
}
