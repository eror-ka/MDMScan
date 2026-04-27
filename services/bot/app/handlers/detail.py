from __future__ import annotations

import logging

from aiogram import Router
from aiogram.types import CallbackQuery

from app.api_client import delete_scan, get_scan
from app.keyboards import delete_confirm_keyboard, main_keyboard, scan_detail_keyboard
from app.utils import format_scan_detail

log = logging.getLogger(__name__)
router = Router()


@router.callback_query(lambda c: c.data and c.data.startswith("sd:"))
async def cb_scan_detail(callback: CallbackQuery) -> None:
    scan_id = callback.data.removeprefix("sd:")
    try:
        scan = await get_scan(scan_id)
    except Exception:
        await callback.answer("Ошибка API", show_alert=True)
        return
    if not scan:
        await callback.answer("Скан не найден", show_alert=True)
        return
    text = format_scan_detail(scan)
    try:
        await callback.message.edit_text(
            text,
            parse_mode="MarkdownV2",
            reply_markup=scan_detail_keyboard(scan_id),
        )
    except Exception:
        await callback.message.answer(
            text,
            parse_mode="MarkdownV2",
            reply_markup=scan_detail_keyboard(scan_id),
        )
    await callback.answer()


@router.callback_query(lambda c: c.data and c.data.startswith("del_conf:"))
async def cb_delete_confirm(callback: CallbackQuery) -> None:
    scan_id = callback.data.removeprefix("del_conf:")
    try:
        scan = await get_scan(scan_id)
    except Exception:
        await callback.answer("Ошибка API", show_alert=True)
        return
    image = scan["image_ref"] if scan else f"{scan_id[:8]}…"
    await callback.message.edit_text(
        f"🗑 *Удалить скан?*\n\n📦 `{image}`\n\nЭто действие нельзя отменить\\.",
        parse_mode="MarkdownV2",
        reply_markup=delete_confirm_keyboard(scan_id),
    )
    await callback.answer()


@router.callback_query(lambda c: c.data and c.data.startswith("del_ok:"))
async def cb_delete_ok(callback: CallbackQuery) -> None:
    scan_id = callback.data.removeprefix("del_ok:")
    try:
        await delete_scan(scan_id)
    except Exception:
        await callback.answer("Ошибка при удалении", show_alert=True)
        return
    await callback.message.edit_text(
        "✅ *Скан удалён\\.*\n\nВернись в историю или запусти новое сканирование\\.",
        parse_mode="MarkdownV2",
        reply_markup=main_keyboard(),
    )
    await callback.answer("Удалено ✓")
