"use client";

import { useEffect, useRef, useState } from "react";

interface Props {
  startedAt: string;
  finishedAt: string | null;
  status: string;
}

export default function ScanTimer({ startedAt, finishedAt, status }: Props) {
  const isDone = status === "done" || status === "failed";

  const actualDuration =
    isDone && finishedAt
      ? (new Date(finishedAt).getTime() - new Date(startedAt).getTime()) / 1000
      : null;

  const mountTimeRef = useRef(Date.now());
  const [liveElapsed, setLiveElapsed] = useState(0);

  useEffect(() => {
    if (isDone) return;
    const id = setInterval(() => {
      setLiveElapsed((Date.now() - mountTimeRef.current) / 1000);
    }, 100);
    return () => clearInterval(id);
  }, [isDone]);

  const elapsed = actualDuration !== null ? actualDuration : liveElapsed;
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
