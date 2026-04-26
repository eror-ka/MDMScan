from __future__ import annotations

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def main_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🔍 Проверить образ", callback_data="menu_scan")
    builder.button(text="📋 История сканов", callback_data="menu_list")
    builder.button(text="ℹ️ О проекте", callback_data="menu_about")
    builder.button(text="❓ Справка", callback_data="menu_help")
    builder.adjust(2)
    return builder.as_markup()


def scan_done_keyboard(scan_id: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="🔄 Проверить статус",
        callback_data=f"status_{scan_id}",
    )
    return builder.as_markup()
