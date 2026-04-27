from __future__ import annotations

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

FINDINGS_PAGE_SIZE = 5
HISTORY_PAGE_SIZE = 5

SEVERITIES = [
    ("CRITICAL", "🔴 CRITICAL"),
    ("HIGH", "🟠 HIGH"),
    ("MEDIUM", "🟡 MEDIUM"),
    ("LOW", "🔵 LOW"),
    ("INFO", "⚪ INFO"),
]

CATEGORIES = [
    ("vuln", "🐛 Уязвимости"),
    ("secret", "🔑 Секреты"),
    ("misconfig", "⚙️ Мисконфиги"),
    ("hygiene", "🧹 Гигиена"),
    ("supply_chain", "🔗 Supply Chain"),
]

STATUS_EMOJI_KB: dict[str, str] = {
    "done": "✅",
    "running": "⏳",
    "pending": "🕐",
    "failed": "❌",
}


def main_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🔍 Новый скан", callback_data="scan_new")
    builder.button(text="📋 История сканов", callback_data="hist_p:0")
    builder.button(text="ℹ️ О проекте", callback_data="menu_about")
    builder.button(text="❓ Справка", callback_data="menu_help")
    builder.adjust(2)
    return builder.as_markup()


def scan_running_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🏠 Меню", callback_data="menu")
    return builder.as_markup()


def scan_done_keyboard(scan_id: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="📊 Находки", callback_data=f"fn:{scan_id}")
    builder.button(text="📥 JSON", callback_data=f"json_rep:{scan_id}")
    builder.button(text="📄 PDF", callback_data=f"pdf_rep:{scan_id}")
    builder.button(text="🗑 Удалить", callback_data=f"del_conf:{scan_id}")
    builder.button(text="🏠 Меню", callback_data="menu")
    builder.adjust(2, 2, 1)
    return builder.as_markup()


def history_keyboard(
    scans: list,
    page: int,
    has_more: bool,
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for scan in scans:
        emoji = STATUS_EMOJI_KB.get(scan["status"], "❓")
        short_id = scan["scan_id"][:8]
        image = scan["image_ref"]
        if len(image) > 22:
            image = image[:19] + "…"
        label = f"{emoji} {image} [{short_id}]"
        builder.button(text=label, callback_data=f"sd:{scan['scan_id']}")
    builder.adjust(1)

    nav = InlineKeyboardBuilder()
    if page > 0:
        nav.button(text="⬅ Назад", callback_data=f"hist_p:{page - 1}")
    if has_more:
        nav.button(text="Вперёд ➡", callback_data=f"hist_p:{page + 1}")
    nav.adjust(2)

    bottom = InlineKeyboardBuilder()
    bottom.button(text="🏠 Меню", callback_data="menu")

    builder.attach(nav)
    builder.attach(bottom)
    return builder.as_markup()


def scan_detail_keyboard(scan_id: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="📊 Находки", callback_data=f"fn:{scan_id}")
    builder.button(text="📥 JSON", callback_data=f"json_rep:{scan_id}")
    builder.button(text="📄 PDF", callback_data=f"pdf_rep:{scan_id}")
    builder.button(text="🗑 Удалить", callback_data=f"del_conf:{scan_id}")
    builder.button(text="📋 История", callback_data="hist_p:0")
    builder.button(text="🏠 Меню", callback_data="menu")
    builder.adjust(3, 1, 2)
    return builder.as_markup()


def findings_filter_keyboard(scan_id: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for sev_key, sev_label in SEVERITIES:
        builder.button(
            text=sev_label,
            callback_data=f"fnp:{scan_id}:s_{sev_key}:0",
        )
    builder.button(text="📂 По категории", callback_data=f"fn_cat:{scan_id}")
    builder.button(text="📋 Все находки", callback_data=f"fnp:{scan_id}:all:0")
    builder.button(text="🔙 К скану", callback_data=f"sd:{scan_id}")
    builder.adjust(2, 2, 1, 1, 1)
    return builder.as_markup()


def findings_category_keyboard(scan_id: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for cat_key, cat_label in CATEGORIES:
        builder.button(
            text=cat_label,
            callback_data=f"fnp:{scan_id}:c_{cat_key}:0",
        )
    builder.button(text="🔙 Назад", callback_data=f"fn:{scan_id}")
    builder.adjust(2, 2, 1, 1)
    return builder.as_markup()


def findings_list_keyboard(
    scan_id: str,
    filter_key: str,
    page: int,
    total_pages: int,
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    nav_row: list[tuple[str, str]] = []
    if page > 0:
        nav_row.append(("⬅", f"fnp:{scan_id}:{filter_key}:{page - 1}"))
    if page < total_pages - 1:
        nav_row.append(("➡", f"fnp:{scan_id}:{filter_key}:{page + 1}"))
    for label, cb in nav_row:
        builder.button(text=label, callback_data=cb)
    if nav_row:
        builder.adjust(len(nav_row))

    ctrl = InlineKeyboardBuilder()
    ctrl.button(text="🔍 Фильтры", callback_data=f"fn:{scan_id}")
    ctrl.button(text="🔙 К скану", callback_data=f"sd:{scan_id}")
    ctrl.adjust(2)
    builder.attach(ctrl)
    return builder.as_markup()


def delete_confirm_keyboard(scan_id: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Да, удалить", callback_data=f"del_ok:{scan_id}")
    builder.button(text="❌ Отмена", callback_data=f"sd:{scan_id}")
    builder.adjust(2)
    return builder.as_markup()
