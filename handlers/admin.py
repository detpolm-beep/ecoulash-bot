from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command
from aiogram import Bot

from database.db import (
    get_stats, get_all_users, get_all_active_user_ids,
    get_donations, get_requests, log_event
)
from keyboards.main_kb import admin_menu, main_menu, broadcast_target_kb
from utils.config import ADMIN_IDS

router = Router()


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


class BroadcastForm(StatesGroup):
    target = State()
    message_text = State()
    confirm = State()


# ===== ADMIN PANEL =====
@router.message(Command("admin"))
async def admin_panel(message: Message):
    if not is_admin(message.from_user.id):
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
    await message.answer("🏠 Asosiy menyu:", reply_markup=main_menu())


# ===== STATISTIKA =====
@router.message(F.text == "📊 Statistika")
async def admin_stats(message: Message):
    if not is_admin(message.from_user.id):
        return

    stats = await get_stats()
    text = (
        "📊 <b>Batafsil Statistika</b>\n"
        "━━━━━━━━━━━━━━━━\n\n"
        f"👥 Jami foydalanuvchilar: <b>{stats['total_users']}</b>\n"
        f"🆕 Bugun: <b>{stats['new_users_today']}</b>\n\n"
        f"♻️ Jami ehsonlar: <b>{stats['total_donations']}</b>\n"
        f"⏳ Kutayotgan: <b>{stats['pending_donations']}</b>\n\n"
        f"🤲 Jami so'rovlar: <b>{stats['total_requests']}</b>\n"
        f"⏳ Kutayotgan: <b>{stats['pending_requests']}</b>\n\n"
        f"🙋 Ko'ngillilar: <b>{stats['total_volunteers']}</b>"
    )
    await message.answer(text, reply_markup=admin_menu())


# ===== FOYDALANUVCHILAR =====
@router.message(F.text == "👥 Foydalanuvchilar")
async def admin_users(message: Message):
    if not is_admin(message.from_user.id):
        return

    users = await get_all_users()
    if not users:
        await message.answer("Foydalanuvchilar yo'q.")
        return

    text = f"👥 <b>Foydalanuvchilar ({len(users)} ta):</b>\n\n"
    for i, user in enumerate(users[:30], 1):
        user_id, username, full_name = user
        uname = f"@{username}" if username else "yo'q"
        text += f"{i}. {full_name} ({uname}) — <code>{user_id}</code>\n"

    if len(users) > 30:
        text += f"\n<i>...va yana {len(users) - 30} ta</i>"

    await message.answer(text, reply_markup=admin_menu())


# ===== EHSONLAR =====
@router.message(F.text == "🎁 Ehsonlar")
async def admin_donations(message: Message):
    if not is_admin(message.from_user.id):
        return

    donations = await get_donations()
    if not donations:
        await message.answer("Ehsonlar yo'q.")
        return

    text = f"♻️ <b>Ehsonlar ({len(donations)} ta):</b>\n\n"
    for i, d in enumerate(donations[:20], 1):
        # (id, donor_id, item_name, quantity, description, status, created_at)
        text += (
            f"{i}. <b>{d[2]}</b> — {d[3]} dona\n"
            f"   👤 ID: <code>{d[1]}</code> | 📌 {d[5]}\n\n"
        )

    await message.answer(text, reply_markup=admin_menu())


# ===== SO'ROVLAR =====
@router.message(F.text == "📋 So'rovlar")
async def admin_requests(message: Message):
    if not is_admin(message.from_user.id):
        return

    requests = await get_requests()
    if not requests:
        await message.answer("So'rovlar yo'q.")
        return

    text = f"🤲 <b>So'rovlar ({len(requests)} ta):</b>\n\n"
    for i, r in enumerate(requests[:20], 1):
        # (id, user_id, item_name, quantity, description, status, created_at)
        text += (
            f"{i}. <b>{r[2]}</b> — {r[3]} dona\n"
            f"   👤 ID: <code>{r[1]}</code> | 📌 {r[5]}\n\n"
        )

    await message.answer(text, reply_markup=admin_menu())


# ===== XABAR YUBORISH (BROADCAST) =====
@router.message(F.text == "📢 Xabar yuborish")
async def broadcast_start(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return

    await state.set_state(BroadcastForm.target)
    await message.answer(
        "📢 <b>Xabar yuborish</b>\n\nKimga yubormoqchisiz?",
        reply_markup=broadcast_target_kb()
    )


@router.callback_query(F.data.startswith("broadcast_"))
async def broadcast_target_selected(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
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
        "<i>(HTML formatlash qo'llab-quvvatlanadi: "
        "&lt;b&gt;qalin&lt;/b&gt;, &lt;i&gt;qiya&lt;/i&gt;)</i>"
    )
    await callback.answer()


@router.message(BroadcastForm.message_text)
async def broadcast_message(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return

    await state.update_data(message_text=message.text)
    data = await state.get_data()

    target_text = "Hamma foydalanuvchilarga" if data["target"] == "all" else "Ko'ngillilarga"

    preview = (
        f"📢 <b>Xabar ko'rgazmasi:</b>\n\n"
        f"👥 Kimga: <b>{target_text}</b>\n"
        f"📝 Matn:\n\n{message.text}\n\n"
        f"Yuborishni tasdiqlaysizmi?"
    )

    from keyboards.main_kb import confirm_kb
    await state.set_state(BroadcastForm.confirm)
    await message.answer(preview, reply_markup=confirm_kb("broadcast"))


@router.callback_query(F.data == "confirm_broadcast")
async def broadcast_confirmed(callback: CallbackQuery, state: FSMContext, bot: Bot):
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Ruxsat yo'q!")
        return

    data = await state.get_data()
    await state.clear()

    target = data.get("target", "all")
    text = data.get("message_text", "")

    user_ids = await get_all_active_user_ids()

    await callback.message.edit_text(
        f"⏳ Xabar yuborilmoqda... (0/{len(user_ids)})"
    )

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

    await log_event("broadcast", callback.from_user.id, f"sent={sent},failed={failed}")

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
    await callback.message.edit_text("❌ Xabar yuborish bekor qilindi.")
    await callback.message.answer("Admin panel:", reply_markup=admin_menu())
    await callback.answer()
