from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command
from aiogram import Bot

from database.db import (
    get_stats, get_all_users, get_all_active_user_ids,
    get_donations, get_requests, get_all_volunteers, log_event
)
from keyboards.main_kb import admin_menu, main_menu, broadcast_target_kb, confirm_kb
from utils.config import ADMIN_IDS

router = Router()


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


class BroadcastForm(StatesGroup):
    target = State()
    message_text = State()
    confirm = State()


# ── ADMIN PANEL ───────────────────────────────────────────────────────────────

@router.message(Command("admin"))
async def admin_panel(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("Ruxsat yoq!")
        return
    stats = await get_stats()
    text = (
        "Admin Panel\n\n"
        "Foydalanuvchilar: " + str(stats["total_users"]) + "\n"
        "Ehsonlar: " + str(stats["total_donations"]) + "\n"
        "Sorovlar: " + str(stats["total_requests"]) + "\n"
        "Kongillilar: " + str(stats["total_volunteers"])
    )
    await message.answer(text, reply_markup=admin_menu())


@router.message(F.text == "🏠 Asosiy menyu")
async def back_to_main(message: Message):
    await message.answer("Asosiy menyu:", reply_markup=main_menu())


# ── STATISTIKA ────────────────────────────────────────────────────────────────

@router.message(F.text == "📊 Statistika")
async def admin_stats(message: Message):
    stats = await get_stats()
    lines = [
        "Statistika",
        "",
        "Jami foydalanuvchilar: " + str(stats["total_users"]),
        "Bugun: " + str(stats["new_users_today"]),
        "",
        "Jami ehsonlar: " + str(stats["total_donations"]),
        "Kutayotgan: " + str(stats["pending_donations"]),
        "",
        "Jami sorovlar: " + str(stats["total_requests"]),
        "Kutayotgan: " + str(stats["pending_requests"]),
        "",
        "Kongillilar: " + str(stats["total_volunteers"]),
    ]
    kb = admin_menu() if is_admin(message.from_user.id) else main_menu()
    await message.answer("\n".join(lines), reply_markup=kb)


# ── FOYDALANUVCHILAR ──────────────────────────────────────────────────────────

@router.message(F.text == "👥 Foydalanuvchilar")
async def admin_users(message: Message):
    if not is_admin(message.from_user.id):
        return
    users = await get_all_users()
    if not users:
        await message.answer("Foydalanuvchilar yoq.", reply_markup=admin_menu())
        return
    lines = ["Foydalanuvchilar: " + str(len(users)) + " ta", ""]
    for i, row in enumerate(users[:30], 1):
        # row = (user_id, username, full_name, phone)
        uid, uname, fname, phone = row
        un = "@" + uname if uname else "-"
        ph = phone if phone else "-"
        lines.append(str(i) + ". " + str(fname) + " | " + ph + " | " + un)
    if len(users) > 30:
        lines.append("...va yana " + str(len(users) - 30) + " ta")
    await message.answer("\n".join(lines), reply_markup=admin_menu())


# ── RO'YXATDAN O'TGANLAR ──────────────────────────────────────────────────────

@router.message(F.text == "📝 Ro'yxatdan o'tganlar")
async def admin_registered(message: Message):
    if not is_admin(message.from_user.id):
        return
    users = await get_all_users()
    registered = [u for u in users if u[3]]  # phone bor
    if not registered:
        await message.answer("Royxatdan otganlar yoq.", reply_markup=admin_menu())
        return
    lines = ["Royxatdan otganlar: " + str(len(registered)) + " ta", ""]
    for i, row in enumerate(registered[:30], 1):
        uid, uname, fname, phone = row
        un = "@" + uname if uname else "-"
        lines.append(str(i) + ". " + str(fname) + " | " + str(phone) + " | " + un)
    if len(registered) > 30:
        lines.append("...va yana " + str(len(registered) - 30) + " ta")
    await message.answer("\n".join(lines), reply_markup=admin_menu())


# ── EHSONLAR ──────────────────────────────────────────────────────────────────

@router.message(F.text == "🎁 Ehsonlar")
async def admin_donations(message: Message):
    if not is_admin(message.from_user.id):
        return
    donations = await get_donations()
    if not donations:
        await message.answer("Ehsonlar yoq.", reply_markup=admin_menu())
        return
    lines = ["Ehsonlar: " + str(len(donations)) + " ta", ""]
    for i, d in enumerate(donations[:20], 1):
        lines.append(str(i) + ". " + str(d[2]) + " - " + str(d[3]) + " dona | " + str(d[5]))
    await message.answer("\n".join(lines), reply_markup=admin_menu())


# ── SO'ROVLAR ─────────────────────────────────────────────────────────────────

@router.message(F.text == "📋 So'rovlar")
async def admin_requests(message: Message):
    if not is_admin(message.from_user.id):
        return
    requests = await get_requests()
    if not requests:
        await message.answer("Sorovlar yoq.", reply_markup=admin_menu())
        return
    lines = ["Sorovlar: " + str(len(requests)) + " ta", ""]
    for i, r in enumerate(requests[:20], 1):
        lines.append(str(i) + ". " + str(r[2]) + " - " + str(r[3]) + " dona | " + str(r[5]))
    await message.answer("\n".join(lines), reply_markup=admin_menu())


# ── KO'NGILLILAR ──────────────────────────────────────────────────────────────

@router.message(F.text == "Kongillilar royxati")
async def admin_volunteers(message: Message):
    if not is_admin(message.from_user.id):
        return
    volunteers = await get_all_volunteers()
    if not volunteers:
        await message.answer("Kongillilar yoq.", reply_markup=admin_menu())
        return
    lines = ["Kongillilar: " + str(len(volunteers)) + " ta", ""]
    for i, v in enumerate(volunteers, 1):
        # v = (user_id, full_name, phone, skills, availability)
        uid, fname, phone, skills, avail = v
        name = fname if fname else "Nomalum"
        tel = phone if phone else "-"
        lines.append(str(i) + ". " + name)
        lines.append("   Tel: " + tel)
        lines.append("   Komak: " + str(skills))
        lines.append("   Vaqt: " + str(avail))
        lines.append("")
    await message.answer("\n".join(lines), reply_markup=admin_menu())


# ── XABAR YUBORISH ────────────────────────────────────────────────────────────

@router.message(F.text == "📢 Xabar yuborish")
async def broadcast_start(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.set_state(BroadcastForm.target)
    await message.answer("Kimga yubormoqchisiz?", reply_markup=broadcast_target_kb())


@router.callback_query(F.data.startswith("broadcast_"))
async def broadcast_target_selected(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("Ruxsat yoq!")
        return
    target = callback.data.replace("broadcast_", "")
    if target == "cancel":
        await state.clear()
        await callback.message.edit_text("Bekor qilindi.")
        await callback.message.answer("Admin panel:", reply_markup=admin_menu())
        await callback.answer()
        return
    await state.update_data(target=target)
    await state.set_state(BroadcastForm.message_text)
    await callback.message.edit_text("Xabar matnini kiriting:")
    await callback.answer()


@router.message(BroadcastForm.message_text)
async def broadcast_message(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.update_data(message_text=message.text)
    data = await state.get_data()
    target_text = "Hamma" if data["target"] == "all" else "Kongillilar"
    await state.set_state(BroadcastForm.confirm)
    await message.answer(
        "Kimga: " + target_text + "\n\nMatn:\n" + message.text + "\n\nTasdiqlaysizmi?",
        reply_markup=confirm_kb("broadcast")
    )


@router.callback_query(F.data == "confirm_broadcast")
async def broadcast_confirmed(callback: CallbackQuery, state: FSMContext, bot: Bot):
    if not is_admin(callback.from_user.id):
        await callback.answer("Ruxsat yoq!")
        return
    data = await state.get_data()
    await state.clear()
    text = data.get("message_text", "")
    user_ids = await get_all_active_user_ids()
    await callback.message.edit_text("Yuborilmoqda... 0/" + str(len(user_ids)))
    sent = 0
    failed = 0
    for uid in user_ids:
        try:
            await bot.send_message(chat_id=uid, text="EcoUlash xabari:\n\n" + text)
            sent += 1
        except Exception:
            failed += 1
    await log_event("broadcast", callback.from_user.id, "sent=" + str(sent))
    await callback.message.answer(
        "Xabar yuborildi!\nMuvaffaqiyatli: " + str(sent) + "\nYuborilmadi: " + str(failed),
        reply_markup=admin_menu()
    )
    await callback.answer()


@router.callback_query(F.data == "cancel_broadcast")
async def broadcast_cancelled(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("Bekor qilindi.")
    await callback.message.answer("Admin panel:", reply_markup=admin_menu())
    await callback.answer()
