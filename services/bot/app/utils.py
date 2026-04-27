from __future__ import annotations

import json
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

CAT_LABELS: dict[str, str] = {
    "vuln": "Уязвимости",
    "secret": "Секреты",
    "misconfig": "Мисконфиги",
    "hygiene": "Гигиена",
    "supply_chain": "Supply Chain",
}

_SPECIAL = set(r"\_*[]()~`>#+-=|{}.!")


def _esc(text: str) -> str:
    """Escape MarkdownV2 special characters for use OUTSIDE code spans."""
    return "".join(f"\\{c}" if c in _SPECIAL else c for c in str(text))


def _score_emoji(score: int) -> str:
    if score >= 80:
        return "🟢"
    if score >= 60:
        return "🟡"
    if score >= 40:
        return "🟠"
    return "🔴"


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

    score = scan.get("security_score")
    score_line = ""
    if score is not None:
        score_line = f"\n{_score_emoji(score)} Безопасность: *{score}/100*"

    statuses = scan.get("scanner_statuses") or {}
    all_ok = all(v == "ok" for v in statuses.values())
    scanners_str = "✅ все" if all_ok else "⚠️ часть с ошибкой"

    lines = [
        f"{status_emoji} *Сканирование завершено\\!*",
        "",
        f"📦 Образ: `{scan['image_ref']}`",
        f"🆔 ID: `{scan['scan_id'][:8]}…`{_esc(duration)}{score_line}",
        "",
        f"📊 *Находки \\({findings.get('total', 0)}\\):*",
    ]
    for sev in SEV_ORDER:
        if sev in sev_counts:
            lines.append(f"  {SEV_EMOJI.get(sev, '⬜')} {sev}: {sev_counts[sev]}")
    if not sev_counts:
        lines.append("  Находок не обнаружено")
    lines += ["", f"🤖 Сканеры: {scanners_str}"]
    return "\n".join(lines)


def format_scan_status(scan: dict) -> str:
    emoji = STATUS_EMOJI.get(scan["status"], "❓")
    score = scan.get("security_score")
    score_line = ""
    if score is not None:
        score_line = f"\n{_score_emoji(score)} Безопасность: *{score}/100*"
    lines = [
        f"{emoji} *Статус: {scan['status']}*",
        "",
        f"📦 Образ: `{scan['image_ref']}`",
        f"🆔 ID: `{scan['scan_id']}`",
        f"📊 Находок: {scan['findings_count']}{score_line}",
    ]
    if scan.get("finished_at"):
        finished = _esc(scan["finished_at"][:19].replace("T", " "))
        lines.append(f"🏁 Завершён: {finished}")
    return "\n".join(lines)


def format_scan_detail(scan: dict) -> str:
    emoji = STATUS_EMOJI.get(scan["status"], "❓")
    score = scan.get("security_score")
    score_line = ""
    if score is not None:
        score_line = f"\n{_score_emoji(score)} *Оценка безопасности: {score}/100*"

    duration_line = ""
    if scan.get("finished_at") and scan.get("created_at"):
        start = datetime.fromisoformat(scan["created_at"])
        end = datetime.fromisoformat(scan["finished_at"])
        secs = int((end - start).total_seconds())
        duration_line = f"\n⏱ Длительность: {secs}с"

    created = _esc(scan.get("created_at", "")[:19].replace("T", " "))

    statuses = scan.get("scanner_statuses") or {}
    scanner_lines = []
    for name, st in sorted(statuses.items()):
        sc_emoji = "✅" if st == "ok" else "❌"
        scanner_lines.append(f"  {sc_emoji} {_esc(name)}")
    scanner_section = (
        "\n\n🤖 *Сканеры:*\n" + "\n".join(scanner_lines) if scanner_lines else ""
    )

    return (
        f"{emoji} *Скан `{scan['scan_id'][:8]}…`*\n\n"
        f"📦 Образ: `{scan['image_ref']}`\n"
        f"📅 Создан: {created}{_esc(duration_line)}\n"
        f"📊 Находок: *{scan['findings_count']}*{score_line}"
        f"{scanner_section}"
    )


def format_scans_list(scans: list) -> str:
    if not scans:
        return "📭 Сканирований ещё не было\\."
    lines = ["📋 *Последние сканирования:*", ""]
    for i, s in enumerate(scans, 1):
        emoji = STATUS_EMOJI.get(s["status"], "❓")
        short_id = s["scan_id"][:8]
        image = _esc(s["image_ref"])
        cnt = s["findings_count"]
        score = s.get("security_score")
        score_str = f" \\| 🛡 {score}" if score is not None else ""
        lines.append(
            f"{i}\\. {emoji} `{image}` — {cnt} нах\\.{score_str} — `{short_id}`"
        )
    return "\n".join(lines)


