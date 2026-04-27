from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher, Router
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    BotCommand,
    InlineKeyboardMarkup,
    Message,
    WebAppInfo,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.config import settings

log = logging.getLogger(__name__)
router = Router()


def _webapp_keyboard(path: str = "") -> InlineKeyboardMarkup:
    """
    Use web_app button when URL is HTTPS (required by Telegram for Mini Apps).
    Fall back to plain URL button for HTTP (local/dev environment).
    """
    builder = InlineKeyboardBuilder()
    url = settings.web_url.rstrip("/") + path
    if url.startswith("https://"):
        builder.button(text="🌐 Открыть MDMScan", web_app=WebAppInfo(url=url))
    else:
        builder.button(text="🌐 Открыть MDMScan", url=url)
    return builder.as_markup()


_WELCOME = """\
👋 *MDMScan Web*

Полный веб\\-интерфейс системы безопасности Docker\\-образов\\.

Что доступно в веб\\-приложении:
🔍 Запустить сканирование образа
📋 История всех сканирований
📊 Детальный анализ находок по категориям
🛡 Оценка безопасности \\(0–100\\)
🗑 Управление результатами

Нажми кнопку ниже, чтобы открыть интерфейс:\
"""

_ABOUT = """\
ℹ️ *MDMScan — автоматическая оценка безопасности Docker\\-образов*

Сканирует образы с помощью 7 инструментов:
• *Trivy* — CVE, мисконфигурации, секреты
• *Syft* — SBOM \\(перечень компонентов\\)
• *Dockle* — CIS Docker Benchmark
• *OSV\\-Scanner* — база Google OSV
• *Dive* — эффективность слоёв
• *TruffleHog* — утечки токенов
• *Cosign* — проверка подписи образа

📚 Дипломный проект, 2026\
"""


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer(
        _WELCOME,
        reply_markup=_webapp_keyboard(),
        parse_mode="MarkdownV2",
    )


@router.message(Command("open"))
async def cmd_open(message: Message) -> None:
    await message.answer(
        "🌐 Открывай веб\\-интерфейс MDMScan:",
        reply_markup=_webapp_keyboard(),
        parse_mode="MarkdownV2",
    )


@router.message(Command("about"))
async def cmd_about(message: Message) -> None:
    await message.answer(
        _ABOUT,
        reply_markup=_webapp_keyboard(),
        parse_mode="MarkdownV2",
    )


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    help_text = (
        "📖 *Команды:*\n\n"
        "/start — приветствие и кнопка открытия\n"
        "/open — открыть веб\\-интерфейс\n"
        "/about — о проекте\n"
        "/help — эта справка\n\n"
        "Бот открывает полный веб\\-интерфейс MDMScan\\.\n"
        "Для работы как Telegram Mini App требуется HTTPS\\."
    )
    await message.answer(
        help_text,
        reply_markup=_webapp_keyboard(),
        parse_mode="MarkdownV2",
    )


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    session = AiohttpSession(proxy=settings.proxy_url) if settings.proxy_url else None
    bot = Bot(token=settings.bot_token, session=session)
    dp = Dispatcher()
    dp.include_router(router)

    await bot.set_my_commands(
        [
            BotCommand(command="open", description="Открыть веб-интерфейс"),
            BotCommand(command="about", description="О проекте"),
            BotCommand(command="help", description="Справка"),
        ]
    )
    await bot.delete_webhook(drop_pending_updates=True)
    log.info("MDMScan mini-app bot started (web_url=%s)", settings.web_url)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
