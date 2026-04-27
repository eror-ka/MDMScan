"use server";

import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";

const API_URL = process.env.API_URL ?? "http://localhost:8000";

export async function submitScan(formData: FormData) {
  const image = (formData.get("image") as string)?.trim();
  if (!image) return;

  const res = await fetch(`${API_URL}/scans`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ image }),
  });

  if (!res.ok) throw new Error("Failed to submit scan");
  const data = await res.json();
  redirect(`/scans/${data.scan_id}`);
}

export async function deleteScan(formData: FormData) {
  const scanId = formData.get("scan_id") as string;
  if (!scanId) return;
  await fetch(`${API_URL}/scans/${scanId}`, { method: "DELETE" });
  revalidatePath("/");
}