def format_findings_page(
    findings: dict,
    filter_desc: str,
    page: int,
    page_size: int,
) -> str:
    total = findings.get("total", 0)
    items = findings.get("items", [])
    total_pages = max(1, (total + page_size - 1) // page_size)

    header = (
        f"🔍 *Находки — {_esc(filter_desc)}*\n"
        f"Всего: {total} \\| Стр\\. {page + 1}/{total_pages}\n"
    )
    if not items:
        return header + "\nНет находок по данному фильтру\\."

    lines = [header]
    for f in items:
        sev_emoji = SEV_EMOJI.get(f["severity"], "⬜")
        title = _esc(f["title"][:55])
        pkg = f.get("package") or ""
        ver = f.get("version") or ""
        pkg_info = f" `{pkg}`" + (f" {_esc(ver)}" if ver else "") if pkg else ""
        raw = f.get("raw_ref") or ""
        raw_line = f"\n   📎 `{raw[:45]}`" if raw else ""
        lines.append(f"{sev_emoji} *{title}*{pkg_info}{raw_line}")

    return "\n".join(lines)


# ─── PDF generation ────────────────────────────────────────────────────────────


def _safe_latin(text: str | None, max_len: int = 100) -> str:
    if not text:
        return ""
    return text.encode("latin-1", errors="replace").decode("latin-1")[:max_len]


def generate_pdf_report(scan: dict, findings: dict) -> bytes:
    from fpdf import FPDF  # type: ignore

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Title
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 12, "MDMScan Security Report", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(2)

    # Scan meta
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Scan Information", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)

    def kv(label: str, value: str) -> None:
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(45, 7, label, new_x="RIGHT", new_y="TOP")
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 7, value, new_x="LMARGIN", new_y="NEXT")

    kv("Image:", _safe_latin(scan.get("image_ref"), 70))
    kv("Scan ID:", _safe_latin(scan.get("scan_id"), 40))
    kv("Status:", _safe_latin(scan.get("status"), 20))
    score = scan.get("security_score")
    if score is not None:
        kv("Security Score:", f"{score}/100")
    created = (scan.get("created_at") or "")[:19].replace("T", " ")
    kv("Created:", created)
    if scan.get("finished_at") and scan.get("created_at"):
        start = datetime.fromisoformat(scan["created_at"])
        end = datetime.fromisoformat(scan["finished_at"])
        kv("Duration:", f"{int((end - start).total_seconds())}s")
    pdf.ln(4)

    # Severity / category summary table
    sev_counts: dict[str, int] = {}
    cat_counts: dict[str, int] = {}
    for f in findings.get("items", []):
        sev_counts[f["severity"]] = sev_counts.get(f["severity"], 0) + 1
        cat_counts[f["category"]] = cat_counts.get(f["category"], 0) + 1

    pdf.set_font("Helvetica", "B", 12)
    total_label = f"Findings Summary  (total: {findings.get('total', 0)})"
    pdf.cell(0, 8, total_label, new_x="LMARGIN", new_y="NEXT")

    col = [48, 22, 70, 22]
    pdf.set_fill_color(220, 220, 220)
    pdf.set_font("Helvetica", "B", 9)
    for text, width in zip(["Severity", "Count", "Category", "Count"], col):
        pdf.cell(width, 7, text, border=1, fill=True)
    pdf.ln()
    pdf.set_font("Helvetica", "", 9)

    sev_rows = [(s, sev_counts[s]) for s in SEV_ORDER if s in sev_counts]
    cat_rows = list(cat_counts.items())
    for i in range(max(len(sev_rows), len(cat_rows))):
        sl = sev_rows[i][0] if i < len(sev_rows) else ""
        sc = str(sev_rows[i][1]) if i < len(sev_rows) else ""
        cl = cat_rows[i][0] if i < len(cat_rows) else ""
        cc = str(cat_rows[i][1]) if i < len(cat_rows) else ""
        for text, width in zip([sl, sc, cl, cc], col):
            pdf.cell(width, 7, text, border=1)
        pdf.ln()
    pdf.ln(5)

    # Scanner statuses
    statuses = scan.get("scanner_statuses") or {}
    if statuses:
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, "Scanner Statuses", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 9)
        for name, st in sorted(statuses.items()):
            mark = "OK" if st == "ok" else "FAIL"
            row = f"  [{mark}] {_safe_latin(name, 40)}"
            pdf.cell(0, 6, row, new_x="LMARGIN", new_y="NEXT")
        pdf.ln(4)

    # Findings detail
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Findings Detail", new_x="LMARGIN", new_y="NEXT")

    for f in findings.get("items", []):
        if pdf.get_y() > 262:
            pdf.add_page()
        pdf.set_font("Helvetica", "B", 9)
        title = _safe_latin(f.get("title"), 75)
        pdf.cell(0, 6, f"[{f['severity']}] {title}", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 8)
        if f.get("package"):
            ver = _safe_latin(f.get("version"), 20)
            fix = _safe_latin(f.get("fix_version"), 20)
            line = f"  Package: {_safe_latin(f['package'], 40)} {ver}"
            if fix:
                line += f"  ->  {fix}"
            pdf.cell(0, 5, line, new_x="LMARGIN", new_y="NEXT")
        if f.get("raw_ref"):
            ref_row = f"  Ref: {_safe_latin(f['raw_ref'], 60)}"
            pdf.cell(0, 5, ref_row, new_x="LMARGIN", new_y="NEXT")
        if f.get("location"):
            loc_row = f"  Location: {_safe_latin(f['location'], 60)}"
            pdf.cell(0, 5, loc_row, new_x="LMARGIN", new_y="NEXT")
        pdf.ln(1)

    # Footer
    pdf.set_y(-15)
    pdf.set_font("Helvetica", "I", 8)
    pdf.cell(0, 10, "Generated by MDMScan  |  Diploma Project 2026", align="C")

    return bytes(pdf.output())


# ─── JSON report ───────────────────────────────────────────────────────────────


def generate_json_report(scan: dict, findings: dict) -> str:
    by_sev: dict[str, int] = {}
    by_cat: dict[str, int] = {}
    for f in findings.get("items", []):
        by_sev[f["severity"]] = by_sev.get(f["severity"], 0) + 1
        by_cat[f["category"]] = by_cat.get(f["category"], 0) + 1

    report = {
        "generated_by": "MDMScan",
        "scan": scan,
        "findings_summary": {
            "total": findings.get("total", 0),
            "by_severity": by_sev,
            "by_category": by_cat,
        },
        "findings": findings.get("items", []),
    }
    return json.dumps(report, ensure_ascii=False, indent=2, default=str)
