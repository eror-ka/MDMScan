"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";

export default function AutoRefresh({ status }: { status: string }) {
  const router = useRouter();

  useEffect(() => {
    if (status !== "running" && status !== "pending") return;
    const id = setInterval(() => router.refresh(), 4000);
    return () => clearInterval(id);
  }, [status, router]);

  return null;
}
