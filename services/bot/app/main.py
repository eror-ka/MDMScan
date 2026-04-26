from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand

from app.config import settings
from app.handlers import about, list_scans, scan, start, status

log = logging.getLogger(__name__)


async def _set_commands(bot: Bot) -> None:
    await bot.set_my_commands(
        [
            BotCommand(command="scan", description="Проверить Docker-образ"),
            BotCommand(command="status", description="Статус сканирования"),
            BotCommand(command="list", description="Последние сканирования"),
            BotCommand(command="about", description="О проекте"),
            BotCommand(command="help", description="Справка"),
        ]
    )


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    bot = Bot(token=settings.bot_token)
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(start.router)
    dp.include_router(scan.router)
    dp.include_router(status.router)
    dp.include_router(list_scans.router)
    dp.include_router(about.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await _set_commands(bot)
    log.info("MDMScan bot started")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
