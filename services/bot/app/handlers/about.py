from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()

_ABOUT = """\
ℹ️ *MDMScan — система оценки безопасности Docker\\-образов*

Проект автоматически проверяет Docker\\-образы с помощью 7 открытых сканеров безопасности:

🔍 *Сканеры:*
• *Trivy* — CVE\\-уязвимости, мисконфигурации, секреты
• *Syft* — SBOM \\(перечень компонентов образа\\)
• *Dockle* — соответствие CIS Docker Benchmark
• *OSV\\-Scanner* — база уязвимостей Google OSV
• *Dive* — эффективность слоёв образа
• *TruffleHog* — утечки секретов и токенов
• *Cosign* — проверка подписи \\(supply chain\\)

📁 *Хранение:*
Артефакты сканирования хранятся в MinIO\\.
Нормализованные находки сохраняются в PostgreSQL\\.

🌐 *Интерфейсы:*
• REST API \\(FastAPI\\) — документация на `/docs`
• Web UI \\(Next\\.js\\)
• Telegram\\-бот \\(вы здесь\\)

📚 *Дипломный проект, 2026*\
"""


def about_text() -> str:
    return _ABOUT


@router.message(Command("about"))
async def cmd_about(message: Message) -> None:
    await message.answer(_ABOUT, parse_mode="MarkdownV2")
