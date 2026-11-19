from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command

from database.db import get_stats, log_event
from keyboards.main_kb import main_menu

router = Router()


@router.message(F.text == "📊 Statistika")
@router.message(Command("stats"))
async def stats_handler(message: Message):
    await log_event("view_stats", message.from_user.id)
    stats = await get_stats()

    text = (
        "📊 <b>EcoUlash Statistikasi</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"👥 Jami foydalanuvchilar: <b>{stats['total_users']}</b>\n"
        f"🆕 Bugun qo'shilganlar: <b>{stats['new_users_today']}</b>\n\n"
        f"♻️ Jami ehsonlar: <b>{stats['total_donations']}</b>\n"
        f"⏳ Kutayotgan ehsonlar: <b>{stats['pending_donations']}</b>\n\n"
        f"🤲 Jami so'rovlar: <b>{stats['total_requests']}</b>\n"
        f"⏳ Kutayotgan so'rovlar: <b>{stats['pending_requests']}</b>\n\n"
        f"🙋 Ko'ngillilar: <b>{stats['total_volunteers']}</b>\n\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "🌿 <i>EcoUlash — buyumlarga ikkinchi hayot!</i>"
    )

    await message.answer(text, reply_markup=main_menu())
