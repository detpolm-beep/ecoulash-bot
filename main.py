import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

from utils.config import BOT_TOKEN
from database.db import init_db
from handlers import start, donation, request, volunteer, items, stats, admin

# Logging sozlash
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("bot.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


async def main():
    # Ma'lumotlar bazasini ishga tushirish
    await init_db()
    logger.info("✅ Ma'lumotlar bazasi tayyor")

    # Bot va Dispatcher
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher(storage=MemoryStorage())

    # Handlerlarni ro'yxatdan o'tkazish (tartib muhim)
    dp.include_router(admin.router)
    dp.include_router(start.router)
    dp.include_router(donation.router)
    dp.include_router(request.router)
    dp.include_router(volunteer.router)
    dp.include_router(items.router)
    dp.include_router(stats.router)

    # Botni ishga tushirish
    logger.info("🚀 EcoUlash boti ishga tushmoqda...")
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        logger.info("⛔ Bot to'xtatildi")


if __name__ == "__main__":
    asyncio.run(main())
