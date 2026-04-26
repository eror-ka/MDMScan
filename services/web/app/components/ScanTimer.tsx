"use client";

import { useEffect, useState } from "react";

interface Props {
  startedAt: string;
  finishedAt: string | null;
  status: string;
}

export default function ScanTimer({ startedAt, finishedAt, status }: Props) {
  const startMs = new Date(startedAt).getTime();
  const endMs = finishedAt ? new Date(finishedAt).getTime() : null;

  const [elapsed, setElapsed] = useState(() =>
    endMs ? (endMs - startMs) / 1000 : (Date.now() - startMs) / 1000,
  );

  useEffect(() => {
    if (endMs) {
      setElapsed((endMs - startMs) / 1000);
      return;
    }
    const id = setInterval(
      () => setElapsed((Date.now() - startMs) / 1000),
      100,
    );
    return () => clearInterval(id);
  }, [startMs, endMs]);

  const running = status === "running" || status === "pending";

  return (
    <div className="flex items-center gap-2">
      <span className="text-gray-500 text-sm">⏱</span>
      <span className="font-mono text-lg tabular-nums text-gray-100">
        {elapsed.toFixed(1)}с
      </span>
      {running && (
        <span className="text-blue-400 text-xs animate-pulse">● идёт</span>
      )}
    </div>
  );
}
