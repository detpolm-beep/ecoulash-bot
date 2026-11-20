from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database.db import add_volunteer, log_event
from keyboards.main_kb import main_menu, cancel_button

router = Router()


class VolunteerForm(StatesGroup):
    skills = State()
    availability = State()


@router.message(F.text == "🙋 Ko'ngilli bo'lish")
async def volunteer_start(message: Message, state: FSMContext):
    await state.clear()
    await log_event("volunteer_start", message.from_user.id)
    await state.set_state(VolunteerForm.skills)
    await message.answer(
        "🙋 <b>Ko'ngilli bo'lish</b>\n\n"
        "Qanday yordam bera olasiz?\n\n"
        "<i>Masalan:\n"
        "• Buyum yig'ish va tashish\n"
        "• Tikuvchilik va ta'mirlash\n"
        "• Tarqatish va yetkazib berish\n"
        "• Boshqa...</i>",
        reply_markup=cancel_button()
    )


@router.message(VolunteerForm.skills)
async def volunteer_skills(message: Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("Bekor qilindi.", reply_markup=main_menu())
        return

    await state.update_data(skills=message.text)
    await state.set_state(VolunteerForm.availability)
    await message.answer(
        "Qachon vaqtingiz bor?\n\n"
        "<i>Masalan:\n"
        "• Hafta oxiri\n"
        "• Har kuni kechqurun\n"
        "• Istalgan vaqt...</i>",
        reply_markup=cancel_button()
    )


@router.message(VolunteerForm.availability)
async def volunteer_availability(message: Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("Bekor qilindi.", reply_markup=main_menu())
        return

    data = await state.get_data()
    skills = data.get("skills", "")
    availability = message.text

    await add_volunteer(
        user_id=message.from_user.id,
        skills=skills,
        availability=availability
    )
    await log_event("volunteer_registered", message.from_user.id)
    await state.clear()

    await message.answer(
        "Ko'ngilli sifatida ro'yxatdan o'tdingiz!\n\n"
        "Koмak turi: " + skills + "\n"
        "Vaqt: " + availability + "\n\n"
        "Rahmat! Adminlar siz bilan bog'lanadi.",
        reply_markup=main_menu()
    )
