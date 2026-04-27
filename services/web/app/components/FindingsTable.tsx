import type { Finding } from "../lib/api";
import CategoryTable from "./CategoryTable";

const CAT_ORDER = ["vuln", "secret", "misconfig", "supply_chain", "hygiene"];
const CAT_LABEL: Record<string, string> = {
  vuln: "Уязвимости",
  secret: "Секреты",
  misconfig: "Мисконфигурации",
  supply_chain: "Цепочка поставок",
  hygiene: "Гигиена образа",
};
const SEV_ORDER = ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO", "UNKNOWN"];

function maxSev(items: Finding[]): string {
  for (const s of SEV_ORDER) {
    if (items.some((f) => f.severity === s)) return s;
  }
  return "UNKNOWN";
}

function countByCategory(findings: Finding[]) {
  const counts: Record<string, number> = {};
  for (const f of findings) {
    counts[f.category] = (counts[f.category] ?? 0) + 1;
  }
  return counts;
}

function AnalyticsSummary({
  imageRef,
  findings,
}: {
  imageRef: string;
  findings: Finding[];
}) {
  const counts = countByCategory(findings);

  return (
    <div className="rounded-lg border border-gray-800 overflow-hidden">
      <div className="bg-gray-900 px-4 py-3 text-center">
        <span className="font-bold text-gray-100 text-lg">Краткая аналитика</span>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="bg-gray-950 text-gray-300 text-sm uppercase tracking-wide border-t border-gray-800">
            <tr>
              <th className="px-4 py-2 text-left">Цель</th>
              <th className="px-4 py-2 text-center">Тип</th>
              {CAT_ORDER.map((cat) => (
                <th key={cat} className="px-4 py-2 text-center">
                  {CAT_LABEL[cat]}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            <tr className="border-t border-gray-800">
              <td className="px-4 py-3 font-mono text-gray-200 text-sm">
                {imageRef}
              </td>
              <td className="px-4 py-3 text-center text-gray-500 text-sm">
                Docker
              </td>
              {CAT_ORDER.map((cat) => {
                const n = counts[cat] ?? 0;
                return (
                  <td
                    key={cat}
                    className={`px-4 py-3 text-center font-mono text-base font-bold ${
                      n > 0 ? "text-red-400" : "text-gray-500"
                    }`}
                  >
                    {n}
                  </td>
                );
              })}
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
}

interface Props {
  imageRef: string;
  findings: Finding[];
}

export default function FindingsTable({ imageRef, findings }: Props) {
  const map = new Map<string, Finding[]>();
  for (const f of findings) {
    const arr = map.get(f.category) ?? [];
    arr.push(f);
    map.set(f.category, arr);
  }

  return (
    <div className="space-y-4">
      <div className="text-xs text-gray-500 bg-gray-900/50 rounded px-4 py-2 border border-gray-800 flex gap-4">
        <span className="font-medium text-gray-400">Заметки:</span>
        <span>
          <span className="font-mono">—</span> Не сканировалось
        </span>
        <span>
          <span className="font-mono text-green-400">0</span> Безопасно
        </span>
      </div>

      <AnalyticsSummary imageRef={imageRef} findings={findings} />

      {CAT_ORDER.map((cat) => {
        const items = map.get(cat) ?? [];
        return (
          <CategoryTable
            key={cat}
            category={cat}
            findings={items}
            maxSeverity={maxSev(items)}
          />
        );
      })}
    </div>
  );
}
