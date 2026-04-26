import type { Metadata } from "next";
import "./globals.css";

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
      <body className="bg-gray-950 text-gray-100 min-h-screen">
        <header className="border-b border-gray-800 px-6 py-4">
          <a href="/" className="inline-block">
            <h1 className="text-xl font-bold text-indigo-400">MDMScan</h1>
            <p className="text-xs text-gray-500">
              Оценка безопасности Docker-образов
            </p>
          </a>
        </header>
        <main className="max-w-5xl mx-auto px-6 py-8">{children}</main>
      </body>
    </html>
  );
}
