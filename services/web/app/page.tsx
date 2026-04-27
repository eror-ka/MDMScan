import Link from "next/link";
import { deleteScan } from "./actions";
import ScanForm from "./components/ScanForm";
import StatusBadge from "./components/StatusBadge";
import { listScans } from "./lib/api";

export const dynamic = "force-dynamic";

function scoreColor(score: number): string {
  if (score >= 80) return "text-green-400";
  if (score >= 60) return "text-yellow-400";
  if (score >= 40) return "text-orange-400";
  return "text-red-400";
}

function scanDuration(createdAt: string, finishedAt: string | null): number | null {
  if (!finishedAt) return null;
  return Math.round(
    (new Date(finishedAt).getTime() - new Date(createdAt).getTime()) / 1000,
  );
}

export default async function HomePage() {
  const scans = await listScans();

  return (
    <div className="space-y-10">
      <section>
        <h2 className="text-base font-semibold text-gray-300 mb-3">
          Проверить образ
        </h2>
        <ScanForm />
      </section>

      <section>
        <h2 className="text-base font-semibold text-gray-300 mb-3">
          История сканирований
        </h2>
        {scans.length === 0 ? (
          <p className="text-gray-500 text-sm">Сканирований пока нет.</p>
        ) : (
          <div className="overflow-hidden rounded-lg border border-gray-800">
            <table className="w-full text-sm">
              <thead className="bg-gray-900 text-gray-400 text-xs uppercase tracking-wide">
                <tr>
                  <th className="px-4 py-3 text-left">Образ</th>
                  <th className="px-4 py-3 text-left">Статус</th>
                  <th className="px-4 py-3 text-right">Безопасность (0–100)</th>
                  <th className="px-4 py-3 text-left">Проверен</th>
                  <th className="px-4 py-3 text-left">Удалить скан</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-800">
                {scans.map((scan) => {
                  const duration = scanDuration(scan.created_at, scan.finished_at);
                  return (
                    <tr
                      key={scan.scan_id}
                      className="hover:bg-gray-900/50 transition-colors"
                    >
                      <td className="px-4 py-3">
                        <Link
                          href={`/scans/${scan.scan_id}`}
                          className="text-indigo-400 hover:text-indigo-300 font-mono"
                        >
                          {scan.image_ref}
                        </Link>
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-2">
                          <StatusBadge status={scan.status} />
                          {duration !== null && (
                            <span className="text-gray-500 text-xs">
                              ({duration}с)
                            </span>
                          )}
                        </div>
                      </td>
                      <td className="px-4 py-3 text-right font-mono font-bold text-lg">
                        {scan.security_score !== null ? (
                          <span className={scoreColor(scan.security_score)}>
                            {scan.security_score}
                          </span>
                        ) : (
                          <span className="text-gray-600 text-sm font-normal">
                            —
                          </span>
                        )}
                      </td>
                      <td className="px-4 py-3 text-gray-500 text-xs whitespace-nowrap">
                        {new Date(scan.created_at).toLocaleString("ru-RU", {
                          timeZone: "Europe/Moscow",
                        })}
                        {scan.finished_at &&
                          ` — ${new Date(scan.finished_at).toLocaleTimeString("ru-RU", { timeZone: "Europe/Moscow" })}`}
                      </td>
                      <td className="px-4 py-3">
                        <form action={deleteScan}>
                          <input
                            type="hidden"
                            name="scan_id"
                            value={scan.scan_id}
                          />
                          <button
                            type="submit"
                            className="px-3 py-1 text-xs bg-red-900/40 text-red-400 hover:bg-red-900/70 rounded transition-colors"
                          >
                            Очистить
                          </button>
                        </form>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
}
