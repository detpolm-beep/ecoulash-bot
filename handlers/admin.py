from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command
from aiogram import Bot

from database.db import (
    get_stats, get_all_users, get_all_active_user_ids,
    get_donations, get_requests, get_all_volunteers,
    get_all_admins, add_admin, remove_admin,
    get_admin_ids, log_event
)
from keyboards.main_kb import admin_menu, main_menu, broadcast_target_kb, confirm_kb
from utils.config import ADMIN_IDS

router = Router()


async def is_admin(user_id: int) -> bool:
    if user_id in ADMIN_IDS:
        return True
    db_admins = await get_admin_ids()
    return user_id in db_admins


class BroadcastForm(StatesGroup):
    target = State()
    message_text = State()
    confirm = State()


class AddAdminForm(StatesGroup):
    user_id = State()


class RemoveAdminForm(StatesGroup):
    user_id = State()


# ===== ADMIN PANEL =====
@router.message(Command("admin"))
async def admin_panel(message: Message):
    if not await is_admin(message.from_user.id):
        await message.answer("⛔ Ruxsat yo'q!")
        return

    stats = await get_stats()
    text = (
        "👑 <b>Admin Panel</b>\n\n"
        f"👥 Foydalanuvchilar: <b>{stats['total_users']}</b>\n"
        f"♻️ Ehsonlar: <b>{stats['total_donations']}</b>\n"
        f"🤲 So'rovlar: <b>{stats['total_requests']}</b>\n"
        f"🙋 Ko'ngillilar: <b>{stats['total_volunteers']}</b>\n"
    )
    await message.answer(text, reply_markup=admin_menu())


@router.message(F.text == "🏠 Asosiy menyu")
async def back_to_main(message: Message):
    from keyboards.main_kb import main_menu
    await message.answer("🏠 Asosiy menyu:", reply_markup=main_menu())


# ===== STATISTIKA =====
@router.message(F.text == "📊 Statistika")
async def admin_stats(message: Message):
    stats = await get_stats()
    text = (
        "📊 <b>Statistika</b>\n"
        "━━━━━━━━━━━━━━━━\n\n"
        f"👥 Jami foydalanuvchilar: <b>{stats['total_users']}</b>\n"
        f"🆕 Bugun: <b>{stats['new_users_today']}</b>\n\n"
        f"♻️ Jami ehsonlar: <b>{stats['total_donations']}</b>\n"
        f"⏳ Kutayotgan: <b>{stats['pending_donations']}</b>\n\n"
        f"🤲 Jami so'rovlar: <b>{stats['total_requests']}</b>\n"
        f"⏳ Kutayotgan: <b>{stats['pending_requests']}</b>\n\n"
        f"🙋 Ko'ngillilar: <b>{stats['total_volunteers']}</b>"
    )
    if await is_admin(message.from_user.id):
        await message.answer(text, reply_markup=admin_menu())
    else:
        await message.answer(text, reply_markup=main_menu())


# ===== FOYDALANUVCHILAR =====
@router.message(F.text == "👥 Foydalanuvchilar")
async def admin_users(message: Message):
    if not await is_admin(message.from_user.id):
        return

    users = await get_all_users()
    if not users:
        await message.answer("Foydalanuvchilar yo'q.", reply_markup=admin_menu())
        return

    text = f"👥 <b>Foydalanuvchilar ({len(users)} ta):</b>\n\n"
    for i, user in enumerate(users[:30], 1):
        user_id, username, full_name, phone = user
        uname = f"@{username}" if username else "—"
        phone_str = phone or "—"
        text += f"{i}. {full_name} | {uname} | {phone_str}\n"

    if len(users) > 30:
        text += f"\n<i>...va yana {len(users) - 30} ta</i>"

    await message.answer(text, reply_markup=admin_menu())


