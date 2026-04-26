from __future__ import annotations

import json
from pathlib import Path

from app.parsers.base import Finding


def _cvss_to_severity(score_str: str) -> str:
    try:
        score = float(score_str)
    except (ValueError, TypeError):
        return "UNKNOWN"
    if score >= 9.0:
        return "CRITICAL"
    if score >= 7.0:
        return "HIGH"
    if score >= 4.0:
        return "MEDIUM"
    if score > 0:
        return "LOW"
    return "INFO"


def parse(path: Path) -> list[Finding]:
    try:
        data = json.loads(path.read_text())
    except Exception:
        return []

    findings: list[Finding] = []
    for result in data.get("results", []):
        for pkg_entry in result.get("packages", []):
            pkg_info = pkg_entry.get("package", {})
            pkg_name = pkg_info.get("name", "")
            pkg_ver = pkg_info.get("version", "")

            for vuln in pkg_entry.get("vulnerabilities", []):
                vuln_id = vuln.get("id", "")
                summary = vuln.get("summary", vuln_id)

                sev = "UNKNOWN"
                for s in vuln.get("severity", []):
                    candidate = _cvss_to_severity(s.get("score", ""))
                    if candidate not in ("UNKNOWN", "INFO"):
                        sev = candidate
                        break

                findings.append(
                    Finding(
                        category="vuln",
                        severity=sev,
                        title=summary,
                        description=vuln.get("details", ""),
                        package=pkg_name,
                        version=pkg_ver,
                        raw_ref=vuln_id,
                        sources=["osv-scanner"],
                        fix_advice=f"Обновить {pkg_name} {pkg_ver}: {vuln_id}",
                    )
                )
    return findings
