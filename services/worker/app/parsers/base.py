from __future__ import annotations

import hashlib
from dataclasses import dataclass, field

SEVERITY_ORDER = {"CRITICAL": 5, "HIGH": 4, "MEDIUM": 3, "LOW": 2, "INFO": 1, "UNKNOWN": 0}


def _max_severity(a: str, b: str) -> str:
    return a if SEVERITY_ORDER.get(a, 0) >= SEVERITY_ORDER.get(b, 0) else b


@dataclass
class Finding:
    category: str
    severity: str
    title: str
    description: str = ""
    package: str | None = None
    version: str | None = None
    fix_version: str | None = None
    location: str | None = None
    raw_ref: str | None = None
    sources: list[str] = field(default_factory=list)
    fix_advice: str | None = None

    @property
    def fingerprint(self) -> str:
        key = "|".join([
            self.category,
            self.raw_ref or self.title,
            self.package or "",
            self.version or "",
            self.location or "",
        ])
        return hashlib.sha1(key.encode()).hexdigest()  # noqa: S324


def deduplicate(findings: list[Finding]) -> list[Finding]:
    merged: dict[str, Finding] = {}
    for f in findings:
        fp = f.fingerprint
        if fp not in merged:
            merged[fp] = f
        else:
            existing = merged[fp]
            existing.sources = sorted(set(existing.sources) | set(f.sources))
            existing.severity = _max_severity(existing.severity, f.severity)
            if f.fix_version and not existing.fix_version:
                existing.fix_version = f.fix_version
    return list(merged.values())
