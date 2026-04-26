from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Router
from aiogram.filters import Command, StateFilter
from aiogram.filters.command import CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from app.api_client import get_findings, get_scan, submit_scan
from app.utils import format_scan_result

log = logging.getLogger(__name__)
router = Router()


class ScanState(StatesGroup):
    waiting_image = State()


@router.message(Command("scan"))
async def cmd_scan(
    message: Message,
    command: CommandObject,
    state: FSMContext,
) -> None:
    image = (command.args or "").strip()
    if not image:
        await state.set_state(ScanState.waiting_image)
        await message.answer(
            "📦 Введи имя Docker\\-образа:\n\nНапример: `alpine:latest`",
            parse_mode="MarkdownV2",
        )
        return
    await _start_scan(message, image, state)


@router.message(StateFilter(ScanState.waiting_image))
async def got_image(message: Message, state: FSMContext) -> None:
    await state.clear()
    await _start_scan(message, (message.text or "").strip(), state)


async def _start_scan(message: Message, image: str, state: FSMContext) -> None:
    if not image:
        await message.answer(
            "❌ Имя образа не может быть пустым\\.", parse_mode="MarkdownV2"
        )
        return
    try:
        data = await submit_scan(image)
    except Exception:
        await message.answer(
            "❌ Не удалось запустить сканирование\\. Проверь имя образа\\.",
            parse_mode="MarkdownV2",
        )
        return

    scan_id = data["scan_id"]
    await message.answer(
        f"🔍 *Сканирование запущено*\n\n"
        f"📦 Образ: `{image}`\n"
        f"🆔 ID: `{scan_id}`\n\n"
        f"⏳ Уведомлю автоматически когда завершится\\.\\.\\.",
        parse_mode="MarkdownV2",
    )
    bot = message.bot
    assert bot is not None
    asyncio.create_task(_poll(bot, message.chat.id, scan_id))


async def _poll(bot: Bot, chat_id: int, scan_id: str) -> None:
    for _ in range(72):  # max 6 минут
        await asyncio.sleep(5)
        try:
            scan = await get_scan(scan_id)
        except Exception:
            continue
        if scan and scan["status"] in ("done", "failed"):
            try:
                findings = await get_findings(scan_id)
            except Exception:
                findings = {"total": 0, "items": []}
            text = format_scan_result(scan, findings)
            await bot.send_message(chat_id, text, parse_mode="MarkdownV2")
            return
    short = scan_id[:8]
    await bot.send_message(
        chat_id,
        f"⏰ Превышено время ожидания для скана `{short}…`",
        parse_mode="MarkdownV2",
    )


@router.callback_query(lambda c: c.data and c.data.startswith("status_"))
async def cb_status(callback: CallbackQuery) -> None:
    scan_id = (callback.data or "").removeprefix("status_")
    try:
        scan = await get_scan(scan_id)
    except Exception:
        await callback.answer("Ошибка запроса", show_alert=True)
        return
    if not scan:
        await callback.answer("Скан не найден", show_alert=True)
        return
    await callback.message.answer(
        f"Статус: *{scan['status']}*, находок: {scan['findings_count']}",
        parse_mode="Markdown",
    )
    await callback.answer()
