from __future__ import annotations

from datetime import datetime

SEV_EMOJI: dict[str, str] = {
    "CRITICAL": "🔴",
    "HIGH": "🟠",
    "MEDIUM": "🟡",
    "LOW": "🔵",
    "INFO": "⚪",
    "UNKNOWN": "⬜",
}

STATUS_EMOJI: dict[str, str] = {
    "done": "✅",
    "running": "⏳",
    "pending": "🕐",
    "failed": "❌",
}

SEV_ORDER = ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO", "UNKNOWN"]


def format_scan_result(scan: dict, findings: dict) -> str:
    status_emoji = STATUS_EMOJI.get(scan["status"], "❓")

    sev_counts: dict[str, int] = {}
    for f in findings.get("items", []):
        sev = f["severity"]
        sev_counts[sev] = sev_counts.get(sev, 0) + 1

    duration = ""
    if scan.get("finished_at") and scan.get("created_at"):
        start = datetime.fromisoformat(scan["created_at"])
        end = datetime.fromisoformat(scan["finished_at"])
        secs = (end - start).total_seconds()
        duration = f"\n⏱ Время: {secs:.1f}с"

    statuses = scan.get("scanner_statuses") or {}
    all_ok = all(v == "ok" for v in statuses.values())
    scanners_str = "✅ все" if all_ok else "⚠️ часть завершилась с ошибкой"

    lines = [
        f"{status_emoji} *Сканирование завершено\\!*",
        "",
        f"📦 Образ: `{scan['image_ref']}`",
        f"🆔 ID: `{scan['scan_id'][:8]}…`{duration}",
        "",
        f"📊 *Находки ({findings.get('total', 0)}):*",
    ]

    for sev in SEV_ORDER:
        if sev in sev_counts:
            emoji = SEV_EMOJI.get(sev, "⬜")
            lines.append(f"  {emoji} {sev}: {sev_counts[sev]}")

    if not sev_counts:
        lines.append("  Находок не обнаружено")

    lines += ["", f"🤖 Сканеры: {scanners_str}"]
    return "\n".join(lines)


def format_scan_status(scan: dict) -> str:
    emoji = STATUS_EMOJI.get(scan["status"], "❓")
    lines = [
        f"{emoji} *Статус: {scan['status']}*",
        "",
        f"📦 Образ: `{scan['image_ref']}`",
        f"🆔 ID: `{scan['scan_id']}`",
        f"📊 Находок: {scan['findings_count']}",
    ]
    if scan.get("finished_at"):
        lines.append(f"🏁 Завершён: {scan['finished_at'][:19].replace('T', ' ')}")
    return "\n".join(lines)


def format_scans_list(scans: list) -> str:
    if not scans:
        return "📭 Сканирований ещё не было\\."
    lines = ["📋 *Последние сканирования:*", ""]
    for i, s in enumerate(scans, 1):
        emoji = STATUS_EMOJI.get(s["status"], "❓")
        short_id = s["scan_id"][:8]
        image = s["image_ref"]
        cnt = s["findings_count"]
        lines.append(f"{i}\\. {emoji} `{image}` — {cnt} нах\\. — `{short_id}`")
    return "\n".join(lines)
