"use client";

import { useEffect, useState } from "react";

interface TgUser {
  id: number;
  first_name: string;
  last_name?: string;
  username?: string;
}

declare global {
  interface Window {
    Telegram?: {
      WebApp?: {
        initData: string;
        initDataUnsafe: { user?: TgUser };
        colorScheme: "light" | "dark";
        expand(): void;
        ready(): void;
      };
    };
  }
}

export default function TelegramWebApp() {
  const [user, setUser] = useState<TgUser | null>(null);

  useEffect(() => {
    const tg = window.Telegram?.WebApp;
    if (!tg) return;
    tg.ready();
    tg.expand();
    const u = tg.initDataUnsafe?.user;
    if (u) setUser(u);
  }, []);

  if (!user) return null;

  const name = [user.first_name, user.last_name].filter(Boolean).join(" ");
  const handle = user.username ? ` (@${user.username})` : "";

  return (
    <span className="text-xs text-indigo-300 ml-2">
      👤 {name}
      {handle}
    </span>
  );
}
