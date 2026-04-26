from __future__ import annotations

from pathlib import Path

from app.parsers.base import Finding


def parse(path: Path) -> list[Finding]:
    try:
        text = path.read_text()
    except Exception:
        return []

    signed = any(kw in text for kw in ("Attestations", "Signatures", "sha256:"))
    if signed:
        return [
            Finding(
                category="supply_chain",
                severity="INFO",
                title="Образ подписан (Cosign)",
                description=text.strip(),
                raw_ref="cosign-signed",
                sources=["cosign"],
            )
        ]
    return [
        Finding(
            category="supply_chain",
            severity="INFO",
            title="Образ не подписан (Cosign)",
            description="Supply-chain артефакты (подписи, attestations) не обнаружены.",
            raw_ref="cosign-unsigned",
            sources=["cosign"],
            fix_advice="Подписать образ с помощью cosign sign при публикации в registry",
        )
    ]
