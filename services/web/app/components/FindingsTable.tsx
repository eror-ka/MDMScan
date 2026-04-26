import type { Finding } from "../lib/api";
import SeverityBadge from "./SeverityBadge";

const CAT_LABEL: Record<string, string> = {
  vuln: "Уязвимости",
  secret: "Секреты",
  misconfig: "Мисконфигурации",
  supply_chain: "Цепочка поставок",
  hygiene: "Гигиена образа",
};

const CAT_ORDER = ["vuln", "secret", "misconfig", "supply_chain", "hygiene"];
const SEV_ORDER = ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO", "UNKNOWN"];

const INTERNAL_REFS = new Set([
  "syft-sbom",
  "dive-efficiency",
  "cosign-unsigned",
  "cosign-signed",
]);

function maxSev(items: Finding[]): string {
  for (const s of SEV_ORDER) {
    if (items.some((f) => f.severity === s)) return s;
  }
  return "UNKNOWN";
}

function groupFindings(findings: Finding[]) {
  const map = new Map<string, Finding[]>();
  for (const f of findings) {
    const arr = map.get(f.category) ?? [];
    arr.push(f);
    map.set(f.category, arr);
  }
  const result: { category: string; findings: Finding[]; maxSeverity: string }[] =
    [];
  for (const cat of CAT_ORDER) {
    const items = map.get(cat);
    if (items) {
      items.sort(
        (a, b) => SEV_ORDER.indexOf(a.severity) - SEV_ORDER.indexOf(b.severity),
      );
      result.push({ category: cat, findings: items, maxSeverity: maxSev(items) });
      map.delete(cat);
    }
  }
  for (const [cat, items] of map) {
    result.push({ category: cat, findings: items, maxSeverity: maxSev(items) });
  }
  return result;
}

export default function FindingsTable({ findings }: { findings: Finding[] }) {
  if (findings.length === 0) {
    return <p className="text-gray-500 text-sm">Находок не обнаружено.</p>;
  }

  const groups = groupFindings(findings);

  return (
    <div className="space-y-4">
      {groups.map((g) => {
        const hasPackages = g.findings.some((f) => f.package);
        const hasFixes = g.findings.some((f) => f.fix_version);
        const label = CAT_LABEL[g.category] ?? g.category;

        return (
          <div
            key={g.category}
            className="rounded-lg border border-gray-800 overflow-hidden"
          >
            {/* Заголовок группы с общей оценкой severity */}
            <div className="bg-gray-900 px-4 py-3 flex items-center gap-3">
              <SeverityBadge severity={g.maxSeverity} />
              <span className="font-semibold text-gray-200">{label}</span>
              <span className="text-gray-500 text-xs ml-auto">
                {g.findings.length} нах.
              </span>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-gray-950 text-gray-500 text-xs uppercase tracking-wide">
                  <tr>
                    <th className="px-4 py-2 text-left w-24">Severity</th>
                    <th className="px-4 py-2 text-left">Проблема</th>
                    {hasPackages && (
                      <th className="px-4 py-2 text-left">Пакет</th>
                    )}
                    {hasFixes && (
                      <th className="px-4 py-2 text-left">Исправление</th>
                    )}
                    <th className="px-4 py-2 text-left">Источник</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-800/60">
                  {g.findings.map((f) => {
                    const showRef =
                      f.raw_ref &&
                      !INTERNAL_REFS.has(f.raw_ref) &&
                      f.raw_ref !== f.title;
                    return (
                      <tr key={f.id} className="hover:bg-gray-900/30">
                        <td className="px-4 py-2 whitespace-nowrap">
                          <SeverityBadge severity={f.severity} />
                        </td>
                        <td className="px-4 py-2">
                          <div className="text-gray-200">{f.title}</div>
                          {showRef && (
                            <div className="text-xs text-gray-500 font-mono mt-0.5">
                              {f.raw_ref}
                            </div>
                          )}
                          {f.description &&
                            f.description !== f.title && (
                              <div className="text-xs text-gray-600 mt-0.5 line-clamp-2">
                                {f.description}
                              </div>
                            )}
                        </td>
                        {hasPackages && (
                          <td className="px-4 py-2 font-mono text-xs text-gray-400 whitespace-nowrap">
                            {f.package && <div>{f.package}</div>}
                            {f.version && (
                              <div className="text-gray-600">{f.version}</div>
                            )}
                          </td>
                        )}
                        {hasFixes && (
                          <td className="px-4 py-2 text-xs text-green-400 font-mono whitespace-nowrap">
                            {f.fix_version ?? "—"}
                          </td>
                        )}
                        <td className="px-4 py-2 text-xs text-gray-500 font-mono whitespace-nowrap">
                          {f.sources.join(", ")}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        );
      })}
    </div>
  );
}
