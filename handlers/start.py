from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart, Command

from database.db import add_user, log_event
from keyboards.main_kb import main_menu
from utils.config import ADMIN_IDS

router = Router()

ABOUT_TEXT = """
🌿 <b>EcoUlash haqida</b>

EcoUlash — ekologik barqarorlik va ijtimoiy mas'uliyatni birlashtiruvchi innovatsion loyiha.

<b>Biz nima qilamiz?</b>
♻️ Foydalanilmayotgan buyumlarni yig'amiz
🤲 Ehtiyojmand oilalarga yetkazamiz
👷 Yoshlar uchun ish o'rinlari yaratamiz
🌱 Ekologik madaniyatni rivojlantiramiz

<b>Bizning shiormiz:</b>
<i>"Bir buyum — ikki karra foyda!
Tabiatga foyda, insonga yordam."</i>

🌍 EcoUlash — buyumlarga ikkinchi hayot, insonlarga yangi imkoniyat!
"""

CONTACT_TEXT = """
📞 <b>Aloqa</b>

Savollaringiz bo'lsa, biz bilan bog'laning:

📧 Email: ecoulash@gmail.com
📱 Telefon: +998 93 155 1008
🌐 Vebsayt: ecoulash.uz

👨‍💼 Admin: @Dilraboxon8
"""


@router.message(CommandStart())
async def start_handler(message: Message):
    user = message.from_user
    await add_user(user.id, user.username or "", user.full_name or "")
    await log_event("start", user.id)

    is_admin = user.id in ADMIN_IDS

    welcome_text = (
        f"🌿 Assalomu alaykum, <b>{user.full_name}</b>!\n\n"
        f"EcoUlash botiga xush kelibsiz!\n\n"
        f"Bu bot orqali siz:\n"
        f"♻️ Buyum ehson qilishingiz\n"
        f"🤲 Yordam so'rashingiz\n"
        f"📦 Mavjud buyumlarni ko'rishingiz\n"
        f"🙋 Ko'ngilli bo'lishingiz mumkin!\n\n"
        f"Quyidagi menyudan birini tanlang 👇"
    )

    await message.answer(welcome_text, reply_markup=main_menu())

    if is_admin:
        from keyboards.main_kb import admin_menu
        await message.answer(
            "👑 <b>Admin paneliga xush kelibsiz!</b>\n"
            "Qo'shimcha admin buyruqlari:",
            reply_markup=admin_menu()
        )


@router.message(F.text == "ℹ️ Loyiha haqida")
async def about_handler(message: Message):
    await log_event("about", message.from_user.id)
    await message.answer(ABOUT_TEXT, reply_markup=main_menu())


@router.message(F.text == "📞 Aloqa")
async def contact_handler(message: Message):
    await log_event("contact", message.from_user.id)
    await message.answer(CONTACT_TEXT, reply_markup=main_menu())


@router.message(Command("help"))
async def help_handler(message: Message):
    help_text = (
        "🆘 <b>Yordam</b>\n\n"
        "/start — Botni qayta ishga tushirish\n"
        "/help — Yordam\n"
        "/stats — Statistika\n\n"
        "<b>Menyular:</b>\n"
        "♻️ <b>Ehson qilish</b> — Buyum ehson qiling\n"
        "🤲 <b>Yordam so'rash</b> — Buyum so'rang\n"
        "📦 <b>Mavjud buyumlar</b> — Ko'ring\n"
        "🙋 <b>Ko'ngilli bo'lish</b> — Ro'yxatdan o'ting\n"
    )
    await message.answer(help_text, reply_markup=main_menu())
