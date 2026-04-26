const colors: Record<string, string> = {
  done: "bg-green-900 text-green-400",
  running: "bg-blue-900 text-blue-400",
  pending: "bg-yellow-900 text-yellow-400",
  failed: "bg-red-900 text-red-400",
};

export default function StatusBadge({ status }: { status: string }) {
  const cls = colors[status] ?? "bg-gray-800 text-gray-400";
  return (
    <span
      className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${cls}`}
    >
      {status}
    </span>
  );
}
