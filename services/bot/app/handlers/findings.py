from __future__ import annotations

import logging

from aiogram import Router
from aiogram.types import CallbackQuery

from app.api_client import get_findings
from app.keyboards import (
    FINDINGS_PAGE_SIZE,
    findings_category_keyboard,
    findings_filter_keyboard,
    findings_list_keyboard,
)
from app.utils import CAT_LABELS, SEV_EMOJI, format_findings_page

log = logging.getLogger(__name__)
router = Router()


@router.callback_query(lambda c: c.data and c.data.startswith("fn:"))
async def cb_findings_menu(callback: CallbackQuery) -> None:
    scan_id = callback.data.removeprefix("fn:")
    await callback.message.edit_text(
        "📊 *Фильтр находок*\n\nВыбери фильтр для просмотра:",
        parse_mode="MarkdownV2",
        reply_markup=findings_filter_keyboard(scan_id),
    )
    await callback.answer()


@router.callback_query(lambda c: c.data and c.data.startswith("fn_cat:"))
async def cb_findings_category_menu(callback: CallbackQuery) -> None:
    scan_id = callback.data.removeprefix("fn_cat:")
    await callback.message.edit_text(
        "📂 *Фильтр по категории*\n\nВыбери категорию:",
        parse_mode="MarkdownV2",
        reply_markup=findings_category_keyboard(scan_id),
    )
    await callback.answer()


@router.callback_query(lambda c: c.data and c.data.startswith("fnp:"))
async def cb_findings_page(callback: CallbackQuery) -> None:
    # format: fnp:{uuid}:{filter_key}:{page}
    # filter_key: all | s_CRITICAL | s_HIGH | c_vuln | c_supply_chain | ...
    tail = callback.data.removeprefix("fnp:")
    parts = tail.split(":", 2)
    if len(parts) != 3:
        await callback.answer("Неверный формат", show_alert=True)
        return
    scan_id, filter_key, page_str = parts
    try:
        page = int(page_str)
    except ValueError:
        await callback.answer("Неверная страница", show_alert=True)
        return

    severity: str | None = None
    category: str | None = None
    filter_desc = "Все"

    if filter_key.startswith("s_"):
        severity = filter_key[2:]
        emoji = SEV_EMOJI.get(severity, "⬜")
        filter_desc = f"{emoji} {severity}"
    elif filter_key.startswith("c_"):
        category = filter_key[2:]
        filter_desc = CAT_LABELS.get(category, category)

    offset = page * FINDINGS_PAGE_SIZE
    try:
        findings = await get_findings(
            scan_id,
            severity=severity,
            category=category,
            limit=FINDINGS_PAGE_SIZE,
            offset=offset,
        )
    except Exception:
        await callback.answer("Ошибка при загрузке находок", show_alert=True)
        return

    total = findings.get("total", 0)
    total_pages = max(1, (total + FINDINGS_PAGE_SIZE - 1) // FINDINGS_PAGE_SIZE)
    text = format_findings_page(findings, filter_desc, page, FINDINGS_PAGE_SIZE)
    kb = findings_list_keyboard(scan_id, filter_key, page, total_pages)

    try:
        await callback.message.edit_text(text, parse_mode="MarkdownV2", reply_markup=kb)
    except Exception as exc:
        log.warning("findings edit_text failed: %s", exc)
        await callback.answer("Ошибка отображения", show_alert=True)
        return
    await callback.answer()
