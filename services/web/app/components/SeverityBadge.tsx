const config: Record<string, { label: string; cls: string }> = {
  CRITICAL: {
    label: "Критическая",
    cls: "bg-red-950 text-red-400 border-red-800",
  },
  HIGH: {
    label: "Высокая",
    cls: "bg-orange-950 text-orange-400 border-orange-800",
  },
  MEDIUM: {
    label: "Средняя",
    cls: "bg-yellow-950 text-yellow-400 border-yellow-800",
  },
  LOW: {
    label: "Низкая",
    cls: "bg-blue-950 text-blue-400 border-blue-800",
  },
  INFO: {
    label: "Инфо",
    cls: "bg-gray-900 text-gray-400 border-gray-700",
  },
  UNKNOWN: {
    label: "Неизвестная",
    cls: "bg-gray-900 text-gray-500 border-gray-700",
  },
};

export default function SeverityBadge({ severity }: { severity: string }) {
  const { label, cls } = config[severity] ?? {
    label: severity,
    cls: "bg-gray-900 text-gray-400 border-gray-700",
  };
  return (
    <span
      className={`inline-block px-2 py-0.5 rounded text-xs font-medium border ${cls}`}
    >
      {label}
    </span>
  );
}
