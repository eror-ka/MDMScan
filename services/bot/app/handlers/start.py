from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, Message

from app.handlers.about import about_text
from app.handlers.list_scans import send_list
from app.keyboards import main_keyboard

router = Router()

WELCOME = (
    "👋 Добро пожаловать в *MDMScan*\\!\n\n"
    "Система автоматической оценки безопасности Docker\\-образов\\.\n\n"
    "Выбери действие в меню ниже или используй команды:"
)

HELP_TEXT = (
    "📖 *Доступные команды:*\n\n"
    "/scan \\<образ\\> — запустить сканирование\n"
    "/status \\<scan\\_id\\> — статус по ID\n"
    "/list — последние 5 сканирований\n"
    "/about — о проекте\n"
    "/help — эта справка"
)


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer(
        WELCOME,
        reply_markup=main_keyboard(),
        parse_mode="MarkdownV2",
    )


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer(HELP_TEXT, parse_mode="MarkdownV2")


@router.callback_query(lambda c: c.data == "menu_scan")
async def cb_scan(callback: CallbackQuery) -> None:
    await callback.message.answer(
        "📦 Отправь команду:\n\n`/scan alpine:latest`\n\nили `/scan nginx:1.25`",
        parse_mode="MarkdownV2",
    )
    await callback.answer()


@router.callback_query(lambda c: c.data == "menu_list")
async def cb_list(callback: CallbackQuery) -> None:
    await send_list(callback.message)
    await callback.answer()


@router.callback_query(lambda c: c.data == "menu_about")
async def cb_about(callback: CallbackQuery) -> None:
    await callback.message.answer(about_text(), parse_mode="MarkdownV2")
    await callback.answer()


@router.callback_query(lambda c: c.data == "menu_help")
async def cb_help(callback: CallbackQuery) -> None:
    await callback.message.answer(HELP_TEXT, parse_mode="MarkdownV2")
    await callback.answer()
