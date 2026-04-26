import Link from "next/link";
import ScanForm from "./components/ScanForm";
import StatusBadge from "./components/StatusBadge";
import { listScans } from "./lib/api";

export const dynamic = "force-dynamic";

export default async function HomePage() {
  const scans = await listScans();

  return (
    <div className="space-y-10">
      <section>
        <h2 className="text-base font-semibold text-gray-300 mb-3">
          Scan an image
        </h2>
        <ScanForm />
      </section>

      <section>
        <h2 className="text-base font-semibold text-gray-300 mb-3">
          Recent scans
        </h2>
        {scans.length === 0 ? (
          <p className="text-gray-500 text-sm">No scans yet.</p>
        ) : (
          <div className="overflow-hidden rounded-lg border border-gray-800">
            <table className="w-full text-sm">
              <thead className="bg-gray-900 text-gray-400 text-xs uppercase tracking-wide">
                <tr>
                  <th className="px-4 py-3 text-left">Image</th>
                  <th className="px-4 py-3 text-left">Status</th>
                  <th className="px-4 py-3 text-right">Findings</th>
                  <th className="px-4 py-3 text-left">Started</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-800">
                {scans.map((scan) => (
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
                    <td className="px-4 py-3 text-gray-500 text-xs">
                      {new Date(scan.created_at).toLocaleString("ru-RU")}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
}
