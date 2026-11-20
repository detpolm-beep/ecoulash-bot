from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database.db import add_volunteer, log_event
from keyboards.main_kb import main_menu, cancel_button, confirm_kb

router = Router()


class VolunteerForm(StatesGroup):
    skills = State()
    availability = State()
    confirm = State()


@router.message(F.text == "🙋 Ko'ngilli bo'lish")
async def volunteer_start(message: Message, state: FSMContext):
    await log_event("volunteer_start", message.from_user.id)
    await state.set_state(VolunteerForm.skills)
    await message.answer(
        "🙋 <b>Ko'ngilli bo'lish</b>\n\n"
        "Siz qanday ko'maklasha olasiz?\n\n"
        "<i>Masalan:\n"
        "• Buyum yig'ish va tashish\n"
        "• Tikuvchilik va ta'mirlash\n"
        "• Tarqatish va yetkazib berish\n"
        "• Reklama va tarqatma\n"
        "• Boshqa...</i>",
        reply_markup=cancel_button()
    )


@router.message(VolunteerForm.skills)
async def volunteer_skills(message: Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("❌ Bekor qilindi.", reply_markup=main_menu())
        return

    await state.update_data(skills=message.text)
    await state.set_state(VolunteerForm.availability)
    await message.answer(
        "🗓️ Qachon vaqtingiz bor?\n\n"
        "<i>Masalan:\n"
        "• Hafta oxiri\n"
        "• Har kuni kechqurun\n"
        "• Dam olish kunlari\n"
        "• Istalgan vaqt...</i>",
        reply_markup=cancel_button()
    )


@router.message(VolunteerForm.availability)
async def volunteer_availability(message: Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("❌ Bekor qilindi.", reply_markup=main_menu())
        return

    data = await state.get_data()
    await state.update_data(availability=message.text)

    summary = (
        f"✅ <b>Ko'ngilli ma'lumotlari:</b>\n\n"
        f"💪 Ko'mak turi: <b>{data['skills']}</b>\n"
        f"🗓️ Vaqt: <b>{message.text}</b>\n\n"
        f"Ro'yxatdan o'tishni tasdiqlaysizmi?"
    )

    await state.set_state(VolunteerForm.confirm)
    await message.answer(summary, reply_markup=confirm_kb("volunteer"))


@router.message(VolunteerForm.confirm)
async def volunteer_text_confirm(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Bekor qilindi.", reply_markup=main_menu())


@router.callback_query(F.data == "confirm_volunteer")
async def volunteer_confirmed(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await state.clear()

    await add_volunteer(
        user_id=callback.from_user.id,
        skills=data.get("skills", ""),
        availability=data.get("availability", "")
    )
    await log_event("volunteer_registered", callback.from_user.id)

    await callback.message.edit_text(
        "🎉 <b>Ko'ngilli sifatida ro'yxatdan o'tdingiz!</b>\n\n"
        "Rahmat! Siz EcoUlash jamoasining bir qismiga aylandingiz.\n\n"
        "Yaqin orada adminlar siz bilan bog'lanadi. 🌿"
    )
    await callback.message.answer("🏠 Asosiy menyu:", reply_markup=main_menu())
    await callback.answer()


@router.callback_query(F.data == "cancel_volunteer")
async def volunteer_cancelled(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ Ro'yxatdan o'tish bekor qilindi.")
    await callback.message.answer("🏠 Asosiy menyu:", reply_markup=main_menu())
    await callback.answer()
