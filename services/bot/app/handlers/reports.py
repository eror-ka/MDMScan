from __future__ import annotations

import logging

from aiogram import Router
from aiogram.types import BufferedInputFile, CallbackQuery

from app.api_client import get_findings, get_scan
from app.utils import generate_json_report, generate_pdf_report

log = logging.getLogger(__name__)
router = Router()


@router.callback_query(lambda c: c.data and c.data.startswith("json_rep:"))
async def cb_json_report(callback: CallbackQuery) -> None:
    scan_id = callback.data.removeprefix("json_rep:")
    await callback.answer("Генерирую JSON отчёт…")
    try:
        scan = await get_scan(scan_id)
        findings = await get_findings(scan_id, limit=500)
    except Exception:
        await callback.message.answer(
            "❌ Ошибка при загрузке данных\\.", parse_mode="MarkdownV2"
        )
        return
    if not scan:
        await callback.message.answer("❌ Скан не найден\\.", parse_mode="MarkdownV2")
        return
    json_str = generate_json_report(scan, findings)
    file_name = f"mdmscan_{scan_id[:8]}.json"
    await callback.message.answer_document(
        BufferedInputFile(json_str.encode("utf-8"), filename=file_name),
        caption=f"📥 JSON отчёт: `{scan['image_ref']}`",
        parse_mode="MarkdownV2",
    )


@router.callback_query(lambda c: c.data and c.data.startswith("pdf_rep:"))
async def cb_pdf_report(callback: CallbackQuery) -> None:
    scan_id = callback.data.removeprefix("pdf_rep:")
    await callback.answer("Генерирую PDF отчёт…")
    try:
        scan = await get_scan(scan_id)
        findings = await get_findings(scan_id, limit=500)
    except Exception:
        await callback.message.answer(
            "❌ Ошибка при загрузке данных\\.", parse_mode="MarkdownV2"
        )
        return
    if not scan:
        await callback.message.answer("❌ Скан не найден\\.", parse_mode="MarkdownV2")
        return
    try:
        pdf_bytes = generate_pdf_report(scan, findings)
    except Exception as exc:
        log.error("PDF generation failed: %s", exc)
        await callback.message.answer(
            "❌ Ошибка генерации PDF\\.", parse_mode="MarkdownV2"
        )
        return
    file_name = f"mdmscan_{scan_id[:8]}.pdf"
    await callback.message.answer_document(
        BufferedInputFile(pdf_bytes, filename=file_name),
        caption=f"📄 PDF отчёт: `{scan['image_ref']}`",
        parse_mode="MarkdownV2",
    )
