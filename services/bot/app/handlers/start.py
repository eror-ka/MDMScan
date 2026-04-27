from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, Message

from app.handlers.about import about_text
from app.keyboards import main_keyboard

router = Router()

WELCOME = (
    "👋 Добро пожаловать в *MDMScan*\\!\n\n"
    "Автоматическая оценка безопасности Docker\\-образов "
    "на базе 7 открытых сканеров\\.\n\n"
    "Что умеет бот:\n"
    "🔍 Запускать сканирование с live\\-статусом\n"
    "📊 Показывать находки — фильтр по severity и категории\n"
    "📥 JSON и 📄 PDF отчёты одной кнопкой\n"
    "🗑 Удалять результаты сканирований\n\n"
    "Выбери действие:"
)

HELP_TEXT = (
    "📖 *Доступные команды:*\n\n"
    "/scan \\<образ\\> — запустить сканирование\n"
    "/status \\<scan\\_id\\> — статус по ID\n"
    "/list — история сканирований\n"
    "/about — о проекте\n"
    "/help — эта справка\n\n"
    "*Через inline\\-кнопки:*\n"
    "🔍 Новый скан → введи имя образа, получи live\\-статус\n"
    "📋 История → список с пагинацией → детали скана\n"
    "  ↳ 📊 Находки → фильтр по severity / категории \\+ пагинация\n"
    "  ↳ 📥 JSON / 📄 PDF → отчёт файлом в чат\n"
    "  ↳ 🗑 Удалить → с подтверждением"
)


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer(WELCOME, reply_markup=main_keyboard(), parse_mode="MarkdownV2")


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer(HELP_TEXT, parse_mode="MarkdownV2")


@router.callback_query(lambda c: c.data == "menu")
async def cb_menu(callback: CallbackQuery) -> None:
    try:
        await callback.message.edit_text(
            WELCOME, parse_mode="MarkdownV2", reply_markup=main_keyboard()
        )
    except Exception:
        await callback.message.answer(
            WELCOME, parse_mode="MarkdownV2", reply_markup=main_keyboard()
        )
    await callback.answer()


@router.callback_query(lambda c: c.data == "menu_about")
async def cb_about(callback: CallbackQuery) -> None:
    await callback.message.answer(about_text(), parse_mode="MarkdownV2")
    await callback.answer()


@router.callback_query(lambda c: c.data == "menu_help")
async def cb_help(callback: CallbackQuery) -> None:
    await callback.message.answer(HELP_TEXT, parse_mode="MarkdownV2")
    await callback.answer()
