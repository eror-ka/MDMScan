"use server";

import { redirect } from "next/navigation";

export async function submitScan(formData: FormData) {
  const image = (formData.get("image") as string)?.trim();
  if (!image) return;

  const apiUrl = process.env.API_URL ?? "http://localhost:8000";
  const res = await fetch(`${apiUrl}/scans`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ image }),
  });

  if (!res.ok) throw new Error("Failed to submit scan");
  const data = await res.json();
  redirect(`/scans/${data.scan_id}`);
}
