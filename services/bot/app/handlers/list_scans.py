from __future__ import annotations

import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from app.api_client import list_scans
from app.keyboards import HISTORY_PAGE_SIZE, history_keyboard

log = logging.getLogger(__name__)
router = Router()


async def _send_history(
    target: Message | CallbackQuery,
    page: int = 0,
) -> None:
    offset = page * HISTORY_PAGE_SIZE
    try:
        scans = await list_scans(limit=HISTORY_PAGE_SIZE + 1, offset=offset)
    except Exception:
        err = "❌ Ошибка при запросе к API\\."
        if isinstance(target, CallbackQuery):
            await target.answer(err, show_alert=True)
        else:
            await target.answer(err, parse_mode="MarkdownV2")
        return

    has_more = len(scans) > HISTORY_PAGE_SIZE
    scans = scans[:HISTORY_PAGE_SIZE]
    kb = history_keyboard(scans, page, has_more)

    if not scans:
        text = (
            "📭 Сканирований ещё не было\\."
            if page == 0
            else "📭 Больше сканирований нет\\."
        )
    else:
        text = (
            f"📋 *История сканирований* \\(стр\\. {page + 1}\\):\n"
            "Выбери скан для просмотра деталей:"
        )

    if isinstance(target, CallbackQuery):
        try:
            await target.message.edit_text(
                text, parse_mode="MarkdownV2", reply_markup=kb
            )
        except Exception:
            await target.message.answer(text, parse_mode="MarkdownV2", reply_markup=kb)
        await target.answer()
    else:
        await target.answer(text, parse_mode="MarkdownV2", reply_markup=kb)


@router.message(Command("list"))
async def cmd_list(message: Message) -> None:
    await _send_history(message, 0)


@router.callback_query(lambda c: c.data and c.data.startswith("hist_p:"))
async def cb_history_page(callback: CallbackQuery) -> None:
    page_str = callback.data.removeprefix("hist_p:")
    try:
        page = int(page_str)
    except ValueError:
        await callback.answer("Неверная страница", show_alert=True)
        return
    await _send_history(callback, max(0, page))
