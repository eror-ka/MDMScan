from __future__ import annotations

import json
from pathlib import Path

from app.parsers.base import Finding

_SEV = {"FATAL": "HIGH", "WARN": "MEDIUM", "INFO": "INFO", "SKIP": "INFO"}


def parse(path: Path) -> list[Finding]:
    try:
        data = json.loads(path.read_text())
    except Exception:
        return []

    findings: list[Finding] = []
    for detail in data.get("details", []):
        level = detail.get("level", "INFO")
        sev = _SEV.get(level, "INFO")
        alerts = detail.get("alerts", [])
        desc = "; ".join(alerts) if alerts else ""
        findings.append(Finding(
            category="misconfig",
            severity=sev,
            title=detail.get("title", detail.get("code", "dockle finding")),
            description=desc,
            raw_ref=detail.get("code"),
            sources=["dockle"],
            fix_advice=desc or None,
        ))
    return findings
