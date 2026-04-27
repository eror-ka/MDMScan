import Link from "next/link";
import ScanForm from "./components/ScanForm";
import StatusBadge from "./components/StatusBadge";
import { listScans } from "./lib/api";

export const dynamic = "force-dynamic";

function calcScore(findingsCount: number, status: string): number | null {
  if (status !== "done") return null;
  if (findingsCount === 0) return 100;
  return Math.max(0, Math.round(100 - Math.log10(findingsCount + 1) * 25));
}

function scoreColor(score: number): string {
  if (score >= 80) return "text-green-400";
  if (score >= 60) return "text-yellow-400";
  if (score >= 40) return "text-orange-400";
  return "text-red-400";
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
                  <th className="px-4 py-3 text-right">Находки</th>
                  <th className="px-4 py-3 text-right">Безопасность (0–100)</th>
                  <th className="px-4 py-3 text-left">Проверен</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-800">
                {scans.map((scan) => {
                  const score = calcScore(scan.findings_count, scan.status);
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
                        <StatusBadge status={scan.status} />
                      </td>
                      <td className="px-4 py-3 text-right font-mono text-gray-300">
                        {scan.findings_count}
                      </td>
                      <td className="px-4 py-3 text-right font-mono font-bold text-lg">
                        {score !== null ? (
                          <span className={scoreColor(score)}>{score}</span>
                        ) : (
                          <span className="text-gray-600 text-sm font-normal">—</span>
                        )}
                      </td>
                      <td className="px-4 py-3 text-gray-500 text-xs whitespace-nowrap">
                        {new Date(scan.created_at).toLocaleString("ru-RU")}
                        {scan.finished_at &&
                          ` — ${new Date(scan.finished_at).toLocaleTimeString("ru-RU")}`}
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
