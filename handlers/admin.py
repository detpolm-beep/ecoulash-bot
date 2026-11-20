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


@router.message(Command("admin"))
async def admin_panel(message: Message):
    if not await is_admin(message.from_user.id):
        await message.answer("Ruxsat yoq!")
        return
    stats = await get_stats()
    text = (
        "Admin Panel\n\n"
        "Foydalanuvchilar: " + str(stats["total_users"]) + "\n"
        "Ehsonlar: " + str(stats["total_donations"]) + "\n"
        "Sorovlar: " + str(stats["total_requests"]) + "\n"
        "Kongillilar: " + str(stats["total_volunteers"]) + "\n"
    )
    await message.answer(text, reply_markup=admin_menu())


@router.message(F.text == "🏠 Asosiy menyu")
async def back_to_main(message: Message):
    await message.answer("Asosiy menyu:", reply_markup=main_menu())


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
    text = "\n".join(lines)
    if await is_admin(message.from_user.id):
        await message.answer(text, reply_markup=admin_menu())
    else:
        await message.answer(text, reply_markup=main_menu())


@router.message(F.text == "👥 Foydalanuvchilar")
async def admin_users(message: Message):
    if not await is_admin(message.from_user.id):
        return
    users = await get_all_users()
    if not users:
        await message.answer("Foydalanuvchilar yoq.", reply_markup=admin_menu())
        return
    lines = ["Foydalanuvchilar: " + str(len(users)) + " ta", ""]
    for i, user in enumerate(users[:30], 1):
        user_id, username, full_name, phone = user
        uname = "@" + username if username else "-"
        phone_str = phone if phone else "-"
        lines.append(str(i) + ". " + str(full_name) + " | " + uname + " | " + phone_str)
    if len(users) > 30:
        lines.append("...va yana " + str(len(users) - 30) + " ta")
    await message.answer("\n".join(lines), reply_markup=admin_menu())


@router.message(F.text == "🎁 Ehsonlar")
async def admin_donations(message: Message):
    if not await is_admin(message.from_user.id):
        return
    donations = await get_donations()
    if not donations:
        await message.answer("Ehsonlar yoq.", reply_markup=admin_menu())
        return
    lines = ["Ehsonlar: " + str(len(donations)) + " ta", ""]
    for i, d in enumerate(donations[:20], 1):
        lines.append(str(i) + ". " + str(d[2]) + " - " + str(d[3]) + " dona | " + str(d[5]))
    await message.answer("\n".join(lines), reply_markup=admin_menu())


@router.message(F.text == "📋 So'rovlar")
async def admin_requests(message: Message):
    if not await is_admin(message.from_user.id):
        return
    requests = await get_requests()
    if not requests:
        await message.answer("Sorovlar yoq.", reply_markup=admin_menu())
        return
    lines = ["Sorovlar: " + str(len(requests)) + " ta", ""]
    for i, r in enumerate(requests[:20], 1):
        lines.append(str(i) + ". " + str(r[2]) + " - " + str(r[3]) + " dona | " + str(r[5]))
    await message.answer("\n".join(lines), reply_markup=admin_menu())


@router.message(F.text == "🙋 Ko'ngillilar")
async def admin_volunteers(message: Message):
    if not await is_admin(message.from_user.id):
        return
    volunteers = await get_all_volunteers()
    if not volunteers:
        await message.answer("Kongillilar yoq.", reply_markup=admin_menu())
        return
    lines = ["Kongillilar: " + str(len(volunteers)) + " ta", ""]
    for i, v in enumerate(volunteers, 1):
        user_id, full_name, phone, skills, availability = v
        name = full_name if full_name else "Nomalum"
        tel = phone if phone else "-"
        lines.append(str(i) + ". " + name)
        lines.append("   Tel: " + tel)
        lines.append("   Komak: " + str(skills))
        lines.append("   Vaqt: " + str(availability))
        lines.append("")
    await message.answer("\n".join(lines), reply_markup=admin_menu())


@router.message(F.text == "➕ Admin qo'shish")
async def add_admin_start(message: Message, state: FSMContext):
    if not await is_admin(message.from_user.id):
        return
    await state.set_state(AddAdminForm.user_id)
    await message.answer(
        "Yangi adminning Telegram ID sini kiriting:\n"
        "(Foydalanuvchi @userinfobot ga /start yuborsa ID sini biladi)",
        reply_markup=main_menu()
    )


@router.message(AddAdminForm.user_id)
async def add_admin_id(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Faqat raqam kiriting! Masalan: 123456789")
        return
    new_admin_id = int(message.text)
    await add_admin(new_admin_id, message.from_user.id)
    await state.clear()
    await message.answer(
        "Admin qoshildi! ID: " + str(new_admin_id) + "\n"
        "Endi u kishi /admin buyrug'i orqali admin panelga kira oladi.",
        reply_markup=admin_menu()
    )


@router.message(F.text == "➖ Admin o'chirish")
async def remove_admin_start(message: Message, state: FSMContext):
    if not await is_admin(message.from_user.id):
        return
    admins = await get_all_admins()
    if not admins:
        await message.answer("Adminlar yoq.", reply_markup=admin_menu())
        return
    lines = ["Mavjud adminlar:", ""]
    for i, a in enumerate(admins, 1):
        user_id, full_name, username = a
        uname = "@" + username if username else "-"
        name = full_name if full_name else "Nomalum"
        lines.append(str(i) + ". " + name + " (" + uname + ") - " + str(user_id))
    lines.append("")
    lines.append("Ochirish uchun admin ID sini kiriting:")
    await state.set_state(RemoveAdminForm.user_id)
    await message.answer("\n".join(lines), reply_markup=main_menu())


@router.message(RemoveAdminForm.user_id)
async def remove_admin_id(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Faqat raqam kiriting!")
        return
    admin_id = int(message.text)
    await remove_admin(admin_id)
    await state.clear()
    await message.answer("Admin ochirildi: " + str(admin_id), reply_markup=admin_menu())


@router.message(F.text == "📢 Xabar yuborish")
async def broadcast_start(message: Message, state: FSMContext):
    if not await is_admin(message.from_user.id):
        return
    await state.set_state(BroadcastForm.target)
    await message.answer("Kimga yubormoqchisiz?", reply_markup=broadcast_target_kb())


@router.callback_query(F.data.startswith("broadcast_"))
async def broadcast_target_selected(callback: CallbackQuery, state: FSMContext):
    if not await is_admin(callback.from_user.id):
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
    if not await is_admin(message.from_user.id):
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
    if not await is_admin(callback.from_user.id):
        await callback.answer("Ruxsat yoq!")
        return
    data = await state.get_data()
    await state.clear()
    text = data.get("message_text", "")
    user_ids = await get_all_active_user_ids()
    await callback.message.edit_text("Yuborilmoqda... 0/" + str(len(user_ids)))
    sent = 0
    failed = 0
    for user_id in user_ids:
        try:
            await bot.send_message(chat_id=user_id, text="EcoUlash xabari:\n\n" + text)
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
