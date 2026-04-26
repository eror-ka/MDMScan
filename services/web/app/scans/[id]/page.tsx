import Link from "next/link";
import { notFound } from "next/navigation";
import AutoRefresh from "../../components/AutoRefresh";
import SeverityBadge from "../../components/SeverityBadge";
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
  const durationMs = scan.finished_at
    ? new Date(scan.finished_at).getTime() -
      new Date(scan.created_at).getTime()
    : null;
  const duration = durationMs !== null ? (durationMs / 1000).toFixed(1) : null;

  return (
    <div className="space-y-6">
      <AutoRefresh status={scan.status} />

      <div className="flex items-center gap-3 flex-wrap">
        <Link
          href="/"
          className="text-gray-500 hover:text-gray-300 text-sm transition-colors"
        >
          ← Back
        </Link>
        <span className="font-mono text-lg text-gray-100">
          {scan.image_ref}
        </span>
        <StatusBadge status={scan.status} />
        {isRunning && (
          <span className="text-xs text-blue-400 animate-pulse">
            Refreshing…
          </span>
        )}
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <InfoCard label="Findings" value={String(scan.findings_count)} />
        <InfoCard label="Duration" value={duration ? `${duration}s` : "—"} />
        <InfoCard
          label="Started"
          value={new Date(scan.created_at).toLocaleTimeString("ru-RU")}
        />
        <InfoCard label="Scan ID" value={scan.scan_id.slice(0, 8) + "…"} />
      </div>

      {scan.scanner_statuses && (
        <div className="bg-gray-900 rounded-lg border border-gray-800 p-4">
          <h3 className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-3">
            Scanner statuses
          </h3>
          <div className="flex flex-wrap gap-2">
            {Object.entries(scan.scanner_statuses).map(([name, status]) => (
              <span
                key={name}
                className={`px-2 py-1 rounded text-xs font-mono ${
                  status === "ok"
                    ? "bg-green-900/40 text-green-400"
                    : "bg-red-900/40 text-red-400"
                }`}
              >
                {name}: {status}
              </span>
            ))}
          </div>
        </div>
      )}

      <div>
        <h3 className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-3">
          Findings ({findings.total})
        </h3>
        {findings.items.length === 0 ? (
          <p className="text-gray-500 text-sm">
            {isRunning ? "Scan in progress…" : "No findings."}
          </p>
        ) : (
          <div className="overflow-hidden rounded-lg border border-gray-800">
            <table className="w-full text-sm">
              <thead className="bg-gray-900 text-gray-400 text-xs uppercase tracking-wide">
                <tr>
                  <th className="px-4 py-3 text-left">Severity</th>
                  <th className="px-4 py-3 text-left">Category</th>
                  <th className="px-4 py-3 text-left">Title</th>
                  <th className="px-4 py-3 text-left">Source</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-800">
                {findings.items.map((f) => (
                  <tr key={f.id} className="hover:bg-gray-900/50">
                    <td className="px-4 py-3 whitespace-nowrap">
                      <SeverityBadge severity={f.severity} />
                    </td>
                    <td className="px-4 py-3 text-gray-500 font-mono text-xs whitespace-nowrap">
                      {f.category}
                    </td>
                    <td className="px-4 py-3">
                      <div className="text-gray-200">{f.title}</div>
                      {f.description && (
                        <div className="text-xs text-gray-500 mt-0.5 line-clamp-1">
                          {f.description}
                        </div>
                      )}
                      {f.package && (
                        <div className="text-xs text-gray-600 font-mono mt-0.5">
                          {f.package}
                          {f.version ? `@${f.version}` : ""}
                          {f.fix_version ? ` → ${f.fix_version}` : ""}
                        </div>
                      )}
                    </td>
                    <td className="px-4 py-3 text-gray-500 font-mono text-xs whitespace-nowrap">
                      {f.sources.join(", ")}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

function InfoCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-gray-900 rounded-lg border border-gray-800 p-4">
      <div className="text-xs text-gray-500 mb-1">{label}</div>
      <div className="font-mono text-lg text-gray-100">{value}</div>
    </div>
  );
}
