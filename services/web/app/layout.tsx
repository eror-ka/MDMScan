import type { Metadata } from "next";
import Script from "next/script";
import "./globals.css";
import TelegramWebApp from "./components/TelegramWebApp";

export const metadata: Metadata = {
  title: "MDMScan",
  description: "Оценка безопасности Docker-образов",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ru">
      <head>
        <Script
          src="https://telegram.org/js/telegram-web-app.js"
          strategy="beforeInteractive"
        />
      </head>
      <body className="bg-gray-950 text-gray-100 min-h-screen">
        <header className="border-b border-gray-800 px-6 py-4">
          <a href="/" className="inline-flex items-baseline gap-2">
            <h1 className="text-xl font-bold text-indigo-400">MDMScan</h1>
            <p className="text-xs text-gray-500">
              Оценка безопасности Docker-образов
            </p>
          </a>
          <TelegramWebApp />
        </header>
        <main className="max-w-7xl mx-auto px-6 py-8">{children}</main>
      </body>
    </html>
  );
}
