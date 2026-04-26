from __future__ import annotations

import json
from pathlib import Path

from app.parsers.base import Finding

_SEV = {"CRITICAL": "CRITICAL", "HIGH": "HIGH", "MEDIUM": "MEDIUM", "LOW": "LOW", "UNKNOWN": "UNKNOWN"}


def parse(path: Path) -> list[Finding]:
    try:
        data = json.loads(path.read_text())
    except Exception:
        return []

    findings: list[Finding] = []
    for result in data.get("Results", []):
        target = result.get("Target", "")

        for v in result.get("Vulnerabilities") or []:
            cve = v.get("VulnerabilityID", "")
            pkg = v.get("PkgName", "")
            ver = v.get("InstalledVersion", "")
            fix = v.get("FixedVersion", "") or None
            sev = _SEV.get(v.get("Severity", "UNKNOWN"), "UNKNOWN")
            findings.append(Finding(
                category="vuln",
                severity=sev,
                title=v.get("Title") or cve,
                description=v.get("Description", ""),
                package=pkg,
                version=ver,
                fix_version=fix,
                location=target,
                raw_ref=cve,
                sources=["trivy"],
                fix_advice=f"Обновить {pkg} до {fix}" if fix else f"Фикс для {pkg} {ver} недоступен",
            ))

        for m in result.get("Misconfigurations") or []:
            sev = _SEV.get(m.get("Severity", "UNKNOWN"), "UNKNOWN")
            findings.append(Finding(
                category="misconfig",
                severity=sev,
                title=m.get("Title", m.get("ID", "misconfig")),
                description=m.get("Description", ""),
                location=target,
                raw_ref=m.get("ID"),
                sources=["trivy"],
                fix_advice=m.get("Resolution") or m.get("Message"),
            ))

        for s in result.get("Secrets") or []:
            findings.append(Finding(
                category="secret",
                severity="HIGH",
                title=s.get("Title", s.get("RuleID", "secret")),
                description=s.get("Match", ""),
                location=target,
                raw_ref=s.get("RuleID"),
                sources=["trivy"],
                fix_advice="Удалить секрет из образа и пересобрать без него",
            ))

    return findings
