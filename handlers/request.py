from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database.db import add_request, log_event
from keyboards.main_kb import main_menu, cancel_button, confirm_kb

router = Router()


class RequestForm(StatesGroup):
    item_name = State()
    quantity = State()
    description = State()
    confirm = State()


@router.message(F.text == "🤲 Yordam so'rash")
async def request_start(message: Message, state: FSMContext):
    await log_event("request_start", message.from_user.id)
    await state.set_state(RequestForm.item_name)
    await message.answer(
        "🤲 <b>Yordam so'rash</b>\n\n"
        "Qanday buyum kerak?\n"
        "<i>Masalan: kiyim, oyoq kiyim, kitob, o'yinchoq...</i>",
        reply_markup=cancel_button()
    )


@router.message(RequestForm.item_name)
async def request_item(message: Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("❌ Bekor qilindi.", reply_markup=main_menu())
        return

    await state.update_data(item_name=message.text)
    await state.set_state(RequestForm.quantity)
    await message.answer(
        "🔢 Nechta kerak?\n<i>Faqat raqam kiriting</i>",
        reply_markup=cancel_button()
    )


@router.message(RequestForm.quantity)
async def request_quantity(message: Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("❌ Bekor qilindi.", reply_markup=main_menu())
        return

    if not message.text.isdigit():
        await message.answer("⚠️ Faqat raqam kiriting!")
        return

    await state.update_data(quantity=int(message.text))
    await state.set_state(RequestForm.description)
    await message.answer(
        "📝 Qo'shimcha ma'lumot kiriting:\n"
        "<i>(o'lchami, yoshi va h.k.) yoki 'yo'q' deb yozing</i>",
        reply_markup=cancel_button()
    )


@router.message(RequestForm.description)
async def request_description(message: Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("❌ Bekor qilindi.", reply_markup=main_menu())
        return

    data = await state.get_data()
    description = message.text if message.text.lower() != "yo'q" else ""
    await state.update_data(description=description)

    yoq = "Yo'q"
    summary = (
        f"✅ <b>So'rov ma'lumotlari:</b>\n\n"
        f"📦 Buyum: <b>{data['item_name']}</b>\n"
        f"🔢 Miqdor: <b>{data['quantity']} dona</b>\n"
        f"📝 Izoh: <b>{description or yoq}</b>\n\n"
        f"Tasdiqlaysizmi?"
    )

    await state.set_state(RequestForm.confirm)
    await message.answer(summary, reply_markup=confirm_kb("request"))


@router.message(RequestForm.confirm)
async def request_text_confirm(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Bekor qilindi.", reply_markup=main_menu())


@router.callback_query(F.data == "confirm_request")
async def request_confirmed(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await state.clear()

    await add_request(
        user_id=callback.from_user.id,
        item_name=data.get("item_name", ""),
        quantity=data.get("quantity", 1),
        description=data.get("description", "")
    )
    await log_event("request_completed", callback.from_user.id, data.get("item_name"))

    await callback.message.edit_text(
        "✅ <b>So'rovingiz qabul qilindi!</b>\n\n"
        "Adminlar so'rovingizni ko'rib chiqib, siz bilan bog'lanadi.\n\n"
        "🌿 EcoUlash — insonlarga yordam, tabiatga foyda!"
    )
    await callback.message.answer("🏠 Asosiy menyu:", reply_markup=main_menu())
    await callback.answer()


@router.callback_query(F.data == "cancel_request")
async def request_cancelled(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ So'rov bekor qilindi.")
    await callback.message.answer("🏠 Asosiy menyu:", reply_markup=main_menu())
    await callback.answer()
