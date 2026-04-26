"use client";

import { useFormStatus } from "react-dom";
import { submitScan } from "../actions";

function SubmitButton() {
  const { pending } = useFormStatus();
  return (
    <button
      type="submit"
      disabled={pending}
      className="px-5 py-2 bg-indigo-600 hover:bg-indigo-500 disabled:bg-indigo-900 disabled:text-indigo-400 rounded-lg text-sm font-medium transition-colors"
    >
      {pending ? "Сканирование…" : "Проверить"}
    </button>
  );
}

export default function ScanForm() {
  return (
    <form action={submitScan} className="flex gap-3 max-w-xl">
      <input
        name="image"
        type="text"
        placeholder="Например: alpine:latest, nginx:1.25"
        required
        className="flex-1 bg-gray-900 border border-gray-700 rounded-lg px-4 py-2 text-sm font-mono placeholder-gray-600 focus:outline-none focus:border-indigo-500"
      />
      <SubmitButton />
    </form>
  );
}
