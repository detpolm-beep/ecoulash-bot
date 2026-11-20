from aiogram import Router, F
from aiogram.types import Message, Contact
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database.db import add_user, get_user, update_user_info, log_event, get_admin_ids
from keyboards.main_kb import main_menu, admin_menu, phone_keyboard, cancel_button
from utils.config import ADMIN_IDS

router = Router()


class RegisterForm(StatesGroup):
    first_name = State()
    last_name = State()
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

📱 Telefon: <b>+998 93 155 10 08</b>
👨‍💼 Telegram: <b>@dilraboxon8</b>
"""


async def is_admin(user_id: int) -> bool:
    if user_id in ADMIN_IDS:
        return True
    db_admins = await get_admin_ids()
    return user_id in db_admins


@router.message(CommandStart())
async def start_handler(message: Message, state: FSMContext):
    await state.clear()
    user = message.from_user
    await add_user(user.id, user.username or "", user.full_name or "")
    await log_event("start", user.id)

    db_user = await get_user(user.id)

    # Telefon yo'q bo'lsa register boshlaylik
    if not db_user or not db_user[6]:  # db_user[6] = phone
        await state.set_state(RegisterForm.first_name)
        await message.answer(
            f"🌿 Assalomu alaykum!\n\n"
            f"EcoUlash botiga xush kelibsiz!\n\n"
            f"Ro'yxatdan o'tish uchun ismingizni kiriting 👇",
            reply_markup=cancel_button()
        )
        return

    await show_main_menu(message)


# --- REGISTER JARAYONI ---

@router.message(RegisterForm.first_name)
async def register_first_name(message: Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("Botdan foydalanish uchun ro'yxatdan o'ting.", reply_markup=cancel_button())
        return

    await state.update_data(first_name=message.text)
    await state.set_state(RegisterForm.last_name)
    await message.answer(
        f"✅ Ism: <b>{message.text}</b>\n\nFamiliyangizni kiriting 👇",
        reply_markup=cancel_button()
    )


@router.message(RegisterForm.last_name)
async def register_last_name(message: Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await state.set_state(RegisterForm.first_name)
        await message.answer("Ismingizni kiriting 👇", reply_markup=cancel_button())
        return

    await state.update_data(last_name=message.text)
    await state.set_state(RegisterForm.phone)
    await message.answer(
        f"✅ Familiya: <b>{message.text}</b>\n\n"
        f"📱 Telefon raqamingizni ulashing 👇",
        reply_markup=phone_keyboard()
    )


@router.message(RegisterForm.phone, F.contact)
async def register_phone(message: Message, state: FSMContext):
    contact: Contact = message.contact
    phone = contact.phone_number
    data = await state.get_data()

    first_name = data.get("first_name", "")
    last_name = data.get("last_name", "")

    await update_user_info(message.from_user.id, first_name, last_name, phone)
    await log_event("registered", message.from_user.id)
    await state.clear()

    await message.answer(
        f"🎉 <b>Ro'yxatdan muvaffaqiyatli o'tdingiz!</b>\n\n"
        f"👤 Ism: <b>{first_name}</b>\n"
        f"👤 Familiya: <b>{last_name}</b>\n"
        f"📱 Telefon: <b>{phone}</b>\n\n"
        f"Xush kelibsiz! 🌿",
        reply_markup=main_menu()
    )


@router.message(RegisterForm.phone)
async def register_phone_text(message: Message, state: FSMContext):
    await message.answer(
        "📱 Iltimos, tugmani bosib telefon raqamingizni ulashing:",
        reply_markup=phone_keyboard()
    )


# --- ASOSIY MENYU ---

async def show_main_menu(message: Message):
    user = message.from_user
    admin = await is_admin(user.id)

    await message.answer(
        f"🌿 Xush kelibsiz, <b>{user.full_name}</b>!\n\n"
        f"Quyidagi menyudan birini tanlang 👇",
        reply_markup=main_menu()
    )

    if admin:
        await message.answer(
            "👑 <b>Admin panel:</b>",
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
        "/help — Yordam\n\n"
        "<b>Menyular:</b>\n"
        "♻️ Ehson qilish\n"
        "🤲 Yordam so'rash\n"
        "📦 Mavjud buyumlar\n"
        "🙋 Ko'ngilli bo'lish\n"
        "📊 Statistika\n"
    )
    await message.answer(help_text, reply_markup=main_menu())
