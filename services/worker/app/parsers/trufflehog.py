from __future__ import annotations

import json
from pathlib import Path

from app.parsers.base import Finding


def parse(path: Path) -> list[Finding]:
    try:
        text = path.read_text()
    except Exception:
        return []

    findings: list[Finding] = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue

        detector = obj.get("DetectorName", "secret")
        verified = obj.get("Verified", False)
        sev = "HIGH" if verified else "MEDIUM"

        meta = obj.get("SourceMetadata", {}).get("Data", {})
        location = ""
        for src_type in ("Docker", "Git", "Filesystem"):
            if src_type in meta:
                src = meta[src_type]
                location = src.get("file", src.get("filename", ""))
                break

        redacted = obj.get("Redacted", "")
        desc = f"Обнаружен секрет типа {detector}."
        if redacted:
            desc += f" Значение (частично): {redacted}"
        if verified:
            desc += " [VERIFIED — секрет активен]"

        findings.append(
            Finding(
                category="secret",
                severity=sev,
                title=f"Секрет: {detector}" + (" (подтверждён)" if verified else ""),
                description=desc,
                location=location or None,
                raw_ref=f"trufflehog-{detector}",
                sources=["trufflehog"],
                fix_advice="Удалить секрет из истории слоёв образа и сменить учётные данные",
            )
        )
    return findings