# ===== EHSONLAR =====
@router.message(F.text == "🎁 Ehsonlar")
async def admin_donations(message: Message):
    if not await is_admin(message.from_user.id):
        return

    donations = await get_donations()
    if not donations:
        await message.answer("Ehsonlar yo'q.", reply_markup=admin_menu())
        return

    text = f"♻️ <b>Ehsonlar ({len(donations)} ta):</b>\n\n"
    for i, d in enumerate(donations[:20], 1):
        text += (
            f"{i}. <b>{d[2]}</b> — {d[3]} dona\n"
            f"   👤 ID: <code>{d[1]}</code> | 📌 {d[5]}\n\n"
        )

    await message.answer(text, reply_markup=admin_menu())


# ===== SO'ROVLAR =====
@router.message(F.text == "📋 So'rovlar")
async def admin_requests(message: Message):
    if not await is_admin(message.from_user.id):
        return

    requests = await get_requests()
    if not requests:
        await message.answer("So'rovlar yo'q.", reply_markup=admin_menu())
        return

    text = f"🤲 <b>So'rovlar ({len(requests)} ta):</b>\n\n"
    for i, r in enumerate(requests[:20], 1):
        text += (
            f"{i}. <b>{r[2]}</b> — {r[3]} dona\n"
            f"   👤 ID: <code>{r[1]}</code> | 📌 {r[5]}\n\n"
        )

    await message.answer(text, reply_markup=admin_menu())


# ===== KO'NGILLILAR =====
@router.message(F.text == "🙋 Ko'ngillilar")
async def admin_volunteers(message: Message):
    if not await is_admin(message.from_user.id):
        return

    volunteers = await get_all_volunteers()
    if not volunteers:
        await message.answer("Ko'ngillilar yo'q.", reply_markup=admin_menu())
        return

    text = f"🙋 <b>Ko'ngillilar ({len(volunteers)} ta):</b>\n\n"
    for i, v in enumerate(volunteers, 1):
        user_id, full_name, phone, skills, availability = v
        noma_lum = "Noma'lum"
        text += (
            f"{i}. <b>{full_name or noma_lum}</b>\n"
            f"   📱 {phone or '—'}\n"
            f"   💪 {skills}\n"
            f"   🗓️ {availability}\n\n"
        )

    await message.answer(text, reply_markup=admin_menu())


# ===== ADMIN QO'SHISH =====
@router.message(F.text == "➕ Admin qo'shish")
async def add_admin_start(message: Message, state: FSMContext):
    if not await is_admin(message.from_user.id):
        return

    await state.set_state(AddAdminForm.user_id)
    await message.answer(
        "➕ <b>Yangi admin qo'shish</b>\n\n"
        "Yangi adminning Telegram ID sini kiriting:\n"
        "<i>(Foydalanuvchi @userinfobot ga /start yuborsa ID sini biladi)</i>",
        reply_markup=main_menu()
    )


