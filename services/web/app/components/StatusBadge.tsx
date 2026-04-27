const config: Record<string, { label: string; cls: string }> = {
  done: { label: "завершён", cls: "bg-green-900 text-green-400" },
  running: { label: "выполняется", cls: "bg-blue-900 text-blue-400" },
  pending: { label: "в очереди", cls: "bg-yellow-900 text-yellow-400" },
  failed: { label: "ошибка", cls: "bg-red-900 text-red-400" },
};

export default function StatusBadge({ status }: { status: string }) {
  const { label, cls } = config[status] ?? {
    label: status,
    cls: "bg-gray-800 text-gray-400",
  };
  return (
    <span
      className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${cls}`}
    >
      {label}
    </span>
  );
}
