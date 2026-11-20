from aiogram import Router, F
from aiogram.types import Message, Contact
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database.db import add_user, get_user, set_user_phone, log_event
from keyboards.main_kb import main_menu, phone_keyboard
from utils.config import ADMIN_IDS

router = Router()


class RegisterForm(StatesGroup):
    phone = State()


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
📱 Telefon: +998 XX XXX XX XX
🌐 Vebsayt: ecoulash.uz

👨‍💼 Admin: @detpolm_beep
"""


@router.message(CommandStart())
async def start_handler(message: Message, state: FSMContext):
    user = message.from_user
    await add_user(user.id, user.username or "", user.full_name or "")
    await log_event("start", user.id)

    # Foydalanuvchi bazada bormi va telefoni bormi tekshiramiz
    db_user = await get_user(user.id)

    # Telefon raqami yo'q bo'lsa — register qilamiz
    if not db_user or not db_user[4]:
        await state.set_state(RegisterForm.phone)
        await message.answer(
            f"🌿 Assalomu alaykum, <b>{user.full_name}</b>!\n\n"
            f"EcoUlash botiga xush kelibsiz!\n\n"
            f"Davom etish uchun telefon raqamingizni ulashing 👇",
            reply_markup=phone_keyboard()
        )
        return

    # Ro'yxatdan o'tgan — asosiy menyuni ko'rsatamiz
    await show_main_menu(message)


async def show_main_menu(message: Message):
    user = message.from_user
    is_admin = user.id in ADMIN_IDS

    welcome_text = (
        f"🌿 Xush kelibsiz, <b>{user.full_name}</b>!\n\n"
        f"Quyidagi menyudan birini tanlang 👇"
    )

    await message.answer(welcome_text, reply_markup=main_menu())

    if is_admin:
        from keyboards.main_kb import admin_menu
        await message.answer(
            "👑 <b>Admin panel:</b>",
            reply_markup=admin_menu()
        )


@router.message(RegisterForm.phone, F.contact)
async def register_phone_contact(message: Message, state: FSMContext):
    contact: Contact = message.contact
    phone = contact.phone_number

    await set_user_phone(message.from_user.id, phone)
    await state.clear()
    await log_event("registered", message.from_user.id, phone)

    await message.answer(
        f"✅ <b>Ro'yxatdan o'tdingiz!</b>\n\n"
        f"📱 Telefon: <b>{phone}</b>\n\n"
        f"Endi botdan to'liq foydalanishingiz mumkin! 🎉",
        reply_markup=main_menu()
    )

    await show_main_menu(message)


@router.message(RegisterForm.phone, F.text)
async def register_phone_text(message: Message, state: FSMContext):
    # Tugma orqali yubormasdan matn yozgan bo'lsa
    if message.text == "⬅️ Orqaga":
        await state.clear()
        await show_main_menu(message)
        return

    await message.answer(
        "📱 Iltimos, quyidagi tugmani bosib telefon raqamingizni ulashing:",
        reply_markup=phone_keyboard()
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
