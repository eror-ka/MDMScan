from __future__ import annotations

import json
from pathlib import Path

from app.parsers.base import Finding


def parse(path: Path) -> list[Finding]:
    """Syft генерирует SBOM, а не security findings.
    Возвращаем одну информационную запись с кол-вом компонентов.
    """
    try:
        data = json.loads(path.read_text())
    except Exception:
        return []

    packages = data.get("packages", [])
    pkg_count = len(packages)

    licenses: set[str] = set()
    for pkg in packages:
        for lic in pkg.get("licenseConcluded", "").split(" AND "):
            lic = lic.strip("() ")
            if lic and lic not in ("NOASSERTION", "NONE", ""):
                licenses.add(lic)

    desc = f"SBOM содержит {pkg_count} компонентов."
    if licenses:
        desc += f" Лицензии: {', '.join(sorted(licenses)[:10])}."

    return [Finding(
        category="supply_chain",
        severity="INFO",
        title=f"SBOM: {pkg_count} компонентов",
        description=desc,
        raw_ref="syft-sbom",
        sources=["syft"],
    )]
