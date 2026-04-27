"use client";

import { useState } from "react";
import type { Finding } from "../lib/api";
import SeverityBadge from "./SeverityBadge";

const SEV_ORDER = ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO", "UNKNOWN"];

const CAT_LABEL: Record<string, string> = {
  vuln: "Уязвимости",
  secret: "Секреты",
  misconfig: "Мисконфигурации",
  supply_chain: "Цепочка поставок",
  hygiene: "Гигиена образа",
};

function EmptyRow({ colSpan }: { colSpan: number }) {
  return (
    <tr>
      <td
        colSpan={colSpan}
        className="px-4 py-5 text-center text-gray-600 text-sm italic"
      >
        Ничего не обнаружено
      </td>
    </tr>
  );
}

function VulnTableContent({
  findings,
  open,
}: {
  findings: Finding[];
  open: boolean;
}) {
  return (
    <table className="w-full text-sm">
      <thead className="bg-gray-950 text-gray-400 text-sm uppercase tracking-wide border-t border-gray-800">
        <tr>
          <th className="px-4 py-2 text-left">Библиотека</th>
          <th className="px-4 py-2 text-left">Уязвимость</th>
          <th className="px-4 py-2 text-left">Серьёзность</th>
          <th className="px-4 py-2 text-left">Установленная версия</th>
          <th className="px-4 py-2 text-left">Исправленная версия</th>
          <th className="px-4 py-2 text-left">Название</th>
          <th className="px-4 py-2 text-left">Источник</th>
        </tr>
      </thead>
      {open && (
        <tbody className="divide-y divide-gray-800/60">
          {findings.length === 0 ? (
            <EmptyRow colSpan={7} />
          ) : (
            findings.map((f) => (
              <tr key={f.id} className="hover:bg-gray-900/30">
                <td className="px-4 py-2 font-mono text-gray-300 whitespace-nowrap">
                  {f.package ?? "—"}
                </td>
                <td className="px-4 py-2 font-mono text-gray-400 whitespace-nowrap">
                  {f.raw_ref ?? "—"}
                </td>
                <td className="px-4 py-2 whitespace-nowrap">
                  <SeverityBadge severity={f.severity} />
                </td>
                <td className="px-4 py-2 font-mono text-gray-500 whitespace-nowrap">
                  {f.version ?? "—"}
                </td>
                <td className="px-4 py-2 font-mono text-green-400 whitespace-nowrap">
                  {f.fix_version ?? "—"}
                </td>
                <td className="px-4 py-2 text-gray-300 max-w-sm">
                  <div className="line-clamp-2">{f.title}</div>
                  {f.description && f.description !== f.title && (
                    <div className="text-gray-600 text-xs mt-0.5 line-clamp-1">
                      {f.description}
                    </div>
                  )}
                </td>
                <td className="px-4 py-2 text-gray-500 font-mono whitespace-nowrap">
                  {f.sources.join(", ")}
                </td>
              </tr>
            ))
          )}
        </tbody>
      )}
    </table>
  );
}

function GenericTableContent({
  findings,
  open,
}: {
  findings: Finding[];
  open: boolean;
}) {
  const hasLocation = findings.some((f) => f.location);
  const colSpan = 3 + (hasLocation ? 1 : 0);
  return (
    <table className="w-full text-sm">
      <thead className="bg-gray-950 text-gray-400 text-sm uppercase tracking-wide border-t border-gray-800">
        <tr>
          <th className="px-4 py-2 text-left">Серьёзность</th>
          <th className="px-4 py-2 text-left">Проверка / Описание</th>
          {hasLocation && (
            <th className="px-4 py-2 text-left">Местоположение</th>
          )}
          <th className="px-4 py-2 text-left">Источник</th>
        </tr>
      </thead>
      {open && (
        <tbody className="divide-y divide-gray-800/60">
          {findings.length === 0 ? (
            <EmptyRow colSpan={colSpan} />
          ) : (
            findings.map((f) => (
              <tr key={f.id} className="hover:bg-gray-900/30">
                <td className="px-4 py-2 whitespace-nowrap">
                  <SeverityBadge severity={f.severity} />
                </td>
                <td className="px-4 py-2 text-gray-300">
                  <div>{f.title}</div>
                  {f.description && f.description !== f.title && (
                    <div className="text-gray-600 text-sm line-clamp-2 mt-0.5">
                      {f.description}
                    </div>
                  )}
                </td>
                {hasLocation && (
                  <td className="px-4 py-2 font-mono text-gray-500 whitespace-nowrap">
                    {f.location ?? "—"}
                  </td>
                )}
                <td className="px-4 py-2 text-gray-500 font-mono whitespace-nowrap">
                  {f.sources.join(", ")}
                </td>
              </tr>
            ))
          )}
        </tbody>
      )}
    </table>
  );
}

interface Props {
  category: string;
  findings: Finding[];
  maxSeverity: string;
}

export default function CategoryTable({ category, findings, maxSeverity }: Props) {
  const [open, setOpen] = useState(true);
  const label = CAT_LABEL[category] ?? category;
  const isVuln = category === "vuln";
  const badgeSeverity = findings.length === 0 ? "INFO" : maxSeverity;

  // Sort findings by severity
  const sorted = [...findings].sort(
    (a, b) => SEV_ORDER.indexOf(a.severity) - SEV_ORDER.indexOf(b.severity),
  );

  return (
    <div className="rounded-lg border border-gray-800 overflow-hidden">
      {/* 3-column grid: badge left | title+button center | empty right */}
      <div className="bg-gray-900 px-4 py-3 grid grid-cols-3 items-center">
        <div>
          <SeverityBadge severity={badgeSeverity} />
        </div>
        <div className="flex items-center justify-center gap-3">
          <span className="font-bold text-gray-100 text-lg">{label}</span>
          <button
            onClick={() => setOpen(!open)}
            className="text-gray-300 hover:text-white transition-colors text-lg select-none"
            title={open ? "Свернуть" : "Развернуть"}
          >
            {open ? "▼" : "▶"}
          </button>
        </div>
        <div />
      </div>
      <div className="overflow-x-auto">
        {isVuln ? (
          <VulnTableContent findings={sorted} open={open} />
        ) : (
          <GenericTableContent findings={sorted} open={open} />
        )}
      </div>
    </div>
  );
}
