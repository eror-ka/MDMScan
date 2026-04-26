from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.api_client import list_scans
from app.utils import format_scans_list

router = Router()


async def send_list(message: Message) -> None:
    try:
        scans = await list_scans(limit=5)
    except Exception:
        await message.answer("❌ Ошибка при запросе к API\\.", parse_mode="MarkdownV2")
        return
    await message.answer(format_scans_list(scans), parse_mode="MarkdownV2")


@router.message(Command("list"))
async def cmd_list(message: Message) -> None:
    await send_list(message)
