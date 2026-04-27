from __future__ import annotations

import asyncio
import logging
import time

from aiogram import Bot, Router
from aiogram.filters import Command, StateFilter
from aiogram.filters.command import CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from app.api_client import get_findings, get_scan, submit_scan
from app.keyboards import main_keyboard, scan_done_keyboard, scan_running_keyboard
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


@router.callback_query(lambda c: c.data == "scan_new")
async def cb_scan_new(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(ScanState.waiting_image)
    await callback.message.answer(
        "📦 Введи имя Docker\\-образа для сканирования:\n\nНапример: `alpine:latest`",
        parse_mode="MarkdownV2",
    )
    await callback.answer()


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
    status_msg = await message.answer(
        f"🔍 *Сканирование запущено*\n\n"
        f"📦 `{image}`\n"
        f"🆔 `{scan_id[:8]}…`\n\n"
        f"⏳ Идёт проверка\\.\\.\\. \\(0с\\)",
        parse_mode="MarkdownV2",
        reply_markup=scan_running_keyboard(),
    )
    bot = message.bot
    assert bot is not None
    asyncio.create_task(
        _poll(bot, message.chat.id, status_msg.message_id, scan_id, image)
    )


async def _poll(
    bot: Bot,
    chat_id: int,
    msg_id: int,
    scan_id: str,
    image: str,
) -> None:
    start_time = time.time()
    for _ in range(72):  # max 6 минут
        await asyncio.sleep(5)
        elapsed = int(time.time() - start_time)
        try:
            scan = await get_scan(scan_id)
        except Exception:
            continue
        if scan and scan["status"] in ("done", "failed"):
            try:
                findings = await get_findings(scan_id, limit=500)
            except Exception:
                findings = {"total": 0, "items": []}
            text = format_scan_result(scan, findings)
            try:
                await bot.edit_message_text(
                    text,
                    chat_id=chat_id,
                    message_id=msg_id,
                    parse_mode="MarkdownV2",
                    reply_markup=scan_done_keyboard(scan_id),
                )
            except Exception:
                await bot.send_message(
                    chat_id,
                    text,
                    parse_mode="MarkdownV2",
                    reply_markup=scan_done_keyboard(scan_id),
                )
            return
        # live update every tick
        try:
            await bot.edit_message_text(
                f"🔍 *Сканирование*\n\n"
                f"📦 `{image}`\n"
                f"🆔 `{scan_id[:8]}…`\n\n"
                f"⏳ Идёт проверка\\.\\.\\. \\({elapsed}с\\)",
                chat_id=chat_id,
                message_id=msg_id,
                parse_mode="MarkdownV2",
                reply_markup=scan_running_keyboard(),
            )
        except Exception:
            pass

    # timeout
    try:
        await bot.edit_message_text(
            f"⏰ Превышено время ожидания для скана `{scan_id[:8]}…`",
            chat_id=chat_id,
            message_id=msg_id,
            parse_mode="MarkdownV2",
            reply_markup=main_keyboard(),
        )
    except Exception:
        await bot.send_message(
            chat_id,
            f"⏰ Превышено время ожидания для скана `{scan_id[:8]}…`",
            parse_mode="MarkdownV2",
        )
