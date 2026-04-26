import Link from "next/link";
import { notFound } from "next/navigation";
import AutoRefresh from "../../components/AutoRefresh";
import FindingsTable from "../../components/FindingsTable";
import ScanTimer from "../../components/ScanTimer";
import StatusBadge from "../../components/StatusBadge";
import { getFindings, getScan } from "../../lib/api";

export const dynamic = "force-dynamic";

export default async function ScanPage({
  params,
}: {
  params: { id: string };
}) {
  const [scan, findings] = await Promise.all([
    getScan(params.id),
    getFindings(params.id),
  ]);

  if (!scan) notFound();

  const isRunning = scan.status === "running" || scan.status === "pending";

  return (
    <div className="space-y-6">
      <AutoRefresh status={scan.status} />

      {/* Заголовок */}
      <div>
        <div className="flex items-center gap-3 mb-2 flex-wrap">
          <Link
            href="/"
            className="text-gray-500 hover:text-gray-300 text-sm transition-colors"
          >
            ← Назад
          </Link>
          <StatusBadge status={scan.status} />
          {isRunning && (
            <span className="text-xs text-blue-400 animate-pulse">
              обновление…
            </span>
          )}
        </div>
        <div className="flex items-center justify-between gap-4 flex-wrap">
          <h2 className="font-mono text-xl text-gray-100">{scan.image_ref}</h2>
          <ScanTimer
            startedAt={scan.created_at}
            finishedAt={scan.finished_at}
            status={scan.status}
          />
        </div>
      </div>

      {/* Статусы сканеров */}
      {scan.scanner_statuses && (
        <div className="bg-gray-900 rounded-lg border border-gray-800 p-4">
          <h3 className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-3">
            Статусы сканеров
          </h3>
          <div className="flex flex-wrap gap-2">
            {Object.entries(scan.scanner_statuses).map(([name, st]) => (
              <span
                key={name}
                className={`px-2 py-1 rounded text-xs font-mono ${
                  st === "ok"
                    ? "bg-green-900/40 text-green-400"
                    : "bg-red-900/40 text-red-400"
                }`}
              >
                {name}: {st}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Результаты */}
      <div>
        <h3 className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-3">
          {isRunning
            ? "Сканирование выполняется…"
            : `Результаты — ${findings.total} находок`}
        </h3>
        <FindingsTable findings={findings.items} />
      </div>
    </div>
  );
}
