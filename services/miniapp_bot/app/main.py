from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import BotCommand, InlineKeyboardMarkup, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.config import settings

log = logging.getLogger(__name__)
router = Router()


def _open_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🌐 Открыть MDMScan", url=settings.web_url)
    return builder.as_markup()


_WELCOME = (
    "👋 *MDMScan Web*\n\n"
    "Нажми кнопку ниже, чтобы открыть веб\\-интерфейс "
    "системы безопасности Docker\\-образов:"
)


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer(
        _WELCOME,
        reply_markup=_open_keyboard(),
        parse_mode="MarkdownV2",
    )


@router.message(Command("open"))
async def cmd_open(message: Message) -> None:
    await message.answer(
        "🌐 Открывай веб\\-интерфейс MDMScan:",
        reply_markup=_open_keyboard(),
        parse_mode="MarkdownV2",
    )


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    bot = Bot(token=settings.bot_token)
    dp = Dispatcher()
    dp.include_router(router)

    await bot.set_my_commands(
        [BotCommand(command="open", description="Открыть веб-интерфейс")]
    )
    await bot.delete_webhook(drop_pending_updates=True)
    log.info("MDMScan mini-app bot started")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
