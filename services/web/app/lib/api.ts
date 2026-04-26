const API_URL = process.env.API_URL ?? "http://localhost:8000";

export interface ScanListItem {
  scan_id: string;
  image_ref: string;
  status: string;
  created_at: string;
  finished_at: string | null;
  findings_count: number;
}

export interface ScanJob extends ScanListItem {
  scanner_statuses: Record<string, string> | null;
}

export interface Finding {
  id: number;
  fingerprint: string;
  category: string;
  severity: string;
  title: string;
  description: string | null;
  package: string | null;
  version: string | null;
  fix_version: string | null;
  location: string | null;
  raw_ref: string | null;
  sources: string[];
  fix_advice: string | null;
}

export interface FindingsResponse {
  scan_id: string;
  total: number;
  items: Finding[];
}

export async function listScans(limit = 20): Promise<ScanListItem[]> {
  try {
    const res = await fetch(`${API_URL}/scans?limit=${limit}`, {
      cache: "no-store",
    });
    if (!res.ok) return [];
    return res.json();
  } catch {
    return [];
  }
}

export async function getScan(scanId: string): Promise<ScanJob | null> {
  try {
    const res = await fetch(`${API_URL}/scans/${scanId}`, {
      cache: "no-store",
    });
    if (!res.ok) return null;
    return res.json();
  } catch {
    return null;
  }
}

export async function getFindings(scanId: string): Promise<FindingsResponse> {
  try {
    const res = await fetch(`${API_URL}/scans/${scanId}/findings?limit=500`, {
      cache: "no-store",
    });
    if (!res.ok) return { scan_id: scanId, total: 0, items: [] };
    return res.json();
  } catch {
    return { scan_id: scanId, total: 0, items: [] };
  }
}
