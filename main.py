import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

from utils.config import BOT_TOKEN
from database.db import init_db
from handlers import start, donation, request, volunteer, items, stats, admin

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def main():
    await init_db()
    logger.info("Ma'lumotlar bazasi tayyor")

    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher(storage=MemoryStorage())

    # admin birinchi bo'lishi kerak
    dp.include_router(admin.router)
    dp.include_router(start.router)
    dp.include_router(donation.router)
    dp.include_router(request.router)
    dp.include_router(volunteer.router)
    dp.include_router(items.router)
    dp.include_router(stats.router)

    logger.info("EcoUlash boti ishga tushmoqda...")
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
