from __future__ import annotations

import json
from pathlib import Path

from app.parsers.base import Finding


def parse(path: Path) -> list[Finding]:
    try:
        data = json.loads(path.read_text())
    except Exception:
        return []

    image = data.get("image", {})
    efficiency = image.get("efficiencyScore", 1.0)
    total_bytes = image.get("sizeBytes", 0)
    wasted_bytes = image.get("inefficientBytes", 0)

    if efficiency >= 0.95:
        sev = "INFO"
    elif efficiency >= 0.85:
        sev = "LOW"
    elif efficiency >= 0.70:
        sev = "MEDIUM"
    else:
        sev = "HIGH"

    wasted_mb = round(wasted_bytes / 1024 / 1024, 1)
    total_mb = round(total_bytes / 1024 / 1024, 1)

    ineff_files = data.get("inefficientFiles", [])
    top_files = ", ".join(f["file"] for f in ineff_files[:5] if "file" in f)

    desc = (
        f"Эффективность образа: {round(efficiency * 100, 1)}%. "
        f"Дублируется {wasted_mb} МБ из {total_mb} МБ."
    )
    advice = None
    if wasted_bytes > 0:
        advice = (
            "Объединить RUN-команды и очищать кэш пакетного менеджера в одном слое."
        )
        if top_files:
            advice += f" Дублирующиеся файлы: {top_files}"

    return [
        Finding(
            category="hygiene",
            severity=sev,
            title=f"Эффективность образа: {round(efficiency * 100, 1)}%",
            description=desc,
            raw_ref="dive-efficiency",
            sources=["dive"],
            fix_advice=advice,
        )
    ]
