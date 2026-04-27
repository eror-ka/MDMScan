from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command
from aiogram.filters.command import CommandObject
from aiogram.types import Message

from app.api_client import get_scan
from app.keyboards import scan_detail_keyboard
from app.utils import format_scan_detail

router = Router()


@router.message(Command("status"))
async def cmd_status(message: Message, command: CommandObject) -> None:
    scan_id = (command.args or "").strip()
    if not scan_id:
        await message.answer(
            "Укажи ID скана: `/status <scan_id>`",
            parse_mode="MarkdownV2",
        )
        return

    try:
        scan = await get_scan(scan_id)
    except Exception:
        await message.answer("❌ Ошибка при запросе к API\\.", parse_mode="MarkdownV2")
        return

    if scan is None:
        await message.answer(
            f"❌ Скан `{scan_id[:8]}…` не найден\\.",
            parse_mode="MarkdownV2",
        )
        return

    await message.answer(
        format_scan_detail(scan),
        parse_mode="MarkdownV2",
        reply_markup=scan_detail_keyboard(scan_id),
    )
