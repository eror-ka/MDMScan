const colors: Record<string, string> = {
  CRITICAL: "bg-red-950 text-red-400 border-red-800",
  HIGH: "bg-orange-950 text-orange-400 border-orange-800",
  MEDIUM: "bg-yellow-950 text-yellow-400 border-yellow-800",
  LOW: "bg-blue-950 text-blue-400 border-blue-800",
  INFO: "bg-gray-900 text-gray-400 border-gray-700",
  UNKNOWN: "bg-gray-900 text-gray-500 border-gray-700",
};

export default function SeverityBadge({ severity }: { severity: string }) {
  const cls =
    colors[severity] ?? "bg-gray-900 text-gray-400 border-gray-700";
  return (
    <span
      className={`inline-block px-2 py-0.5 rounded text-xs font-medium border ${cls}`}
    >
      {severity}
    </span>
  );
}