@router.message(AddAdminForm.user_id)
async def add_admin_id(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("⚠️ Faqat raqam kiriting! Masalan: 123456789")
        return

    new_admin_id = int(message.text)
    await add_admin(new_admin_id, message.from_user.id)
    await state.clear()

    await message.answer(
        f"✅ <b>Admin qo'shildi!</b>\n\n"
        f"ID: <code>{new_admin_id}</code>\n\n"
        f"Endi u kishi /admin buyrug'i orqali admin panelga kira oladi.",
        reply_markup=admin_menu()
    )


# ===== ADMIN O'CHIRISH =====
@router.message(F.text == "➖ Admin o'chirish")
async def remove_admin_start(message: Message, state: FSMContext):
    if not await is_admin(message.from_user.id):
        return

    admins = await get_all_admins()
    if not admins:
        await message.answer("Adminlar yo'q.", reply_markup=admin_menu())
        return

    text = "👑 <b>Mavjud adminlar:</b>\n\n"
    for i, a in enumerate(admins, 1):
        user_id, full_name, username = a
        uname = f"@{username}" if username else "—"
        noma_lum = "Noma'lum"
        text += f"{i}. {full_name or noma_lum} ({uname}) — <code>{user_id}</code>\n"

    text += "\nO'chirish uchun admin ID sini kiriting:"

    await state.set_state(RemoveAdminForm.user_id)
    await message.answer(text, reply_markup=main_menu())


@router.message(RemoveAdminForm.user_id)
async def remove_admin_id(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("⚠️ Faqat raqam kiriting!")
        return

    admin_id = int(message.text)
    await remove_admin(admin_id)
    await state.clear()

    await message.answer(
        f"✅ Admin o'chirildi: <code>{admin_id}</code>",
        reply_markup=admin_menu()
    )


# ===== XABAR YUBORISH =====
@router.message(F.text == "📢 Xabar yuborish")
async def broadcast_start(message: Message, state: FSMContext):
    if not await is_admin(message.from_user.id):
        return

    await state.set_state(BroadcastForm.target)
    await message.answer(
        "📢 <b>Xabar yuborish</b>\n\nKimga yubormoqchisiz?",
        reply_markup=broadcast_target_kb()
    )


@router.callback_query(F.data.startswith("broadcast_"))
async def broadcast_target_selected(callback: CallbackQuery, state: FSMContext):
    if not await is_admin(callback.from_user.id):
        await callback.answer("⛔ Ruxsat yo'q!")
        return

    target = callback.data.replace("broadcast_", "")

    if target == "cancel":
        await state.clear()
        await callback.message.edit_text("❌ Bekor qilindi.")
        await callback.message.answer("Admin panel:", reply_markup=admin_menu())
        await callback.answer()
        return

    await state.update_data(target=target)
    await state.set_state(BroadcastForm.message_text)
    await callback.message.edit_text(
        "✍️ Xabar matnini kiriting:\n"
        "<i>HTML formatlash: <b>qalin</b>, <i>qiya</i></i>"
    )
    await callback.answer()


@router.message(BroadcastForm.message_text)
async def broadcast_message(message: Message, state: FSMContext):
    if not await is_admin(message.from_user.id):
        return

    await state.update_data(message_text=message.text)
    data = await state.get_data()
    target_text = "Hamma" if data["target"] == "all" else "Ko'ngillilar"

    await state.set_state(BroadcastForm.confirm)
    await message.answer(
        f"📢 <b>Kimga:</b> {target_text}\n\n"
        f"<b>Matn:</b>\n{message.text}\n\n"
        f"Yuborishni tasdiqlaysizmi?",
        reply_markup=confirm_kb("broadcast")
    )


@router.callback_query(F.data == "confirm_broadcast")
async def broadcast_confirmed(callback: CallbackQuery, state: FSMContext, bot: Bot):
    if not await is_admin(callback.from_user.id):
        await callback.answer("⛔ Ruxsat yo'q!")
        return

    data = await state.get_data()
    await state.clear()

    text = data.get("message_text", "")
    user_ids = await get_all_active_user_ids()

    await callback.message.edit_text(f"⏳ Yuborilmoqda... (0/{len(user_ids)})")

    sent = 0
    failed = 0
    for user_id in user_ids:
        try:
            await bot.send_message(
                chat_id=user_id,
                text=f"📢 <b>EcoUlash xabari:</b>\n\n{text}"
            )
            sent += 1
        except Exception:
            failed += 1

    await log_event("broadcast", callback.from_user.id, f"sent={sent}")
    await callback.message.answer(
        f"✅ <b>Xabar yuborildi!</b>\n\n"
        f"✔️ Muvaffaqiyatli: <b>{sent}</b>\n"
        f"❌ Yuborilmadi: <b>{failed}</b>",
        reply_markup=admin_menu()
    )
    await callback.answer()


@router.callback_query(F.data == "cancel_broadcast")
async def broadcast_cancelled(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ Bekor qilindi.")
    await callback.message.answer("Admin panel:", reply_markup=admin_menu())
    await callback.answer()
